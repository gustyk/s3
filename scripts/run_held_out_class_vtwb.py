"""
Parallel runner for class-tuned VTWB on held-out replications 15-29 across all 864 cells:
1. VTWB class-tuned by lambda: V* in {0.5: 5, 1.0: 6, 2.0: 8, 4.0: 8, 8.0: 8, 16.0: 8} (12,960 runs)
2. VTWB class-tuned by lambda x group: V* from addendum (12,960 runs)
Total runs: 25,920 runs.
"""

import copy
import sys
import time
from pathlib import Path
import pandas as pd
from multiprocessing import Pool, cpu_count

from src.configuration import load_config, DEFAULT_CONFIG
from src.experiment import run_simulation, Scenario

RATE_MAP = {0.5: 1, 1.0: 2, 2.0: 3, 4.0: 4, 8.0: 5, 16.0: 6}
CART_MAP = {100: 1, 150: 2, 200: 3}
ROUTING_MAP = {"Traversal": 1, "S-shape": 1, "Largest Gap": 2}
BATCHING_MAP = {"FCFS": 1, "EDT": 2}

def m_group(m):
    if m <= 4:
        return '1-4'
    elif m <= 8:
        return '5-8'
    else:
        return '9-12'

# Tuned parameters maps (from addendum, using global V*=8 for uninformative):
V_BY_LAMBDA = {0.5: 5, 1.0: 6, 2.0: 8, 4.0: 8, 8.0: 8, 16.0: 8}
V_BY_LAM_GRP = {
    (0.5, '1-4'): 6, (0.5, '5-8'): 1, (0.5, '9-12'): 1,
    (1.0, '1-4'): 6, (1.0, '5-8'): 4, (1.0, '9-12'): 1,
    (2.0, '1-4'): 8, (2.0, '5-8'): 8, (2.0, '9-12'): 16,
    (4.0, '1-4'): 8, (4.0, '5-8'): 8, (4.0, '9-12'): 8,
    (8.0, '1-4'): 8, (8.0, '5-8'): 8, (8.0, '9-12'): 8,
    (16.0, '1-4'): 8, (16.0, '5-8'): 8, (16.0, '9-12'): 8
}

def run_class_tuned_vtwb(task):
    variant_type, l_val, p_val, c_val, r_val, b_val, rep = task
    assert 15 <= rep <= 29, f"Rep {rep} outside held-out range 15..29"

    config = load_config(DEFAULT_CONFIG)
    params = copy.deepcopy(config.values)

    grp = m_group(p_val)
    if variant_type == "VTWB_class_lambda":
        v_thresh = V_BY_LAMBDA[l_val]
    elif variant_type == "VTWB_class_lam_grp":
        v_thresh = V_BY_LAM_GRP[(l_val, grp)]
    else:
        raise ValueError(f"Unknown variant {variant_type}")

    params["trigger_parameters"]["VTWB_threshold"] = int(v_thresh)

    scen = Scenario(
        incoming_rate_key=RATE_MAP[l_val],
        trigger_key=2, # VTWB
        num_pickers=p_val,
        batching_key=BATCHING_MAP[b_val],
        cart_key=CART_MAP[c_val],
        routing_key=ROUTING_MAP[r_val]
    )

    res = run_simulation(params, scen, rep, config.sha256)
    return {
        "variant": variant_type,
        "incoming_rate": l_val,
        "num_pickers": p_val,
        "cart_capacity": c_val,
        "routing_policy": r_val,
        "batching_method": b_val,
        "repetition": rep,
        "v_threshold": v_thresh,
        "picker_group": grp,
        "total_late_orders": res["total_late_orders"],
        "throughput_per_hour": res["throughput_per_hour"],
        "picker_utility_percent": res["picker_utility_percent"],
        "mean_cart_utilization_percent": res["mean_cart_utilization_percent"],
        "generated_orders": res["generated_orders"],
        "completed_orders": res["completed_orders"],
        "mean_tardiness_seconds": res["mean_tardiness_seconds"]
    }

def main():
    Path("results/WP5").mkdir(parents=True, exist_ok=True)
    out_file = Path("results/WP5/held_out_class_tuned_vtwb_raw.csv")

    fact_df = pd.read_csv("outputs/final-q1-v1/full-factorial/results.csv")
    scenario_keys = ["incoming_rate", "num_pickers", "cart_capacity", "routing_policy", "batching_method"]
    cells_864 = fact_df[scenario_keys].drop_duplicates()
    assert len(cells_864) == 864, f"Expected 864 cells, got {len(cells_864)}"

    tasks = []
    for var in ["VTWB_class_lambda", "VTWB_class_lam_grp"]:
        for _, row in cells_864.iterrows():
            for rep in range(15, 30): # Replications 15..29 strictly
                tasks.append((var, float(row["incoming_rate"]), int(row["num_pickers"]),
                              int(row["cart_capacity"]), str(row["routing_policy"]),
                              str(row["batching_method"]), rep))

    total = len(tasks)
    print(f"Total tasks: {total} (expected 2 * 864 * 15 = 25,920)", flush=True)

    workers = min(7, cpu_count())
    print(f"Launching on {workers} workers...", flush=True)
    start_time = time.time()
    results = []

    with Pool(processes=workers) as pool:
        for idx, res in enumerate(pool.imap_unordered(run_class_tuned_vtwb, tasks, chunksize=25), 1):
            results.append(res)
            if idx % 2000 == 0 or idx == total:
                elapsed = time.time() - start_time
                rate = idx / elapsed
                rem = (total - idx) / rate if rate > 0 else 0
                print(f"[{idx}/{total}] ({idx/total*100:.1f}%) Speed: {rate:.1f} runs/s. Elapsed: {elapsed/60:.1f}m. Rem: {rem/60:.1f}m", flush=True)

    df = pd.DataFrame(results)
    df.to_csv(out_file, index=False)
    print(f"Saved {len(df)} runs to {out_file}", flush=True)

if __name__ == "__main__":
    main()
