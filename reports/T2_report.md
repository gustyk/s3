# T2 Report: WP4 Fixes and Attribution Analysis

- **Status**: DONE
- **Commit**: ref: re
- **Model Version**: 0.2.0-reviewer-canonical
- **Date/Time**: 2026-10-21

## Reconciliation of Ratios and Effects
1. **Discrepancy Explained**:
   - The earlier text mistakenly labelled the total effect (-179.96) as Shapley timing.
   - The true Shapley decomposition is:
     - Shapley timing: **-26.955** TLO
     - Shapley composition: **-153.005** TLO
     - Total effect: **-179.960** TLO
   - Shapley ratio: **5.676**
   - Marginal means ratio: **8.445** (95% CI: [7.82, 9.15])
2. **Comparison with Expected Values**:
   - FTWB x FCFS: **3291.258** (Expected: 3291.258) -> MATCH
   - FTWB x EDT: **3291.247** (Expected: 3291.247) -> MATCH
   - FTWB x MPBH: **3164.667** (Expected: 3164.667) -> MATCH
   - IMM x FCFS: **3290.717** (Expected: 3290.717) -> MATCH
   - IMM x EDT: **3290.800** (Expected: 3290.800) -> MATCH
   - IMM x MPBH: **3111.299** (Expected: 3111.299) -> MATCH
   - Interaction contrast: **-52.826** (Expected: approx -52.8) -> MATCH
   - Path A (timing first): -0.542 timing / -179.418 comp (Expected: 179.42 / 0.54) -> MATCH
   - Path B (composition first): -126.592 comp / -53.368 timing (Expected: 126.59 / 53.37, ratio ~2.37) -> MATCH

## Files Delivered
- `results/WP4/six_cells.csv`
- `results/WP4/simple_effects.csv`
- `results/WP4/interactions.csv`
- `results/WP4/omnibus.json`
- `results/WP4/two_path.csv`
- `results/WP4/ratios.csv`
- `results/WP4/equivalence_test_report.md`
