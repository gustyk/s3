"""Measure simulation and route-kernel scalability on named hardware."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import os
import platform
import statistics
import threading
import time
import tracemalloc
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any

import psutil
from scipy import stats

from src.configuration import load_config
from src.experiment import RESULT_FIELDS, Scenario, run_simulation, scenarios
from src.routing import calculate_total_time


def _measure(operation: Callable[[], Any], sample_interval: float = 0.005) -> tuple[Any, dict]:
    process = psutil.Process()
    stop = threading.Event()
    peak_rss = process.memory_info().rss

    def sample_memory() -> None:
        nonlocal peak_rss
        while not stop.wait(sample_interval):
            peak_rss = max(peak_rss, process.memory_info().rss)

    sampler = threading.Thread(target=sample_memory, daemon=True)
    tracemalloc.start()
    sampler.start()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    try:
        result = operation()
    finally:
        cpu_seconds = time.process_time() - cpu_start
        wall_seconds = time.perf_counter() - wall_start
        stop.set()
        sampler.join()
        _, peak_python = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_rss = max(peak_rss, process.memory_info().rss)
    return result, {
        "wall_seconds": wall_seconds,
        "cpu_seconds": cpu_seconds,
        "cpu_utilization_percent": cpu_seconds / wall_seconds * 100,
        "peak_process_rss_bytes": peak_rss,
        "peak_python_memory_bytes": peak_python,
    }


def _summarize(measurements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in measurements:
        identity = (
            row["benchmark"],
            row.get("incoming_rate"),
            row.get("num_pickers"),
            row.get("item_lines"),
        )
        groups[identity].append(row)
    summaries = []
    metrics = (
        "wall_seconds",
        "cpu_seconds",
        "cpu_utilization_percent",
        "peak_process_rss_bytes",
        "peak_python_memory_bytes",
        "simulated_seconds_per_wall_second",
        "microseconds_per_call",
    )
    for identity, rows in sorted(groups.items(), key=lambda item: str(item[0])):
        summary: dict[str, Any] = {
            "benchmark": identity[0],
            "incoming_rate": identity[1],
            "num_pickers": identity[2],
            "item_lines": identity[3],
            "repeats": len(rows),
        }
        for metric in metrics:
            values = [float(row[metric]) for row in rows if row.get(metric) not in (None, "")]
            if not values:
                continue
            mean = statistics.mean(values)
            standard_deviation = statistics.stdev(values) if len(values) > 1 else 0.0
            critical = float(stats.t.ppf(0.975, len(values) - 1)) if len(values) > 1 else 0.0
            half_width = critical * standard_deviation / len(values) ** 0.5
            summary[f"{metric}_mean"] = mean
            summary[f"{metric}_sd"] = standard_deviation
            summary[f"{metric}_ci95_low"] = max(0.0, mean - half_width)
            summary[f"{metric}_ci95_high"] = mean + half_width
        summaries.append(summary)
    return summaries


def _estimated_row_bytes(row: dict[str, Any]) -> int:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=RESULT_FIELDS, extrasaction="ignore")
    writer.writerow(row)
    return len(buffer.getvalue().encode("utf-8"))


def _exercise_route(items: list[tuple[int, int]], params: dict, calls: int) -> None:
    for _ in range(calls):
        calculate_total_time(items, 1, params)


def benchmark(
    config_path: Path, output_dir: Path, *, repeats: int = 3, route_calls: int = 1000
) -> None:
    if repeats < 2 or route_calls < 1:
        raise ValueError("repeats must be at least 2 and route_calls must be positive")
    temporary_dir = output_dir.with_name(f"{output_dir.name}.tmp")
    if output_dir.exists() or temporary_dir.exists():
        raise FileExistsError("Refusing to overwrite benchmark output or temporary directory")
    loaded = load_config(config_path)
    base = loaded.values
    selected = base["SELECTED_CONFIGURATION"]
    measurements = []
    for incoming_key in [1, 4, 6]:
        for pickers in [1, 4, 12]:
            params = copy.deepcopy(base)
            scenario = Scenario(
                incoming_key,
                selected["trigger_method"],
                pickers,
                selected["batching_method"],
                selected["cart_capacity"],
                selected["routing_policy"],
            )
            for repeat in range(repeats):
                def run_case(
                    params: dict = params,
                    scenario: Scenario = scenario,
                    repeat: int = repeat,
                ) -> dict[str, Any]:
                    return run_simulation(params, scenario, repeat, loaded.sha256)

                result, resources = _measure(
                    run_case
                )
                measurements.append(
                    {
                        "benchmark": "simulation",
                        "repeat": repeat,
                        "incoming_rate": result["incoming_rate"],
                        "num_pickers": pickers,
                        "generated_orders": result["generated_orders"],
                        "result_row_bytes": _estimated_row_bytes(result),
                        "source_tree_sha256": result["source_tree_sha256"],
                        "git_commit": result["git_commit"],
                        **resources,
                        "simulated_seconds": params["simulation_time"],
                        "simulated_seconds_per_wall_second": (
                            params["simulation_time"] / resources["wall_seconds"]
                        ),
                    }
                )

    for item_lines in [1, 16, 64, 128, 256, 384]:
        items = [(item, 1) for item in range(1, item_lines + 1)]
        for repeat in range(repeats):
            def run_route(items: list[tuple[int, int]] = items) -> None:
                _exercise_route(items, base, route_calls)

            _, resources = _measure(run_route)
            measurements.append(
                {
                    "benchmark": "route_kernel",
                    "repeat": repeat,
                    "item_lines": item_lines,
                    "calls": route_calls,
                    **resources,
                    "microseconds_per_call": resources["wall_seconds"] / route_calls * 1_000_000,
                }
            )

    temporary_dir.mkdir(parents=True, exist_ok=False)
    fields = sorted({key for row in measurements for key in row})
    with (temporary_dir / "scalability.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(measurements)
    summaries = _summarize(measurements)
    summary_fields = sorted({key for row in summaries for key in row})
    with (temporary_dir / "scalability_summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summaries)
    simulation_rows = [row for row in measurements if row["benchmark"] == "simulation"]
    planned_final_rows = len(list(scenarios(base, "full"))) * int(base["repetitions"])
    mean_row_bytes = statistics.mean(row["result_row_bytes"] for row in simulation_rows)
    metadata = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python": platform.python_version(),
        "config": str(loaded.path),
        "config_sha256": loaded.sha256,
        "logical_cpu_count": os.cpu_count(),
        "repeats": repeats,
        "route_calls_per_repeat": route_calls,
        "memory_sampling_interval_seconds": 0.005,
        "raw_measurement_csv_bytes": (temporary_dir / "scalability.csv").stat().st_size,
        "raw_measurement_sha256": hashlib.sha256(
            (temporary_dir / "scalability.csv").read_bytes()
        ).hexdigest(),
        "summary_sha256": hashlib.sha256(
            (temporary_dir / "scalability_summary.csv").read_bytes()
        ).hexdigest(),
        "source_tree_sha256": sorted({row["source_tree_sha256"] for row in simulation_rows}),
        "git_commit": sorted({row["git_commit"] for row in simulation_rows}),
        "planned_full_experiment_rows": planned_final_rows,
        "mean_serialized_result_row_bytes": mean_row_bytes,
        "estimated_full_results_csv_bytes": int(mean_row_bytes * planned_final_rows),
        "parallel_worker_upper_candidate": max(1, (os.cpu_count() or 1) - 1),
        "caveats": [
            "RSS is sampled and may miss a peak between samples.",
            "95% intervals use a Student-t approximation and are descriptive timing uncertainty.",
            "Very short kernels can have noisy CPU-time and utilization measurements.",
            "Parallel worker count is an upper candidate, not validated deterministic parallel execution.",
        ],
    }
    (temporary_dir / "benchmark_environment.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    temporary_dir.replace(output_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--route-calls", type=int, default=1000)
    args = parser.parse_args()
    benchmark(args.config, args.output_dir, repeats=args.repeats, route_calls=args.route_calls)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
