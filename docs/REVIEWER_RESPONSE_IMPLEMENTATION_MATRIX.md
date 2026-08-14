# Reviewer-response implementation matrix — EJIE-337519

Status: **draft based on corrected-model pilots; final numerical wording awaits
30-replication/tagged outputs**. Original paper remains unchanged.

| Reviewer item | Implementation/evidence | Current finding | Required manuscript action | Status |
|---|---|---|---|---|
| R1-Major #1 — timing vs composition | Explicit 2×3 crossed adapter and paired contrasts; `outputs/ablation-pilot-v1/` | timing MPBH−FTWB = −18 TLO; composition MPBH−FCFS/EDT = −147.42 TLO | Add design, Table/CI, revise Section 5.4 and Proposition 4 if final direction persists | pilot complete; final n=30 pending |
| R1-Major #2 — calibrate F/V | Grid F={60,…,720}, V={4,…,24}; tuning/held-out split; `outputs/benchmark-calibration-pilot-v1/` | pilot optimum F=60, V=4; F-TLO ties but 60 improves throughput/utilization vs canonical 720 | Distinguish canonical from calibrated benchmark; discuss fairness; do not claim F=720 optimal | pilot complete; final n=30 pending |
| R1-Major #5 — additional metrics | Raw order censoring schema and chunked metric builder; `outputs/representative-pilot-v1/additional_metrics/` | late ratio/on-time and completed tardiness estimable; outstanding final tardiness only lower-bounded | Extend Table 4 and define censoring; never label lower bound as exact average tardiness | implemented; final table pending |
| R1-Major #6 — composite inconsistency | One matched scenario×replication function, constant tie=0.5, four weight schemes, Pareto primary | MPBH ranks first under all four pilot weight schemes | Replace Table 4/narrative from one function and explain old aggregation-scope root cause | implemented; final data pending |
| R1-Major #10 / R2-Major #4 — β | β={1,2,3,4} CRN runner with TLO/trip/cart/runtime; `outputs/beta-sensitivity-pilot-v1/` | MPBH β=1 improves TLO by 66.67 vs β=2 but raises trips/runtime and lowers cart fill; other rules null in this slice | Add sensitivity/trade-off subsection; retain β=2 baseline until confirmatory result | pilot complete; final n=30 pending |
| R2-Major #3 — computation/scaling | 30-repeat decision benchmark, calibrated perf-counter overhead, n={10,…,5000}; `outputs/computation_time_final/` | at n=5000 median: MPBH 74.4 ms, SNH 19.9 ms, urgency ≈7 ms; simple triggers <1 ms | Add hardware/protocol, empirical/theoretical complexity and operational latency trade-off | local benchmark complete; tagged rerun pending |
| R1-Minor #4 — Welch warm-up | 24-hour ×10-rep ×8-method Welch pilot; `outputs/welch-stable-24h-v2/` | maximum stabilization = 5,460 s; λ=4/12 pilot shows non-stationary overload | State 91-min warm-up and distinguish overload finite-horizon interpretation from steady state | implemented; independent review pending |
| Algorithm fidelity / terminology | SNH replaces DVNS; MPBH EDD+β+capacity+restoration; event-driven slot-bounded release | 66 tests pass; 93.88% coverage; Ruff/mypy pass | Replace all Section 4 pseudocode/labels and complexity text | local verification complete |

## Draft response language

### R1-Major #1

We thank the reviewer for identifying the confounding between release timing
and batch composition. We refactored the simulation so timing and composition
can be invoked independently and implemented a balanced 2×3 experiment
(FTWB/MPBH timing × FCFS/EDT/MPBH composition) with common random numbers and
planned paired contrasts. The diagnostic pilot indicates that composition may
explain a larger TLO difference than timing, contrary to our original
Proposition 4. We will report the 30-replication result without conditioning on
whether it supports the proposition.

### R1-Major #2

We parameterized and swept F and V with separate tuning and held-out
replications. The pilot selects shorter thresholds (F=60 s, V=4) under the
declared composite criterion; TLO is tied across F in the tested contexts while
throughput/utilization favor shorter F. The revised manuscript will clearly
separate the owner-specified canonical F=720 s treatment from the calibrated
benchmark and will treat this difference as a benchmark-fairness limitation.

### R1-Major #5

All reruns now persist arrival, due, batch, picker, start, completion, horizon
state, censor time, and tardiness fields per order. We add late-order ratio,
on-time rate, completed-order mean tardiness, and conditional late tardiness.
For unfinished orders, exact final tardiness is not observed at a fixed horizon;
we therefore report a clearly labelled horizon lower bound rather than imputing
a fictitious completion.

### R1-Major #6

We traced the discrepancy to two normalization scopes: Table 4 normalized
within scenario cells, whereas the narrative normalized already-aggregated
global means. The corrected analysis uses complete matched
scenario×replication blocks throughout, assigns 0.5 under constant ranges, and
reports three alternative weight schemes. Pareto dominance is now primary and
the weighted score secondary.

### R1-Major #10 / R2-Major #4

We added a β sensitivity study for all four affected heuristics. The pilot shows
a performance–batching–runtime trade-off for MPBH and null TLO sensitivity for
the other rules in the tested slice. We will avoid presenting β as universally
optimal and will base managerial guidance on the final paired confidence
intervals and operational trade-offs.

### R2-Major #3

We benchmarked the isolated decision kernels using 30 timing repetitions at
six pool sizes on an Intel i7-7700 (4 cores/8 threads, 31.88 GiB RAM, Windows
11, Python 3.14.6). Timer overhead was measured and subtracted. Even the
costliest MPBH kernel had a median decision latency of approximately 74.4 ms at
n=5,000, while simpler methods were below 1 ms. The revision will report both
empirical fits and algorithmic bounds, with hardware and protocol details.

## Claims that cannot be retained from the accepted paper

- The exact 27.04% MPBH reduction and all legacy means/effect sizes.
- Table 4 composite values 0.864/0.924 from inconsistent pipelines.
- Table 6 values, especially high-rate/high-picker MPBH TLO 558.52.
- Strong support for Proposition 4 unless the confirmatory crossed experiment
  overturns the pilot direction.
- Any statement that F=720 or V=12 is empirically calibrated/optimal.
- “Average tardiness of all orders” without a censoring qualifier.

## Remaining gates before response text becomes final

1. Freeze a clean signed source/config tag and a priori 30-replication analysis.
2. Execute/audit all reviewer experiments and the 207,360-run factorial.
3. Obtain domain validation and independent statistical review.
4. Regenerate every table/figure and reconcile every proposition.
5. Perform clean-machine independent reproduction and archive immutable data.
