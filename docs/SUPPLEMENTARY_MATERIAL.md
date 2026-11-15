# Supplementary Material Index

The compiled supplement is [`../supplement/Supplementary_Material.pdf`](../supplement/Supplementary_Material.pdf)
(source: [`../supplement/Supplementary_Material.md`](../supplement/Supplementary_Material.md); build with
`python scripts/build_supplementary.py`, which needs `pip install reportlab` for the PDF).

## Mapping of manuscript items to files

| Manuscript item | Files |
|---|---|
| Appendix A (pseudocode) | [`Appendix_A_pseudocode.md`](Appendix_A_pseudocode.md); extended: [`ALGORITHM_APPENDIX.md`](ALGORITHM_APPENDIX.md) |
| Table B1 | [`../results/WP0/provenance_table_B1.csv`](../results/WP0/provenance_table_B1.csv) |
| Table S1 | `../results/WP5/tuning_surface_global.csv`, `tuning_surface_global_ftwb.csv`, `tuning_surface_global_vtwb.csv`, `tuning_surface_class.csv`, `selected_parameters.csv` |
| Table S2 | `../results/WP3/table4d_status_partition_exact.csv`, `../results/WP3/tardiness_all_policies_summary.csv` |
| Table S3 | `../results/WP9/table10_v3.csv` |
| Table S4 | `../results/WP8/all_arrivals_tlo_v4.csv`, `../results/WP8/backlog_triage_v4.csv` |
| Table S5 | `../results/WP4/crossed_effects_by_lambda_ci.csv`, `../results/WP4/shapley_by_lambda.csv`, `../results/WP5/crossed_tuned_timing_effects_by_lambda_ci.csv`, `../results/WP5/crossed_tuned_timing_shapley.csv` |
| Table S6 | `../results/WP6/setup_sensitivity_with_tuned_and_cis.csv`, `../results/WP6/warmup_11k_vs_5k_by_setup.csv`, `../results/WP6/warmup_11k_vs_5k_by_lambda.csv` |
| Table S7 | `../results/WP7/surrogate_batch_validation.csv`, `../results/WP7/oracle_check_results_rerun.csv`, `../results/WP7/oracle_decision_mismatch.csv` |
| Table S8 | `../results/WP0/change_ladder_ofat.csv`, `../results/WP0/combined_revert_results.csv` |
| Figures S1-S4 (SD and CV of TLO vs arrival rate and vs pickers; Figures 10-13 of revision 1) | `revised-paper-assets/generated/Figure_10_tlo_sd_by_arrival_rate.png`, `Figure_11_tlo_cv_by_arrival_rate.png`, `Figure_12_tlo_sd_by_pickers.png`, `Figure_13_tlo_cv_by_pickers.png` |
| Figure S5 | [`../supplement/Figure_S5_latency_scaling_pinned_core.png`](../supplement/Figure_S5_latency_scaling_pinned_core.png) — median decision-kernel latency with IQR bars across eight policies and eight order-pool sizes; 30 repeats per point, process pinned to CPU core 0. Source: `../results/WP7/all_policies_latency_scaling_pinned_core.csv`. Regenerate with `python scripts/generate_revised_figures.py --supplement-s5-latency`. |

`revised-paper-assets/Table_04c_Flow_and_Tour_Efficiency.csv` is Table 4c (not Table S1).

## Further documentation

- Conceptual equations, algorithms, assumptions: [`MODEL_SPECIFICATION.md`](MODEL_SPECIFICATION.md)
- Parameter provenance and input uncertainty: [`PARAMETER_PROVENANCE.md`](PARAMETER_PROVENANCE.md)
- Data schema and KPI definitions: [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md)
- Confirmatory analysis and deviations: [`ANALYSIS_PLAN.md`](ANALYSIS_PLAN.md)
- Verification evidence: `tests/`, CI coverage and smoke artifacts
- Validation evidence: [`VALIDATION_PROTOCOL.md`](VALIDATION_PROTOCOL.md)
- Engineering extreme/degenerate tests: [`EXTREME_CONDITION_EVIDENCE.md`](EXTREME_CONDITION_EVIDENCE.md)
- Input-distribution fitting: `src/input_analysis.py`
- Local CPU/RSS/disk/scalability evidence: `src/benchmark.py`
- Reporting map: [`STRESS_DES_CHECKLIST.md`](STRESS_DES_CHECKLIST.md)
- Limitations: [`THREATS_TO_VALIDITY.md`](THREATS_TO_VALIDITY.md)
- Artifact exercise: [`ARTIFACT_APPENDIX.md`](ARTIFACT_APPENDIX.md)
- Operational extract contract: [`OPERATIONAL_DATA_SCHEMA.md`](OPERATIONAL_DATA_SCHEMA.md)
- Tagged final-run procedure: [`RELEASE_RUNBOOK.md`](RELEASE_RUNBOOK.md)
