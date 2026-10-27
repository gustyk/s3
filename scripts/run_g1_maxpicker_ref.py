"""
G1 MaxPicker reference runs on the 144 tuning cells, replications 0-14.
144 cells × 15 reps = 2,160 runs.
Output: results/WP5/maxpicker_tuning_raw.csv
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

def run_maxpicker(task):
    cell_idx, lambda_val, pickers, cart_cap, routing_name, batching_name, rep = task
    assert 0 <= rep <= 14, f"Replication {rep} violates tuning split (must be 0..14)"
    config = load_config(DEFAULT_CONFIG)
    params = copy.deepcopy(config.values)
    # MaxPicker: trigger_key=3
    scen = Scenario(
        incoming_rate_key=RATE_MAP[lambda_val],
        trigger_key=3,  # MaxPicker
        num_pickers=pickers,
        batching_key=BATCHING_MAP[batching_name],
        cart_key=CART_MAP[cart_cap],
        routing_key=ROUTING_MAP[routing_name]
    )
    res = run_simulation(params, scen, rep, config.sha256)
    return {
        "cell_idx": cell_idx,
        "incoming_rate": lambda_val,
        "num_pickers": pickers,
        "cart_capacity": cart_cap,
        "routing_policy": routing_name,
        "batching_method": batching_name,
        "method": "MaxPicker",
        "parameter_value": 0,  # F -> 0 reference
        "repetition": rep,
        "generated_orders": res["generated_orders"],
        "completed_orders": res["completed_orders"],
        "total_late_orders": res["total_late_orders"],
        "throughput_per_hour": res["throughput_per_hour"],
        "picker_utility_percent": res["picker_utility_percent"],
        "mean_cart_utilization_percent": res["mean_cart_utilization_percent"],
        "mean_tardiness_seconds": res["mean_tardiness_seconds"],
    }

def main():
    Path("results/WP5").mkdir(parents=True, exist_ok=True)
    out_file = Path("results/WP5/maxpicker_tuning_raw.csv")
    if out_file.exists():
        print(f"Output {out_file} already exists, skipping.")
        existing = pd.read_csv(out_file)
        print(f"Existing rows: {len(existing)}")
        return

    cells_df = pd.read_csv("results/WP5/class_tuning_sample_144cells.csv")
    tasks = []
    for idx, row in cells_df.iterrows():
        for rep in range(15):
            tasks.append((idx, float(row["incoming_rate"]), int(row["num_pickers"]),
                          int(row["cart_capacity"]), str(row["routing_policy"]),
                          str(row["batching_method"]), rep))

    total = len(tasks)
    workers = min(7, cpu_count())
    print(f"Launching {total} MaxPicker tuning runs with {workers} workers...", flush=True)
    start = time.time()
    results = []
    with Pool(processes=workers) as pool:
        for i, res in enumerate(pool.imap_unordered(run_maxpicker, tasks, chunksize=20), 1):
            results.append(res)
            if i % 500 == 0 or i == total:
                elapsed = time.time() - start
                print(f"  {i}/{total} ({i/total*100:.1f}%) in {elapsed:.1f}s", flush=True)
    df = pd.DataFrame(results)
    df.to_csv(out_file, index=False)
    elapsed = time.time() - start
    print(f"Done: {len(df)} rows -> {out_file} in {elapsed:.1f}s")

if __name__ == "__main__":
    main()
