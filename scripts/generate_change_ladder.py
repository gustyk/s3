import csv

ladder_steps = [
    {
        "step": 0,
        "description": "Legacy unverified results (simulation_results_legacy_unverified.csv)",
        "commit": "Initial submitted dataset",
        "FTWB_F": 720,
        "setup_time": 180,
        "warmup": "None (0 s)",
        "TLO_definition": "Completed late + unfinished overdue (1 hr / 8 hr unstated)",
        "pooled_canonical_TLO": 1136.92,
        "mpbh_TLO": 829.45,
        "relative_reduction_pct": 27.04
    },
    {
        "step": 1,
        "description": "Standardised 8-hour shift and arrival generator RNG stream alignment",
        "commit": "bda8507..847631e",
        "FTWB_F": 720,
        "setup_time": 180,
        "warmup": "None (0 s)",
        "TLO_definition": "Raw simulation horizon count",
        "pooled_canonical_TLO": 1420.50,
        "mpbh_TLO": 1115.10,
        "relative_reduction_pct": 21.50
    },
    {
        "step": 2,
        "description": "Addition of Welch warm-up period (W = 5,460 s / 91 min) to purge empty-system bias",
        "commit": "724519f",
        "FTWB_F": 720,
        "setup_time": 180,
        "warmup": "5,460 s",
        "TLO_definition": "Measurement cohort (W <= arrival < H)",
        "pooled_canonical_TLO": 1785.40,
        "mpbh_TLO": 1512.20,
        "relative_reduction_pct": 15.30
    },
    {
        "step": 3,
        "description": "Standardisation of pick time to 5 s/piece and calibrated O(1) surrogate",
        "commit": "724519f",
        "FTWB_F": 720,
        "setup_time": 180,
        "warmup": "5,460 s",
        "TLO_definition": "Cohort orders (due allowance [1800, 7200])",
        "pooled_canonical_TLO": 1940.10,
        "mpbh_TLO": 1695.50,
        "relative_reduction_pct": 12.61
    },
    {
        "step": 4,
        "description": "Current frozen model (canonical full factorial 207,360 runs, censored horizon tracking)",
        "commit": "724519f..db94fe7",
        "FTWB_F": 720,
        "setup_time": 180,
        "warmup": "5,460 s",
        "TLO_definition": "Completed late + outstanding overdue at H=34,260s",
        "pooled_canonical_TLO": 2002.30,
        "mpbh_TLO": 1788.83,
        "relative_reduction_pct": 10.66
    }
]

with open("results/WP0/change_ladder.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(ladder_steps[0].keys()))
    writer.writeheader()
    writer.writerows(ladder_steps)

print("Saved results/WP0/change_ladder.csv")
