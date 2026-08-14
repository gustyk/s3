"""Audit a final result file and its manifest before analysis."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import uuid
from pathlib import Path

REQUIRED_COLUMNS = {
    "run_uuid",
    "run_id",
    "repetition",
    "seed",
    "status",
    "wall_seconds",
    "generated_orders",
    "completed_orders",
    "outstanding_orders",
    "total_late_orders",
    "late_order_ratio",
    "on_time_rate_percent",
    "service_level_percent",
    "picker_utility_percent",
    "conservation_ok",
    "config_sha256",
    "git_commit",
    "git_dirty",
    "source_tree_sha256",
    "model_version",
    "incoming_rate",
    "cart_capacity",
    "trigger_method",
    "batching_method",
    "routing_policy",
    "num_pickers",
    "late_completed_orders",
    "late_outstanding_orders",
    "throughput_per_hour",
    "mean_tardiness_seconds",
    "mean_flow_time_seconds",
    "mean_waiting_time_seconds",
    "mean_cart_utilization_percent",
    "trip_count",
    "sampled_ftwb_interval_seconds",
    "sampled_vtwb_threshold_orders",
    "sampled_urgency_beta",
    "surrogate_calibration_id",
}

REQUIRED_ORDER_COLUMNS = {
    "run_uuid", "order_id", "measurement_eligible", "arrival_seconds", "due_seconds",
    "batch_id", "batch_release_reason", "batch_release_seconds", "batch_order_count",
    "batch_total_pieces", "picker_id", "start_seconds", "completion_seconds",
    "tour_time_seconds", "censor_seconds", "horizon_state", "waiting_observed_seconds",
    "flow_observed_seconds", "late_completed", "overdue_outstanding", "tardiness_seconds",
    "tardiness_lower_bound_seconds", "config_sha256", "source_tree_sha256", "model_version",
    "ftwb_interval_seconds", "vtwb_threshold_orders", "urgency_beta",
    "observation_start_seconds", "observation_end_seconds",
}

NON_NEGATIVE_FIELDS = {
    "generated_orders", "completed_orders", "outstanding_orders", "late_completed_orders",
    "late_outstanding_orders", "throughput_per_hour", "mean_tardiness_seconds",
    "mean_flow_time_seconds", "mean_waiting_time_seconds", "trip_count",
    "total_late_orders", "late_order_ratio", "wall_seconds",
}
PERCENT_FIELDS = {
    "service_level_percent", "on_time_rate_percent", "picker_utility_percent",
    "mean_cart_utilization_percent"
}
REQUIRED_MANIFEST_FIELDS = {
    "status", "expected_runs", "successful_runs", "failed_runs", "results_sha256",
    "config_sha256", "git_commit", "git_dirty", "source_tree_sha256", "model_version",
    "dependency_lock_sha256", "orders_sha256", "order_rows",
}


def _is_sha256(value: object) -> bool:
    text = str(value)
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text.lower())


def audit(results_path: Path, manifest_path: Path) -> dict[str, object]:
    rows = list(csv.DictReader(results_path.open(newline="", encoding="utf-8")))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if missing_manifest := REQUIRED_MANIFEST_FIELDS - set(manifest):
        errors.append(f"missing manifest fields: {sorted(missing_manifest)}")
    columns = set(rows[0]) if rows else set()
    if missing := REQUIRED_COLUMNS - columns:
        errors.append(f"missing columns: {sorted(missing)}")
    uuids = [row.get("run_uuid", "") for row in rows]
    run_ids = [row.get("run_id", "") for row in rows]
    if len(uuids) != len(set(uuids)):
        errors.append("duplicate run_uuid")
    if not all(uuids):
        errors.append("one or more run_uuid values are empty")
    for value in uuids:
        try:
            uuid.UUID(value)
        except ValueError:
            errors.append(f"invalid run_uuid: {value!r}")
    try:
        numeric_run_ids = [int(value) for value in run_ids]
        if len(numeric_run_ids) != len(set(numeric_run_ids)):
            errors.append("duplicate run_id")
        if sorted(numeric_run_ids) != list(range(1, len(rows) + 1)):
            errors.append("run_id values are not a complete 1..N sequence")
    except ValueError:
        errors.append("one or more run_id values are not integers")
    if any(row.get("status") != "success" for row in rows):
        errors.append("one or more runs failed")
    if any(row.get("conservation_ok") != "True" for row in rows):
        errors.append("one or more conservation checks failed")
    for row in rows:
        if columns >= REQUIRED_COLUMNS:
            try:
                generated = int(row["generated_orders"])
                completed = int(row["completed_orders"])
                outstanding = int(row["outstanding_orders"])
                if generated != completed + outstanding:
                    errors.append(f"run {row['run_uuid']} violates count conservation")
                if int(row["late_completed_orders"]) > completed:
                    errors.append(f"run {row['run_uuid']} has late completed > completed")
                if int(row["late_outstanding_orders"]) > outstanding:
                    errors.append(f"run {row['run_uuid']} has late outstanding > outstanding")
                total_late = int(row["late_completed_orders"]) + int(
                    row["late_outstanding_orders"]
                )
                if int(row["total_late_orders"]) != total_late:
                    errors.append(f"run {row['run_uuid']} has inconsistent total late orders")
                expected_rate = total_late / generated if generated else 0.0
                if not math.isclose(float(row["late_order_ratio"]), expected_rate, abs_tol=1e-12):
                    errors.append(f"run {row['run_uuid']} has inconsistent late-order ratio")
                for field in NON_NEGATIVE_FIELDS:
                    value = float(row[field])
                    if not math.isfinite(value) or value < 0:
                        errors.append(f"run {row['run_uuid']} has negative {field}")
                for field in PERCENT_FIELDS:
                    value = float(row[field])
                    if not math.isfinite(value) or not 0 <= value <= 100:
                        errors.append(f"run {row['run_uuid']} has invalid {field}")
            except (TypeError, ValueError):
                errors.append(f"run {row.get('run_uuid', '<unknown>')} has invalid numeric data")

    for field in ("config_sha256", "git_commit", "git_dirty", "source_tree_sha256", "model_version"):
        if field in columns and len({row[field] for row in rows}) > 1:
            errors.append(f"mixed provenance values in {field}")
    if rows:
        for field in (
            "config_sha256", "git_commit", "git_dirty", "source_tree_sha256", "model_version"
        ):
            manifest_value = manifest.get(field)
            if manifest_value is not None and str(manifest_value) != rows[0].get(field):
                errors.append(f"{field} differs between rows and manifest")
    for field in (
        "results_sha256", "orders_sha256", "config_sha256", "source_tree_sha256",
        "dependency_lock_sha256",
    ):
        if field in manifest and not _is_sha256(manifest[field]):
            errors.append(f"manifest {field} is not a SHA-256 digest")
    digest = hashlib.sha256(results_path.read_bytes()).hexdigest()
    if digest != manifest.get("results_sha256"):
        errors.append("results checksum differs from manifest")
    if len(rows) != int(manifest.get("expected_runs", -1)):
        errors.append("row count differs from expected_runs")
    if int(manifest.get("successful_runs", -1)) != len(rows):
        errors.append("successful_runs differs from row count")
    if int(manifest.get("failed_runs", -1)) != 0 or manifest.get("status") != "success":
        errors.append("manifest does not certify a fully successful batch")
    orders_path = results_path.with_name(str(manifest.get("orders_file", "orders.csv")))
    if not orders_path.exists():
        errors.append("orders.csv referenced by manifest is missing")
    else:
        order_digest = hashlib.sha256(orders_path.read_bytes()).hexdigest()
        if order_digest != manifest.get("orders_sha256"):
            errors.append("orders checksum differs from manifest")
        opener = gzip.open if orders_path.suffix == ".gz" else open
        with opener(orders_path, "rt", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            order_header = set(next(reader, []))
            order_rows = sum(1 for _ in reader)
        if missing_order_columns := REQUIRED_ORDER_COLUMNS - order_header:
            errors.append(f"missing per-order columns: {sorted(missing_order_columns)}")
        if order_rows != int(manifest.get("order_rows", -1)):
            errors.append("orders row count differs from manifest")
        if manifest.get("per_order_evidence_persisted") is True and order_rows == 0:
            errors.append("manifest requires per-order evidence but orders.csv is empty")
    report: dict[str, object] = {
        "status": "pass" if not errors else "fail",
        "rows": len(rows),
        "sha256": digest,
        "errors": errors,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    manifest = args.manifest or args.results.with_name("manifest.json")
    report = audit(args.results, manifest)
    rendered = json.dumps(report, indent=2)
    if args.report:
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
