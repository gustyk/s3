"""Reproduce publication tables, models, uncertainty, and diagnostic figures."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson

from src.audit_results import audit

FACTOR_COLUMNS = [
    "trigger_method",
    "batching_method",
    "routing_policy",
    "incoming_rate",
    "cart_capacity",
    "num_pickers",
]
OUTCOMES = [
    "total_late_orders",
    "service_level_percent",
    "throughput_per_hour",
    "picker_utility_percent",
    "mean_cart_utilization_percent",
    "mean_tardiness_seconds",
]
ADAPTIVE_METHODS = ["MaxPicker", "MaxCart", "UrgentPicker", "UrgentCart", "SNH", "MPBH"]


def holm_adjust(p_values: list[float]) -> list[float]:
    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[index]))
        adjusted[index] = running
    return adjusted.tolist()


def paired_trigger_comparisons(df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    index = [
        "seed",
        "incoming_rate",
        "cart_capacity",
        "batching_method",
        "routing_policy",
        "num_pickers",
    ]
    pivot = df.pivot_table(index=index, columns="trigger_method", values=outcome, aggfunc="first")
    records = []
    for left, right in itertools.combinations(sorted(pivot.columns), 2):
        differences = (pivot[left] - pivot[right]).dropna().to_numpy()
        if not len(differences):
            continue
        mean = float(np.mean(differences))
        sem = float(st.sem(differences)) if len(differences) > 1 else 0.0
        critical = float(st.t.ppf(0.975, len(differences) - 1)) if len(differences) > 1 else 0.0
        try:
            p_value = float(st.wilcoxon(differences).pvalue) if np.any(differences) else 1.0
        except ValueError:
            p_value = 1.0
        records.append(
            {
                "outcome": outcome,
                "method_a": left,
                "method_b": right,
                "paired_n": len(differences),
                "mean_difference_a_minus_b": mean,
                "ci95_low": mean - critical * sem,
                "ci95_high": mean + critical * sem,
                "wilcoxon_p": p_value,
            }
        )
    if records:
        adjusted = holm_adjust([record["wilcoxon_p"] for record in records])
        for record, value in zip(records, adjusted, strict=True):
            record["holm_adjusted_p"] = value
    return pd.DataFrame(records)


def planned_adaptive_vs_static_contrasts(df: pd.DataFrame) -> pd.DataFrame:
    """Paired CRN contrasts against the mean of the two static benchmarks."""
    index = [
        "seed",
        "incoming_rate",
        "cart_capacity",
        "batching_method",
        "routing_policy",
        "num_pickers",
    ]
    pivot = df.pivot_table(
        index=index, columns="trigger_method", values="total_late_orders", aggfunc="first"
    )
    static = (pivot["FTWB"] + pivot["VTWB"]) / 2.0
    records = []
    for method in ADAPTIVE_METHODS:
        differences = (pivot[method] - static).dropna().to_numpy()
        mean = float(np.mean(differences))
        sem = float(st.sem(differences))
        critical = float(st.t.ppf(0.975, len(differences) - 1))
        t_result = st.ttest_1samp(differences, popmean=0.0)
        try:
            wilcoxon_p = float(st.wilcoxon(differences).pvalue) if np.any(differences) else 1.0
        except ValueError:
            wilcoxon_p = 1.0
        static_mean = float(np.mean(static))
        records.append(
            {
                "contrast": f"{method} minus mean(FTWB, VTWB)",
                "method": method,
                "paired_n": len(differences),
                "mean_difference_total_late_orders": mean,
                "ci95_low": mean - critical * sem,
                "ci95_high": mean + critical * sem,
                "paired_t_p": float(t_result.pvalue),
                "wilcoxon_p": wilcoxon_p,
                "static_benchmark_mean_tlo": static_mean,
                "method_mean_tlo": float(np.mean(pivot[method])),
                "relative_reduction_percent": -100.0 * mean / static_mean,
            }
        )
    return pd.DataFrame(records)


def pareto_front(summary: pd.DataFrame) -> pd.DataFrame:
    values = summary[["late_rate", "throughput_per_hour", "picker_utility_percent"]].to_numpy()
    dominated = np.zeros(len(summary), dtype=bool)
    for i, candidate in enumerate(values):
        for j, challenger in enumerate(values):
            if i == j:
                continue
            no_worse = challenger[0] <= candidate[0] and np.all(challenger[1:] >= candidate[1:])
            strictly_better = challenger[0] < candidate[0] or np.any(challenger[1:] > candidate[1:])
            if no_worse and strictly_better:
                dominated[i] = True
                break
    result = summary.copy()
    result["pareto_optimal"] = ~dominated
    return result


def run_pipeline(results: Path, manifest: Path, output_dir: Path) -> None:
    certified_audit = manifest.with_name("audit.json")
    if certified_audit.exists():
        audit_report = json.loads(certified_audit.read_text(encoding="utf-8"))
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        digest = hashlib.sha256()
        with results.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        actual_digest = digest.hexdigest()
        if (
            audit_report.get("status") != "pass"
            or int(audit_report.get("rows", -1)) != int(manifest_data["expected_runs"])
            or audit_report.get("sha256") != actual_digest
            or manifest_data.get("results_sha256") != actual_digest
        ):
            raise ValueError("Certified audit or results checksum is inconsistent")
    else:
        audit_report = audit(results, manifest)
    if audit_report["status"] != "pass":
        raise ValueError(f"Dataset failed audit: {audit_report['errors']}")
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(results)
    df["late_orders"] = df["late_completed_orders"] + df["late_outstanding_orders"]
    df["late_rate"] = df["late_orders"] / df["generated_orders"].replace(0, np.nan)
    if df[FACTOR_COLUMNS + OUTCOMES].isna().any().any():
        raise ValueError("Analysis columns contain missing values")

    grouped = df.groupby("trigger_method", as_index=False).agg(
        generated_orders=("generated_orders", "sum"),
        late_orders=("late_orders", "sum"),
        throughput_per_hour=("throughput_per_hour", "mean"),
        picker_utility_percent=("picker_utility_percent", "mean"),
        service_level_mean=("service_level_percent", "mean"),
        service_level_sd=("service_level_percent", "std"),
        mean_tardiness_seconds=("mean_tardiness_seconds", "mean"),
        runs=("run_uuid", "count"),
    )
    grouped["late_rate"] = grouped["late_orders"] / grouped["generated_orders"]
    pareto = pareto_front(grouped)
    pareto.to_csv(output_dir / "trigger_summary_and_pareto.csv", index=False)

    scenario_keys = [
        "incoming_rate",
        "cart_capacity",
        "batching_method",
        "routing_policy",
        "num_pickers",
    ]
    scenario = df.groupby(scenario_keys + ["trigger_method"], as_index=False).agg(
        service_level_percent=("service_level_percent", "mean"),
        throughput_per_hour=("throughput_per_hour", "mean"),
    )
    winners = scenario.sort_values(
        scenario_keys + ["service_level_percent", "throughput_per_hour"],
        ascending=[True] * len(scenario_keys) + [False, False],
    ).drop_duplicates(scenario_keys)
    winners.to_csv(output_dir / "scenario_winners.csv", index=False)

    comparisons = pd.concat(
        [paired_trigger_comparisons(df, outcome) for outcome in OUTCOMES], ignore_index=True
    )
    comparisons.to_csv(output_dir / "paired_effects_ci_holm.csv", index=False)
    planned_adaptive_vs_static_contrasts(df).to_csv(
        output_dir / "planned_adaptive_vs_static_contrasts.csv", index=False
    )

    formula = (
        "late_orders ~ C(trigger_method) * (C(batching_method) + C(routing_policy) + "
        "C(incoming_rate) + C(cart_capacity) + C(num_pickers))"
    )
    factorial_ready = len(df) >= 100 and all(df[column].nunique() >= 2 for column in FACTOR_COLUMNS)
    diagnostics: dict[str, object] = {"factorial_ready": factorial_ready, "models": {}}
    dispersion: float | None = None
    if not factorial_ready:
        (output_dir / "MODELS_NOT_FIT.txt").write_text(
            "Factorial models were intentionally not fit: this dataset lacks at least "
            "100 rows and two observed levels for every design factor. Summary outputs "
            "are diagnostic only and must not support inferential claims.\n",
            encoding="utf-8",
        )
    else:
        # Secondary factorial models operate on one row per factorial cell.  The
        # primary trigger inference above remains paired at the replication level.
        # Cell aggregation avoids constructing a multi-gigabyte 207,360-row dummy
        # matrix while retaining the complete balanced factorial structure.
        model_df = df.groupby(FACTOR_COLUMNS, as_index=False).agg(
            late_orders=("late_orders", "sum"),
            generated_orders=("generated_orders", "sum"),
            throughput_per_hour=("throughput_per_hour", "mean"),
        )
        model_df["service_proportion"] = 1.0 - (
            model_df["late_orders"] / model_df["generated_orders"]
        )
        model_df["log_generated_orders"] = np.log(model_df["generated_orders"])
        diagnostics["model_input"] = {
            "unit": "factorial-cell aggregate across 30 CRN replications",
            "rows": len(model_df),
            "primary_inference": "replication-level paired contrasts with Holm adjustment",
            "secondary_role": "factorial structure and interaction diagnostics",
        }
        if model_df["late_orders"].nunique() > 1:
            try:
                poisson = smf.glm(
                    formula,
                    data=model_df,
                    family=sm.families.Poisson(),
                    offset=model_df["log_generated_orders"],
                ).fit(cov_type="HC3")
                dispersion = float(poisson.pearson_chi2 / poisson.df_resid)
                (output_dir / "poisson_count_model.txt").write_text(
                    poisson.summary().as_text(), encoding="utf-8"
                )
                diagnostics["models"]["poisson"] = {  # type: ignore[index]
                    "status": (
                        "fit"
                        if dispersion <= 2.0
                        else "overdispersed_descriptive_only"
                    ),
                    "aic": float(poisson.aic),
                    "pearson_dispersion": dispersion,
                }
                negative_binomial = smf.negativebinomial(
                    formula,
                    data=model_df,
                    offset=model_df["log_generated_orders"],
                ).fit(disp=0)
                (output_dir / "negative_binomial_model.txt").write_text(
                    negative_binomial.summary().as_text(), encoding="utf-8"
                )
                diagnostics["models"]["negative_binomial"] = {  # type: ignore[index]
                    "status": (
                        "fit"
                        if bool(negative_binomial.mle_retvals.get("converged", False))
                        else "nonconverged_do_not_use_for_inference"
                    ),
                    "aic": float(negative_binomial.aic),
                }
            except (ValueError, np.linalg.LinAlgError) as error:
                diagnostics["models"]["count"] = {  # type: ignore[index]
                    "status": "failed",
                    "error": f"{type(error).__name__}: {error}",
                }
        else:
            diagnostics["models"]["count"] = {  # type: ignore[index]
                "status": "not_fit",
                "reason": "late_orders is constant",
            }

        service_formula = formula.replace("late_orders", "service_proportion")
        if model_df["service_proportion"].nunique() > 1:
            try:
                service_model = smf.glm(
                    service_formula,
                    data=model_df,
                    family=sm.families.Binomial(),
                    freq_weights=model_df["generated_orders"],
                ).fit(cov_type="HC3")
                (output_dir / "binomial_service_model.txt").write_text(
                    service_model.summary().as_text(), encoding="utf-8"
                )
                diagnostics["models"]["binomial_service"] = {  # type: ignore[index]
                    "status": "fit",
                    "aic": float(service_model.aic),
                }
            except (ValueError, np.linalg.LinAlgError) as error:
                diagnostics["models"]["binomial_service"] = {  # type: ignore[index]
                    "status": "failed",
                    "error": f"{type(error).__name__}: {error}",
                }

        continuous_formula = formula.replace("late_orders", "throughput_per_hour")
        ols = smf.ols(continuous_formula, data=model_df).fit(cov_type="HC3")
        (output_dir / "ols_throughput_robust.txt").write_text(
            ols.summary().as_text(), encoding="utf-8"
        )
        lm, lm_pvalue, fvalue, f_pvalue = het_breuschpagan(ols.resid, ols.model.exog)
        diagnostics["models"]["ols_throughput"] = {  # type: ignore[index]
            "status": "fit",
            "r_squared": float(ols.rsquared),
            "breusch_pagan_lm": float(lm),
            "breusch_pagan_p": float(lm_pvalue),
            "breusch_pagan_f": float(fvalue),
            "breusch_pagan_f_p": float(f_pvalue),
            "durbin_watson": float(durbin_watson(ols.resid)),
            "covariance": "HC3",
        }

    (output_dir / "model_diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2), encoding="utf-8"
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    ordered = grouped.sort_values("service_level_mean", ascending=False)
    ci = 1.96 * ordered["service_level_sd"].fillna(0) / np.sqrt(ordered["runs"])
    ax.errorbar(
        ordered["trigger_method"], ordered["service_level_mean"], yerr=ci, fmt="o", capsize=4
    )
    ax.set(ylabel="Mean service level (%) with 95% CI", xlabel="Trigger method")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(output_dir / "service_level_uncertainty.png", dpi=300)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = grouped["trigger_method"].astype("category").cat.codes
    ax.scatter(grouped["throughput_per_hour"], grouped["service_level_mean"], c=colors, s=70)
    for _, row in grouped.iterrows():
        ax.annotate(row["trigger_method"], (row["throughput_per_hour"], row["service_level_mean"]))
    ax.set(xlabel="Mean throughput (orders/hour)", ylabel="Mean service level (%)")
    fig.tight_layout()
    fig.savefig(output_dir / "pareto_service_throughput.png", dpi=300)
    plt.close(fig)

    interaction = df.groupby(["incoming_rate", "num_pickers", "trigger_method"], as_index=False)[
        "service_level_percent"
    ].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    for method, group in interaction.groupby("trigger_method"):
        profile = group.groupby("incoming_rate", as_index=False)["service_level_percent"].mean()
        ax.plot(
            profile["incoming_rate"], profile["service_level_percent"], marker="o", label=method
        )
    ax.set(xlabel="Incoming rate (orders/min)", ylabel="Mean service level (%)")
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "interaction_arrival_trigger.png", dpi=300)
    plt.close(fig)

    metadata = {
        "source_results": str(results.resolve()),
        "source_manifest": str(manifest.resolve()),
        "source_sha256": audit_report["sha256"],
        "rows": len(df),
        "count_model_formula": formula,
        "count_model_pearson_dispersion": dispersion,
        "factorial_model_unit": "factorial-cell aggregate across CRN replications",
        "factorial_models_fit": factorial_ready,
        "multiplicity": "Holm family-wise adjustment per outcome",
        "pairing": "Common-random-number seed and all non-trigger scenario factors",
    }
    (output_dir / "analysis_manifest.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run_pipeline(
        args.results, args.manifest or args.results.with_name("manifest.json"), args.output_dir
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
