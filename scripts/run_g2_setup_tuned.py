"""
Run tuned benchmark variants across setup times t_setup in {30, 60, 120, 180, 300}s
on the 36 setup cells x 30 replications (0..29) = 1,080 runs per variant per setup time.
Total runs per variant: 5,400 runs.
Variants to run:
1. FTWB tuned F*=5s
2. VTWB tuned V*=8 (S1)
3. VTWB tuned V*=6 (S2)
Total runs: 3 * 5,400 = 16,200 runs.
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

def run_single_setup_tuned(task):
    variant_name, setup_t, l_val, p_val, c_val, r_val, b_val, rep = task
    assert 0 <= rep <= 29, f"Rep {rep} outside 0..29"

    config = load_config(DEFAULT_CONFIG)
    params = copy.deepcopy(config.values)
    params["setup_time"] = float(setup_t)

    if variant_name == "FTWB_tuned_F5":
        trigger_key = 1
        params["trigger_parameters"]["FTWB_interval"] = 5
    elif variant_name == "VTWB_tuned_V8":
        trigger_key = 2
        params["trigger_parameters"]["VTWB_threshold"] = 8
    elif variant_name == "VTWB_tuned_V6":
        trigger_key = 2
        params["trigger_parameters"]["VTWB_threshold"] = 6
    else:
        raise ValueError(f"Unknown variant: {variant_name}")

    scen = Scenario(
        incoming_rate_key=RATE_MAP[l_val],
        trigger_key=trigger_key,
        num_pickers=p_val,
        batching_key=BATCHING_MAP[b_val],
        cart_key=CART_MAP[c_val],
        routing_key=ROUTING_MAP[r_val]
    )

    res = run_simulation(params, scen, rep, config.sha256)
    return {
        "variant": variant_name,
        "setup_time": float(setup_t),
        "incoming_rate": l_val,
        "cart_capacity": c_val,
        "routing_policy": r_val,
        "batching_method": b_val,
        "num_pickers": p_val,
        "trigger_method": variant_name,
        "repetition": rep,
        "total_late_orders": res["total_late_orders"],
        "throughput_per_hour": res["throughput_per_hour"],
        "picker_utility_percent": res["picker_utility_percent"],
        "mean_cart_utilization_percent": res["mean_cart_utilization_percent"],
        "trip_count": res["trip_count"],
        "generated_orders": res["generated_orders"],
        "completed_orders": res["completed_orders"],
        "late_completed_orders": res["late_completed_orders"],
        "late_outstanding_orders": res["late_outstanding_orders"]
    }

def main():
    Path("results/WP6").mkdir(parents=True, exist_ok=True)
    out_file = Path("results/WP6/setup_simulation_tuned_raw.csv")

    # Load 36 cells
    raw_df = pd.read_csv("results/WP6/setup_simulation_raw.csv")
    cells_df = raw_df[['incoming_rate', 'num_pickers', 'cart_capacity', 'routing_policy', 'batching_method']].drop_duplicates()
    assert len(cells_df) == 36, f"Expected 36 cells, got {len(cells_df)}"

    setup_times = [30.0, 60.0, 120.0, 180.0, 300.0]
    variants = ["FTWB_tuned_F5", "VTWB_tuned_V8", "VTWB_tuned_V6"]

    tasks = []
    for var in variants:
        for st in setup_times:
            for _, row in cells_df.iterrows():
                for rep in range(30):
                    tasks.append((var, st, float(row["incoming_rate"]), int(row["num_pickers"]),
                                  int(row["cart_capacity"]), str(row["routing_policy"]),
                                  str(row["batching_method"]), rep))

    total = len(tasks)
    print(f"Total tasks to execute: {total} (expected 3 * 5 * 36 * 30 = 16,200)", flush=True)

    workers = min(7, cpu_count())
    print(f"Launching on {workers} parallel workers...", flush=True)
    start_time = time.time()
    results = []

    with Pool(processes=workers) as pool:
        for idx, res in enumerate(pool.imap_unordered(run_single_setup_tuned, tasks, chunksize=25), 1):
            results.append(res)
            if idx % 1000 == 0 or idx == total:
                elapsed = time.time() - start_time
                rate = idx / elapsed
                rem = (total - idx) / rate if rate > 0 else 0
                print(f"[{idx}/{total}] ({idx/total*100:.1f}%) Speed: {rate:.1f} runs/s. Elapsed: {elapsed/60:.1f}m. Rem: {rem/60:.1f}m", flush=True)

    df = pd.DataFrame(results)
    df.to_csv(out_file, index=False)
    print(f"Saved {len(df)} runs to {out_file}", flush=True)

if __name__ == "__main__":
    main()
