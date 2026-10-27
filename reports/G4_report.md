# G4 Report: Status Partition and Mean TLO by Band
- Status: DONE
- Model Version: v1.0-frozen

## 1. Status Partition by Band, Cleared Flag, and Lambda
	able4d_by_band.csv previously contained only mean TLO per policy instead of the 4-category order status partition.
The true status partition has been delivered with:
- Strict on-time rate, Completed on-time rate, Not-yet-late rate, Resolved on-time rate.
- Mutually exclusive 4-category partition shares: Completed on-time, Completed late, Outstanding overdue, Outstanding not-yet-due (both run-mean and order-weighted pooled).

## 2. Mean TLO by rho_lb Band and Reductions vs Canonical & MaxPicker
| rho_lb_band   |   canonical_pooled_mean |   maxpicker_mean |   mpbh_mean |   diff_vs_canon_abs |   diff_vs_canon_ci_low |   diff_vs_canon_ci_high |   reduction_vs_canon_pct |   diff_vs_maxp_abs |   diff_vs_maxp_ci_low |   diff_vs_maxp_ci_high |   reduction_vs_maxp_pct |
|:--------------|------------------------:|-----------------:|------------:|--------------------:|-----------------------:|------------------------:|-------------------------:|-------------------:|----------------------:|-----------------------:|------------------------:|
| 0.7-1         |                924.276  |         828.4    |   542.634   |            381.641  |               378.102  |                385.181  |                 41.2909  |          285.766   |              281.95   |              289.581   |                34.4961  |
| <0.7          |                 61.0108 |          11.7846 |     3.27689 |             57.7339 |                55.9772 |                 59.4907 |                 94.629   |            8.50767 |                7.8658 |                9.14954 |                72.1934  |
| >=1           |               3286.16   |        3284.71   |  3000.02    |            286.144  |               285.05   |                287.238  |                  8.70754 |          284.698   |              283.576  |              285.821   |                 8.66737 |

### Verification against Lead's Target Numbers:
- rho_lb < 0.7: Canonical pooled 61.01 -> MPBH 3.28 (-94.629%) [Lead: 61.01 -> 3.28 (-94.6%)] -- MATCH (diff: 0.00%)
- 0.7 - 1.0: Canonical pooled 924.28 -> MPBH 542.63 (-41.291%) [Lead: 924.28 -> 542.63 (-41.3%)] -- MATCH (diff: 0.00%)
- >= 1.0: Canonical pooled 3286.16 -> MPBH 3000.02 (-8.708%) [Lead: 3286.16 -> 3000.02 (-8.7%)] -- MATCH (diff: 0.00%)

## Files Delivered
- 
esults/WP2/table4d_by_band.csv (overwritten with clean status partition)
- 
esults/WP2/table4d_by_band_v2.csv
- 
esults/WP2/table4d_by_cleared.csv (overwritten with clean status partition)
- 
esults/WP2/table4d_by_cleared_v2.csv
- 
esults/WP2/table4d_by_lambda_v2.csv
- 
esults/WP2/mean_tlo_by_band.csv (with stratified replication cluster CIs)
