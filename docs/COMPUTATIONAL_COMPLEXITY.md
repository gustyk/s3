# Computational Complexity and Scalability

Let `n` be waiting orders, `m` item quantities in a route, `b` retained batches,
and `p` pickers. FCFS is `O(n)`; EDT is `O(n log n)`; route expansion and
position translation are `O(m)`. Batch assignment currently sorts retained
batches and scans pending state, up to `O(b log b)`. Urgency forecasting sorts
orders and heap-schedules them, approximately `O(n log n + n log p)` plus route
calculations. DVNS adds multiple sorts/scans and can dominate runtime at high
demand. MPBH is `O(n log n)` plus one route estimate per order.

The current one-second polling processes simplify semantics but add runtime
proportional to horizon × picker/trigger count. Before the final full factorial
run, benchmark and replace polling with equivalent event signaling if pilot
runtime is prohibitive. Any optimization must pass deterministic equivalence
tests to avoid changing scientific behavior.

Final scalability evidence must report wall time, CPU, peak memory, output size,
and throughput in runs/hour against arrival volume, item count, and picker count,
on named hardware and software. This remains pending the frozen release.

The local engineering benchmark produced by `src/benchmark.py` now records
repeated wall/CPU timing, sampled total-process RSS, Python allocation peak,
CPU utilization, Student-t timing intervals, raw CSV size, serialized
result-row size, and an estimated full-result footprint. It also records a
conservative parallel-worker candidate but does not claim deterministic parallel
equivalence. Publication-final measurements must still be rerun on the tagged
release and named target hardware.
