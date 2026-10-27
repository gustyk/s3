# G8 Report: Crossed Design Full Factorial Fix and Shapley Decomposition
- Status: DONE
- Sign Convention: Delta = TLO_alternative - TLO_baseline (or TLO_baseline - TLO_MPBH for reductions)
- Stratification: Single stratum per lambda, cluster over 30 replications (df = 29)

## 1. Reconciled Six-Cell Factorial Table
IMM x EDT row previously carried stale std = 2295.22 and median = 1041.0 from UrgentPicker.
It has now been regenerated using true MaxPicker x EDT runs:
- IMM x EDT: Mean = 1977.47, Std = 2310.32, Median = 865.0.

| cell_label   | timing_policy   | composition_rule   |   mean_tlo |   std_tlo |   median_tlo |   total_runs |
|:-------------|:----------------|:-------------------|-----------:|----------:|-------------:|-------------:|
| IMM x MPBH   | IMM             | MPBH               |    1788.83 |   2193.37 |        760   |        25920 |
| FTWB x MPBH  | FTWB            | MPBH               |    1874.96 |   2207.26 |        822.5 |        12960 |
| IMM x FCFS   | IMM             | FCFS               |    1977.93 |   2309.1  |        865   |        12960 |
| IMM x EDT    | IMM             | EDT                |    1977.47 |   2310.32 |        865   |        12960 |
| FTWB x EDT   | FTWB            | EDT                |    2022.51 |   2280.32 |       1032.5 |        12960 |
| FTWB x FCFS  | FTWB            | FCFS               |    2023.78 |   2278.77 |        976   |        12960 |

## 2. Shapley Split by Lambda (with 95% CIs)
Cluster SE over 30 replications (df = 29).

|   incoming_rate |   total_reduction |   shapley_timing |   shapley_composition |   timing_share_pct |   timing_share_ci_low |   timing_share_ci_high |
|----------------:|------------------:|-----------------:|----------------------:|-------------------:|----------------------:|-----------------------:|
|             0.5 |           20.7167 |          12.0037 |               8.71296 |            57.9423 |               57.1408 |                58.7437 |
|             1   |           77.8787 |          43.7954 |              34.0833  |            56.2354 |               55.8173 |                56.6534 |
|             2   |          290.284  |         162.021  |             128.263   |            55.8146 |               55.4672 |                56.1621 |
|             4   |          334.482  |          75.7377 |             258.744   |            22.6433 |               21.7735 |                23.5131 |
|             8   |          337.794  |          49.8713 |             287.923   |            14.7638 |               14.5942 |                14.9334 |
|            16   |          348.554  |          52.513  |             296.041   |            15.0659 |               14.9025 |                15.2294 |

### Key Takeaways:
- Timing accounts for the majority of MPBH's benefit under light to moderate loads (~58% at lambda=0.5, ~56% at lambda=1.0 and 2.0).
- Under heavy and saturated loads, Composition dominates overwhelmingly (~77% at lambda=4.0, ~85% at lambda=8.0 and 16.0), confirming that batching composition becomes paramount when pickers are the primary bottleneck.

## Files Delivered
- 
esults/WP4/six_cells_full.csv
- 
esults/WP4/six_cells_full_corrected.csv
- 
esults/WP4/six_cells_by_lambda_ci.csv
- 
esults/WP4/shapley_by_lambda.csv
