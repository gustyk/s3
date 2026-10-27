# T9 Report: WP0 Provenance Table and Change Ladder

- **Status**: DONE
- **Commit**: ref: re
- **Model Version**: 0.2.0-reviewer-canonical
- **Date/Time**: 2026-10-21

## Provenance Findings
1. **Legacy Dataset Identification**: Traced to commit `50c4298` (SHA-256: `F02689EA9D4BFDA4BB31C56287F0F33F0328DAB5B35AA1946ACD5EABBDF674C6`). The file does not store parameter columns for F and t_setup; Column (c) is marked `NOT AVAILABLE`.
2. **Table B1 Classification**:
   - Column (a) left strictly as `LEAD_TO_FILL`.
   - All differences between original code and current code explicitly classified as `same` or `code differs from current`.
   - Pick time (3s -> 5s), beta (1 -> 2), warm-up (none -> 5,460s), simulation length (3,600s -> 28,800s), and travel estimation (exact -> surrogate) are all confirmed implementation changes prior to freeze.
3. **Change Ladders**:
   - `change_ladder_ofat.csv` (One-Factor-At-A-Time reverts from current model).
   - `change_ladder_cumulative.csv` (Cumulative progression from legacy 27.04% to canonical 10.66%).

## Files Delivered
- `results/WP0/provenance_table_B1.csv`
- `results/WP0/change_ladder_ofat.csv`
- `results/WP0/change_ladder_cumulative.csv`
- `results/WP0/setup_provenance.md`
