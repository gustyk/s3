import sys
import copy
import logging
from pathlib import Path
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.configuration import load_config, DEFAULT_CONFIG
from src.experiment import run_simulation, Scenario

logging.basicConfig(level=logging.WARNING)

def run_single(args):
    params_dict, scen, rep, config_hash = args
    res = run_simulation(params_dict, scen, rep, config_hash)
    return {
        "incoming_rate": float(params_dict["incoming_rate"][scen.incoming_rate_key]),
        "cart_capacity": int(params_dict["cart_capacity"][scen.cart_key]),
        "routing_policy": params_dict["routing_policy"][scen.routing_key],
        "batching_method": params_dict["batching_method"][scen.batching_key],
        "num_pickers": scen.num_pickers,
        "timing_policy": "FTWB",
        "composition_rule": "MPBH",
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
    base_params = copy.deepcopy(config.values)
    base_params["timing_policy_override"] = "FTWB"
    base_params["composition_rule_override"] = "MPBH"

    # All 432 scenarios x 30 reps = 12,960 runs
    # 6 lambdas x 12 pickers x 3 carts x 2 routings = 432 scenarios
    rate_map = {float(v): k for k, v in base_params["incoming_rate"].items()}
    cart_map = {int(v): k for k, v in base_params["cart_capacity"].items()}
    rout_map = {str(v): k for k, v in base_params["routing_policy"].items()}

    # Load unique 432 scenarios from full factorial
    stored_df = pd.read_csv("outputs/final-q1-v1/full-factorial/results.csv")
    scen_df = stored_df.drop_duplicates(subset=["incoming_rate", "num_pickers", "cart_capacity", "routing_policy"])[
        ["incoming_rate", "num_pickers", "cart_capacity", "routing_policy"]
    ]
    print(f"Extracted {len(scen_df)} unique scenarios from full factorial (expected 432).")
    assert len(scen_df) == 432

    tasks = []
    for _, row in scen_df.iterrows():
        scen = Scenario(
            incoming_rate_key=rate_map[float(row["incoming_rate"])],
            trigger_key=1, # FTWB
            num_pickers=int(row["num_pickers"]),
            batching_key=1, # FCFS key dummy, overridden by MPBH
            cart_key=cart_map[int(row["cart_capacity"])],
            routing_key=rout_map[str(row["routing_policy"])]
        )
        for rep in range(1, 31):
            tasks.append((base_params, scen, rep, config.sha256))

    print(f"Total FTWB x MPBH crossed runs: {len(tasks)} (expected 432 x 30 = 12,960)")
    assert len(tasks) == 12960, f"Expected 12,960 tasks, got {len(tasks)}"

    Path("results/WP4").mkdir(parents=True, exist_ok=True)
    out_file = Path("results/WP4/ftwb_mpbh_raw.csv")

    results = []
    done_count = 0
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(run_single, t) for t in tasks]
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            done_count += 1
            if done_count % 1000 == 0:
                print(f"Progress: {done_count}/12960 ({done_count/12960*100:.1f}%)")

    df = pd.DataFrame(results)
    df.to_csv(out_file, index=False)
    print(f"Saved {len(df)} runs to {out_file}")

if __name__ == "__main__":
    main()
