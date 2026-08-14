# Extreme and Degenerate Condition Evidence

Status: **DONE_LOCAL for engineering behavior; domain-calibrated limits remain external**.

The automated suite exercises the following deterministic cases with common
random numbers and conservation checks:

| Case | Expected behavior / oracle |
|---|---|
| Near-zero demand (`0.001` orders/minute) | zero generated and completed orders for the fixed seed/horizon; service level is well-defined as 100%; conservation holds |
| Severe overload (`100` orders/minute, one picker) | generated exceeds completed, backlog remains visible, and `generated = completed + outstanding` |
| Staffing boundary (one versus twelve pickers) | identical generated demand; additional pickers do not reduce completed orders |
| Tight versus relaxed due allowance | identical generated demand; relaxed due allowance cannot increase late-order count |
| Exact/over cart capacity | exact capacity is accepted and exceeding capacity fails explicitly in batching tests |
| Empty pool, one order/item, due exactly at completion, and day rollover | behavior is covered by unit/golden tests and numeric-time invariants |

Run with `python -m pytest tests/test_experiment.py tests/test_core.py`.
These checks verify model logic, not operational plausibility. Demand/layout/
productivity bounds must be replaced or approved from WMS and domain evidence
before confirmatory experiments.
