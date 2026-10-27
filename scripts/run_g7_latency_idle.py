import os
import time
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from src.trigger_method import (
    ftwb_trigger, vtwb_trigger, max_picker_trigger, max_cart_trigger,
    urgent_picker_trigger, urgent_cart_trigger, snh_trigger, _mpbh_batch
)
from src.configuration import load_config, DEFAULT_CONFIG

class DummyEnv:
    now = 10000.0

def get_git_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        return "unknown"

def main():
    commit = get_git_hash()
    config = load_config(DEFAULT_CONFIG)
    params = config.values

    Path("results/WP7").mkdir(parents=True, exist_ok=True)

    env = DummyEnv()
    pool_sizes = [10, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 20000, 40000]
    repeats = 30

    print("Running idle-machine latency benchmark for MPBH up to n=40,000...")
    records = []

    for n in pool_sizes:
        trial_times = []
        for r in range(repeats):
            np.random.seed(1000 * r + n)
            waiting = []
            for i in range(n):
                waiting.append({
                    'Order ID': f'O_{i}',
                    'Created Time Seconds': float(np.random.uniform(0, 10000)),
                    'Due Time Seconds': float(10000 + np.random.uniform(300, 7200)),
                    'Total Item': 2,
                    'Order List': [(int(np.random.randint(1, 1000)), 1), (int(np.random.randint(1, 1000)), 1)]
                })
            t0 = time.perf_counter()
            _ = _mpbh_batch(env, waiting, 100, 2, 'S-shape', params)
            t1 = time.perf_counter()
            trial_times.append((t1 - t0) * 1000.0)

        mean_t = float(np.mean(trial_times))
        std_t = float(np.std(trial_times, ddof=1))
        min_t = float(np.min(trial_times))
        max_t = float(np.max(trial_times))

        records.append({
            "order_pool_size": n,
            "mean_latency_ms": mean_t,
            "std_latency_ms": std_t,
            "min_latency_ms": min_t,
            "max_latency_ms": max_t,
            "repeats": repeats,
            "commit_hash": commit
        })
        print(f"Pool size {n:5d}: Mean {mean_t:7.3f} ms (max: {max_t:7.3f} ms)")

    df = pd.DataFrame(records)
    csv_path = "results/WP7/mpbh_latency_scaling_v2.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved {csv_path}")

    # Compute Complexity Fits & AIC from this single CSV
    x = df['order_pool_size'].values
    y = df['mean_latency_ms'].values
    n_obs = len(y)

    def f_const(n, a): return np.full_like(n, a, dtype=float)
    def f_linear(n, a, b): return a * n + b
    def f_nlogn(n, a, b): return a * n * np.log2(n) + b
    def f_quad(n, a, b): return a * (n ** 2) + b

    p_c, _ = curve_fit(f_const, x, y)
    p_l, _ = curve_fit(f_linear, x, y)
    p_nl, _ = curve_fit(f_nlogn, x, y)
    p_q, _ = curve_fit(f_quad, x, y)

    fits = []
    for name, p, func, k in [('Constant', p_c, f_const, 1), ('Linear', p_l, f_linear, 2), ('n_log_n', p_nl, f_nlogn, 2), ('Quadratic', p_q, f_quad, 2)]:
        res = y - func(x, *p)
        rss = float(np.sum(res ** 2))
        aic = float(n_obs * np.log(rss / n_obs) + 2 * k)
        fits.append({
            'model': name,
            'k_params': k,
            'rss': rss,
            'aic': aic,
            'popt': str(p.tolist())
        })

    fits_df = pd.DataFrame(fits)
    fits_df.to_csv("results/WP7/complexity_fits_aic_v2.csv", index=False)
    print("Saved results/WP7/complexity_fits_aic_v2.csv")

    # Compute log-log slope
    slope, intercept = np.polyfit(np.log10(x), np.log10(y), 1)
    print(f"Log-log slope: {slope:.4f}, intercept: {intercept:.4f}")

if __name__ == '__main__':
    main()
