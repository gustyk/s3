"""Global epistemic sensitivity screening with paired Latin-hypercube scenarios."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import qmc, spearmanr

from src.configuration import load_config
from src.experiment import RESULT_FIELDS, Scenario, run_simulation

INPUT_RANGES = {
    "arrival_rate": (0.5, 8.0),
    "due_time_min_seconds": (1200.0, 2400.0),
    "due_time_max_seconds": (5400.0, 9000.0),
    "picking_time_per_item": (2.0, 5.0),
    "setup_time": (120.0, 300.0),
    "walking_time_multiplier": (0.75, 1.50),
}
OUTCOMES = ["service_level_percent", "throughput_per_hour", "mean_tardiness_seconds"]


def _config_hash(params: dict) -> str:
    canonical = json.dumps(params, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def generate_samples(sample_count: int, seed: int) -> list[dict[str, float]]:
    if sample_count < 8:
        raise ValueError("At least eight sensitivity samples are required")
    unit = qmc.LatinHypercube(d=len(INPUT_RANGES), seed=seed).random(sample_count)
    lower = np.array([bounds[0] for bounds in INPUT_RANGES.values()])
    upper = np.array([bounds[1] for bounds in INPUT_RANGES.values()])
    scaled = qmc.scale(unit, lower, upper)
    return [dict(zip(INPUT_RANGES, row, strict=True)) for row in scaled]


def run_sensitivity(config_path: Path, output_dir: Path, sample_count: int) -> Path:
    loaded = load_config(config_path)
    base = loaded.values
    selected = base["SELECTED_CONFIGURATION"]
    scenario = Scenario(
        selected["incoming_rate"],
        selected["trigger_method"],
        selected["num_pickers_options"],
        selected["batching_method"],
        selected["cart_capacity"],
        selected["routing_policy"],
    )
    rows = []
    for sample_id, sample in enumerate(generate_samples(sample_count, int(base["master_seed"]))):
        params = copy.deepcopy(base)
        params["input_sample_id"] = sample_id
        params["incoming_rate"][scenario.incoming_rate_key] = sample["arrival_rate"]
        params["due_time_min_seconds"] = int(sample["due_time_min_seconds"])
        params["due_time_max_seconds"] = int(sample["due_time_max_seconds"])
        params["picking_time_per_item"] = sample["picking_time_per_item"]
        params["setup_time"] = sample["setup_time"]
        params["walking_time_multiplier"] = sample["walking_time_multiplier"]
        for key in params["walking_times"]:
            params["walking_times"][key] *= sample["walking_time_multiplier"]
        row = run_simulation(params, scenario, 0, _config_hash(params))
        row["run_id"] = sample_id + 1
        rows.append(row)

    output_dir.mkdir(parents=True, exist_ok=False)
    results = output_dir / "sensitivity_results.csv"
    with results.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    digest = hashlib.sha256(results.read_bytes()).hexdigest()
    manifest = {
        "status": "success",
        "design": "Latin hypercube global screening",
        "samples": sample_count,
        "master_seed": base["master_seed"],
        "input_ranges": INPUT_RANGES,
        "results_sha256": digest,
        "source_tree_sha256": sorted({row["source_tree_sha256"] for row in rows}),
        "git_commit": sorted({row["git_commit"] for row in rows}),
        "warning": "Ranges require domain validation before confirmatory interpretation.",
    }
    (output_dir / "sensitivity_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    analyze_sensitivity(results, output_dir / "spearman_global_sensitivity.csv")
    return results


def run_oat(config_path: Path, output_dir: Path) -> Path:
    """Run low/base/high one-at-a-time directional checks around the selected case."""
    loaded = load_config(config_path)
    base = loaded.values
    selected = base["SELECTED_CONFIGURATION"]
    scenario = Scenario(
        selected["incoming_rate"],
        selected["trigger_method"],
        selected["num_pickers_options"],
        selected["batching_method"],
        selected["cart_capacity"],
        selected["routing_policy"],
    )
    rows: list[dict] = []
    design: list[tuple[str, str, float | None]] = [("baseline", "base", None)]
    for input_name, (low, high) in INPUT_RANGES.items():
        design.extend([(input_name, "low", low), (input_name, "high", high)])
    for run_id, (input_name, level, value) in enumerate(design, 1):
        params = copy.deepcopy(base)
        params["input_sample_id"] = f"{input_name}:{level}"
        if input_name != "baseline":
            assert value is not None
        numeric_value = 0.0 if value is None else value
        if input_name == "arrival_rate":
            params["incoming_rate"][scenario.incoming_rate_key] = numeric_value
        elif input_name == "walking_time_multiplier":
            params["walking_time_multiplier"] = numeric_value
            for key in params["walking_times"]:
                params["walking_times"][key] *= numeric_value
        elif input_name != "baseline":
            params[input_name] = int(numeric_value) if "seconds" in input_name else numeric_value
        row = run_simulation(params, scenario, 0, _config_hash(params))
        row.update({"run_id": run_id, "oat_input": input_name, "oat_level": level})
        rows.append(row)

    output_dir.mkdir(parents=True, exist_ok=False)
    results = output_dir / "oat_results.csv"
    fields = RESULT_FIELDS + ["oat_input", "oat_level"]
    with results.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    frame = pd.DataFrame(rows)
    baseline = frame.loc[frame["oat_input"] == "baseline", OUTCOMES].iloc[0]
    comparisons = frame.loc[frame["oat_input"] != "baseline", ["oat_input", "oat_level", *OUTCOMES]].copy()
    for outcome in OUTCOMES:
        comparisons[f"delta_{outcome}"] = comparisons[outcome] - baseline[outcome]
    comparisons.to_csv(output_dir / "oat_directional_effects.csv", index=False)
    manifest = {
        "status": "success",
        "design": "one-at-a-time low/base/high directional sanity check",
        "runs": len(rows),
        "input_ranges": INPUT_RANGES,
        "results_sha256": hashlib.sha256(results.read_bytes()).hexdigest(),
        "source_tree_sha256": sorted({row["source_tree_sha256"] for row in rows}),
        "git_commit": sorted({row["git_commit"] for row in rows}),
        "warning": "One stochastic realization; directional engineering check only.",
    }
    (output_dir / "oat_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return results


def analyze_sensitivity(results: Path, output: Path) -> None:
    frame = pd.read_csv(results)
    mapping = {
        "arrival_rate": "incoming_rate",
        "due_time_min_seconds": "sampled_due_time_min_seconds",
        "due_time_max_seconds": "sampled_due_time_max_seconds",
        "picking_time_per_item": "sampled_picking_time_per_item",
        "setup_time": "sampled_setup_time",
        "walking_time_multiplier": "sampled_walking_time_multiplier",
    }
    records = []
    for input_name, column in mapping.items():
        for outcome in OUTCOMES:
            if frame[column].nunique() < 2 or frame[outcome].nunique() < 2:
                records.append(
                    {
                        "input": input_name,
                        "outcome": outcome,
                        "status": "not_estimable",
                        "spearman_rho": None,
                        "exact_p_value": None,
                        "interpretation": "constant input or outcome",
                    }
                )
            else:
                statistic = spearmanr(frame[column], frame[outcome])
                records.append(
                    {
                        "input": input_name,
                        "outcome": outcome,
                        "status": "estimated",
                        "spearman_rho": statistic.statistic,
                        "exact_p_value": statistic.pvalue,
                        "interpretation": "global monotonic screening; not a Sobol variance decomposition",
                    }
                )
    pd.DataFrame(records).to_csv(output, index=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=32)
    parser.add_argument("--design", choices=("lhs", "oat"), default="lhs")
    args = parser.parse_args()
    if args.design == "oat":
        print(run_oat(args.config, args.output_dir))
    else:
        print(run_sensitivity(args.config, args.output_dir, args.samples))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
