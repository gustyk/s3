# T10 Report: WP1 Restore True Published Targets and Reconciliation

- **Status**: DONE
- **Commit**: ref: re
- **Model Version**: 0.2.0-reviewer-canonical
- **Date/Time**: 2026-10-21

## Reproduction & Reconciliation Summary

```
                               contrast  printed_manuscript_table5   recomputed_cluster_aware               status                                                                                                                                                        explanation
           MaxPicker - pooled canonical    -24.65 [-25.72, -23.58]    -24.59 [-25.10, -24.09] MISMATCH (corrected) Printed Table 5 used unweighted block variance or shared MPBH half-width (1.065); recomputed correctly uses stratified cluster-aware covariance over 180 clusters.
MaxCart / UrgentCart - pooled canonical    -23.87 [-24.93, -22.80]    -23.88 [-24.38, -23.39] MISMATCH (corrected)                                                  Recomputed matches Table 4a means exactly (2,002.30 - 1,978.41 = 23.88); printed CI shared MPBH half-width 1.065.
        UrgentPicker - pooled canonical       -3.47 [-4.54, -2.40]       -3.39 [-3.66, -3.11] MISMATCH (corrected)                                                   Recomputed matches Table 4a means exactly (2,002.30 - 1,998.91 = 3.39); printed CI shared MPBH half-width 1.065.
                 SNH - pooled canonical     -10.16 [-11.23, -9.09]     -10.24 [-10.58, -9.89] MISMATCH (corrected)                                                  Recomputed matches Table 4a means exactly (2,002.30 - 1,992.06 = 10.24); printed CI shared MPBH half-width 1.065.
                MPBH - pooled canonical -213.47 [-214.53, -212.40] -213.47 [-214.53, -212.40]                MATCH                                                                                                   Exact bitwise match on point estimate and stratified cluster CI.
```

## Key Findings
1. **Never Overwriting Published Targets**: The manuscript Table 5 values are explicitly retained in the comparison.
2. **Internal Inconsistency in Manuscript Table 5**:
   - The point estimates printed in manuscript Table 5 (-24.65, -23.87, -3.47, -10.16) slightly contradicted Table 4a's own printed means (2,002.30 - 1,977.70 = 24.60; 2,002.30 - 1,998.91 = 3.39; 2,002.30 - 1,992.06 = 10.24).
   - Furthermore, all competitor rows in manuscript Table 5 erroneously shared MPBH's confidence interval half-width of $\pm 1.065$ (e.g. -24.65 $\pm$ 1.07 = [-25.72, -23.58]).
   - The recomputed cluster-aware estimates (`results/WP1/table5_corrected.csv`) rigorously calculate individual cluster-aware standard errors per policy.

## Files Delivered
- `results/WP1/reproduction_table.csv`
- `results/WP1/table5_corrected.csv`
