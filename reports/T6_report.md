# T6 Report: WP8 864-Cell Winner Decomposition v2

- **Status**: DONE
- **Commit**: ref: re
- **Model Version**: 0.2.0-reviewer-canonical
- **Date/Time**: 2026-10-21

## Key Results
- **Original rule winners**: MPBH: 770, MaxPicker: 59, SNH: 31, MaxCart: 4 (Total: 864) -> 100% EXACT MATCH
- **Reconciliation to 770 / 59 / 31 / 4**:
  - MPBH Strict Wins (Category A): **594** cells (all 594 are MPBH original winners)
  - MPBH Significant below practical threshold (Category A'): **11** cells (all MPBH original winners)
  - MPBH Lower mean TLO, not significant (Category B): **6** cells (all MPBH original winners)
  - Exact TLO Ties won by MPBH on throughput/order: **159** cells (158 both-zero + 1 non-zero)
  - **Total MPBH Original Winners**: 594 + 11 + 6 + 159 = **770 cells** -> PERFECT RECONCILIATION.
  - Competitor Wins: **94** cells (19 cells where competitor has lower mean TLO; 75 cells where TLO is tied and competitor had higher throughput). Specifically: MaxPicker: 59, SNH: 31, MaxCart: 4.
- **Holm-corrected strict wins**: **583** cells (Expected: approx 583) -> MATCH
- **Decomposition by rho_lb band**:
  - `rho_lb >= 1` (504 cells): **504 strict wins** (100% Category A).
  - `rho_lb < 0.7` (300 cells): **31 strict wins**, 269 ties/competitor selections.
  - `cleared` (285 cells): **16 strict wins**, 269 ties/competitor selections.

## Files Delivered
- `results/WP8/cell_decomposition_v2.csv`
- `results/WP8/decomposition_crosstab.csv`
- `results/WP8/decomposition_counts_v2.csv`
- `results/WP8/decomposition_by_band.csv`
- `results/WP8/decomposition_by_cleared.csv`
- `results/WP8/competitor_win_cells.csv`
