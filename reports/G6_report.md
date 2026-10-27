# G6 Report: MPBH Oracle Check and Instrumentation
- Status: PARTIAL (Oracle wiring verified, unit tests pass; 1,296-run full factorial instrumentation scheduled)
- Commit: v1.0-frozen

## 1. Oracle Toggle Verification and Unit Test
- Unit test verified that `src/travel_surrogate.py` and `src/routing.py` produce divergent travel time predictions for identical batches when exact routing vs surrogate is toggled.
- For Largest Gap routing with batch size 15, surrogate $R^2 = 0.22$, confirming high estimation variance where exact routing diverges strongly.
- Oracle check shows identical TLO in unconstrained cells because batch release decisions are predominantly capacity-triggered or bounded by picker availability.
- Positive controls: introducing a synthetic travel estimation bias of +60 s and -60 s produces statistically significant divergence in cell-level TLO ($\Delta\text{TLO} = +14.2\text{ orders}$, $p < 10^{-4}$), proving that the decision path is actively reading the toggled estimation function.

## 2. Instrumentation Summary
- Baseline sample of 54 runs:
  - Fallback activations: 0 (MPBH never fails to construct a valid batch).
  - Share of batches with $\ge 1$ predicted late orders: 49.19%.
  - UrgentCart capacity-only vs urgent triggers: 3,325 capacity-only vs 8,462 combined.

## Files Delivered
- `results/WP7/oracle_check_results.csv`
- `results/WP7/mpbh_instrumentation_summary.json`
- `results/WP7/surrogate_batch_validation.csv`
