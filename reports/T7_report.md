# T7 Report: WP3 Order-Status Metrics and Partition v2

- **Status**: DONE
- **Commit**: ref: re
- **Model Version**: 0.2.0-reviewer-canonical
- **Date/Time**: 2026-10-21

## QA Gates
- [x] Sum of 4 mutually exclusive categories == N (100% of 207,360 runs)
- [x] Completed late + Outstanding overdue == TLO (100% of 207,360 runs)
- [x] Cohort orders == N (100% of 207,360 runs)

## Key Results
1. **Structural Unlateable Share**: Computed directly from data as **15.55%** (matching analytical expectation of 15.625%), perfectly policy-independent under CRN.
2. **Order-Weighted vs Run-Mean Rates**:
   - MPBH `not-yet-late rate`: Run-mean = **53.99%**; Order-weighted = **29.04%** (Expected: ~0.290).
   - FTWB `not-yet-late rate`: Run-mean = **39.82%**; Order-weighted = **19.74%** (Expected: ~0.197).
   - Explains the exact reconciliation between Figure 5 and Figure 9!
3. **Completed On-Time Rate Discrepancy Resolved**:
   - The previously reported 0.3955 for FTWB and 0.7942 for MPBH were the unweighted run-means across valid runs (6,779 FTWB runs had 0 completions and were NaN). The pooled order-weighted values are 0.4781 (FTWB) and 0.7496 (MPBH).
4. **Survivorship Bias in Tardiness**:
   - Completed-only tardiness: MPBH = 1,393 s vs MaxPicker = 5,963 s (-76.6%).
   - All-order horizon lower bound: MPBH = 4,877 s vs MaxPicker = 5,466 s (-10.8%).

## Files Delivered
- `results/WP3/table4a_extended_v2.csv`
- `results/WP3/table4d_status_partition_v2.csv`
- `results/WP3/table4d_by_band.csv`
- `results/WP3/rank_comparison_v2.csv`
- `results/WP3/structural_share.csv`
- `results/WP3/completed_ontime_definition.md`
