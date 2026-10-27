import os
import sys
import time
import subprocess
from pathlib import Path
import psutil
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from src.trigger_method import _mpbh_batch
from src.configuration import load_config, DEFAULT_CONFIG

class DummyEnv:
    now = 10000.0

def get_git_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        return "unknown"

def log_system_load(log_file, phase_label):
    cpu_percent = psutil.cpu_percent(interval=1.0)
    cpu_freq = psutil.cpu_freq()
    mem = psutil.virtual_memory()
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write(f"SYSTEM LOAD & PROCESS LIST: {phase_label} ({time.strftime('%Y-%m-%d %H:%M:%S')})\n")
        f.write("="*80 + "\n")
        f.write(f"Overall CPU Utilization: {cpu_percent}%\n")
        if cpu_freq:
            f.write(f"CPU Frequency: {cpu_freq.current:.1f} MHz (min: {cpu_freq.min}, max: {cpu_freq.max})\n")
        f.write(f"Memory Utilization: {mem.percent}% (Used: {mem.used/(1024**3):.2f} GB / Total: {mem.total/(1024**3):.2f} GB)\n")
        f.write(f"Active Process Count: {len(psutil.pids())}\n\n")
        
        f.write(f"{'PID':>8} {'Name':<25} {'CPU %':>8} {'Memory (MB)':>12} {'Status':<12}\n")
        f.write("-" * 70 + "\n")
        
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
            try:
                info = p.info
                mem_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0
                processes.append((info['pid'], info['name'] or 'unknown', info['cpu_percent'] or 0.0, mem_mb, info['status'] or 'unknown'))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        # Sort by CPU usage descending
        processes.sort(key=lambda x: x[2], reverse=True)
        for pid, name, cpu_p, mem_mb, status in processes[:40]: # Top 40 processes
            f.write(f"{pid:>8} {name[:24]:<25} {cpu_p:>8.1f} {mem_mb:>12.1f} {status:<12}\n")
        f.write("\n")
        f.flush()
    print(f"Logged {phase_label} load: CPU={cpu_percent}%, Mem={mem.percent}%")

def main():
    Path("results/WP7").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    load_log_file = Path("logs/latency_benchmark_load.log")
    if load_log_file.exists():
        load_log_file.unlink() # Fresh log
        
    log_system_load(load_log_file, "PRE-BENCHMARK IDLE STATE")
    
    # Pin process to CPU core 0
    p = psutil.Process()
    try:
        p.cpu_affinity([0])
        print("Successfully pinned process to CPU core [0]")
    except Exception as e:
        print(f"Warning: could not set CPU affinity: {e}")
        
    commit = get_git_hash()
    config = load_config(DEFAULT_CONFIG)
    params = config.values

    env = DummyEnv()
    pool_sizes = [10, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 20000, 40000]
    repeats = 30

    print(f"Starting idle-machine pinned-core latency benchmark (n in {pool_sizes}, repeats={repeats})...")
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

        trial_times = np.array(trial_times)
        mean_t = float(np.mean(trial_times))
        std_t = float(np.std(trial_times, ddof=1))
        med_t = float(np.median(trial_times))
        q25_t = float(np.percentile(trial_times, 25))
        q75_t = float(np.percentile(trial_times, 75))
        iqr_t = float(q75_t - q25_t)
        min_t = float(np.min(trial_times))
        max_t = float(np.max(trial_times))

        records.append({
            "order_pool_size": n,
            "mean_latency_ms": mean_t,
            "std_latency_ms": std_t,
            "median_latency_ms": med_t,
            "iqr_latency_ms": iqr_t,
            "q25_latency_ms": q25_t,
            "q75_latency_ms": q75_t,
            "min_latency_ms": min_t,
            "max_latency_ms": max_t,
            "repeats": repeats,
            "core_pinned": 0,
            "commit_hash": commit
        })
        print(f"Pool size {n:5d}: Median {med_t:7.3f} ms [IQR: {iqr_t:7.3f} ms], Mean {mean_t:7.3f} ms (max: {max_t:7.3f} ms)")

    df = pd.DataFrame(records)
    csv_path = "results/WP7/mpbh_latency_scaling_pinned_core.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved {csv_path}")

    # Compute Complexity Fits & AIC
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
            'aic': aic
        })
    df_fits = pd.DataFrame(fits).sort_values('aic')
    df_fits['delta_aic'] = df_fits['aic'] - df_fits['aic'].min()
    fits_path = "results/WP7/complexity_fits_aic.csv"
    df_fits.to_csv(fits_path, index=False)
    print(f"Saved {fits_path}")
    print("\nAIC Complexity Ranking:")
    print(df_fits.to_string(index=False))

    log_system_load(load_log_file, "POST-BENCHMARK LOAD STATE")

if __name__ == "__main__":
    main()
