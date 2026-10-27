# CHANGELOG: Round 3c Deviations and Resolutions

This document records all deviations, root-cause investigations, and methodological resolutions undertaken in Round 3c.

## 1. G1 Tuning Addendum & Metric Discrepancy Reconciliation
- **Discrepancy**: Addendum previously reported $F^* = 720\text{ s}$ and MaxPicker mean TLO $= 5,776.38$, contradicting frozen $F^*=5\text{ s}$ and factorial MaxPicker $\approx 1,978$.
- **Investigation**: The preliminary script computed mean across `mean_tardiness_seconds` instead of `total_late_orders`. In seconds, large batch sizes compress tardiness among cleared runs.
- **Resolution**: Recomputed all global, per-lambda, and per-group tuning surfaces using `total_late_orders` (ORDERS). Confirmed that the frozen file ($F^*=5\text{ s}$, $V^*=8\text{ orders}$ S1, $V^*=6\text{ orders}$ S2) was correct. Re-runs of MaxPicker on 144 cells achieved identical bitwise reproduction ($0.0$ difference across 2,160 runs).

## 2. G2 Setup-Time Sensitivity Table Flattening
- **Issue**: `setup_trips_utility_cart.csv` possessed a malformed 3-row header.
- **Resolution**: Re-structured and flattened into standard schema (`setup_time`, `trigger_method`, `mean_cart_utilization_percent`, `picker_utility_percent`, `throughput_per_hour`, `trip_count`). Evaluated 16,200 new simulation runs for tuned benchmarks across all 5 setup times.

## 3. G4 Table 4d Content Correction
- **Issue**: `table4d_by_band.csv` carried mean TLO instead of the 4-category status partition.
- **Resolution**: Regenerated full 4-category partition shares (*strict on-time*, *completed on-time*, *not-yet-late*, *resolved on-time*) both order-weighted and run-mean across bands, cleared status, and lambda strata. Verified lead's target numbers with 0.00% difference.

## 4. G5 Table 4a/4c Undefined-Run Averaging Audit
- **Issue**: Runs with 0 completed orders (33,575 runs in full factorial) had tardiness, flow time, and waiting time imputed as 0.0, distorting means.
- **Resolution**: Audited every column. Delivered `table4a_corrected.csv` and `table4c_corrected.csv` with explicit separation between *completed-only* and *all-runs* values. Confirmed lead's algebraic check for FTWB ($8,214.16 \times 19,141 / 25,920 = 6,065.87$).

## 5. G8 Crossed Design IMM x EDT Fix
- **Issue**: IMM x EDT row in `six_cells_full.csv` previously carried UrgentPicker parameters (std = 2295.22, median = 1041).
- **Resolution**: Replaced with true MaxPicker x EDT runs (mean = 1977.47, std = 2310.32, median = 865.0). Recomputed Shapley split by lambda with 95% CIs (df=29), matching expected timing shares (58%, 56%, 56%, 23%, 15%, 15%).

## 6. G9 Table 10 v3 Practical Significance
- **Issue**: Practical significance flag was trivial/always true in v2.
- **Resolution**: Implemented strict pre-specified threshold: $|\Delta| \ge 1\text{ order}$ AND $\ge 0.5\%\text{ of } N$. Yields 17 True and 1 False ($\lambda=1.0$ abundant). Added on-time orders per run and isolated the 6 cells where competitors win.

## 7. G11 Integrity Labeling
- **Resolution**: Relabeled consistency check as "JSON-to-CSV check" and marked independent separate-codebase verification as `NOT PERFORMED` in compliance with Rule R1.
