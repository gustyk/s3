# G9 Report: Table 10 v3 and Winner Decomposition
- Status: DONE
- Model Version: v1.0-frozen
- Commit / Config: verified against canonical full-factorial outputs

## 1. Table 10 v3 Summary with Pre-Specified Practical Significance
- Pre-specified practical significance threshold: |Delta| >= 1 order AND >= 0.5% of N.
- Result: 17 out of 18 classes satisfy the practical significance threshold. Only lambda=1.0, abundant pickers (m=9-12) has delta = -1.93 orders (-0.41% of N), correctly showing False.
- On-time completed cohort orders per run: in heavy overload (lambda >= 4), canonical benchmarks achieve 0.00 to 0.42 on-time orders per run (0.0%), whereas MPBH achieves 143.3 to 569.6 on-time orders per run (up to 40%+ of N).

## 2. Winner Decomposition: Holm and Bonferroni Counts
- Total cells: 864
- Holm strict wins (p_val adjusted < 0.05 & delta < 0): **583 cells**
  - By lambda: 0.5: 19, 1.0: 43, 2.0: 89, 4.0: 144, 8.0: 144, 16.0: 144.
  - By band: <0.7: 21, 0.7-1: 58, >=1: 504.
- Bonferroni strict wins (p_val < 0.05/864 = 5.787e-5 & delta < 0): **581 cells**
  - By lambda: 0.5: 19, 1.0: 41, 2.0: 89, 4.0: 144, 8.0: 144, 16.0: 144.
  - By band: <0.7: 19, 0.7-1: 58, >=1: 504.

## 3. The 6 Cells Where Competitor is Statistically Significantly Better
|   lam |   m |   C | routing     | composition   | original_rule_winner   |   best_competitor_tlo |   mpbh_tlo |   diff_mean |      p_val |
|------:|----:|----:|:------------|:--------------|:-----------------------|----------------------:|-----------:|------------:|-----------:|
|     1 |   4 | 150 | Largest Gap | EDT           | MaxPicker              |             0.0333333 |   0.4      |    0.366667 | 0.0190436  |
|     1 |   4 | 200 | Largest Gap | EDT           | MaxPicker              |             0.733333  |   1.7      |    0.966667 | 0.0133213  |
|     1 |   4 | 200 | S-shape     | EDT           | MaxCart                |             2.56667   |   4.76667  |    2.2      | 0.00589988 |
|     2 |   8 | 200 | Largest Gap | EDT           | MaxCart                |             0.1       |   0.7      |    0.6      | 0.0173724  |
|     2 |   8 | 200 | S-shape     | EDT           | MaxCart                |             0.5       |   2.4      |    1.9      | 0.00147884 |
|     2 |   9 | 200 | S-shape     | EDT           | MaxCart                |             0.0666667 |   0.433333 |    0.366667 | 0.001135   |

### Characteristics of the 6 Competitor Win Cells:
- All 6 cells occur at light-to-moderate arrival rates (lambda = 1.0 and 2.0) with large cart capacity (C = 150 or 200).
- Winners: MaxCart (4 cells) and MaxPicker (2 cells).
- In these specific conditions with abundant cart capacity and moderate arrival rates, holding orders slightly longer to fill large carts (MaxCart) yields a minor travel efficiency advantage over MPBH's urgency-based release.

## Files Delivered
- 
esults/WP9/table10_v3.csv
- 
esults/WP8/holm_bonferroni_strict_wins.csv
- 
esults/WP8/competitor_significantly_better_6cells.csv
