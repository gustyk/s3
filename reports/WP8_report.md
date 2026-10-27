# WP8 Report: The 864-Cell Winner Decomposition

- **Status**: DONE
- **Total Operational Cells**: 864 cells (6 arrival rates x 12 picker levels x 3 cart capacities x 2 routings x 2 compositions)

## 1. Overall Category Counts

```
                                                       category  count
                                                  A. Strict win    594
              B. TLO tie, MPBH selected on throughput tie-break    134
D. MPBH not selected (Competitor selected on throughput or tie)    116
   D. MPBH not selected (Competitor lower TLO, not significant)     13
      D. MPBH not selected (Competitor significantly lower TLO)      6
                              C. Exact tie (all policies TLO=0)      1
```

## 2. Counts by Regime

```
       regime  A. Strict win  B. TLO tie, MPBH selected on throughput tie-break  C. Exact tie (all policies TLO=0)  D. MPBH not selected (Competitor lower TLO, not significant)  D. MPBH not selected (Competitor selected on throughput or tie)  D. MPBH not selected (Competitor significantly lower TLO)
Near-critical              0                                                 59                                  1                                                             3                                                               85                                                          0
   Overloaded            594                                                 75                                  0                                                            10                                                               31                                                          6
```

## 3. Strict Win Count vs Original 770
- **Category A (Strict Win)**: MPBH wins **594** cells with 95% paired CI strictly excluding 0 and exceeding the practical threshold (>= 1 order and >= 1% of competitor TLO).
- **Category B (TLO Tie, Throughput Tie-Break)**: **134** cells where TLO is tied or CI includes 0, with MPBH winning on throughput.
- **Category C (Exact Tie)**: **1** cell where all policies achieve TLO = 0.
- **Category D (Competitor Wins or Selected)**: **135** cells (116 selected on competitor throughput tie-break; 13 competitor lower TLO not significant; 6 competitor significantly lower TLO).

## 4. Files Delivered
- `results/WP8/cell_decomposition.csv`
- `results/WP8/decomposition_counts.csv`
- `results/WP8/decomposition_counts_by_lambda.csv`
- `results/WP8/decomposition_counts_by_regime.csv`
- `results/WP8/decomposition_counts_by_m.csv`
