"""Fit and compare candidate distributions for operational simulation inputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

CANDIDATES = {
    "exponential": stats.expon,
    "gamma": stats.gamma,
    "lognormal": stats.lognorm,
    "weibull": stats.weibull_min,
    "uniform": stats.uniform,
}


def _clean(values: np.ndarray, outlier_rule: str) -> tuple[np.ndarray, int]:
    if outlier_rule == "none":
        return values, 0
    if outlier_rule != "iqr":
        raise ValueError("outlier_rule must be 'none' or 'iqr'")
    first, third = np.quantile(values, [0.25, 0.75])
    spread = third - first
    keep = (values >= first - 1.5 * spread) & (values <= third + 1.5 * spread)
    return values[keep], int((~keep).sum())


def _fit_one(name: str, values: np.ndarray, validation: np.ndarray) -> dict[str, Any]:
    distribution = CANDIDATES[name]
    parameters = distribution.fit(values, floc=0)
    log_density = distribution.logpdf(values, *parameters)
    if not np.isfinite(log_density).all():
        raise ValueError("non-finite fitted log density")
    log_likelihood = float(log_density.sum())
    parameter_count = len(parameters)
    ks = stats.kstest(values, distribution.cdf, args=parameters)
    validation_log_density = (
        distribution.logpdf(validation, *parameters) if len(validation) else np.array([])
    )
    validation_nll = (
        float(-validation_log_density.mean())
        if len(validation) and np.isfinite(validation_log_density).all()
        else None
    )
    return {
        "distribution": name,
        "parameters": [float(value) for value in parameters],
        "log_likelihood": log_likelihood,
        "aic": float(2 * parameter_count - 2 * log_likelihood),
        "bic": float(parameter_count * math.log(len(values)) - 2 * log_likelihood),
        "ks_statistic": float(ks.statistic),
        "ks_p_value": float(ks.pvalue),
        "validation_mean_negative_log_likelihood": validation_nll,
    }


def analyze_inputs(input_path: Path, *, outlier_rule: str = "none") -> dict[str, Any]:
    """Fit positive continuous distributions using calibration data only."""
    with input_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        if missing := {"parameter", "value", "split"} - columns:
            raise ValueError(f"missing columns: {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError("input data is empty")

    grouped: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"calibration": [], "validation": []}
    )
    missing_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        parameter = row["parameter"].strip()
        split = row["split"].strip()
        if not parameter:
            raise ValueError("parameter names must not be empty")
        if split not in {"calibration", "validation"}:
            raise ValueError(f"invalid split {split!r}")
        if not row["value"].strip():
            missing_counts[parameter] += 1
            continue
        try:
            value = float(row["value"])
        except ValueError as error:
            raise ValueError(f"non-numeric value for {parameter}") from error
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{parameter} values must be finite and positive")
        grouped[parameter][split].append(value)

    analyses = []
    for parameter, splits in sorted(grouped.items()):
        calibration = np.asarray(splits["calibration"], dtype=float)
        validation = np.asarray(splits["validation"], dtype=float)
        if len(calibration) < 8 or len(validation) < 3:
            raise ValueError(
                f"{parameter} requires at least 8 calibration and 3 validation observations"
            )
        cleaned, removed = _clean(calibration, outlier_rule)
        if len(cleaned) < 8:
            raise ValueError(f"{parameter} has fewer than 8 calibration values after cleaning")
        fits = []
        failures = []
        for name in CANDIDATES:
            try:
                fits.append(_fit_one(name, cleaned, validation))
            except (FloatingPointError, RuntimeError, ValueError) as error:
                failures.append({"distribution": name, "error": str(error)})
        if not fits:
            raise ValueError(f"all candidate distributions failed for {parameter}")
        fits.sort(key=lambda fit: fit["aic"])
        analyses.append(
            {
                "parameter": parameter,
                "calibration_n_raw": len(calibration),
                "calibration_n_used": len(cleaned),
                "validation_n": len(validation),
                "missing_n": missing_counts[parameter],
                "outliers_removed": removed,
                "outlier_rule": outlier_rule,
                "empirical_quantiles": {
                    str(quantile): float(np.quantile(cleaned, quantile))
                    for quantile in (0.05, 0.25, 0.5, 0.75, 0.95)
                },
                "selected_by_calibration_aic": fits[0]["distribution"],
                "candidate_fits": fits,
                "fit_failures": failures,
            }
        )
    return {
        "status": "complete",
        "input": str(input_path),
        "selection_rule": "minimum calibration AIC; report held-out mean negative log likelihood",
        "warning": "Distribution choice still requires diagnostics and domain plausibility review.",
        "parameters": analyses,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--outlier-rule", choices=("none", "iqr"), default="none")
    args = parser.parse_args()
    report = analyze_inputs(args.input, outlier_rule=args.outlier_rule)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
