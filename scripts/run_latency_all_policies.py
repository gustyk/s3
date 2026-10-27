import os
import sys
import time
import subprocess
from pathlib import Path
import psutil
import simpy
import numpy as np
import pandas as pd
import winreg

sys.path.insert(0, str(Path('.')))
from src.trigger_method import (
    _mpbh_batch,
    _snh_batch,
    calculate_urgent_orders,
)
from src.order_pool import OrderPool
from src.io_pool import IOPool
from src.configuration import load_config, DEFAULT_CONFIG
from tests.conftest import make_order

def get_cpu_model():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        return name.strip()
    except Exception:
        return "Unknown CPU"

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
        f.write(f"CPU Model: {get_cpu_model()}\n")
        f.write(f"Overall CPU Utilization: {cpu_percent}%\n")
        if cpu_freq:
            f.write(f"CPU Frequency: {cpu_freq.current:.1f} MHz (min: {cpu_freq.min}, max: {cpu_freq.max})\n")
        f.write(f"Memory Utilization: {mem.percent}% (Used: {mem.used/(1024**3):.2f} GB / Total: {mem.total/(1024**3):.2f} GB)\n")
        f.write(f"Active Process Count: {len(psutil.pids())}\n\n")
        
        # Check running python processes
        py_procs = []
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
            try:
                info = p.info
                name = info['name'] or 'unknown'
                mem_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0
                cpu_p = info['cpu_percent'] or 0.0
                status = info['status'] or 'unknown'
                processes.append((info['pid'], name, cpu_p, mem_mb, status))
                if 'python' in name.lower():
                    py_procs.append((info['pid'], name, cpu_p, mem_mb))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        f.write(f"Python processes active ({len(py_procs)}):\n")
        for pid, name, cpu_p, mem_mb in py_procs:
            f.write(f"  PID {pid}: {name} (CPU: {cpu_p}%, Mem: {mem_mb:.1f} MB)\n")
        f.write("\n")
        
        f.write(f"{'PID':>8} {'Name':<25} {'CPU %':>8} {'Memory (MB)':>12} {'Status':<12}\n")
        f.write("-" * 70 + "\n")
        processes.sort(key=lambda x: x[2], reverse=True)
        for pid, name, cpu_p, mem_mb, status in processes[:40]:
            f.write(f"{pid:>8} {name[:24]:<25} {cpu_p:>8.1f} {mem_mb:>12.1f} {status:<12}\n")
        f.write("\n")
        f.flush()
    print(f"Logged {phase_label} load: CPU={cpu_percent}%, Mem={mem.percent}%, Python procs={len(py_procs)}")

def build_kernel_callable(method, env, waiting, pool, io_pool, capacity, beta, params):
    if method == "FTWB":
        interval = float(params["trigger_parameters"]["FTWB_interval"])
        return lambda: float(env.now) >= interval
    if method == "VTWB":
        threshold = int(params["trigger_parameters"]["VTWB_threshold"])
        return lambda: len(waiting) >= threshold
    if method == "MaxPicker":
        return lambda: bool(waiting) and io_pool.get_release_slots() > 0
    if method == "MaxCart":
        return lambda: sum(int(order["Total Item"]) for order in waiting) >= capacity
    if method in {"UrgentPicker", "UrgentCart"}:
        return lambda: calculate_urgent_orders(env, pool, "S-shape", io_pool, params)
    if method == "SNH":
        return lambda: _snh_batch(env, pool, capacity, io_pool, beta, "S-shape", params)
    if method == "MPBH":
        return lambda: _mpbh_batch(env, waiting, capacity, beta, "S-shape", params)
    raise ValueError(f"Unknown method: {method}")

def main():
    Path("results/WP7").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    load_log_file = Path("logs/latency_benchmark_load.log")
    if load_log_file.exists():
        load_log_file.unlink()
        
    log_system_load(load_log_file, "PRE-BENCHMARK IDLE STATE")
    
    # Core pinning
    p = psutil.Process()
    try:
        p.cpu_affinity([0])
        print("Successfully pinned process to CPU core [0]")
    except Exception as e:
        print(f"Warning: could not set CPU affinity: {e}")
        
    commit = get_git_hash()
    config = load_config(DEFAULT_CONFIG)
    params = config.values

    env = simpy.Environment(initial_time=10000.0)
    pool_sizes = [10, 50, 100, 250, 500, 1000, 2500, 5000]
    repeats = 30
    policies = ["FTWB", "VTWB", "MaxPicker", "MaxCart", "UrgentPicker", "UrgentCart", "SNH", "MPBH"]

    print(f"Starting 8-policy pinned-core latency benchmark (n in {pool_sizes}, repeats={repeats})...")
    records = []

    for method in policies:
        print(f"\n--- Benchmarking {method} ---")
        for n in pool_sizes:
            trial_times = []
            for r in range(repeats):
                np.random.seed(1000 * r + n)
                waiting = []
                pool = OrderPool(env)
                for i in range(n):
                    created = float(np.random.uniform(0, 10000))
                    due = float(10000 + np.random.uniform(300, 7200))
                    order = make_order(f"O_{i}", created=created, due=due, total=2, item=1)
                    waiting.append(order)
                    pool.add_order(order)
                
                io_pool = IOPool(env, 12)
                kernel = build_kernel_callable(method, env, waiting, pool, io_pool, 100, 2, params)
                
                # Warm-up call
                _ = kernel()
                
                t0 = time.perf_counter()
                _ = kernel()
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
                "policy": method,
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
            if n in [1000, 5000]:
                print(f"[{method}] n={n:5d}: Median={med_t:7.4f} ms [IQR={iqr_t:7.4f} ms], Mean={mean_t:7.4f} ms")

    log_system_load(load_log_file, "POST-BENCHMARK LOAD STATE")

    df = pd.DataFrame(records)
    csv_path = "results/WP7/all_policies_latency_scaling_pinned_core.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved all policies latency scaling to {csv_path}")

if __name__ == "__main__":
    main()
