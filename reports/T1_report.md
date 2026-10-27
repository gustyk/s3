# Report T1: Work Package 6 (Setup-Time Sensitivity Analysis)

**Status:** PASS  
**Git Commit:** `222784287f05eea5d847ac749a4bb2783daedb6c`  
**Model Version:** `v1.0-frozen`  
**Hardware / Execution:** 34,560 simulation runs at setups {30, 60, 120, 300} + aligned 8,640 runs at setup 180 (replications 1..30 perfectly aligned across all setups; $N = 43,200$).  
**Output Files:**
- Raw Data: [`results/WP6/setup_simulation_raw.csv`](file:///d:/Apps/S3/results/WP6/setup_simulation_raw.csv)
- Sensitivity Table: [`results/WP6/setup_sensitivity.csv`](file:///d:/Apps/S3/results/WP6/setup_sensitivity.csv)
- Per-$\lambda$ Breakdown: [`results/WP6/setup_by_lambda.csv`](file:///d:/Apps/S3/results/WP6/setup_by_lambda.csv)
- Cleared Counts by Setup: [`results/WP6/cleared_counts_by_setup.csv`](file:///d:/Apps/S3/results/WP6/cleared_counts_by_setup.csv)
- Trips, Utilisation & Cart: [`results/WP6/setup_trips_utility_cart.csv`](file:///d:/Apps/S3/results/WP6/setup_trips_utility_cart.csv)
- Confidence Intervals: [`results/WP6/setup_ci_table.csv`](file:///d:/Apps/S3/results/WP6/setup_ci_table.csv)
- MPBH vs MaxPicker & SNH: [`results/WP6/mpbh_vs_maxpicker_snh.csv`](file:///d:/Apps/S3/results/WP6/mpbh_vs_maxpicker_snh.csv)
- Parameter Provenance & Grep Audit: [`results/WP6/setup_provenance.md`](file:///d:/Apps/S3/results/WP6/setup_provenance.md)
- Break-even Analysis: [`results/WP6/breakeven.csv`](file:///d:/Apps/S3/results/WP6/breakeven.csv)
- Warm-up Check Memo: [`results/WP6/warmup_check.md`](file:///d:/Apps/S3/results/WP6/warmup_check.md)

---

## 1. Setup Sensitivity Performance & Confidence Intervals

Setup time was varied across five levels: $t_{\text{setup}} \in \{30, 60, 120, 180, 300\}\text{ s}$ across the 36 canonical cells and 30 replications (1..30). The cohort generation $N$ is **identically $21,764,016$ total generated orders** (mean $2518.98$ per run) across all five setup levels.

### Table T1.1: Overall Performance vs. Pooled Canonical Benchmark across $t_{\text{setup}}$
*(Pooled Canonical Benchmark = per-block mean of canonical FTWB and VTWB)*

| $t_{\text{setup}}$ (s) | MPBH Mean TLO | Canonical Pooled TLO | MPBH Advantage ($\Delta$) | 95% Confidence Interval ($\Delta$) | Rel. Reduction vs Benchmark | MPBH Cleared Runs (/1080) |
|---|---|---|---|---|---|---|
| **30** | 1736.14 | 1975.03 | **+238.89** | [224.54, 253.24] | **12.10%** | **350 / 1080** (32.4%) |
| **60** | 1752.62 | 1982.70 | **+230.08** | [216.72, 243.43] | **11.60%** | **337 / 1080** (31.2%) |
| **120** | 1780.21 | 2000.15 | **+219.93** | [208.05, 231.81] | **11.00%** | **313 / 1080** (29.0%) |
| **180** (Baseline) | 1801.22 | 2012.22 | **+211.01** | [199.97, 222.04] | **10.49%** | **303 / 1080** (28.1%) |
| **300** | 1831.09 | 2024.97 | **+193.89** | [184.04, 203.73] | **9.57%** | **276 / 1080** (25.6%) |

---

## 2. Head-to-Head Comparisons: MPBH vs. MaxPicker and SNH

Reviewer 1 noted that MPBH makes more trips and may lose to MaxPicker or SNH under high setup times. Empirical results disprove this hypothesis:

### Table T1.2: MPBH Advantage vs. MaxPicker and SNH across Setup Times
| $t_{\text{setup}}$ (s) | MPBH Mean TLO | MaxPicker TLO | $\Delta$ vs MaxPicker | Rel. Advantage (%) | SNH Mean TLO | $\Delta$ vs SNH | Rel. Advantage (%) |
|---|---|---|---|---|---|---|---|
| **30** | 1736.14 | 1945.63 | **+209.49** | **10.77%** | 1980.49 | **+244.35** | **12.34%** |
| **60** | 1752.62 | 1956.61 | **+203.98** | **10.43%** | 1988.08 | **+235.45** | **11.84%** |
| **120** | 1780.21 | 1974.13 | **+193.92** | **9.82%** | 1997.57 | **+217.36** | **10.88%** |
| **180** | 1801.22 | 1986.33 | **+185.11** | **9.32%** | 2003.15 | **+201.94** | **10.08%** |
| **300** | 1831.09 | 2000.91 | **+169.83** | **8.49%** | 2009.86 | **+178.77** | **8.89%** |

MPBH strictly outperforms both MaxPicker and SNH across all setup levels from 30 s to 300 s.

---

## 3. Operational Metrics: Trips, Picker Utility, and Cart Utilization

### Table T1.3: Mean Operational Metrics across Setup Durations
| $t_{\text{setup}}$ (s) | Policy | Mean Trips | Picker Utility (%) | Mean Cart Util (%) | Throughput (/hr) |
|---|---|---|---|---|---|
| **30** | MPBH | 263.4 | 87.15% | 56.78% | 70.54 |
| 30 | MaxPicker | 189.1 | 87.16% | 48.00% | 50.21 |
| 30 | SNH | 210.4 | 87.14% | 74.61% | 55.42 |
| 30 | FTWB | 78.6 | 67.34% | 58.00% | 36.97 |
| 30 | VTWB | 107.1 | 83.04% | 63.82% | 49.44 |
| **180** | MPBH | 216.0 | 91.56% | 57.68% | 59.91 |
| 180 | MaxPicker | 144.0 | 91.57% | 46.25% | 41.28 |
| 180 | SNH | 166.4 | 91.54% | 78.01% | 47.33 |
| 180 | FTWB | 58.6 | 65.68% | 53.97% | 28.69 |
| 180 | VTWB | 86.7 | 85.56% | 59.67% | 40.75 |
| **300** | MPBH | 187.3 | 93.72% | 58.95% | 53.54 |
| 300 | MaxPicker | 119.8 | 93.75% | 47.56% | 36.40 |
| 300 | SNH | 141.8 | 93.71% | 80.02% | 42.45 |
| 300 | FTWB | 50.1 | 64.74% | 50.05% | 24.34 |
| 300 | VTWB | 76.4 | 87.33% | 59.01% | 36.04 |

---

## 4. Welch Warm-up Verification at $t_{\text{setup}} = 30$ and $300$ s
The Welch procedure was re-executed at the most sensitive staffing configuration ($\lambda = 0.5$, $m = 12$) over 10 replications of 24-hour simulations:
- **$t_{\text{setup}} = 30\text{ s}$:** Stabilization observed at $t \le 2,100\text{ s}$.
- **$t_{\text{setup}} = 300\text{ s}$:** Stabilization observed at $t \le 3,360\text{ s}$.
- **Conclusion:** Both stabilization points are well below the frozen warm-up threshold $W = 5,460\text{ s}$ (91 minutes), confirming that the warm-up period safely eliminates initial transient effects across the entire setup range.
