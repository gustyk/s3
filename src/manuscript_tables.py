"""Generate manuscript-ready Tables 4–6 from certified final outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.artifacts import atomic_dataframe_csv, atomic_write_text

CONTEXTS = (
    (0.5, 1, "Low rate / low pickers"),
    (0.5, 12, "Low rate / high pickers"),
    (16.0, 1, "High rate / low pickers"),
    (16.0, 12, "High rate / high pickers"),
)


def build(root: Path, output_dir: Path) -> None:
    extended = pd.read_csv(root / "additional-metrics" / "table4_extended.csv")
    composite = pd.read_csv(root / "composite" / "table4_corrected.csv")[
        ["trigger_method", "composite_mean", "composite_sd", "rank"]
    ]
    table4 = extended.merge(composite, on="trigger_method", validate="one_to_one")
    method_order = [
        "FTWB",
        "VTWB",
        "MaxPicker",
        "MaxCart",
        "UrgentPicker",
        "UrgentCart",
        "SNH",
        "MPBH",
    ]
    table4["trigger_method"] = pd.Categorical(
        table4["trigger_method"], categories=method_order, ordered=True
    )
    table4 = table4.sort_values("trigger_method")
    atomic_dataframe_csv(table4, output_dir / "table4_final.csv")

    contrasts = pd.read_csv(root / "analysis" / "planned_adaptive_vs_static_contrasts.csv")
    atomic_dataframe_csv(contrasts, output_dir / "table5_primary_paired_contrasts.csv")

    results = pd.read_csv(
        root / "results.csv",
        usecols=[
            "incoming_rate",
            "num_pickers",
            "batching_method",
            "cart_capacity",
            "routing_policy",
            "trigger_method",
            "total_late_orders",
        ],
    )
    fixed = results.loc[
        (results["batching_method"] == "FCFS")
        & (results["cart_capacity"] == 100)
        & (results["routing_policy"] == "S-shape")
    ]
    context_rows = []
    winner_rows = []
    for rate, pickers, label in CONTEXTS:
        selected = fixed.loc[
            (fixed["incoming_rate"] == rate) & (fixed["num_pickers"] == pickers)
        ]
        summary = (
            selected.groupby("trigger_method", as_index=False)["total_late_orders"]
            .agg(["mean", "std", "count"])
            .reset_index()
        )
        summary.insert(0, "operational_context", label)
        summary.insert(1, "incoming_rate_orders_per_minute", rate)
        summary.insert(2, "num_pickers", pickers)
        context_rows.append(summary)
        best = float(summary["mean"].min())
        winners = summary.loc[np.isclose(summary["mean"], best), "trigger_method"].tolist()
        winner_rows.append(
            {
                "operational_context": label,
                "incoming_rate_orders_per_minute": rate,
                "num_pickers": pickers,
                "best_method_or_ties": "; ".join(winners),
                "mean_total_late_orders": best,
                "secondary_factors_fixed": "FCFS; cart capacity 100; S-shape",
            }
        )
    atomic_dataframe_csv(
        pd.concat(context_rows, ignore_index=True), output_dir / "table6_context_method_means.csv"
    )
    atomic_dataframe_csv(pd.DataFrame(winner_rows), output_dir / "table6_context_winners.csv")
    atomic_write_text(
        output_dir / "README.md",
        "# Final manuscript tables\n\n"
        "All tables derive from the certified 207,360-run factorial. Table 4 joins "
        "censoring-aware metrics to the corrected original-weight composite. Table 5 "
        "uses the preregistered paired CRN adaptive-versus-static contrasts and replaces "
        "the legacy one-way ANOVA evidence. Table 6 fixes FCFS, cart capacity 100, and "
        "S-shape so incoming-rate/picker contexts are not confounded by secondary-factor "
        "averaging; ties are retained explicitly.\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    build(args.root, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
