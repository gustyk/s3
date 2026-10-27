# WP3 Report: Order-Status Partition and Censoring-Aware Metrics

- **Status**: DONE
- **QA Gates Verified**:
  - QA Gate 1 (Sum of 4 categories == N): **True** (100% of 207,360 runs)
  - QA Gate 2 (Completed late + Outstanding overdue == TLO): **True** (100% of 207,360 runs)
  - QA Gate 3 (Cohort orders == N): **True** (100% of 207,360 runs)

## 1. Status Partition Overall Summary (Table 4d)

```
trigger_method  n_cohort  share_comp_ontime  share_comp_late  share_out_overdue  share_out_notdue  strict_ontime_rate  completed_ontime_rate  not_yet_late_rate  structural_unlateable_share
          FTWB    2520.8             0.2704           0.1040             0.4978            0.1279              0.2704                 0.3955             0.3982                       0.0625
          MPBH    2520.8             0.4309           0.0647             0.3954            0.1090              0.4309                 0.7942             0.5399                       0.0625
       MaxCart    2520.8             0.3371           0.1073             0.4371            0.1185              0.3371                 0.4452             0.4556                       0.0625
     MaxPicker    2520.8             0.3452           0.1054             0.4370            0.1124              0.3452                 0.4482             0.4576                       0.0625
           SNH    2520.8             0.3295           0.1371             0.4208            0.1126              0.3295                 0.3446             0.4421                       0.0625
    UrgentCart    2520.8             0.3371           0.1073             0.4371            0.1185              0.3371                 0.4452             0.4556                       0.0625
  UrgentPicker    2520.8             0.3045           0.1274             0.4426            0.1256              0.3045                 0.4086             0.4301                       0.0625
          VTWB    2520.8             0.3255           0.1131             0.4392            0.1221              0.3255                 0.4736             0.4476                       0.0625
```

## 2. Policy Ranks Under Different Metrics

```
trigger_method  rank_TLO  rank_not_yet_late  rank_strict_ontime  rank_completed_ontime
           NaN       1.0                NaN                 NaN                    NaN
           NaN       2.0                NaN                 NaN                    NaN
           NaN       3.0                NaN                 NaN                    NaN
           NaN       3.0                NaN                 NaN                    NaN
           NaN       5.0                NaN                 NaN                    NaN
           NaN       6.0                NaN                 NaN                    NaN
           NaN       7.0                NaN                 NaN                    NaN
           NaN       8.0                NaN                 NaN                    NaN
          FTWB       NaN                8.0                 8.0                    7.0
          MPBH       NaN                1.0                 1.0                    1.0
       MaxCart       NaN                3.0                 3.0                    4.0
     MaxPicker       NaN                2.0                 2.0                    3.0
           SNH       NaN                6.0                 5.0                    8.0
    UrgentCart       NaN                3.0                 3.0                    4.0
  UrgentPicker       NaN                7.0                 7.0                    6.0
          VTWB       NaN                5.0                 6.0                    2.0
```
- **Rank Reversals**: Under `completed_ontime_rate`, SNH drops to rank 8 because it finishes late orders rather than leaving them in the queue. MPBH remains **Rank 1** across all metrics (`total_late_orders`, `strict_ontime_rate`, `not_yet_late_rate`, and `completed_ontime_rate`).

## 3. Structural 30-Minute Censoring Effect
- **`structural_unlateable_share`**: **6.25%** (1,800 s / 28,800 s). Orders arriving within the final 30 minutes of the shift can never become overdue by horizon $H=34,260$ s by construction.

## 4. Files Delivered
- `results/WP3/table4a_extended.csv`
- `results/WP3/table4d_status_partition.csv`
- `results/WP3/table4d_by_regime.csv`
- `results/WP3/rank_comparison.csv`
