"""Build censoring-aware extended Table 4 metrics (R1-Mayor #5)."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd


def aggregate_order_evidence(
    orders_path: Path,
    *,
    chunksize: int = 1_000_000,
    progress_label: str = "orders",
) -> pd.DataFrame:
    """Stream one immutable order artifact into run-level sufficient statistics."""
    partials = []
    columns = [
        "run_uuid",
        "measurement_eligible",
        "completion_seconds",
        "tardiness_seconds",
        "tardiness_lower_bound_seconds",
    ]
    processed = 0
    for chunk in pd.read_csv(orders_path, usecols=columns, chunksize=chunksize):
        eligible = chunk["measurement_eligible"].astype(str).str.lower().eq("true")
        measured = chunk.loc[eligible].copy()
        measured["completed"] = measured["completion_seconds"].notna()
        measured["completed_tardiness"] = pd.to_numeric(
            measured["tardiness_seconds"], errors="coerce"
        ).fillna(0.0)
        measured["outstanding_tardiness_lower_bound"] = pd.to_numeric(
            measured["tardiness_lower_bound_seconds"], errors="coerce"
        ).fillna(0.0)
        partials.append(
            measured.groupby("run_uuid", as_index=False).agg(
                raw_measurement_orders=("run_uuid", "size"),
                completed_order_count=("completed", "sum"),
                completed_tardiness_sum_seconds=("completed_tardiness", "sum"),
                outstanding_tardiness_lower_bound_sum_seconds=(
                    "outstanding_tardiness_lower_bound",
                    "sum",
                ),
            )
        )
        processed += len(chunk)
        if processed % (10 * chunksize) == 0:
            print(f"{progress_label}: {processed:,} order rows processed", flush=True)
    raw = pd.concat(partials, ignore_index=True)
    return raw.groupby("run_uuid", as_index=False).sum(numeric_only=True)


def build_extended_metrics_from_aggregate(
    results_path: Path,
    raw: pd.DataFrame,
    output_dir: Path,
    *,
    order_sources: list[str],
    source_metadata: dict[str, Any] | None = None,
) -> Path:
    """Join run-level order evidence and create reviewer-ready metric outputs."""
    results = pd.read_csv(results_path)
    required_results = {
        "run_uuid",
        "trigger_method",
        "generated_orders",
        "total_late_orders",
        "late_order_ratio",
        "on_time_rate_percent",
        "mean_tardiness_seconds",
        "mean_late_tardiness_seconds",
        "throughput_per_hour",
        "picker_utility_percent",
        "mean_cart_utilization_percent",
        "trip_count",
        "mean_flow_time_seconds",
        "p95_flow_time_seconds",
        "mean_waiting_time_seconds",
        "p95_waiting_time_seconds",
    }
    missing = required_results - set(results)
    if missing:
        raise ValueError(f"Result fields missing: {sorted(missing)}")
    merged = results.merge(raw, on="run_uuid", how="left", validate="one_to_one")
    if not (merged["raw_measurement_orders"] == merged["generated_orders"]).all():
        raise ValueError("Raw-order measurement cohort does not match aggregate denominator")
    merged["mean_tardiness_lower_bound_all_orders_seconds"] = (
        merged["completed_tardiness_sum_seconds"]
        + merged["outstanding_tardiness_lower_bound_sum_seconds"]
    ) / merged["generated_orders"]

    metrics = [
        "total_late_orders",
        "late_order_ratio",
        "on_time_rate_percent",
        "mean_tardiness_seconds",
        "mean_late_tardiness_seconds",
        "mean_tardiness_lower_bound_all_orders_seconds",
        "throughput_per_hour",
        "picker_utility_percent",
        "mean_cart_utilization_percent",
        "trip_count",
        "mean_flow_time_seconds",
        "p95_flow_time_seconds",
        "mean_waiting_time_seconds",
        "p95_waiting_time_seconds",
    ]
    records = []
    for method, rows in merged.groupby("trigger_method"):
        record: dict[str, object] = {"trigger_method": method, "runs": len(rows)}
        for metric in metrics:
            record[f"{metric}_mean"] = float(rows[metric].mean())
            record[f"{metric}_sd"] = float(rows[metric].std(ddof=1))
        records.append(record)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "table4_extended.csv"
    pd.DataFrame(records).sort_values("trigger_method").to_csv(output, index=False)
    notes = (
        "# Extended Table 4 metric definitions\n\n"
        "Addresses R1-Mayor #5. `mean_tardiness_seconds` is calculated over completed orders, "
        "with on-time completions contributing zero. `mean_late_tardiness_seconds` is conditional "
        "on completed-late orders. Outstanding orders are right-censored, so their exact final "
        "tardiness is unknowable at the fixed horizon; `mean_tardiness_lower_bound_all_orders_seconds` "
        "uses max(0, horizon-due) for those orders and must be labelled a conservative lower bound, "
        "not average final tardiness.\n"
    )
    (output_dir / "METRIC_NOTES.md").write_text(notes, encoding="utf-8")
    manifest = {
        "status": "success",
        "reviewer_id": "R1-Mayor #5",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "results": str(results_path.resolve()),
        "orders": order_sources,
        "runs": len(results),
        "raw_measurement_orders": int(raw["raw_measurement_orders"].sum()),
        "raw_total_order_rows": (source_metadata or {}).get("raw_total_order_rows"),
        "censoring_rule": "outstanding exact tardiness unavailable; report horizon lower bound",
        "source_metadata": source_metadata or {},
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output


def build_extended_metrics(
    results_path: Path, orders_path: Path, output_dir: Path
) -> Path:
    """Aggregate run and order evidence without treating censored times as completions."""
    raw = aggregate_order_evidence(orders_path)
    return build_extended_metrics_from_aggregate(
        results_path,
        raw,
        output_dir,
        order_sources=[str(orders_path.resolve())],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("orders", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(build_extended_metrics(args.results, args.orders, args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
