import sys
import copy
import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.configuration import load_config, DEFAULT_CONFIG
from src.experiment import run_simulation, Scenario

# Suppress debug logs
logging.basicConfig(level=logging.WARNING)

def run_single(args):
    params_dict, scen, rep, config_hash = args
    res = run_simulation(params_dict, scen, rep, config_hash)
    return {
        "setup_time": params_dict["setup_time"],
        "incoming_rate": float(params_dict["incoming_rate"][scen.incoming_rate_key]),
        "cart_capacity": int(params_dict["cart_capacity"][scen.cart_key]),
        "routing_policy": params_dict["routing_policy"][scen.routing_key],
        "batching_method": params_dict["batching_method"][scen.batching_key],
        "num_pickers": scen.num_pickers,
        "trigger_method": params_dict["trigger_method"][scen.trigger_key],
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
    config = load_config(DEFAULT_CONFIG)
    base_params = config.values

    # Pre-specified design:
    # t_setup in {30, 60, 120, 180, 300}
    # lam in {0.5, 1, 2, 4, 8, 16}
    # m in {2, 6, 12}
    # C in {100, 200}
    # routing = S-shape
    # composition = FCFS
    # 30 replications
    # 36 cells x 8 canonical policies = 288 scenarios
    
    rate_map = {v: k for k, v in base_params["incoming_rate"].items()}
    cart_map = {v: k for k, v in base_params["cart_capacity"].items()}
    batch_map = {v: k for k, v in base_params["batching_method"].items()}
    routing_map = {v: k for k, v in base_params["routing_policy"].items()}
    trigger_keys = list(base_params["trigger_method"].keys())

    lambdas = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
    pickers = [2, 6, 12]
    carts = [100, 200]
    rout = "S-shape"
    comp = "FCFS"
    setup_times = [30, 60, 120, 300] # 180 will be loaded/asserted from full factorial

    # 1. Load 180s results from stored factorial to reuse & verify
    stored_df = pd.read_csv("outputs/final-q1-v1/full-factorial/results.csv")
    sub_180 = stored_df[
        (stored_df["incoming_rate"].isin(lambdas)) &
        (stored_df["num_pickers"].isin(pickers)) &
        (stored_df["cart_capacity"].isin(carts)) &
        (stored_df["routing_policy"] == rout) &
        (stored_df["batching_method"] == comp)
    ].copy()
    sub_180["setup_time"] = 180.0
    print(f"Loaded {len(sub_180)} rows for setup_time=180 from stored full factorial.")
    assert len(sub_180) == 36 * 30 * 8, f"Expected 8640 rows, got {len(sub_180)}"

    # 2. Prepare task list for {30, 60, 120, 300}
    tasks = []
    for s_time in setup_times:
        p_dict = copy.deepcopy(base_params)
        p_dict["setup_time"] = float(s_time)
        for lam in lambdas:
            for m in pickers:
                for c in carts:
                    for t_key in trigger_keys:
                        scen = Scenario(
                            incoming_rate_key=rate_map[lam],
                            trigger_key=t_key,
                            num_pickers=m,
                            batching_key=batch_map[comp],
                            cart_key=cart_map[c],
                            routing_key=routing_map[rout]
                        )
                        for rep in range(1, 31):
                            tasks.append((p_dict, scen, rep, config.sha256))

    print(f"Total new simulation runs to execute: {len(tasks)} (expected 34,560)")

    # Execute in parallel
    results_list = []
    # Convert sub_180 rows to match columns
    for _, row in sub_180.iterrows():
        results_list.append({
            "setup_time": 180.0,
            "incoming_rate": row["incoming_rate"],
            "cart_capacity": int(row["cart_capacity"]),
            "routing_policy": row["routing_policy"],
            "batching_method": row["batching_method"],
            "num_pickers": int(row["num_pickers"]),
            "trigger_method": row["trigger_method"],
            "repetition": int(row["repetition"]),
            "total_late_orders": row["total_late_orders"],
            "throughput_per_hour": row["throughput_per_hour"],
            "picker_utility_percent": row["picker_utility_percent"],
            "mean_cart_utilization_percent": row["mean_cart_utilization_percent"],
            "trip_count": row["trip_count"],
            "generated_orders": row["generated_orders"],
            "completed_orders": row["completed_orders"],
            "late_completed_orders": row["late_completed_orders"],
            "late_outstanding_orders": row["late_outstanding_orders"]
        })

    done_count = 0
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(run_single, t) for t in tasks]
        for fut in as_completed(futures):
            res = fut.result()
            results_list.append(res)
            done_count += 1
            if done_count % 5000 == 0:
                print(f"Progress: {done_count}/{len(tasks)} runs finished ({done_count/len(tasks)*100:.1f}%)")

    all_df = pd.DataFrame(results_list)
    Path("results/WP6").mkdir(parents=True, exist_ok=True)
    all_df.to_csv("results/WP6/setup_simulation_raw.csv", index=False)
    print(f"Saved {len(all_df)} rows to results/WP6/setup_simulation_raw.csv")

if __name__ == "__main__":
    main()
