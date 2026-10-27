"""Matched-block composite score and reviewer-requested weight sensitivity.

Addresses R1-Mayor #6. One function supplies every table and narrative value.
Composite score is secondary to the Pareto analysis.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

REFERENCE_METHODS: Final[tuple[str, ...]] = (
    "FTWB",
    "VTWB",
    "MaxPicker",
    "MaxCart",
    "UrgentPicker",
    "UrgentCart",
    "SNH",
    "MPBH",
)
BLOCK_COLUMNS: Final[tuple[str, ...]] = (
    "incoming_rate",
    "num_pickers",
    "batching_method",
    "cart_capacity",
    "routing_policy",
    "repetition",
    "seed",
)
WEIGHT_SCHEMES: Final[dict[str, tuple[float, float, float]]] = {
    "original": (0.6, 0.3, 0.1),
    "equal": (1 / 3, 1 / 3, 1 / 3),
    "throughput_priority": (0.3, 0.6, 0.1),
    "utilisation_priority": (0.3, 0.1, 0.6),
}


def _matched_minmax(values: pd.Series, *, lower_is_better: bool) -> pd.Series:
    minimum = values.min()
    maximum = values.max()
    if np.isclose(maximum, minimum):
        return pd.Series(0.5, index=values.index, dtype=float)
    normalized = (values - minimum) / (maximum - minimum)
    return 1.0 - normalized if lower_is_better else normalized


def score_blocks(
    frame: pd.DataFrame,
    *,
    weights: tuple[float, float, float] = WEIGHT_SCHEMES["original"],
) -> pd.DataFrame:
    required = {
        *BLOCK_COLUMNS,
        "trigger_method",
        "total_late_orders",
        "throughput_per_hour",
        "picker_utility_percent",
    }
    missing = required - set(frame)
    if missing:
        raise ValueError(f"Composite input missing columns: {sorted(missing)}")
    if any(weight < 0 for weight in weights) or not np.isclose(sum(weights), 1.0):
        raise ValueError("Composite weights must be non-negative and sum to one")
    if frame.duplicated([*BLOCK_COLUMNS, "trigger_method"]).any():
        raise ValueError("Composite input has duplicate method rows within a matched block")
    expected = set(REFERENCE_METHODS)
    observed_methods = set(frame["trigger_method"].dropna().unique())
    if observed_methods != expected:
        raise ValueError(
            f"Composite input has methods {sorted(observed_methods)}, expected {sorted(expected)}"
        )
    completeness = frame.groupby(list(BLOCK_COLUMNS), dropna=False)["trigger_method"].agg(
        rows="size", methods="nunique"
    )
    incomplete = completeness[
        (completeness["rows"] != len(REFERENCE_METHODS))
        | (completeness["methods"] != len(REFERENCE_METHODS))
    ]
    if not incomplete.empty:
        raise ValueError(
            f"Composite input has {len(incomplete)} incomplete matched blocks; "
            f"first={incomplete.index[0]!r}"
        )

    scored = frame.copy()
    groups = scored.groupby(list(BLOCK_COLUMNS), group_keys=False, dropna=False)
    for source, target, lower_is_better in (
        ("total_late_orders", "tlo_normalized", True),
        ("throughput_per_hour", "throughput_normalized", False),
        ("picker_utility_percent", "utilisation_normalized", False),
    ):
        minimum = groups[source].transform("min")
        maximum = groups[source].transform("max")
        span = maximum - minimum
        normalized = (scored[source] - minimum) / span.where(~np.isclose(span, 0.0), 1.0)
        if lower_is_better:
            normalized = 1.0 - normalized
        scored[target] = normalized.where(~np.isclose(span, 0.0), 0.5)
    scored["composite_score"] = (
        weights[0] * scored["tlo_normalized"]
        + weights[1] * scored["throughput_normalized"]
        + weights[2] * scored["utilisation_normalized"]
    )
    return scored


def analyze(results: Path, output_dir: Path) -> None:
    frame = pd.read_csv(results)
    output_dir.mkdir(parents=True, exist_ok=True)
    ranking_rows = []
    original_summary: pd.DataFrame | None = None
    for scheme, weights in WEIGHT_SCHEMES.items():
        scored = score_blocks(frame, weights=weights)
        scored.to_csv(output_dir / f"matched_scores_{scheme}.csv", index=False)
        summary = scored.groupby("trigger_method", as_index=False).agg(
            composite_mean=("composite_score", "mean"),
            composite_sd=("composite_score", "std"),
            blocks=("composite_score", "size"),
        )
        summary["rank"] = summary["composite_mean"].rank(method="min", ascending=False)
        summary["weight_scheme"] = scheme
        summary["weight_tlo"] = weights[0]
        summary["weight_throughput"] = weights[1]
        summary["weight_utilisation"] = weights[2]
        if scheme == "original":
            original_summary = summary.copy()
        ranking_rows.append(summary)
    rankings = pd.concat(ranking_rows, ignore_index=True)
    rankings.to_csv(output_dir / "weight_sensitivity_rankings.csv", index=False)
    assert original_summary is not None
    original_summary.to_csv(output_dir / "table4_corrected.csv", index=False)
    root_cause = {
        "reviewer_id": "R1-Mayor #6",
        "corrected_scope": "matched scenario x repetition across fixed eight-method reference set",
        "constant_range_rule": "assign 0.5 to every tied method in that metric/block",
        "primary_multiobjective_analysis": "Pareto",
        "composite_role": "secondary descriptive robustness analysis",
        "legacy_root_cause": {
            "table_4": "normalization within scenario cells while pooling 30 repetitions",
            "narrative": "normalization after aggregating eight global method means",
        },
    }
    (output_dir / "ROOT_CAUSE.json").write_text(
        json.dumps(root_cause, indent=2), encoding="utf-8"
    )
    (output_dir / "ROOT_CAUSE.md").write_text(
        "# Root cause of the Table 4 / narrative discrepancy\n\n"
        "Addresses R1-Mayor #6. Table 4 normalized outcomes within scenario "
        "cells while pooling repetitions, whereas the narrative normalized "
        "the eight already-aggregated global method means. Min-max "
        "normalization is not invariant to this change of aggregation level, "
        "so the two pipelines produced different composite values.\n\n"
        "The corrected pipeline uses one scope everywhere: each complete "
        "scenario × repetition block containing the fixed eight-method set. "
        "A constant metric range assigns every tied method 0.5. Pareto "
        "dominance is primary and the composite is a secondary, explicitly "
        "weight-sensitive summary.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    analyze(args.results, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
