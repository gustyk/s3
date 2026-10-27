import sys
import copy
import logging
from pathlib import Path
import numpy as np
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
        "trip_count": res["trip_count"]
    }

def main():
    config = load_config(DEFAULT_CONFIG)
    base_params = copy.deepcopy(config.values)

    # 432 scenarios x 30 reps = 12,960 runs
    # timing_policy = "FTWB", composition_rule = "MPBH"
    base_params["timing_policy_override"] = "FTWB"
    base_params["composition_rule_override"] = "MPBH"
    
    # Check trigger method for crossed design
    # In trigger_method.py, crossed_timing_composition_trigger handles timing_policy="FTWB", composition_rule="MPBH"
    # Let's inspect how experiment.py routes crossed design overrides.
    print("Testing crossed execution setup...")

if __name__ == "__main__":
    main()
