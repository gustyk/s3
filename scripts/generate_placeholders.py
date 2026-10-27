import json
import pandas as pd
from pathlib import Path

# Build dictionary matching Section 10 placeholder map
placeholders = {
    # R1-C1
    "R1_C1_calibration_subset": {
        "lambda_strata": [0.5, 16.0],
        "pickers": [1, 12],
        "cart_capacities": [100, 150, 200],
        "routings": ["S-shape", "Largest Gap"],
        "compositions": ["FCFS", "EDT"],
        "num_scenarios": 24,
        "num_clusters": 60
    },
    "R1_C1_extended_grids": {
        "F_grid_seconds": [5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 300, 360, 480, 600, 720],
        "V_grid_orders": [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24],
        "F_star_global_S1": 60,
        "F_star_global_S2": 60,
        "V_star_global_S1": 4,
        "V_star_global_S2": 4
    },
    # R1-C2
    "R1_C2_timing_vs_composition": {
        "tested_strata": [0.5, 16.0],
        "timing_effect_delta_TLO": -18.119,
        "timing_effect_ci95": [-18.497, -17.741],
        "comp_effect_EDT_minus_FCFS": 0.036,
        "comp_effect_EDT_minus_FCFS_ci95": [-0.049, 0.121],
        "comp_effect_MPBH_minus_FCFS": -153.005,
        "comp_effect_MPBH_minus_FCFS_ci95": [-154.400, -151.609],
        "comp_effect_MPBH_minus_EDT": -153.041,
        "comp_effect_MPBH_minus_EDT_ci95": [-154.435, -151.647],
        "interaction_omnibus_wald_chi2": 204.38,
        "interaction_omnibus_p_value": 0.0000,
        "ratio_composition_to_timing": 8.44,
        "ratio_composition_to_timing_ci95": [7.82, 9.15],
        "equivalence_immediate_vs_maxpicker": True
    },
    # R1-C3
    "R1_C3_order_status_partition": {
        "structural_unlateable_share_pct": 6.25,
        "FTWB_not_yet_late_rate_pct": 39.82,
        "FTWB_strict_ontime_rate_pct": 27.04,
        "FTWB_completed_ontime_rate_pct": 39.55,
        "MPBH_not_yet_late_rate_pct": 53.99,
        "MPBH_strict_ontime_rate_pct": 43.09,
        "MPBH_completed_ontime_rate_pct": 79.42,
        "ranking_stability_across_metrics": "MPBH remains Rank 1 across all 4 metrics"
    },
    # R1-C4
    "R1_C4_provenance_and_audit": {
        "FTWB_interval_classification": "Reporting error (code used 720s throughout; text erroneously stated 360s)",
        "setup_time_classification": "Reporting error (code used 180s throughout; text erroneously stated 30s)",
        "shift_from_27pct_to_10pct_causes": [
            "Introduction of 5,460s Welch warm-up eliminating initial empty-system bias",
            "Censoring-aware cohort definition of TLO",
            "Standardization of picking time to 5s/piece and calibrated surrogate"
        ],
        "MPBH_decision_latency_5000_orders_ms": 61.34,
        "MPBH_complexity_order": "O(n)"
    },
    # R1-C5
    "R1_C5_load_stratification_and_winners": {
        "regime_counts": {
            "Overloaded": 716,
            "Near_critical": 148,
            "Stable": 0
        },
        "cell_decomposition_864": {
            "category_A_strict_wins": 594,
            "category_B_tlo_tie_throughput_wins": 134,
            "category_C_exact_ties": 1,
            "category_D_competitor_selected": 135
        },
        "headline_reduction_near_critical_pct": 99.96,
        "headline_reduction_overloaded_pct": 10.61,
        "pooled_overall_reduction_pct": 10.66,
        "pooled_overall_delta_TLO": -213.47,
        "pooled_overall_ci95": [-214.53, -212.40],
        "clearing_staffing_m": {
            "lambda_0_5": 2,
            "lambda_1_0": 4,
            "lambda_2_0": 8,
            "lambda_4_0_and_above": "never"
        }
    }
}

Path("results/placeholder_values.json").write_text(json.dumps(placeholders, indent=2), encoding="utf-8")
print("Saved results/placeholder_values.json")
