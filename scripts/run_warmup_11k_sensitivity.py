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
TRIG_MAP = {
    "FTWB": 1,
    "VTWB": 2,
    "MaxPicker": 3,
    "MaxCart": 4,
    "UrgentPicker": 5,
    "UrgentCart": 6,
    "SNH": 7,
    "MPBH": 8
}

def run_task(task):
    setup_t, pol, l_val, p_val, c_val, r_val, b_val, rep = task
    config = load_config(DEFAULT_CONFIG)
    params = copy.deepcopy(config.values)
    params["setup_time"] = float(setup_t)
    params["warmup_seconds"] = 11000.0
    params["simulation_time"] = 28800.0

    scen = Scenario(
        incoming_rate_key=RATE_MAP[l_val],
        trigger_key=TRIG_MAP[pol],
        num_pickers=p_val,
        batching_key=BATCHING_MAP[b_val],
        cart_key=CART_MAP[c_val],
        routing_key=ROUTING_MAP[r_val]
    )

    res = run_simulation(params, scen, rep, config.sha256)
    return {
        "setup_time": float(setup_t),
        "warmup_seconds": 11000.0,
        "incoming_rate": l_val,
        "cart_capacity": c_val,
        "routing_policy": r_val,
        "batching_method": b_val,
        "num_pickers": p_val,
        "trigger_method": pol,
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
    out_file = Path("results/WP6/setup_simulation_raw_w11k.csv")

    raw_df = pd.read_csv("results/WP6/setup_simulation_raw.csv")
    cells_df = raw_df[['incoming_rate', 'num_pickers', 'cart_capacity', 'routing_policy', 'batching_method']].drop_duplicates()
    assert len(cells_df) == 36, f"Expected 36 cells, got {len(cells_df)}"

    setup_times = [30.0, 60.0]
    policies = ["FTWB", "VTWB", "MaxPicker", "MaxCart", "UrgentPicker", "UrgentCart", "SNH", "MPBH"]

    tasks = []
    for st in setup_times:
        for pol in policies:
            for _, row in cells_df.iterrows():
                for rep in range(30):
                    tasks.append((
                        st, pol,
                        float(row["incoming_rate"]),
                        int(row["num_pickers"]),
                        int(row["cart_capacity"]),
                        str(row["routing_policy"]),
                        str(row["batching_method"]),
                        rep
                    ))

    total = len(tasks)
    print(f"Total tasks: {total} (expected 2 setup x 8 pol x 36 cells x 30 reps = 17,280)")

    workers = max(1, min(7, cpu_count() - 1))
    print(f"Executing with {workers} worker processes...")
    t0 = time.time()
    results = []

    with Pool(processes=workers) as pool:
        for idx, res in enumerate(pool.imap_unordered(run_task, tasks, chunksize=32), 1):
            results.append(res)
            if idx % 1000 == 0 or idx == total:
                elapsed = time.time() - t0
                speed = idx / elapsed
                rem = (total - idx) / speed if speed > 0 else 0
                print(f"[{idx:,}/{total:,}] ({idx/total*100:.1f}%) Speed: {speed:.1f} runs/s. Elapsed: {elapsed/60:.1f}m. Rem: {rem/60:.1f}m", flush=True)

    df = pd.DataFrame(results)
    df.to_csv(out_file, index=False)
    print(f"Completed! Saved {len(df):,} runs to {out_file}")

if __name__ == "__main__":
    main()
