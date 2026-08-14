# Sensitivity, Uncertainty, and Ablation Plan

Status: **DRAFT — execution requires validated parameter ranges and frozen model**.

## Uncertainty separation

- Aleatory: arrival/order/due-time random streams; quantified by paired repeated
  runs and confidence intervals.
- Epistemic: uncertain input parameters/model forms; quantified by scenarios or
  global sensitivity over expert/data-supported ranges.

## Required design

1. Directional sanity checks for arrival rate, picker count, cart capacity,
   setup/pick/walking times, and due allowance.
2. Latin hypercube or Sobol design over validated epistemic ranges; report first
   and total-order sensitivity indices with bootstrap uncertainty.
3. Structural scenarios for layout, nonstationary demand, picker heterogeneity,
   congestion, and due-time regimes where evidence supports implementation.
4. DVNS ablations: urgency neighborhood only, cart neighborhood only, hybrid
   removed, configured batching switched.
5. MPBH ablations: remove slack normalization by quantity and remove route-time
   adjustment.
6. Rank policy regions as win/tie/loss using the prespecified MPID, not only
   p-values. Report Pareto sets across service, throughput, utilization, and cost.

No range may be invented after observing favorable outcomes. Input ranges and
ablation hypotheses require domain/PI approval before execution.

