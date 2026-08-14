# Conceptual Model Specification

## Objective and intended use

The model compares warehouse order-release triggers, batching rules, routing
policies, cart capacities, and picker staffing under stochastic demand. Its
intended use is comparative policy evaluation within the parameter domain in
`config/parameters.yaml`; it is not a calibrated digital twin and must not be
used for a real staffing decision until Gate C validation is approved.

Primary research question: how do release-trigger policies affect service
level and throughput under varying demand and resources? Secondary questions
cover tardiness, picker utilization, cart utilization, and interactions among
policy and operating factors. Confirmatory hypotheses must be frozen in
`docs/ANALYSIS_PLAN.md` before the final run.

## Entities, resources, queues, and events

- **Order:** immutable identity, numeric arrival/due time, item lines, quantity;
  gains start/completion, waiting, flow-time, and tardiness observations.
- **Picker:** capacity-one resource represented by an independent SimPy process.
- **Cart/batch:** ordered collection of complete orders; order splitting is not
  permitted and total quantity cannot exceed cart capacity.
- **Order pool:** orders generated but not yet released.
- **I/O pool:** pending, assigned, and completed batches.
- **Events:** arrival, trigger inspection, batch creation, picker assignment,
  route completion, and fixed-horizon censoring.

State sequence:

```text
generated -> waiting in order pool -> pending batch -> assigned batch -> completed
                                      | fixed horizon: right-censored |
```

Every generated order occupies exactly one state. The runner asserts this
conservation invariant at the horizon.

## Time and KPI definitions

All model time is numeric seconds from simulation start. `HH:MM:SS` is display
only. Due time is arrival time plus a sampled allowance. Completion exactly at
due time is on time. Tardiness is `max(0, completion - due)`. Waiting time is
`picking_start - arrival`; flow time is `completion - arrival`.

The verified horizon policy is fixed horizon with explicit right-censoring.
Outstanding orders remain in the service-level denominator. Service level is
`on-time completed / generated`; late outstanding and late completed are
reported separately. Setup time applies once per picker trip/batch.

## Algorithms

- **FCFS:** preserve release order and use next-fit batching.
- **EDT:** ascending numeric due time, then use next-fit batching.
- **Traversal/Largest Gap:** deterministic route-time equations implemented in
  `src/routing.py`; both include setup, walking, and quantity-dependent pick time.
- **FTWB:** release all waiting orders every fixed interval.
- **VTWB:** release the oldest threshold-sized group.
- **MaxPicker:** release waiting orders when a picker is available.
- **MaxCart:** release the longest FCFS prefix fitting one cart once waiting
  quantity reaches capacity.
- **UrgentPicker:** release when all pickers are idle or forecast urgent count
  reaches the threshold.
- **UrgentCart:** release when waiting quantity reaches capacity or urgency
  reaches the threshold.
- **DVNS:** evaluate EDT urgency, descending-size cart fill, and hybrid
  neighborhoods; use the configured batching policy for the selected solution.
- **MPBH:** rank by `(due - now - individual trip time) / quantity`, then due
  time and order ID; greedily fill one cart whenever a picker is available.

Urgency forecasting schedules EDT orders onto a min-heap of projected picker
availability, seeded by elapsed active-batch workloads. It is a deterministic
forecast approximation, not an oracle.

## Assumptions and boundaries

- No aisle congestion, picker interference, equipment failures, breaks, order
  cancellation, replenishment, stockout, or order splitting.
- Item locations and travel/pick times are deterministic conditional on an order.
- Arrivals are homogeneous Poisson; due allowance, order lines, quantities, and
  item popularity follow configured/specified synthetic distributions.
- Results generalize only to scenarios covered by validation and sensitivity
  evidence. These omissions can overstate throughput and understate variability.

