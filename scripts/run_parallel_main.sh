#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
WORKERS=3
OUT="outputs/final-q1-v1/full-factorial-workers"
MERGED="outputs/final-q1-v1/full-factorial"
CONFIG="config/parameters.yaml"
LOG_DIR="$OUT/logs"
mkdir -p "$OUT" "$LOG_DIR"

for ((i=0; i<WORKERS; i++)); do
  worker_dir=$(printf "%s/worker-%02d" "$OUT" "$i")
  mkdir -p "$worker_dir"
done

pids=()
for ((i=0; i<WORKERS; i++)); do
  log=$(printf "%s/worker-%02d.log" "$LOG_DIR" "$i")
  worker_dir=$(printf "%s/worker-%02d" "$OUT" "$i")
  python -u -m src.experiment \
    --config "$CONFIG" --output-dir "$worker_dir" --mode full --repetitions 30 \
    --worker-index "$i" --worker-count "$WORKERS" --log-level WARNING \
    >"$log" 2>&1 &
  pids+=("$!")
  echo "worker-$i PID=${pids[$i]} output=$worker_dir"
done

status=0
for pid in "${pids[@]}"; do
  if ! wait "$pid"; then status=1; fi
done
if [[ "$status" -ne 0 ]]; then
  echo "At least one worker failed; inspect $LOG_DIR and checkpoint.json files." >&2
  exit "$status"
fi

python -u -m src.merge_parallel_results \
  --config "$CONFIG" --workers-dir "$OUT" --output-dir "$MERGED" \
  --mode full --repetitions 30 --worker-count "$WORKERS"
echo "Merged and audited output: $MERGED"
