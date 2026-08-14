"""Pilot precision, sensitivity-design, and scalability helpers."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd
import scipy.stats as st

from src.audit_results import audit


def repetitions_for_ci_half_width(differences: pd.Series, target_half_width: float) -> int:
    """Normal-approximation starting estimate for paired-run precision.

    The returned count must be confirmed iteratively using a new pilot if the
    estimate materially exceeds the available pilot size.
    """
    if target_half_width <= 0 or len(differences.dropna()) < 2:
        raise ValueError("A positive target and at least two paired differences are required")
    standard_deviation = float(differences.std(ddof=1))
    return max(2, math.ceil((st.norm.ppf(0.975) * standard_deviation / target_half_width) ** 2))


def pilot_report(results: Path, manifest: Path, outcome: str, baseline: str, target: float) -> dict:
    report = audit(results, manifest)
    if report["status"] != "pass":
        raise ValueError(f"Pilot failed audit: {report['errors']}")
    frame = pd.read_csv(results)
    index = [
        "seed",
        "incoming_rate",
        "cart_capacity",
        "batching_method",
        "routing_policy",
        "num_pickers",
    ]
    pivot = frame.pivot_table(
        index=index, columns="trigger_method", values=outcome, aggfunc="first"
    )
    estimates = {}
    if baseline not in pivot:
        raise ValueError(f"Baseline {baseline!r} is absent")
    for method in pivot.columns:
        if method == baseline:
            continue
        differences = (pivot[method] - pivot[baseline]).dropna()
        estimates[method] = {
            "paired_pilot_n": len(differences),
            "pilot_sd": float(differences.std(ddof=1)) if len(differences) > 1 else None,
            "estimated_repetitions": repetitions_for_ci_half_width(differences, target)
            if len(differences) > 1
            else None,
        }
    return {
        "outcome": outcome,
        "baseline": baseline,
        "target_ci_half_width": target,
        "method_estimates": estimates,
        "warning": "Freeze the maximum justified estimate before final runs; recheck precision after collection.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--outcome", default="service_level_percent")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--target-half-width", required=True, type=float)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = pilot_report(
        args.results,
        args.manifest or args.results.with_name("manifest.json"),
        args.outcome,
        args.baseline,
        args.target_half_width,
    )
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
