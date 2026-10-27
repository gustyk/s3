"""Merge and audit disjoint deterministic simulation worker outputs."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from src.audit_results import audit
from src.configuration import load_config
from src.experiment import ORDER_RESULT_FIELDS, RESULT_FIELDS, _file_sha256, _run_uuid, scenarios


def merge(config_path: Path, workers_dir: Path, output_dir: Path, mode: str, repetitions: int, worker_count: int) -> Path:
    config = load_config(config_path)
    worker_dirs = [workers_dir / f"worker-{index:02d}" for index in range(worker_count)]
    manifests = []
    rows: list[dict[str, str]] = []
    for worker_dir in worker_dirs:
        manifest_path = worker_dir / "manifest.json"
        results_path = worker_dir / "results.csv"
        orders_path = worker_dir / "orders.csv.gz"
        if not manifest_path.exists() or not results_path.exists() or not orders_path.exists():
            raise FileNotFoundError(f"Incomplete worker output: {worker_dir}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") != "success":
            raise ValueError(f"Worker is not successful: {worker_dir}")
        if manifest.get("config_sha256") != config.sha256 or manifest.get("mode") != mode:
            raise ValueError(f"Worker provenance/plan mismatch: {worker_dir}")
        worker_index = worker_dirs.index(worker_dir)
        if manifest.get("worker_count") != worker_count or manifest.get("worker_index") != worker_index:
            raise ValueError(f"Worker partition metadata mismatch: {worker_dir}")
        manifests.append(manifest)
        with results_path.open(newline="", encoding="utf-8") as handle:
            worker_rows = list(csv.DictReader(handle))
        if int(manifest.get("expected_runs", -1)) != len(worker_rows):
            raise ValueError(f"Worker row count mismatch: {worker_dir}")
        rows.extend(worker_rows)

    planned = list(scenarios(config.values, mode))
    expected_runs = len(planned) * repetitions
    expected_ids = set(range(1, expected_runs + 1))
    actual_ids = {int(row["run_id"]) for row in rows}
    if actual_ids != expected_ids or len(rows) != expected_runs:
        raise ValueError("Merged run_id set is not exactly the canonical full plan")
    if len({row["run_uuid"] for row in rows}) != expected_runs:
        raise ValueError("Duplicate run_uuid detected across workers")
    expected_uuids = {
        _run_uuid(config.sha256, scenario, repetition)
        for scenario in planned
        for repetition in range(repetitions)
    }
    if {row["run_uuid"] for row in rows} != expected_uuids:
        raise ValueError("Merged run_uuid set differs from canonical scenario/repetition plan")
    if any(row.get("status") != "success" for row in rows):
        raise ValueError("Merged output contains failed runs")
    rows.sort(key=lambda row: int(row["run_id"]))

    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "results.csv"
    orders_path = output_dir / "orders.csv.gz"
    with results_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    order_rows = 0
    seen_order_runs: set[str] = set()
    with gzip.open(orders_path, "wt", newline="", encoding="utf-8") as output_handle:
        writer = csv.DictWriter(output_handle, fieldnames=ORDER_RESULT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for worker_dir in worker_dirs:
            with gzip.open(worker_dir / "orders.csv.gz", "rt", newline="", encoding="utf-8") as input_handle:
                for row in csv.DictReader(input_handle):
                    run_uuid = row.get("run_uuid", "")
                    if run_uuid not in expected_uuids:
                        raise ValueError("Order record belongs to an unknown run")
                    writer.writerow(row)
                    order_rows += 1
                    seen_order_runs.add(run_uuid)
    generated_runs = {
        row["run_uuid"] for row in rows if int(float(row.get("generated_orders", 0) or 0)) > 0
    }
    if not generated_runs.issubset(seen_order_runs):
        raise ValueError("One or more successful runs are missing raw order evidence")

    first = rows[0]
    source_hash = first["source_tree_sha256"]
    manifest = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "status": "success",
        "mode": mode,
        "expected_runs": expected_runs,
        "successful_runs": expected_runs,
        "failed_runs": 0,
        "execution_order_randomized": bool(config.values.get("randomize_execution_order", True)),
        "results_sha256": hashlib.sha256(results_path.read_bytes()).hexdigest(),
        "orders_sha256": hashlib.sha256(orders_path.read_bytes()).hexdigest(),
        "order_rows": order_rows,
        "orders_file": "orders.csv.gz",
        "order_output_compression": "gzip",
        "per_order_evidence_persisted": True,
        "config_path": str(config.path),
        "config_sha256": config.sha256,
        "git_commit": first["git_commit"],
        "git_dirty": first["git_dirty"],
        "source_tree_sha256": source_hash,
        "model_version": first["model_version"],
        "dependency_lock_sha256": _file_sha256(Path("requirements.lock")),
        "worker_count": worker_count,
        "merged_from": [str(path) for path in worker_dirs],
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    report = audit(results_path, manifest_path)
    (output_dir / "audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if report["status"] != "pass":
        raise RuntimeError(f"Merged artifact audit failed: {report['errors']}")
    return results_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/parameters.yaml"))
    parser.add_argument("--workers-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", default="full", choices=("selected", "smoke", "full"))
    parser.add_argument("--repetitions", type=int, required=True)
    parser.add_argument("--worker-count", type=int, default=3)
    args = parser.parse_args()
    print(merge(args.config, args.workers_dir, args.output_dir, args.mode, args.repetitions, args.worker_count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
