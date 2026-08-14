"""Calibrate FTWB F and VTWB V on held-out CRN replications (R1-Mayor #2)."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.artifacts import atomic_dataframe_csv, atomic_write_text
from src.audit_results import audit
from src.configuration import LoadedConfig, load_config
from src.experiment import run_experiment

F_CANDIDATES_SECONDS = (60, 120, 180, 240, 300, 360, 480, 600, 720)
V_CANDIDATES_ORDERS = (4, 6, 8, 10, 12, 16, 20, 24)
WEIGHTS = {"tlo": 0.6, "throughput": 0.3, "utilization": 0.1}


def _cell_config(
    loaded: LoadedConfig, method: str, value: int
) -> LoadedConfig:
    params = copy.deepcopy(loaded.values)
    trigger_key = 1 if method == "FTWB" else 2
    params["experiment_design"]["trigger_method_keys"] = [trigger_key]
    params["trigger_parameters"]["FTWB_interval" if method == "FTWB" else "VTWB_threshold"] = value
    canonical = json.dumps(params, sort_keys=True, separators=(",", ":")).encode()
    return LoadedConfig(loaded.path, params, hashlib.sha256(canonical).hexdigest())


def _minmax(series: pd.Series, *, benefit: bool) -> pd.Series:
    span = float(series.max() - series.min())
    if span == 0:
        return pd.Series(0.5, index=series.index)
    scaled = (series - series.min()) / span
    return scaled if benefit else 1.0 - scaled


def _score_candidates(frame: pd.DataFrame, parameter: str) -> pd.DataFrame:
    block = [
        "incoming_rate",
        "num_pickers",
        "batching_method",
        "cart_capacity",
        "routing_policy",
        "repetition",
    ]
    scored = frame.copy()
    scored["tlo_normalized"] = scored.groupby(block)["total_late_orders"].transform(
        lambda values: _minmax(values, benefit=False)
    )
    scored["throughput_normalized"] = scored.groupby(block)["throughput_per_hour"].transform(
        lambda values: _minmax(values, benefit=True)
    )
    scored["utilization_normalized"] = scored.groupby(block)["picker_utility_percent"].transform(
        lambda values: _minmax(values, benefit=True)
    )
    scored["calibration_composite_score"] = (
        WEIGHTS["tlo"] * scored["tlo_normalized"]
        + WEIGHTS["throughput"] * scored["throughput_normalized"]
        + WEIGHTS["utilization"] * scored["utilization_normalized"]
    )
    return scored


def _summarize(scored: pd.DataFrame, parameter: str, split: str) -> pd.DataFrame:
    return (
        scored.groupby(parameter, as_index=False)
        .agg(
            runs=("run_uuid", "count"),
            mean_total_late_orders=("total_late_orders", "mean"),
            sd_total_late_orders=("total_late_orders", "std"),
            mean_composite_score=("calibration_composite_score", "mean"),
            mean_throughput_per_hour=("throughput_per_hour", "mean"),
            mean_picker_utilization_percent=("picker_utility_percent", "mean"),
        )
        .assign(split=split)
    )


def run_calibration(config_path: Path, output_dir: Path, repetitions: int) -> None:
    """Execute F/V sweeps; addresses R1-Mayor #2."""
    if repetitions < 2:
        raise ValueError("At least two repetitions are required for tuning/evaluation separation")
    loaded = load_config(config_path)
    result_paths: list[Path] = []
    for method, candidates in (
        ("FTWB", F_CANDIDATES_SECONDS),
        ("VTWB", V_CANDIDATES_ORDERS),
    ):
        for value in candidates:
            cell = _cell_config(loaded, method, value)
            result_paths.append(
                run_experiment(cell, output_dir / method / f"value={value}", "full", repetitions)
            )
    reports = [audit(path, path.with_name("manifest.json")) for path in result_paths]
    if any(report["status"] != "pass" for report in reports):
        raise RuntimeError("At least one calibration cell failed artifact audit")

    # Runtime configs are recoverable from each result path; annotate values
    # directly to avoid relying on optional result-schema fields.
    annotated: list[pd.DataFrame] = []
    for path in result_paths:
        cell = pd.read_csv(path)
        value = int(path.parent.name.split("=", 1)[1])
        cell["parameter_value"] = value
        annotated.append(cell)
    combined = pd.concat(annotated, ignore_index=True)

    split_at = max(1, repetitions // 2)
    combined["data_split"] = combined["repetition"].apply(
        lambda repetition: "tuning" if int(repetition) < split_at else "held_out_evaluation"
    )
    summaries: list[pd.DataFrame] = []
    selections: dict[str, dict[str, Any]] = {}
    for method, filename, unit in (
        ("FTWB", "ftwb_sweep_results.csv", "seconds"),
        ("VTWB", "vtwb_sweep_results.csv", "orders"),
    ):
        method_rows = combined.loc[combined["trigger_method"] == method].copy()
        scored = _score_candidates(method_rows, "parameter_value")
        atomic_dataframe_csv(scored, output_dir / filename)
        tuning = scored.loc[scored["data_split"] == "tuning"]
        evaluation = scored.loc[scored["data_split"] == "held_out_evaluation"]
        tune_summary = _summarize(tuning, "parameter_value", "tuning")
        eval_summary = _summarize(evaluation, "parameter_value", "held_out_evaluation")
        summaries.extend([tune_summary.assign(method=method), eval_summary.assign(method=method)])
        tlo_best = tune_summary.sort_values(
            ["mean_total_late_orders", "parameter_value"]
        ).iloc[0]
        composite_best = tune_summary.sort_values(
            ["mean_composite_score", "parameter_value"], ascending=[False, True]
        ).iloc[0]
        selections[method] = {
            "unit": unit,
            "minimum_TLO_value": int(tlo_best["parameter_value"]),
            "maximum_composite_value": int(composite_best["parameter_value"]),
            "paper_canonical_value": 720 if method == "FTWB" else 12,
        }
    summary = pd.concat(summaries, ignore_index=True)
    atomic_dataframe_csv(summary, output_dir / "sensitivity_curves_data.csv")

    lines = [
        "# Calibrated benchmark parameters",
        "",
        "Addresses R1-Mayor #2. Selection used the first half of CRN repetitions; the second half is held out.",
        "The manuscript-canonical F=720 s remains explicitly reported even if a sweep optimum differs.",
        "",
    ]
    for method, choice in selections.items():
        lines.append(
            f"- {method}: minimum-TLO value = {choice['minimum_TLO_value']} {choice['unit']}; "
            f"maximum-composite value = {choice['maximum_composite_value']} {choice['unit']}; "
            f"paper-canonical value = {choice['paper_canonical_value']} {choice['unit']}."
        )
    atomic_write_text(output_dir / "calibrated_params.md", "\n".join(lines) + "\n")
    manifest = {
        "status": "success",
        "reviewer_id": "R1-Mayor #2",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "config_sha256": loaded.sha256,
        "repetitions": repetitions,
        "tuning_repetitions": list(range(split_at)),
        "held_out_repetitions": list(range(split_at, repetitions)),
        "F_candidates_seconds": list(F_CANDIDATES_SECONDS),
        "V_candidates_orders": list(V_CANDIDATES_ORDERS),
        "weights": WEIGHTS,
        "selection": selections,
        "audit_statuses": [report["status"] for report in reports],
    }
    atomic_write_text(output_dir / "manifest.json", json.dumps(manifest, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=30)
    args = parser.parse_args()
    run_calibration(args.config, args.output_dir, args.repetitions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
