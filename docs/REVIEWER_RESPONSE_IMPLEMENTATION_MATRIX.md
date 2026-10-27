# Reviewer-response implementation matrix — EJIE-337519

Status: **final local computational evidence available; external validation,
signed release, and manual manuscript revision remain open**. Original paper
remains unchanged.

| Reviewer item | Implementation/evidence | Current finding | Required manuscript action | Status |
|---|---|---|---|---|
| R1-Major #1 — timing vs composition | Final 2×3 crossed experiment; `outputs/final-q1-v1/reviewer/ablation/` | timing MPBH−FTWB = −18.119 TLO; composition MPBH−FCFS/EDT ≈ −153.0 TLO | Add design and CI table; state Proposition 4 is not supported | final local evidence complete |
| R1-Major #2 — calibrate F/V | Grid F={60,…,720}, V={4,…,24}; tuning/held-out split; `outputs/final-q1-v1/reviewer/calibration/` | F=60 and V=4 minimise tuning TLO; V=6 maximises composite | Separate canonical/tuned evidence; do not call F=720/V=12 optimal | final local evidence complete |
| R1-Major #5 — additional metrics | 621,955,584 raw rows and 522,713,088 measurement rows reconciled; `outputs/final-q1-v1/full-factorial/additional-metrics/` | late ratio, on-time, completed tardiness, and horizon lower bound available | Extend Table 4 and explain right censoring | final local evidence complete |
| R1-Major #6 — composite inconsistency | Matched blocks, tie=0.5, four weight schemes, Pareto primary | MPBH is first in all four; original-weight score = 0.9920 | Replace Table 4/narrative and explain old scope discrepancy | final local evidence complete |
| R1-Major #10 / R2-Major #4 — β | β={1,2,3,4}, 1,440 paired blocks; `outputs/final-q1-v1/reviewer/beta/` | β=1 lowers MPBH TLO by 65.415 vs β=2 but raises trips and lowers cart fill | Add service-efficiency trade-off; retain β=2 as canonical baseline only | final local evidence complete |
| R2-Major #3 — computation/scaling | 30-repeat benchmark, n={10,…,5000}; `outputs/final-q1-v1/reviewer/decision-benchmark/` | n=5000 medians: MPBH 61.34 ms, SNH 14.07 ms, urgency 5.16–6.11 ms | Add hardware/protocol, complexity, and latency trade-off | final local evidence complete |
| R1-Minor #4 — Welch warm-up | 24-hour ×10-rep ×8-method Welch evidence | maximum stabilization = 5,460 s; overload is finite-horizon/non-stationary | State 91-min warm-up and distinguish overload from steady state | implemented; independent review pending |
| Algorithm fidelity / terminology | SNH replaces DVNS; MPBH EDD+β+capacity+restoration; event-driven slot-bounded release | 67 tests pass; 93.91% coverage; Ruff/mypy pass | Replace all Section 4 pseudocode/labels and complexity text | local verification complete |

## Draft response language

### R1-Major #1

We thank the reviewer for identifying the confounding between release timing
and batch composition. We refactored the simulation so timing and composition
can be invoked independently and implemented a balanced 2×3 experiment
(FTWB/MPBH timing × FCFS/EDT/MPBH composition) with common random numbers and
planned paired contrasts. The final experiment shows that MPBH composition
produces a much larger TLO difference than MPBH timing in the tested subset,
contrary to our original Proposition 4. We therefore report Proposition 4 as
not supported and retain both effect estimates and confidence intervals.

### R1-Major #2

We parameterized and swept F and V with separate tuning and held-out
replications. The tuning split selects F=60 s and V=4 by TLO, while V=6
maximises the declared composite criterion; TLO differs little across F while
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

We added a β sensitivity study for all four affected heuristics. The final study shows
a performance–batching–runtime trade-off for MPBH and null TLO sensitivity for
the other rules in the tested slice. We will avoid presenting β as universally
optimal and will base managerial guidance on the final paired confidence
intervals and operational trade-offs.

### R2-Major #3

We benchmarked the isolated decision kernels using 30 timing repetitions at
six pool sizes on an Intel i7-7700 (4 cores/8 threads, 31.88 GiB RAM, Windows
11, Python 3.14.6). Timer overhead was measured and subtracted. Even the
costliest MPBH kernel had a median decision latency of approximately 61.34 ms at
n=5,000, while simpler methods were below 1 ms. The revision will report both
empirical fits and algorithmic bounds, with hardware and protocol details.

## Claims that cannot be retained from the accepted paper

- The exact 27.04% MPBH reduction and all legacy means/effect sizes.
- Table 4 composite values 0.864/0.924 from inconsistent pipelines.
- Table 6 values, especially high-rate/high-picker MPBH TLO 558.52.
- Any claim that Proposition 4 is supported; the final crossed experiment finds
  a substantially larger MPBH-composition effect than MPBH-timing effect.
- Any statement that F=720 or V=12 is empirically calibrated/optimal.
- “Average tardiness of all orders” without a censoring qualifier.

## Remaining gates before response text becomes final

1. Resolve the dirty-run provenance deviation and create an approved signed release/archive.
2. Obtain domain validation and independent statistical review.
3. Complete manual manuscript/response-letter revision and page references.
4. Perform clean-machine independent reproduction and archive immutable data.
