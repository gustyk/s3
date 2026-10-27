"""
Parallel runner for class-tuning:
144 cells * 15 reps * 28 grid points = 60,480 runs.
Writes progress and checkpoints every 2,000 runs to results/WP5/class_tuning_checkpoint.csv.
Final output saved to results/WP5/class_tuning_raw.csv.gz.
"""

import copy
import sys
import os
import time
from pathlib import Path
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count

from src.configuration import load_config, DEFAULT_CONFIG
from src.experiment import run_simulation, Scenario

F_GRID = [5, 15, 30, 60, 120, 180, 240, 300, 360, 480, 600, 720, 900, 1200]
V_GRID = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32]

RATE_MAP = {0.5: 1, 1.0: 2, 2.0: 3, 4.0: 4, 8.0: 5, 16.0: 6}
CART_MAP = {100: 1, 150: 2, 200: 3}
ROUTING_MAP = {"Traversal": 1, "S-shape": 1, "Largest Gap": 2}
BATCHING_MAP = {"FCFS": 1, "EDT": 2}

def execute_single_run(task):
    cell_idx, lambda_val, pickers, cart_cap, routing_name, batching_name, method, param_val, rep = task
    config = load_config(DEFAULT_CONFIG)
    params = copy.deepcopy(config.values)
    
    if method == "FTWB":
        trigger_key = 1
        params["trigger_parameters"]["FTWB_interval"] = int(param_val)
    else:
        trigger_key = 2
        params["trigger_parameters"]["VTWB_threshold"] = int(param_val)
        
    scen = Scenario(
        incoming_rate_key=RATE_MAP[lambda_val],
        trigger_key=trigger_key,
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
        "method": method,
        "parameter_value": param_val,
        "repetition": rep,
        "generated_orders": res["generated_orders"],
        "completed_orders": res["completed_orders"],
        "total_late_orders": res["total_late_orders"],
        "throughput_per_hour": res["throughput_per_hour"],
        "picker_utility_percent": res["picker_utility_percent"],
        "mean_cart_utilization_percent": res["mean_cart_utilization_percent"],
        "mean_tardiness_seconds": res["mean_tardiness_seconds"]
    }

def main():
    Path("results/WP5").mkdir(parents=True, exist_ok=True)
    cells_df = pd.read_csv("results/WP5/class_tuning_sample_144cells.csv")
    
    tasks = []
    for idx, row in cells_df.iterrows():
        l_val = float(row["incoming_rate"])
        p_val = int(row["num_pickers"])
        c_val = int(row["cart_capacity"])
        r_val = str(row["routing_policy"])
        b_val = str(row["batching_method"])
        
        for rep in range(15): # Replications 0..14 for tuning
            for f_val in F_GRID:
                tasks.append((idx, l_val, p_val, c_val, r_val, b_val, "FTWB", f_val, rep))
            for v_val in V_GRID:
                tasks.append((idx, l_val, p_val, c_val, r_val, b_val, "VTWB", v_val, rep))
                
    total_tasks = len(tasks)
    workers = min(7, cpu_count())
    print(f"Starting execution of {total_tasks} runs with {workers} parallel workers...", flush=True)
    
    out_file = Path("results/WP5/class_tuning_raw.csv.gz")
    checkpoint_file = Path("results/WP5/class_tuning_checkpoint.csv")
    chunk_size = 2000
    results_list = []
    start_time = time.time()
    
    with Pool(processes=workers) as pool:
        for idx, res in enumerate(pool.imap_unordered(execute_single_run, tasks, chunksize=25), 1):
            results_list.append(res)
            if idx % chunk_size == 0 or idx == total_tasks:
                elapsed = time.time() - start_time
                rate = idx / elapsed
                remaining = (total_tasks - idx) / rate if rate > 0 else 0
                print(f"[{idx}/{total_tasks}] Completed ({idx/total_tasks*100:.1f}%). Speed: {rate:.1f} runs/s. Elapsed: {elapsed/60:.1f} min. Remaining: {remaining/60:.1f} min.", flush=True)
                
                # Checkpoint
                temp_df = pd.DataFrame(results_list)
                temp_df.to_csv(checkpoint_file, index=False)
                
    final_df = pd.DataFrame(results_list)
    final_df.to_csv(out_file, index=False, compression="gzip")
    print(f"Finished all {total_tasks} runs. Saved to {out_file}.", flush=True)

if __name__ == "__main__":
    main()
