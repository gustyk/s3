#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKERS_DIR="$ROOT/outputs/final-q1-v1/full-factorial-workers"
WORKERS=3

while true; do
  clear
  printf 'S3 main simulation — %s\n\n' "$(date '+%Y-%m-%d %H:%M:%S')"
  WORKERS_DIR="$WORKERS_DIR" WORKERS="$WORKERS" python - <<'PY'
import json, os
from pathlib import Path

root = Path(os.environ["WORKERS_DIR"])
worker_count = int(os.environ["WORKERS"])
total_done = total_expected = 0
for index in range(worker_count):
    directory = root / f"worker-{index:02d}"
    checkpoint = directory / "checkpoint.json"
    manifest = directory / "manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        done = int(data.get("successful_runs", data.get("expected_runs", 0)))
        expected = int(data.get("expected_runs", 0))
        state = "DONE" if data.get("status") == "success" else str(data.get("status"))
        remaining = "0"
    elif checkpoint.exists():
        data = json.loads(checkpoint.read_text(encoding="utf-8"))
        done = int(data.get("completed_runs", 0))
        expected = int(data.get("expected_runs", 0))
        state = "RUNNING"
        remaining = data.get("estimated_remaining_simulation_wall_seconds")
        remaining = "calculating" if remaining is None else f"{float(remaining)/3600:.2f} h"
    else:
        done = expected = 0
        state = "NOT STARTED"
        remaining = "-"
    total_done += done
    total_expected += expected
    pct = 100 * done / expected if expected else 0
    print(f"worker-{index:02d} | {state:11} | {done:>6}/{expected:<6} | {pct:6.2f}% | remaining {remaining}")

print()
if total_expected:
    print(f"TOTAL     | {total_done:>6}/{total_expected:<6} | {100*total_done/total_expected:6.2f}%")
else:
    print("TOTAL     | no checkpoint yet")
merged = root.parent / "full-factorial" / "audit.json"
merged_dir = root.parent / "full-factorial"
if merged.exists():
    print(f"Merged audit: {'PASS' if json.loads(merged.read_text(encoding='utf-8')).get('status') == 'pass' else 'FAIL'}")
else:
    partial_orders = merged_dir / "orders.csv.gz"
    partial_results = merged_dir / "results.csv"
    if partial_orders.exists():
        print(f"MERGE IN PROGRESS | orders.csv.gz {partial_orders.stat().st_size / 1024**3:.2f} GiB")
    elif partial_results.exists():
        print("MERGE IN PROGRESS | results.csv complete; raw orders are being combined")
    else:
        print("Merged audit: not started")
PY
  sleep 30
done
