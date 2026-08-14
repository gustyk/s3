"""Evaluate simulation predictions against held-out operational observations."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

REQUIRED_COLUMNS = {"split", "metric", "observed", "simulated"}


def _bootstrap_interval(
    observed: np.ndarray,
    simulated: np.ndarray,
    statistic: str,
    *,
    seed: int,
    samples: int,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    values = np.empty(samples)
    for index in range(samples):
        selected = rng.integers(0, len(observed), len(observed))
        errors = simulated[selected] - observed[selected]
        values[index] = (
            np.mean(np.abs(errors))
            if statistic == "mae"
            else np.sqrt(np.mean(np.square(errors)))
        )
    lower, upper = np.quantile(values, [0.025, 0.975])
    return float(lower), float(upper)


def evaluate(
    input_path: Path,
    tolerances: dict[str, dict[str, float]],
    *,
    seed: int = 20260812,
    bootstrap_samples: int = 2000,
) -> dict[str, Any]:
    """Return deterministic error estimates and predeclared tolerance decisions."""
    if bootstrap_samples < 100:
        raise ValueError("bootstrap_samples must be at least 100")
    with input_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        if missing := REQUIRED_COLUMNS - columns:
            raise ValueError(f"missing columns: {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError("validation input is empty")
    unknown_splits = {row["split"] for row in rows} - {"calibration", "validation"}
    if unknown_splits:
        raise ValueError(f"invalid split values: {sorted(unknown_splits)}")
    if {row["split"] for row in rows} != {"calibration", "validation"}:
        raise ValueError("both calibration and validation splits are required")

    grouped: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        try:
            row_observed = float(row["observed"])
            row_simulated = float(row["simulated"])
        except ValueError as error:
            raise ValueError("observed and simulated values must be numeric") from error
        if not np.isfinite(row_observed) or not np.isfinite(row_simulated):
            raise ValueError("observed and simulated values must be finite")
        grouped[(row["split"], row["metric"])].append((row_observed, row_simulated))

    estimates: list[dict[str, Any]] = []
    violations: list[str] = []
    for group_index, ((split, metric), pairs) in enumerate(sorted(grouped.items())):
        observed_values = np.array([pair[0] for pair in pairs])
        simulated_values = np.array([pair[1] for pair in pairs])
        errors = simulated_values - observed_values
        mae = float(np.mean(np.abs(errors)))
        rmse = float(np.sqrt(np.mean(np.square(errors))))
        nonzero = observed_values != 0
        mape = (
            float(np.mean(np.abs(errors[nonzero] / observed_values[nonzero])) * 100)
            if nonzero.any()
            else None
        )
        mae_ci = _bootstrap_interval(
            observed_values,
            simulated_values,
            "mae",
            seed=seed + group_index * 2,
            samples=bootstrap_samples,
        )
        rmse_ci = _bootstrap_interval(
            observed_values,
            simulated_values,
            "rmse",
            seed=seed + group_index * 2 + 1,
            samples=bootstrap_samples,
        )
        estimate = {
            "split": split,
            "metric": metric,
            "n": len(pairs),
            "bias": float(np.mean(errors)),
            "mae": mae,
            "mae_ci95": list(mae_ci),
            "rmse": rmse,
            "rmse_ci95": list(rmse_ci),
            "mape_percent": mape,
        }
        if split == "validation":
            limits = tolerances.get(metric)
            if limits is None:
                violations.append(f"{metric}: no predeclared validation tolerance")
            else:
                measured = {"mae": mae, "rmse": rmse, "mape_percent": mape}
                for key, value in measured.items():
                    limit_key = f"max_{key}"
                    if limit_key in limits and (value is None or value > limits[limit_key]):
                        violations.append(
                            f"{metric}: {key}={value} exceeds {limits[limit_key]}"
                        )
        estimates.append(estimate)
    return {
        "status": "pass" if not violations else "fail",
        "input": str(input_path),
        "bootstrap_seed": seed,
        "bootstrap_samples": bootstrap_samples,
        "estimates": estimates,
        "violations": violations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--tolerances", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    args = parser.parse_args()
    tolerances = json.loads(args.tolerances.read_text(encoding="utf-8"))
    report = evaluate(args.input, tolerances, bootstrap_samples=args.bootstrap_samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
