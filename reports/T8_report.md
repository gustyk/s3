# T8 Report: WP9 Load-Stratified Results and Overload Check

- **Status**: DONE
- **Commit**: ref: re
- **Model Version**: 0.2.0-reviewer-canonical
- **Date/Time**: 2026-10-21

## Key Results
1. **Clearing Thresholds**:
   - Matches Expected values exactly:
     - lam=0.5: MPBH, MaxPicker, SNH need m=3; FTWB needs m=5.
     - lam=1.0: MPBH needs m=5; MaxPicker, SNH, MaxCart need m=6.
     - lam=2.0: MPBH needs m=9; MaxPicker, SNH, MaxCart need m=11.
     - lam>=4.0: All policies "never" clear the pool.
2. **Table 10 v2**:
   - Fully calculated with relative reduction %, delta as % of N, and practical significance flags.
3. **Headline Reductions by rho_lb band**:
   - Band `<0.7` (300 cells): delta = -8.13 orders (40.91% reduction).
   - Band `0.7-1` (60 cells): delta = -135.25 orders (29.23% reduction).
   - Band `>=1` (504 cells): delta = -344.88 orders (9.63% reduction).
4. **Overload Artifact Check**:
   - At lam >= 8.0, static competitor TLO equals N_resolved to the last digit because backlogs inherited from the warm-up period overwhelm available picker capacity, causing competitors to complete virtually zero cohort orders on time. MPBH avoids this deadlock via forward-looking lateness estimation and selective batch trimming.

## Files Delivered
- `results/WP9/clearing_thresholds_v2.csv`
- `results/WP9/staffing_equivalence.csv`
- `results/WP9/table10_v2.csv`
- `results/WP9/headline_by_band.csv`
- `results/WP9/overload_check.csv`
- `results/WP9/claim_checks.md`
