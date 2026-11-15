# Revised Paper Assets

This folder collects the verified final-result tables and figure assets of the
revised manuscript. Filenames use the revised manuscript numbering.

## Tables

| Revised item | File | Status |
|---|---|---|
| Table 1 | `Table_01_Literature_Comparison.md` | Revised manuscript table |
| Table 2 | `Table_02_Research_Gap_Mapping.md` | Revised manuscript table |
| Tables 3a--3b | `Table_03a_Dynamic_Variables_and_Outcomes.md`; `Table_03b_Fixed_and_Experimental_Parameters.md` | Revised manuscript tables |
| Table 4 | `Table_04_Final_Factorial_Summary.csv` | Final manuscript table |
| Table 5 | `Table_05_Primary_Paired_CRN_Contrasts.csv` | Final manuscript table |
| Table 6 | `Table_06_Context_Winners.csv` | Final manuscript table |
| Table 7 | `Table_07_Timing_Composition_Ablation.csv` | Final paired-contrast source |
| Table 8 | `Table_08_Decision_Kernel_Latency.csv` | Final benchmark observations |
| Table 4c | `Table_04c_Flow_and_Tour_Efficiency.csv` | Final extended-metrics source |

## Figures

| Revised item | Asset or source file | Status |
|---|---|---|
| Figure 1 | `generated/Figure_01_warehouse_layout.png` | Final image available |
| Figures 2--4 | `Figure_02_to_05_source_final_summary.csv` | Regeneration required |
| Figure 5 | `generated/Figure_05_service_throughput_pareto.png` | Regenerated from the order-weighted Table 4d status partition and full-factorial `results.csv`; global frontier maximises service, throughput, and picker utilisation |
| Figures 6--8 | `Figure_06_to_08_source_final_results.csv` | Regeneration required |
| Figure 9 | `Figure_09_Pareto_Service_Throughput.png` | Final image available |
| Figures 10--13 | `Figure_10_to_13_source_final_results.csv` | Regeneration required |
| WP4 Figure 10 (Panel B) | `generated/Figure_10_wp4_panel_b_conditional_effects.png` | 9 conditional effects and 2 interactions with 95% confidence intervals; regenerate with `python scripts/generate_revised_figures.py --wp4-panel-b` |
| WP5 Figure 11 (formerly Figure 16) | `generated/Figure_11_wp5_benchmark_calibration_sensitivity.png` | "Figure 11 Tuning and held-out sensitivity of FTWB and VTWB parameters (selected values marked; MaxPicker shown for reference)"; regenerate with `python scripts/generate_revised_figures.py --wp5-figure-11` |
| Figure 14 | `Figure_14_source_final_results.csv` | Regeneration required |
| Figure 15 | `Figure_15_source_crossed_timing_composition.csv` | Regeneration required |
| Figure 17 | `Figure_17_source_beta_sensitivity.csv` | Regeneration required |
| Figure 18 | `Figure_18_source_decision_latency.csv` | Regeneration required |

Only final-result artifacts are included. No legacy figures are copied under a
revised figure number.

The WP4 Panel B Figure 10 is a separate analysis asset from revised-manuscript
Figures 10--13. Its scoped filename preserves the existing manuscript Figure 10
output.

The WP5 Figure 11 is also a separately named analysis asset; its held-out curve
connects only the selected and canonical parameter values available in the
held-out results, not a held-out evaluation of the full expanded grid. Its
scoped filename preserves the existing manuscript Figure 11 output.