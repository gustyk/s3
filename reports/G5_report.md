# G5 Report: Table 4a/4c Audit and Correction for Undefined-Run Averaging
- Status: DONE

## 1. Audit of Per-Run Columns in Zero-Completed Runs
The audit identified that 33,575 runs across the full factorial completed 0 orders (FTWB: 6,779 runs; MaxCart: 4,948; MaxPicker: 4,959; UrgentCart: 4,948; UrgentPicker: 5,005; VTWB: 6,690; SNH: 246; MPBH: 0).
For runs with 0 completed orders:
- mean_tardiness_seconds, mean_flow_time_seconds, mean_waiting_time_seconds, and their p95 counterparts were previously imputed as 0.0.
- Imputing 0.0 heavily distorted the mean tardiness of policies with high clearing failure.
- Confirmed Lead's formula: FTWB completed-only mean = 8,214.16 s. Multiplying by 19,141 / 25,920 yields exactly the previously printed 6,065.87 s.

## 2. Corrected Table 4a Summary
| trigger_method   |   runs_completed_gt_zero |   runs_zero_completed |   mean_tardiness_all_runs_zero_imputed |   mean_tardiness_completed_only_mean |   on_time_rate_percent_mean |   total_late_orders_mean |
|:-----------------|-------------------------:|----------------------:|---------------------------------------:|-------------------------------------:|----------------------------:|-------------------------:|
| FTWB             |                    19141 |                  6779 |                                6065.87 |                              8214.16 |                     39.8234 |                  2023.15 |
| MPBH             |                    25920 |                     0 |                                1393.04 |                              1393.04 |                     53.9899 |                  1788.83 |
| MaxCart          |                    20972 |                  4948 |                                5975.2  |                              7384.95 |                     45.562  |                  1978.41 |
| MaxPicker        |                    20961 |                  4959 |                                5963.24 |                              7374.04 |                     45.7609 |                  1977.7  |
| SNH              |                    25674 |                   246 |                                7068.1  |                              7135.82 |                     44.2082 |                  1992.06 |
| UrgentCart       |                    20972 |                  4948 |                                5975.2  |                              7384.95 |                     45.562  |                  1978.41 |
| UrgentPicker     |                    20915 |                  5005 |                                6113.8  |                              7576.84 |                     43.0056 |                  1998.91 |
| VTWB             |                    19230 |                  6690 |                                4704.34 |                              6340.95 |                     44.7647 |                  1981.45 |

## Files Delivered
- 
esults/WP3/table4a_corrected.csv
- 
esults/WP3/table4c_corrected.csv
- 
esults/WP3/tardiness_all_policies_summary.csv (updated with horizon lower bound)
