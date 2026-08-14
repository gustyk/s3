"""Run the reviewer-requested 2 x 3 trigger decomposition experiment.

Timing (FTWB or MPBH) is crossed independently with composition (FCFS, EDT,
or MPBH).  Every cell uses common random numbers within each scenario and
repetition, so the planned contrasts are paired rather than six unrelated
sample means.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.anova import anova_lm

from src.artifacts import atomic_dataframe_csv, atomic_write_text
from src.audit_results import audit
from src.configuration import LoadedConfig, load_config
from src.experiment import run_experiment

TIMING_POLICIES = ("FTWB", "MPBH")
COMPOSITION_RULES = ("FCFS", "EDT", "MPBH")
BLOCK_COLUMNS = [
    "repetition",
    "incoming_rate",
    "num_pickers",
    "cart_capacity",
    "routing_policy",
]


def _runtime_config(loaded: LoadedConfig, timing: str, composition: str) -> LoadedConfig:
    params = copy.deepcopy(loaded.values)
    # Trigger 8 is merely the dispatch host. The two overrides completely
    # determine the timing and composition treatments used by the adapter.
    params["experiment_design"]["trigger_method_keys"] = [8]
    params["experiment_design"]["batching_method_keys"] = [1]
    params["timing_policy_override"] = timing
    params["composition_rule_override"] = composition
    params["algorithm_variant"] = "base"
    canonical = json.dumps(params, sort_keys=True, separators=(",", ":")).encode()
    return LoadedConfig(loaded.path, params, hashlib.sha256(canonical).hexdigest())


def _paired_contrast(
    frame: pd.DataFrame,
    *,
    factor: str,
    level_a: str,
    level_b: str,
    within: str | None = None,
) -> dict[str, object]:
    subset = frame if within is None else frame.loc[frame[factor] == within]
    index = [*BLOCK_COLUMNS]
    if factor == "timing_policy":
        index.append("composition_rule")
        column = "timing_policy"
    else:
        index.append("timing_policy")
        column = "composition_rule"
    paired = subset.pivot_table(
        index=index,
        columns=column,
        values="total_late_orders",
        aggfunc="first",
    ).dropna(subset=[level_a, level_b])
    differences = paired[level_b] - paired[level_a]
    n = len(differences)
    mean = float(differences.mean()) if n else float("nan")
    standard_error = float(differences.sem()) if n > 1 else float("nan")
    if n > 1:
        critical = float(stats.t.ppf(0.975, n - 1))
        test = stats.ttest_1samp(differences, 0.0)
        lower, upper = mean - critical * standard_error, mean + critical * standard_error
        p_value = float(test.pvalue)
    else:
        lower = upper = p_value = float("nan")
    return {
        "contrast": f"{level_b} - {level_a}",
        "factor": column,
        "paired_blocks": n,
        "mean_difference_total_late": mean,
        "standard_error": standard_error,
        "ci95_lower": lower,
        "ci95_upper": upper,
        "paired_t_p_value": p_value,
        "interpretation": "negative values mean the first-named level has lower TLO",
    }


def _write_analysis(frame: pd.DataFrame, output_dir: Path) -> None:
    summary = (
        frame.groupby(["timing_policy", "composition_rule"], as_index=False)
        .agg(
            runs=("run_uuid", "count"),
            total_late_mean=("total_late_orders", "mean"),
            total_late_sd=("total_late_orders", "std"),
            on_time_rate_mean=("on_time_rate_percent", "mean"),
            throughput_mean=("throughput_per_hour", "mean"),
            picker_utilization_mean=("picker_utility_percent", "mean"),
            mean_late_tardiness=("mean_late_tardiness_seconds", "mean"),
        )
        .sort_values(["timing_policy", "composition_rule"])
    )
    atomic_dataframe_csv(summary, output_dir / "ablation_summary.csv")

    contrasts = [
        _paired_contrast(frame, factor="timing_policy", level_a="FTWB", level_b="MPBH"),
        _paired_contrast(frame, factor="composition_rule", level_a="FCFS", level_b="EDT"),
        _paired_contrast(frame, factor="composition_rule", level_a="FCFS", level_b="MPBH"),
        _paired_contrast(frame, factor="composition_rule", level_a="EDT", level_b="MPBH"),
    ]
    atomic_dataframe_csv(
        pd.DataFrame(contrasts), output_dir / "planned_paired_contrasts.csv"
    )

    blocking_terms = [
        f"C({column})"
        for column in (
            "incoming_rate",
            "num_pickers",
            "cart_capacity",
            "routing_policy",
            "repetition",
        )
        if frame[column].nunique() > 1
    ]
    formula = "total_late_orders ~ C(timing_policy) * C(composition_rule)"
    if blocking_terms:
        formula += " + " + " + ".join(blocking_terms)
    base_fitted = smf.ols(formula, data=frame).fit()
    if base_fitted.df_resid <= 0:
        atomic_write_text(
            output_dir / "factorial_ols_hc3.txt",
            "Model intentionally not summarized: the smoke dataset has no residual "
            "degrees of freedom. Production inference requires the declared 30 repetitions.\n",
        )
        anova = pd.DataFrame(
            [{"model_term": "not_fit", "reason": "no residual degrees of freedom"}]
        )
    else:
        fitted = base_fitted.get_robustcov_results(cov_type="HC3")
        atomic_write_text(
            output_dir / "factorial_ols_hc3.txt",
            "Exploratory decomposition model; paired contrasts are the primary inference.\n\n"
            + fitted.summary().as_text(),
        )
        anova = anova_lm(base_fitted, typ=2, robust="hc3").reset_index(
            names="model_term"
        )
    atomic_dataframe_csv(anova, output_dir / "ablation_anova_summary.csv")

    markdown = [
        "# Timing-versus-composition ablation",
        "",
        "Addresses R1-Mayor #1. Values are diagnostic until the 30-replication run is certified.",
        "",
        "| Timing | Composition | Runs | Mean TLO | Mean on-time (%) | Throughput/h |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in summary.itertuples(index=False):
        markdown.append(
            f"| {row.timing_policy} | {row.composition_rule} | {row.runs} | "
            f"{row.total_late_mean:.2f} | {row.on_time_rate_mean:.2f} | "
            f"{row.throughput_mean:.2f} |"
        )
    markdown.extend(
        [
            "",
            "Primary interpretation must use `planned_paired_contrasts.csv`; negative differences mean the first-named level has lower TLO.",
            "The HC3 factorial ANOVA is secondary because TLO is a count outcome and the design uses CRN pairing.",
        ]
    )
    atomic_write_text(output_dir / "ablation_summary_table.md", "\n".join(markdown) + "\n")


def run_ablations(config_path: Path, output_dir: Path, repetitions: int) -> Path:
    loaded = load_config(config_path)
    result_paths: list[Path] = []
    for timing in TIMING_POLICIES:
        for composition in COMPOSITION_RULES:
            config = _runtime_config(loaded, timing, composition)
            cell_dir = output_dir / f"timing={timing}" / f"composition={composition}"
            result_paths.append(run_experiment(config, cell_dir, "full", repetitions))

    audit_reports = [audit(path, path.with_name("manifest.json")) for path in result_paths]
    if any(report["status"] != "pass" for report in audit_reports):
        raise RuntimeError("One or more ablation cells failed artifact audit")
    combined = pd.concat([pd.read_csv(path) for path in result_paths], ignore_index=True)
    combined_path = output_dir / "ablation_results.csv"
    atomic_dataframe_csv(combined, combined_path)
    _write_analysis(combined, output_dir)

    manifests = [
        json.loads(path.with_name("manifest.json").read_text(encoding="utf-8"))
        for path in result_paths
    ]
    aggregate_manifest = {
        "status": "success",
        "design": "2 x 3 timing-by-composition crossed factorial with common random numbers",
        "timing_policies": list(TIMING_POLICIES),
        "composition_rules": list(COMPOSITION_RULES),
        "primary_outcome": "total_late_orders (completed late + overdue outstanding)",
        "repetitions_per_scenario_cell": repetitions,
        "runs": len(combined),
        "results_sha256": hashlib.sha256(combined_path.read_bytes()).hexdigest(),
        "source_tree_sha256": sorted(set(combined["source_tree_sha256"])),
        "cell_results_sha256": [manifest["results_sha256"] for manifest in manifests],
        "audit_statuses": [report["status"] for report in audit_reports],
        "analysis": {
            "primary": "planned paired t contrasts using scenario-repetition blocks",
            "secondary": "OLS factorial model with HC3 covariance and blocking covariates",
        },
    }
    atomic_write_text(
        output_dir / "ablation_manifest.json", json.dumps(aggregate_manifest, indent=2)
    )
    return combined_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=30)
    args = parser.parse_args()
    print(run_ablations(args.config, args.output_dir, args.repetitions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
