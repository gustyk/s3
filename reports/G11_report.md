# G11 Report: Release, Audit, and Final Integrity Verification
- Status: DONE (Release packaging, unit test verification, and JSON-to-CSV audit complete; independent separate-codebase recomputation marked NOT PERFORMED per Rule R1)
- Model Version: `v1.0-frozen`
- Git Commit: Current working tree clean of absolute local path artifacts.

## 1. Environment and Test Verification
- Unit test suite: **68 tests PASSED** in 17.20 s (`python -m pytest tests/ --no-cov`).
- Clean repository tree: No hardcoded local drive paths (`d:/Apps/S3`) embedded in code logic; relative repository paths used throughout.
- Code documentation and pseudocode in `docs/Appendix_A_pseudocode.md` aligned with core policy implementations in `src/trigger_method.py` and `src/batching_method.py`.

## 2. Placeholder JSON Integrity & JSON-to-CSV Audit
- `results/placeholder_values.json` regenerated cleanly with all stale entries removed ($\chi^2 = 204.38$, ratio $8.44$, structural share $6.25\%$, clearing thresholds $2/4/8$, $F^*/V^* = 60/4$, $99.96\%$).
- Automated consistency checker script passed with **0.0 discrepancy** against all authoritative source CSV files (`results/WP2/mean_tlo_by_band.csv`, `results/WP3/table4a_corrected.csv`, `results/WP4/shapley_by_lambda.csv`, `results/WP9/table10_v3.csv`).
- Explicitly documented:
  - `check_type`: **JSON-to-CSV check**.
  - `independent_verification_status`: **`NOT PERFORMED`** (a separate recomputation script from raw aggregates by an independent codebase was not conducted).

## 3. Master Index of Delivered Reports and Statuses
| Task Group | Description | Status | Primary Output Files |
|---|---|---|---|
| **G1** | Benchmark Tuning, S2, MaxPicker Reference, Scope B Head-to-Head | **DONE** | `selected_parameters_addendum.csv`, `maxpicker_tuning_raw.csv`, `held_out_evaluation_raw.csv.gz`, `head_to_head_scopeB*.csv`, `crossed_tuned_timing_*.csv` |
| **G2** | Setup Sensitivity with Tuned Rows & CIs, Flattened Table | **DONE** | `setup_simulation_tuned_raw.csv`, `setup_sensitivity_with_tuned_and_cis.csv`, `setup_trips_utility_cart.csv` (flattened), `welch_stabilization_points.csv` |
| **G3** | Inherited Backlog Triage v2 & All-Arrivals TLO v2 | **DONE** | `backlog_triage_v2.csv`, `all_arrivals_tlo_v2.csv` |
| **G4** | Status Partition by Band, Cleared Flag, and Lambda | **DONE** | `table4d_by_band_v2.csv`, `table4d_by_cleared_v2.csv`, `table4d_by_lambda_v2.csv`, `mean_tlo_by_band.csv` |
| **G5** | Table 4a/4c Corrected for Undefined-Run Averaging | **DONE** | `table4a_corrected.csv`, `table4c_corrected.csv`, `tardiness_all_policies_summary.csv` |
| **G6** | MPBH Oracle Check & Instrumentation | **PARTIAL** | `oracle_check_results.csv`, `mpbh_instrumentation_summary.json` |
| **G7** | Decision Benchmark Latency Scaling & AIC Complexity Fits | **DONE** | `mpbh_latency_scaling.csv`, `complexity_fits_aic.csv` |
| **G8** | Full Factorial Crossed Design IMM x EDT Fix & Shapley Split with CIs | **DONE** | `six_cells_full.csv`, `six_cells_by_lambda_ci.csv`, `shapley_by_lambda.csv` |
| **G9** | Table 10 v3 with CIs & Practical Significance, Winner Decomposition | **DONE** | `table10_v3.csv`, `holm_bonferroni_strict_wins.csv`, `competitor_significantly_better_6cells.csv` |
| **G10** | Provenance and Change Ladders (Cumulative & OFAT) | **DONE** | `change_ladder_cumulative.csv`, `change_ladder_ofat.csv`, `provenance_table_B1.csv` |
| **G11** | Release Verification, JSON-to-CSV Audit, and CHANGELOG | **DONE** | `placeholder_values.json`, `reports/G11_report.md`, `reports/CHANGELOG_R3c.md` |

## Files Delivered
- `results/placeholder_values.json`
- `reports/G11_report.md`
- `reports/CHANGELOG_R3c.md`
