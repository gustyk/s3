# G2 Report: Setup-Time Sensitivity (Tuned Benchmarks, Reconciled 1-30 Numbers, and CIs)
- Status: DONE
- Configuration: Fixed parameter tuning frozen from 180s setup: FTWB(F* = 5s), VTWB(V* = 8 orders S1, V* = 6 orders S2).
- Runs: 43,200 canonical runs (reps 0..29) + 16,200 tuned runs (reps 0..29 across 3 variants: FTWB_F5, VTWB_V8, VTWB_V6) = **59,400 runs total**.
- Replications: Strictly aligned 0-29 across all five setup times {30, 60, 120, 180, 300}s.

## 1. Setup Sensitivity with Pooled Tuned & Canonical Benchmarks (with 95% CIs)
Cluster over 30 replications (df = 29):

| Setup Time (s) | MPBH Mean TLO | Canonical Pooled TLO | Tuned Pooled TLO | Tuned FTWB(F5) TLO | MaxPicker TLO | MPBH Adv vs Canon [95% CI] | Rel Red vs Canon (%) | MPBH Adv vs Tuned FTWB [95% CI] | Rel Red vs Tuned FTWB (%) | MPBH Adv vs MaxPicker [95% CI] |
|---|---|---|---|---|---|---|---|---|---|---|
| **30 s** | 1,738.12 | 1,976.98 | 1,948.52 | 1,948.52 | 1,947.61 | +238.86 [235.12, 242.61] | 12.08% | +210.41 [206.88, 213.93] | 10.80% | +209.49 [205.95, 213.04] |
| **60 s** | 1,754.39 | 1,984.67 | 1,959.23 | 1,959.23 | 1,958.58 | +230.29 [226.71, 233.86] | 11.60% | +204.84 [201.44, 208.24] | 10.46% | +204.19 [200.78, 207.60] |
| **120 s** | 1,782.10 | 2,002.06 | 1,976.54 | 1,976.54 | 1,976.10 | +219.96 [216.59, 223.33] | 10.99% | +194.44 [201.18, 197.71] | 9.84% | +194.00 [190.73, 197.27] |
| **180 s** | 1,803.16 | 2,014.18 | 1,988.64 | 1,988.64 | 1,988.36 | +211.02 [207.78, 214.27] | 10.48% | +185.49 [182.37, 188.60] | 9.33% | +185.21 [182.08, 188.33] |
| **300 s** | 1,832.91 | 2,026.87 | 2,003.00 | 2,003.00 | 2,002.86 | +193.96 [190.91, 197.00] | 9.57% | +170.09 [167.19, 173.00] | 8.49% | +169.95 [167.04, 172.87] |

### Key Findings:
- MPBH maintains a statistically significant advantage across **all five setup times** ($p < 10^{-15}$).
- Even when comparing MPBH against the globally tuned FTWB(F* = 5s) or MaxPicker, MPBH's advantage remains robust, reducing late orders by **170.1 to 210.4 orders** (8.49% to 10.80% relative reduction).

## 2. Flattened Setup Utility & Trips Table
- `results/WP6/setup_trips_utility_cart.csv` has been flattened from a 3-row header into standard flat CSV format with columns: `setup_time`, `trigger_method`, `mean_cart_utilization_percent`, `picker_utility_percent`, `throughput_per_hour`, `trip_count`.

## 3. Welch Warm-Up Verification Across Policies
- Standard setting ($t_{\text{setup}} = 180\text{ s}$): Stabilisation analysis reproduces the maximum warm-up requirement across all 8 policies at **5,460 s** (achieved by MPBH, MaxPicker, and SNH).
- Stabilisation points per policy:
  - FTWB: 3,300 s
  - MaxCart: 2,220 s
  - UrgentCart: 2,220 s
  - UrgentPicker: 2,760 s
  - VTWB: 1,860 s
  - MPBH / MaxPicker / SNH: 5,460 s
- Confirming that the canonical 5,460 s warm-up bound strictly covers the longest transient phase across all policies.

## Files Delivered
- `results/WP6/setup_simulation_tuned_raw.csv` (16,200 runs)
- `results/WP6/setup_sensitivity_with_tuned_and_cis.csv`
- `results/WP6/setup_by_lambda_with_cis.csv`
- `results/WP6/setup_trips_utility_cart.csv` (flattened format)
- `results/WP6/welch_stabilization_points.csv`
- `results/WP6/welch_curves_180s.csv`
