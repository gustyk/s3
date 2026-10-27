"""Parallel, resumable per-worker aggregation for 621M order records."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.additional_metrics import aggregate_order_evidence, build_extended_metrics_from_aggregate


def _aggregate_worker(order_path: Path, partial_path: Path, source_sha256: str) -> str:
    sidecar = partial_path.with_suffix(".json")
    source_stat = order_path.stat()
    if partial_path.exists() and sidecar.exists():
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        if (
            metadata.get("source_sha256") == source_sha256
            and int(metadata.get("source_size", -1)) == source_stat.st_size
            and metadata.get("status") == "success"
        ):
            return str(partial_path)
    raw = aggregate_order_evidence(order_path, progress_label=order_path.parent.name)
    partial_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = partial_path.with_suffix(".csv.tmp")
    raw.to_csv(temporary, index=False)
    temporary.replace(partial_path)
    sidecar.write_text(
        json.dumps(
            {
                "status": "success",
                "created_at_utc": datetime.now(UTC).isoformat(),
                "source": str(order_path.resolve()),
                "source_sha256": source_sha256,
                "source_size": source_stat.st_size,
                "run_rows": len(raw),
                "order_rows": int(raw["raw_measurement_orders"].sum()),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return str(partial_path)


def run(results: Path, workers_dir: Path, output_dir: Path, worker_count: int) -> Path:
    jobs = []
    source_metadata = []
    raw_total_order_rows = 0
    partial_dir = output_dir / "partials"
    for index in range(worker_count):
        worker_dir = workers_dir / f"worker-{index:02d}"
        order_path = worker_dir / "orders.csv.gz"
        manifest_path = worker_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") != "success":
            raise ValueError(f"Worker manifest is not successful: {worker_dir}")
        source_sha256 = str(manifest["orders_sha256"])
        raw_total_order_rows += int(manifest["order_rows"])
        partial_path = partial_dir / f"worker-{index:02d}.csv"
        jobs.append((order_path, partial_path, source_sha256))
        source_metadata.append(
            {
                "worker_index": index,
                "orders_sha256": source_sha256,
                "order_rows": int(manifest["order_rows"]),
                "path": str(order_path),
            }
        )

    partial_paths: list[Path] = []
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(_aggregate_worker, order_path, partial_path, source_sha256): index
            for index, (order_path, partial_path, source_sha256) in enumerate(jobs)
        }
        for future in as_completed(futures):
            path = Path(future.result())
            partial_paths.append(path)
            print(f"worker-{futures[future]:02d} aggregate complete: {path}", flush=True)

    raw = pd.concat((pd.read_csv(path) for path in sorted(partial_paths)), ignore_index=True)
    if raw["run_uuid"].duplicated().any():
        raise ValueError("Per-worker order aggregates contain duplicate run UUIDs")
    return build_extended_metrics_from_aggregate(
        results,
        raw,
        output_dir,
        order_sources=[str(job[0].resolve()) for job in jobs],
        source_metadata={
            "worker_count": worker_count,
            "raw_total_order_rows": raw_total_order_rows,
            "workers": source_metadata,
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--workers-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--worker-count", type=int, default=3)
    args = parser.parse_args()
    print(run(args.results, args.workers_dir, args.output_dir, args.worker_count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
