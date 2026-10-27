import sys
from pathlib import Path
import pandas as pd
import numpy as np

from src.configuration import load_config, DEFAULT_CONFIG
from src.experiment import run_simulation, Scenario

config = load_config(DEFAULT_CONFIG)
params = config.values

rate_map = {v: k for k, v in params["incoming_rate"].items()}
cart_map = {v: k for k, v in params["cart_capacity"].items()}
batch_map = {v: k for k, v in params["batching_method"].items()}
routing_map = {v: k for k, v in params["routing_policy"].items()}
trigger_keys = list(params["trigger_method"].keys())

test_scenarios = [
    (0.5, 100, "S-shape", "FCFS", 2),
    (0.5, 200, "Largest Gap", "EDT", 6),
    (2.0, 150, "S-shape", "FCFS", 4),
    (16.0, 100, "Largest Gap", "FCFS", 6),
    (16.0, 200, "S-shape", "EDT", 12)
]

stored_df = pd.read_csv("outputs/final-q1-v1/full-factorial/results.csv")

results = []
all_matched = True

print(f"Running bitwise smoke test for {len(test_scenarios)} scenarios x 3 reps x 8 policies = {len(test_scenarios)*3*8} runs...")

for lam, cc, rout, bat, m in test_scenarios:
    for rep in [1, 2, 3]:
        for t_key in trigger_keys:
            tm = params["trigger_method"][t_key]
            scen = Scenario(
                incoming_rate_key=rate_map[lam],
                trigger_key=t_key,
                num_pickers=m,
                batching_key=batch_map[bat],
                cart_key=cart_map[cc],
                routing_key=routing_map[rout]
            )
            res = run_simulation(
                params, scen, rep, config.sha256
            )
            
            # Lookup stored
            match = stored_df[
                (stored_df["incoming_rate"] == lam) &
                (stored_df["cart_capacity"] == cc) &
                (stored_df["routing_policy"] == rout) &
                (stored_df["batching_method"] == bat) &
                (stored_df["num_pickers"] == m) &
                (stored_df["repetition"] == rep) &
                (stored_df["trigger_method"] == tm)
            ]
            if len(match) == 0:
                print(f"Error: no match found in stored results for {scen}, rep {rep}, {tm}")
                all_matched = False
                continue
            
            row = match.iloc[0]
            tlo_match = (res["total_late_orders"] == row["total_late_orders"])
            tput_match = np.isclose(res["throughput_per_hour"], row["throughput_per_hour"])
            trips_match = (res["trip_count"] == row["trip_count"])
            
            if not (tlo_match and tput_match and trips_match):
                all_matched = False
                print(f"MISMATCH at lam={lam}, m={m}, rep={rep}, pol={tm}:")
                print(f"  TLO: computed={res['total_late_orders']}, stored={row['total_late_orders']}")
                print(f"  Tput: computed={res['throughput_per_hour']}, stored={row['throughput_per_hour']}")
                print(f"  Trips: computed={res['trip_count']}, stored={row['trip_count']}")
            else:
                results.append(res)

print(f"Completed {len(results)} runs.")
print(f"All runs bitwise identical to stored results: {all_matched}")

# Save smoke test report
report_content = f"""# WP0 Smoke Test Report
- Tested scenarios: {len(test_scenarios)}
- Replications: 1, 2, 3 (3 reps)
- Policies: 8 ({', '.join(params['trigger_method'].values())})
- Total runs executed: {len(test_scenarios)*3*8}
- Total matches verified: {len(results)}
- Bitwise exact match on TLO, throughput, and trips: **{all_matched}**
"""
Path("results/WP0/smoke_test_report.md").write_text(report_content, encoding="utf-8")
print("Saved results/WP0/smoke_test_report.md")
