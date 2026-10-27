# Table 4c. Composite score sensitivity

| Trigger method | Original (0.6/0.3/0.1) | Equal (0.3333/0.3333/0.3333) | Throughput-priority (0.3/0.6/0.1) | Utilisation-priority (0.3/0.1/0.6) |
|---|---:|---:|---:|---:|
| FTWB | 0.1590 | 0.1049 | 0.1171 | 0.0809 |
| VTWB | 0.3041 | 0.4286 | 0.3471 | 0.5319 |
| MaxPicker | 0.4864 | 0.6424 | 0.5487 | 0.7643 |
| MaxCart | 0.4084 | 0.5132 | 0.4396 | 0.6048 |
| UrgentPicker | 0.2600 | 0.3926 | 0.3055 | 0.5031 |
| UrgentCart | 0.4084 | 0.5132 | 0.4396 | 0.6048 |
| SNH | 0.4999 | 0.6682 | 0.6053 | 0.7651 |
| MPBH | 0.9920 | 0.9941 | 0.9930 | 0.9956 |

Sanity check: MPBH Original-weight composite computed = 0.9919728028, rounded to 0.9920; manuscript value = 0.9920.

## Ranking check

- Original: MPBH > SNH > MaxPicker > MaxCart = UrgentCart > VTWB > UrgentPicker > FTWB
- Equal: MPBH > SNH > MaxPicker > MaxCart = UrgentCart > VTWB > UrgentPicker > FTWB
- Throughput-priority: MPBH > SNH > MaxPicker > MaxCart = UrgentCart > VTWB > UrgentPicker > FTWB
- Utilisation-priority: MPBH > SNH > MaxPicker > MaxCart = UrgentCart > VTWB > UrgentPicker > FTWB

MPBH ranks first under all four weighting schemes.
