"""
Held-out evaluation runner:
Replications strictly 15 to 29 (15 reps).
Total tasks:
1. Scope B (Tuned benchmarks vs Canonical on all 864 cells):
   - FTWB(F*=5s, S1 & S2): 864 cells * 15 reps = 12,960 runs
   - VTWB(V*=8 orders, S1): 864 cells * 15 reps = 12,960 runs
   - VTWB(V*=6 orders, S2): 864 cells * 15 reps = 12,960 runs
   (Total Scope B tuned runs = 38,880 runs)
2. MPBH beta=1 sensitivity:
   - 432 scenarios * 15 reps = 6,480 runs
3. Crossed FTWB(F*=5s) x MPBH-composition:
   - 432 scenarios * 15 reps = 6,480 runs
Total runs to simulate = 51,840 runs.
Strict assertion log verifies replication indices are in 15..29.
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

RATE_MAP = {0.5: 1, 1.0: 2, 2.0: 3, 4.0: 4, 8.0: 5, 16.0: 6}
CART_MAP = {100: 1, 150: 2, 200: 3}
ROUTING_MAP = {"Traversal": 1, "S-shape": 1, "Largest Gap": 2}
BATCHING_MAP = {"FCFS": 1, "EDT": 2}

def execute_heldout_run(task):
    experiment_type, lambda_val, pickers, cart_cap, routing_name, batching_name, rep, extra_params = task
    assert 15 <= rep <= 29, f"Replication {rep} violates held-out split (must be 15..29)"
    
    config = load_config(DEFAULT_CONFIG)
    params = copy.deepcopy(config.values)
    
    if experiment_type == "FTWB_tuned_F5":
        trigger_key = 1
        batching_key = BATCHING_MAP[batching_name]
        params["trigger_parameters"]["FTWB_interval"] = 5
    elif experiment_type == "VTWB_tuned_V8":
        trigger_key = 2
        batching_key = BATCHING_MAP[batching_name]
        params["trigger_parameters"]["VTWB_threshold"] = 8
    elif experiment_type == "VTWB_tuned_V6":
        trigger_key = 2
        batching_key = BATCHING_MAP[batching_name]
        params["trigger_parameters"]["VTWB_threshold"] = 6
    elif experiment_type == "MPBH_beta1":
        trigger_key = 8
        batching_key = 1 # dummy
        params["trigger_parameters"]["Urgent_threshold"] = 1
    elif experiment_type == "FTWB_F5_x_MPBH_comp":
        trigger_key = 1
        batching_key = 1
        params["trigger_parameters"]["FTWB_interval"] = 5
        params["timing_policy_override"] = "FTWB"
        params["composition_rule_override"] = "MPBH"
    else:
        raise ValueError(f"Unknown experiment type: {experiment_type}")

    scen = Scenario(
        incoming_rate_key=RATE_MAP[lambda_val],
        trigger_key=trigger_key,
        num_pickers=pickers,
        batching_key=batching_key,
        cart_key=CART_MAP[cart_cap],
        routing_key=ROUTING_MAP[routing_name]
    )
    
    res = run_simulation(params, scen, rep, config.sha256)
    return {
        "experiment_type": experiment_type,
        "incoming_rate": lambda_val,
        "num_pickers": pickers,
        "cart_capacity": cart_cap,
        "routing_policy": routing_name,
        "batching_method": batching_name,
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
    
    # Load 864 cells
    ff = pd.read_csv("outputs/final-q1-v1/full-factorial/results.csv")
    cells_864 = ff[["incoming_rate", "num_pickers", "cart_capacity", "routing_policy", "batching_method"]].drop_duplicates()
    scens_432 = ff[["incoming_rate", "num_pickers", "cart_capacity", "routing_policy"]].drop_duplicates()
    
    tasks = []
    
    # 1. Scope B tuned benchmarks on 864 cells x reps 15..29
    for _, row in cells_864.iterrows():
        l_val = float(row["incoming_rate"])
        p_val = int(row["num_pickers"])
        c_val = int(row["cart_capacity"])
        r_val = str(row["routing_policy"])
        b_val = str(row["batching_method"])
        for rep in range(15, 30):
            tasks.append(("FTWB_tuned_F5", l_val, p_val, c_val, r_val, b_val, rep, {}))
            tasks.append(("VTWB_tuned_V8", l_val, p_val, c_val, r_val, b_val, rep, {}))
            tasks.append(("VTWB_tuned_V6", l_val, p_val, c_val, r_val, b_val, rep, {}))
            
    # 2. MPBH beta=1 on 432 scenarios x reps 15..29
    for _, row in scens_432.iterrows():
        l_val = float(row["incoming_rate"])
        p_val = int(row["num_pickers"])
        c_val = int(row["cart_capacity"])
        r_val = str(row["routing_policy"])
        for rep in range(15, 30):
            tasks.append(("MPBH_beta1", l_val, p_val, c_val, r_val, "FCFS", rep, {}))
            
    # 3. FTWB(F*=5s) x MPBH-comp on 432 scenarios x reps 15..29
    for _, row in scens_432.iterrows():
        l_val = float(row["incoming_rate"])
        p_val = int(row["num_pickers"])
        c_val = int(row["cart_capacity"])
        r_val = str(row["routing_policy"])
        for rep in range(15, 30):
            tasks.append(("FTWB_F5_x_MPBH_comp", l_val, p_val, c_val, r_val, "FCFS", rep, {}))
            
    total_tasks = len(tasks)
    print(f"Total held-out evaluation tasks generated: {total_tasks}", flush=True)
    assert total_tasks == 51840, f"Expected 51,840 tasks, got {total_tasks}"
    
    workers = min(7, cpu_count())
    print(f"Launching held-out execution across {workers} parallel workers...", flush=True)
    
    out_file = Path("results/WP5/held_out_evaluation_raw.csv.gz")
    checkpoint_file = Path("results/WP5/held_out_evaluation_checkpoint.csv")
    chunk_size = 2000
    results_list = []
    start_time = time.time()
    
    with Pool(processes=workers) as pool:
        for idx, res in enumerate(pool.imap_unordered(execute_heldout_run, tasks, chunksize=25), 1):
            results_list.append(res)
            if idx % chunk_size == 0 or idx == total_tasks:
                elapsed = time.time() - start_time
                rate = idx / elapsed
                remaining = (total_tasks - idx) / rate if rate > 0 else 0
                print(f"[{idx}/{total_tasks}] Completed ({idx/total_tasks*100:.1f}%). Speed: {rate:.1f} runs/s. Elapsed: {elapsed/60:.1f} min. Remaining: {remaining/60:.1f} min.", flush=True)
                
                temp_df = pd.DataFrame(results_list)
                temp_df.to_csv(checkpoint_file, index=False)
                
    final_df = pd.DataFrame(results_list)
    final_df.to_csv(out_file, index=False, compression="gzip")
    print(f"Finished held-out evaluation of {total_tasks} runs. Saved to {out_file}.", flush=True)

if __name__ == "__main__":
    main()
