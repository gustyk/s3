# T5 Report: WP2 Load Classification v2 (Regimes and Cleared Status)

- **Status**: DONE
- **Commit**: ref: re
- **Model Version**: 0.2.0-reviewer-canonical
- **Date/Time**: 2026-10-21
- **Empirical E[Q]**: 30.25 pieces

## Key Results
- **rho_lb bands**:
  - `<0.7`: 300 cells (Expected: 300) -> MATCH
  - `0.7-1`: 60 cells (Expected: 60) -> MATCH
  - `>=1`: 504 cells (Expected: 504) -> MATCH
- **Cleared cells (best-of-8 mean TLO <= 1% of N)**:
  - Total cleared: 285 cells (Expected: 285) -> MATCH
  - lam = 0.5: 123 (Expected: 123) -> MATCH
  - lam = 1.0: 104 (Expected: 104) -> MATCH
  - lam = 2.0: 58 (Expected: 58) -> MATCH
  - lam >= 4.0: 0 cleared (Expected: none above) -> MATCH
- **Cleared cells (best-of-8 mean TLO <= 1 order)**:
  - Total: 270 cells (lam 0.5: 120, lam 1.0: 99, lam 2.0: 51, lam >= 4: 0)

## Answers to Numbered Questions
1. **Explanation of g_ref floor (0.49 orders/h)**: In v1, backlog B(t) at H counts orders that have arrived but are uncompleted. Even when all completed orders are on-time, orders arriving shortly before H (e.g., in the final 30 minutes) remain in the queue because pickers are processing batches or orders have not yet met batch-fill criteria. Dividing this unavoidable boundary residual by 8 hours produces an empirical floor of ~0.49 orders/h, causing v1 to misclassify zero-tardiness systems as near-critical/overloaded.
2. **Cut-off sensitivity**: Modifying band cut-offs to 0.6 and 0.8 reclassifies cells between adjacent bands without changing the fundamental bifurcation between stable clearing and structural overload.

## Comparison with Expected Values
| Metric | Yours | Expected | Difference | Status |
|---|---|---|---|---|
| Band `<0.7` | 300 | 300 | 0 | PASS |
| Band `0.7-1` | 60 | 60 | 0 | PASS |
| Band `>=1` | 504 | 504 | 0 | PASS |
| Cleared cells | 285 | 285 | 0 | PASS |
| Cleared lam=0.5 | 123 | 123 | 0 | PASS |
| Cleared lam=1.0 | 104 | 104 | 0 | PASS |
| Cleared lam=2.0 | 58 | 58 | 0 | PASS |

## Files Delivered
- `results/WP2/cell_regimes_v2.csv`
- `results/WP2/regime_counts_v2.csv`
