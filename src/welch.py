"""Welch warm-up pilot and deterministic stabilization recommendation.

Addresses R1-Minor #4 and the reviewer-requested initialization correction.
The tool never edits the production config. It writes trace/diagnostic evidence
that must be reviewed before ``warmup_seconds`` is frozen.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd
from scipy import stats

from src.configuration import load_config
from src.experiment import Scenario, run_simulation

TRACE_METRICS = ("backlog_orders", "active_pickers")


def _smooth(values: pd.Series, window_points: int) -> pd.Series:
    return values.rolling(window_points, center=True, min_periods=max(2, window_points // 2)).mean()


def recommend_warmup(
    trace: pd.DataFrame,
    *,
    interval_seconds: float,
    smoothing_window_points: int = 11,
    tail_fraction: float = 0.20,
    relative_tolerance: float = 0.05,
    consecutive_points: int = 10,
    relative_drift_per_hour_limit: float = 0.05,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    required = {"trigger_method", "repetition", "time_seconds", *TRACE_METRICS}
    missing = required - set(trace)
    if missing:
        raise ValueError(f"Welch trace missing columns: {sorted(missing)}")
    if (
        not 0 < tail_fraction < 0.5
        or relative_tolerance <= 0
        or relative_drift_per_hour_limit <= 0
    ):
        raise ValueError("Invalid Welch tail/tolerance controls")

    averaged = trace.groupby(["trigger_method", "time_seconds"], as_index=False)[
        list(TRACE_METRICS)
    ].mean()
    diagnostics: list[dict[str, Any]] = []
    for method, method_rows in averaged.groupby("trigger_method"):
        ordered = method_rows.sort_values("time_seconds").reset_index(drop=True)
        tail_start = max(2, int(len(ordered) * (1 - tail_fraction)))
        for metric in TRACE_METRICS:
            smoothed = _smooth(ordered[metric], smoothing_window_points)
            ordered[f"{metric}_smoothed"] = smoothed
            tail = smoothed.iloc[tail_start:].dropna()
            if len(tail) < 3:
                raise ValueError("Welch trace is too short for tail diagnostics")
            tail_times = ordered.loc[tail.index, "time_seconds"]
            slope, _, _, slope_p, _ = stats.linregress(tail_times, tail)
            reference = float(tail.mean())
            tolerance = max(relative_tolerance * max(abs(reference), 1.0), float(tail.std()) * 0.25)
            deviations = (smoothed - reference).abs()
            recommendation: float | None = None
            for index in range(0, max(0, len(ordered) - consecutive_points + 1)):
                window = deviations.iloc[index : index + consecutive_points]
                if window.notna().all() and bool((window <= tolerance).all()):
                    recommendation = float(ordered.loc[index, "time_seconds"])
                    break
            tail_change = abs(float(slope)) * interval_seconds * max(1, len(tail))
            relative_drift_per_hour = (
                abs(float(slope)) * 3600 / max(abs(reference), 1.0)
            )
            # Pointwise regression p-values are anti-conservative for a highly
            # autocorrelated Welch curve. Require a materially large drift as
            # well as statistical evidence; this cleanly separates overload
            # growth from small stochastic tail trends.
            nonstationary = bool(
                slope_p < 0.05
                and tail_change > tolerance
                and relative_drift_per_hour > relative_drift_per_hour_limit
            )
            diagnostics.append(
                {
                    "trigger_method": method,
                    "metric": metric,
                    "tail_mean": reference,
                    "tail_sd": float(tail.std()),
                    "tail_slope_per_second": float(slope),
                    "tail_slope_p_value": float(slope_p),
                    "tolerance": tolerance,
                    "relative_drift_per_hour": relative_drift_per_hour,
                    "relative_drift_per_hour_limit": relative_drift_per_hour_limit,
                    "nonstationary_tail": nonstationary,
                    "recommended_warmup_seconds": "" if recommendation is None else recommendation,
                }
            )
        averaged.loc[ordered.index, [column for column in ordered if column.endswith("_smoothed")]] = ordered[
            [column for column in ordered if column.endswith("_smoothed")]
        ].values

    diagnostic_frame = pd.DataFrame(diagnostics)
    valid = diagnostic_frame[
        (~diagnostic_frame["nonstationary_tail"])
        & (diagnostic_frame["recommended_warmup_seconds"] != "")
    ]
    all_valid = len(valid) == len(diagnostic_frame)
    recommendation = (
        float(valid["recommended_warmup_seconds"].astype(float).max()) if all_valid else None
    )
    summary = {
        "status": "recommendation_available" if all_valid else "manual_review_required",
        "recommended_warmup_seconds": recommendation,
        "rule": "maximum stabilization time across trigger × {backlog, active pickers}",
        "interval_seconds": interval_seconds,
        "smoothing_window_points": smoothing_window_points,
        "tail_fraction": tail_fraction,
        "relative_tolerance": relative_tolerance,
        "consecutive_points": consecutive_points,
        "relative_drift_per_hour_limit": relative_drift_per_hour_limit,
        "warning": (
            "A nonstationary/overloaded trace invalidates steady-state warm-up; "
            "do not force a deletion point."
        ),
    }
    return diagnostic_frame, summary


def run_welch_pilot(
    config_path: Path,
    output_dir: Path,
    *,
    repetitions: int,
    pilot_duration_seconds: int,
) -> None:
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite Welch output: {output_dir}")
    loaded = load_config(config_path)
    params = copy.deepcopy(loaded.values)
    params["warmup_seconds"] = 0
    params["simulation_time"] = pilot_duration_seconds
    selected = params["SELECTED_CONFIGURATION"]
    traces: list[dict[str, Any]] = []
    for trigger_key, method in params["trigger_method"].items():
        scenario = Scenario(
            selected["incoming_rate"],
            int(trigger_key),
            selected["num_pickers_options"],
            selected["batching_method"],
            selected["cart_capacity"],
            selected["routing_policy"],
        )
        for repetition in range(repetitions):
            run_trace: list[dict[str, Any]] = []
            run_simulation(params, scenario, repetition, loaded.sha256, trace_records=run_trace)
            for row in run_trace:
                row.update({"trigger_method": method, "repetition": repetition})
            traces.extend(run_trace)
    output_dir.mkdir(parents=True)
    trace_path = output_dir / "welch_trace.csv"
    with trace_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(traces[0]))
        writer.writeheader()
        writer.writerows(traces)
    diagnostics, summary = recommend_warmup(
        pd.DataFrame(traces),
        interval_seconds=float(params["welch_observation_interval_seconds"]),
    )
    diagnostics.to_csv(output_dir / "welch_diagnostics.csv", index=False)
    summary.update(
        {
            "reviewer_ids": ["R1-Minor #4"],
            "config_sha256": loaded.sha256,
            "pilot_duration_seconds": pilot_duration_seconds,
            "repetitions": repetitions,
        }
    )
    (output_dir / "welch_recommendation.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--pilot-duration-seconds", type=int, default=28_800)
    args = parser.parse_args()
    run_welch_pilot(
        args.config,
        args.output_dir,
        repetitions=args.repetitions,
        pilot_duration_seconds=args.pilot_duration_seconds,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
