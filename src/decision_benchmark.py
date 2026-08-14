"""Benchmark all eight trigger decision kernels (R2-Mayor #3).

This benchmark deliberately excludes SimPy event advancement and route
execution. It measures only the information processing needed to decide or
construct the next release for synthetic pools of controlled size.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import platform
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd
import psutil
import simpy

from src.artifacts import atomic_dataframe_csv, atomic_write_text
from src.configuration import load_config
from src.io_pool import IOPool
from src.models import Order
from src.order_pool import OrderPool
from src.trigger_method import _mpbh_batch, _snh_batch, calculate_urgent_orders

POOL_SIZES = (10, 50, 100, 500, 1000, 5000)
METHODS = (
    "FTWB",
    "VTWB",
    "MaxPicker",
    "MaxCart",
    "UrgentPicker",
    "UrgentCart",
    "SNH",
    "MPBH",
)


def _orders(n: int, seed: int) -> list[Order]:
    rng = np.random.default_rng(seed)
    rows: list[Order] = []
    for index in range(n):
        quantity = int(rng.integers(1, 11))
        item = int(rng.integers(1, 385))
        rows.append(
            {
                "Order ID": f"B{index:05d}",
                "Created Time": "00:00:00",
                "Created Time Seconds": float(index),
                "Due Time": "01:00:00",
                "Due Time Seconds": float(index + rng.integers(1800, 7201)),
                "Order List": [(item, quantity)],
                "Total Item": quantity,
            }
        )
    return rows


def _kernel(method: str, n: int, params: dict[str, Any], seed: int) -> Callable[[], Any]:
    env = simpy.Environment(initial_time=600)
    pool = OrderPool()
    for order in _orders(n, seed):
        pool.add_order(order)
    io_pool = IOPool(env, 12)
    waiting = pool.get_all_orders()
    capacity = 100
    beta = int(params["trigger_parameters"]["Urgent_threshold"])
    if method == "FTWB":
        return lambda: float(env.now) >= float(params["trigger_parameters"]["FTWB_interval"])
    if method == "VTWB":
        return lambda: len(waiting) >= int(params["trigger_parameters"]["VTWB_threshold"])
    if method == "MaxPicker":
        return lambda: bool(waiting) and io_pool.get_release_slots() > 0
    if method == "MaxCart":
        return lambda: sum(int(order["Total Item"]) for order in waiting) >= capacity
    if method in {"UrgentPicker", "UrgentCart"}:
        return lambda: calculate_urgent_orders(env, pool, "S-shape", io_pool, params)
    if method == "SNH":
        return lambda: _snh_batch(env, pool, capacity, io_pool, beta, "S-shape", params)
    if method == "MPBH":
        generic_waiting = cast(list[dict[str, Any]], waiting)
        return lambda: _mpbh_batch(env, generic_waiting, capacity, beta, "S-shape", params)
    raise ValueError(f"Unknown method: {method}")


def _time_calls(operation: Callable[[], Any], calls: int) -> tuple[float, float]:
    def empty() -> None:
        return None

    operation()  # untimed cache/warm-up call
    gc_enabled = gc.isenabled()
    gc.disable()
    try:
        start = time.perf_counter_ns()
        for _ in range(calls):
            operation()
        elapsed = time.perf_counter_ns() - start
        overhead_start = time.perf_counter_ns()
        for _ in range(calls):
            empty()
        overhead = time.perf_counter_ns() - overhead_start
    finally:
        if gc_enabled:
            gc.enable()
    raw = elapsed / calls
    return raw, max(0.0, (elapsed - overhead) / calls)


def _calibrate_calls(operation: Callable[[], Any], maximum_calls: int) -> int:
    """Choose enough calls for timer resolution without making slow kernels prohibitive."""
    pilot_calls = 3
    start = time.perf_counter_ns()
    for _ in range(pilot_calls):
        operation()
    nanoseconds_per_call = max(1.0, (time.perf_counter_ns() - start) / pilot_calls)
    calls_for_20_ms = int(20_000_000 / nanoseconds_per_call)
    return max(3, min(maximum_calls, calls_for_20_ms))


def _complexity_fits(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    candidates = {
        "O(1)": lambda n: np.ones_like(n),
        "O(n)": lambda n: n,
        "O(n log n)": lambda n: n * np.log2(np.maximum(n, 2)),
    }
    for method, values in summary.groupby("trigger_method"):
        n = values["pool_size_n"].to_numpy(dtype=float)
        y = values["adjusted_microseconds_per_call_median"].to_numpy(dtype=float)
        for label, transform in candidates.items():
            x = transform(n)
            design = np.column_stack([np.ones(len(x)), x])
            if label == "O(1)":
                design = np.ones((len(x), 1))
            coefficients, _, _, _ = np.linalg.lstsq(design, y, rcond=None)
            predicted = design @ coefficients
            residual = y - predicted
            rss = max(float(np.dot(residual, residual)), np.finfo(float).tiny)
            tss = float(np.dot(y - y.mean(), y - y.mean()))
            k = design.shape[1]
            rows.append(
                {
                    "trigger_method": method,
                    "candidate_complexity": label,
                    "r_squared": 1.0 - rss / tss if tss else 1.0,
                    "rmse_microseconds": math.sqrt(rss / len(y)),
                    "aic": len(y) * math.log(rss / len(y)) + 2 * k,
                    "intercept_microseconds": float(coefficients[0]),
                    "scale_coefficient": "" if k == 1 else float(coefficients[1]),
                }
            )
    fitted = pd.DataFrame(rows)
    fitted["best_by_aic"] = fitted["aic"].eq(
        fitted.groupby("trigger_method")["aic"].transform("min")
    )
    fitted["practically_constant"] = False
    fitted["selected_classification"] = False
    for method, values in summary.groupby("trigger_method"):
        timings = values["adjusted_microseconds_per_call_median"]
        spread = float(timings.max() - timings.min())
        practical_limit = max(0.1, 0.25 * float(timings.median()))
        practically_constant = spread <= practical_limit
        method_mask = fitted["trigger_method"] == method
        fitted.loc[method_mask, "practically_constant"] = practically_constant
        if practically_constant:
            selection = method_mask & (fitted["candidate_complexity"] == "O(1)")
        else:
            selection = method_mask & fitted["best_by_aic"]
        fitted.loc[selection, "selected_classification"] = True
    return fitted


def benchmark_decisions(
    config_path: Path,
    output_dir: Path,
    *,
    repeats: int = 30,
    target_operations: int = 100_000,
) -> Path:
    """Measure decision latency and empirical scaling; addresses R2-Mayor #3."""
    if repeats < 5 or target_operations < 100:
        raise ValueError("Use at least five repeats and 100 target operations")
    loaded = load_config(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    completed_manifest = output_dir / "manifest.json"
    completed_results = output_dir / "scalability_results.csv"
    if completed_manifest.exists() and completed_results.exists():
        prior = json.loads(completed_manifest.read_text(encoding="utf-8"))
        digest = hashlib.sha256(completed_results.read_bytes()).hexdigest()
        if (
            prior.get("status") == "success"
            and prior.get("config_sha256") == loaded.sha256
            and int(prior.get("repeats", -1)) == repeats
            and int(prior.get("target_operations", -1)) == target_operations
            and prior.get("results_sha256") == digest
        ):
            return completed_results
        raise ValueError("Existing decision benchmark is incompatible or corrupted")
    measurements: list[dict[str, Any]] = []
    for method in METHODS:
        for n in POOL_SIZES:
            for repeat in range(repeats):
                operation = _kernel(
                    method,
                    n,
                    loaded.values,
                    seed=int(loaded.values["master_seed"]) + repeat,
                )
                calls = _calibrate_calls(operation, target_operations)
                raw, adjusted = _time_calls(operation, calls)
                measurements.append(
                    {
                        "trigger_method": method,
                        "pool_size_n": n,
                        "repeat": repeat,
                        "calls": calls,
                        "raw_microseconds_per_call": raw / 1000,
                        "adjusted_microseconds_per_call": adjusted / 1000,
                    }
                )
    raw_path = output_dir / "scalability_results.csv"
    frame = pd.DataFrame(measurements)
    atomic_dataframe_csv(frame, raw_path)
    summary = (
        frame.groupby(["trigger_method", "pool_size_n"], as_index=False)
        .agg(
            repeats=("repeat", "count"),
            calls_per_repeat=("calls", "first"),
            adjusted_microseconds_per_call_mean=("adjusted_microseconds_per_call", "mean"),
            adjusted_microseconds_per_call_sd=("adjusted_microseconds_per_call", "std"),
            adjusted_microseconds_per_call_median=("adjusted_microseconds_per_call", "median"),
            adjusted_microseconds_per_call_p95=("adjusted_microseconds_per_call", lambda x: x.quantile(0.95)),
        )
    )
    atomic_dataframe_csv(summary, output_dir / "scalability_plot_data.csv")
    fits = _complexity_fits(summary)
    atomic_dataframe_csv(fits, output_dir / "complexity_fit_results.csv")

    processor = platform.processor() or "Unavailable from Python; see OS query in hardware_spec.md"
    memory = psutil.virtual_memory().total
    hardware = (
        "# Decision-kernel benchmark environment\n\n"
        f"Generated UTC: {datetime.now(UTC).isoformat()}  \n"
        f"Platform: {platform.platform()}  \n"
        f"Processor: {processor}  \n"
        f"Logical CPUs: {os.cpu_count()}  \n"
        f"Physical CPUs: {psutil.cpu_count(logical=False)}  \n"
        f"RAM: {memory / 1024**3:.2f} GiB  \n"
        f"Python: {platform.python_version()}  \n"
        f"Config SHA-256: `{loaded.sha256}`\n"
    )
    atomic_write_text(output_dir / "hardware_spec.md", hardware)
    best = fits.loc[fits["selected_classification"]].sort_values("trigger_method")
    lines = [
        "# Decision-kernel scalability fit",
        "",
        "Addresses R2-Mayor #3. AIC selects among O(1), O(n), and O(n log n) descriptive fits;",
        "a kernel is classified as practically O(1) when its cross-n spread is <= max(0.1 us, 25% of its median).",
        "The fit is empirical and does not replace the algorithmic upper-bound proof.",
        "",
        "| Method | Best fit | R² | RMSE (µs) |",
        "|---|---:|---:|---:|",
    ]
    for row in best.itertuples(index=False):
        lines.append(
            f"| {row.trigger_method} | {row.candidate_complexity} | "
            f"{row.r_squared:.4f} | {row.rmse_microseconds:.3f} |"
        )
    atomic_write_text(output_dir / "complexity_fit_summary.md", "\n".join(lines) + "\n")
    manifest = {
        "status": "success",
        "reviewer_id": "R2-Mayor #3",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "config_sha256": loaded.sha256,
        "pool_sizes": list(POOL_SIZES),
        "methods": list(METHODS),
        "repeats": repeats,
        "target_operations": target_operations,
        "timer": "time.perf_counter_ns; empty-call overhead subtracted; GC disabled within timing loop",
        "results_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
    }
    atomic_write_text(output_dir / "manifest.json", json.dumps(manifest, indent=2))
    return raw_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/parameters.yaml"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=30)
    parser.add_argument("--target-operations", type=int, default=100_000)
    args = parser.parse_args()
    print(
        benchmark_decisions(
            args.config,
            args.output_dir,
            repeats=args.repeats,
            target_operations=args.target_operations,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
