"""Sweep urgency threshold beta for affected heuristics (R1-Mayor #10/R2-Mayor #4)."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from scipy import stats

from src.artifacts import atomic_dataframe_csv, atomic_write_text
from src.audit_results import audit
from src.configuration import LoadedConfig, load_config
from src.experiment import run_experiment

BETA_VALUES = (1, 2, 3, 4)
METHOD_KEYS = {"UrgentPicker": 5, "UrgentCart": 6, "SNH": 7, "MPBH": 8}
BLOCKS = [
    "incoming_rate",
    "num_pickers",
    "batching_method",
    "cart_capacity",
    "routing_policy",
    "repetition",
]


def _config(loaded: LoadedConfig, trigger_key: int, beta: int) -> LoadedConfig:
    params = copy.deepcopy(loaded.values)
    params["experiment_design"]["trigger_method_keys"] = [trigger_key]
    params["trigger_parameters"]["Urgent_threshold"] = beta
    canonical = json.dumps(params, sort_keys=True, separators=(",", ":")).encode()
    return LoadedConfig(loaded.path, params, hashlib.sha256(canonical).hexdigest())


def _paired_against_beta_two(frame: pd.DataFrame) -> pd.DataFrame:
    records = []
    for method, method_rows in frame.groupby("trigger_method"):
        pivot = method_rows.pivot_table(
            index=BLOCKS,
            columns="beta",
            values="total_late_orders",
            aggfunc="first",
        )
        for beta in BETA_VALUES:
            if beta == 2:
                continue
            paired = pivot.dropna(subset=[2, beta])
            difference = paired[beta] - paired[2]
            n = len(difference)
            mean = float(difference.mean()) if n else float("nan")
            sem = float(difference.sem()) if n > 1 else float("nan")
            critical = float(stats.t.ppf(0.975, n - 1)) if n > 1 else float("nan")
            test = stats.ttest_1samp(difference, 0.0) if n > 1 else None
            records.append(
                {
                    "trigger_method": method,
                    "contrast": f"beta={beta} minus beta=2",
                    "paired_blocks": n,
                    "mean_difference_total_late_orders": mean,
                    "ci95_lower": mean - critical * sem if n > 1 else float("nan"),
                    "ci95_upper": mean + critical * sem if n > 1 else float("nan"),
                    "paired_t_p_value": float(test.pvalue) if test is not None else float("nan"),
                }
            )
    return pd.DataFrame(records)


def run_beta_sensitivity(config_path: Path, output_dir: Path, repetitions: int) -> Path:
    """Execute the predeclared beta sweep with CRN; addresses R1#10/R2#4."""
    loaded = load_config(config_path)
    frames: list[pd.DataFrame] = []
    reports = []
    timings = []
    for method, trigger_key in METHOD_KEYS.items():
        for beta in BETA_VALUES:
            config = _config(loaded, trigger_key, beta)
            cell_dir = output_dir / method / f"beta={beta}"
            result_path = run_experiment(config, cell_dir, "full", repetitions)
            report = audit(result_path, result_path.with_name("manifest.json"))
            reports.append(report)
            cell = pd.read_csv(result_path)
            cell["beta"] = beta
            frames.append(cell)
            timings.append(
                {
                    "trigger_method": method,
                    "beta": beta,
                    "runs": len(cell),
                    "wall_seconds": float(cell["wall_seconds"].sum()),
                    "wall_seconds_per_run": float(cell["wall_seconds"].mean()),
                }
            )
    if any(report["status"] != "pass" for report in reports):
        raise RuntimeError("At least one beta-sweep cell failed artifact audit")
    combined = pd.concat(frames, ignore_index=True)
    output_path = output_dir / "beta_sweep_results.csv"
    atomic_dataframe_csv(combined, output_path)
    summary = (
        combined.groupby(["trigger_method", "beta"], as_index=False)
        .agg(
            runs=("run_uuid", "count"),
            total_late_mean=("total_late_orders", "mean"),
            total_late_sd=("total_late_orders", "std"),
            on_time_rate_mean_percent=("on_time_rate_percent", "mean"),
            mean_late_tardiness_seconds=("mean_late_tardiness_seconds", "mean"),
            throughput_mean_per_hour=("throughput_per_hour", "mean"),
            trips_mean=("trip_count", "mean"),
            cart_utilization_mean_percent=("mean_cart_utilization_percent", "mean"),
        )
    )
    atomic_dataframe_csv(summary, output_dir / "beta_sweep_summary.csv")
    atomic_dataframe_csv(
        _paired_against_beta_two(combined), output_dir / "beta_planned_contrasts.csv"
    )
    atomic_dataframe_csv(pd.DataFrame(timings), output_dir / "beta_computation_time.csv")
    manifest = {
        "status": "success",
        "reviewer_ids": ["R1-Mayor #10", "R2-Mayor #4"],
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "config_sha256": loaded.sha256,
        "beta_values": list(BETA_VALUES),
        "affected_methods": list(METHOD_KEYS),
        "baseline_beta": 2,
        "repetitions": repetitions,
        "primary_outcome": "total_late_orders",
        "results_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
        "audit_statuses": [report["status"] for report in reports],
    }
    atomic_write_text(output_dir / "manifest.json", json.dumps(manifest, indent=2))
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=30)
    args = parser.parse_args()
    print(run_beta_sensitivity(args.config, args.output_dir, args.repetitions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
