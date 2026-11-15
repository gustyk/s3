"""Generate the revised manuscript figures from verified final-result assets."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch, Rectangle

ASSET_DIR = Path("docs/revised-paper-assets")
STATUS_PARTITION_PATH = Path("results/WP3/table4d_status_partition_exact.csv")
FULL_FACTORIAL_RESULTS_PATH = Path("outputs/final-q1-v1/full-factorial/results.csv")
WP4_SIMPLE_EFFECTS_PATH = Path("results/WP4/simple_effects_v2.csv")
WP4_INTERACTIONS_PATH = Path("results/WP4/interactions_v2.csv")
WP5_GLOBAL_TUNING_PATH = Path("results/WP5/tuning_surface_global.csv")
WP5_SELECTED_PARAMETERS_PATH = Path("results/WP5/selected_parameters.csv")
WP5_TUNING_SAMPLE_PATH = Path("results/WP5/class_tuning_sample_144cells.csv")
WP5_HELD_OUT_PATH = Path("results/WP5/held_out_evaluation_raw.csv.gz")
WP7_LATENCY_PATH = Path("results/WP7/all_policies_latency_scaling_pinned_core.csv")
SUPPLEMENT_DIR = Path("supplement")
POLICIES = ["FTWB", "VTWB", "MaxCart", "MaxPicker", "UrgentCart", "UrgentPicker", "SNH", "MPBH"]
COLORS = dict(zip(POLICIES, plt.get_cmap("tab10").colors[: len(POLICIES)], strict=True))
RAW_COLUMNS = ["incoming_rate", "cart_capacity", "trigger_method", "num_pickers", "generated_orders", "total_late_orders", "on_time_rate_percent", "throughput_per_hour", "picker_utility_percent", "mean_cart_utilization_percent", "trip_count"]


def save(fig: plt.Figure, output_dir: Path, number: int, name: str) -> None:
    fig.savefig(output_dir / f"Figure_{number:02d}_{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def boxplot(ax: plt.Axes, data: pd.DataFrame, column: str, label: str) -> None:
    values = [data.loc[data.trigger_method == policy, column].dropna() for policy in POLICIES]
    boxes = ax.boxplot(values, tick_labels=POLICIES, patch_artist=True, showfliers=False)
    for patch, policy in zip(boxes["boxes"], POLICIES, strict=True):
        patch.set_facecolor(COLORS[policy])
        patch.set_alpha(0.75)
    ax.set_ylabel(label)
    ax.tick_params(axis="x", rotation=35)
    ax.grid(axis="y", alpha=0.25)


def profile(ax: plt.Axes, data: pd.DataFrame, factor: str, metric: str, ylabel: str, ci: bool = False) -> None:
    aggregate = data.groupby(["trigger_method", factor], as_index=False)[metric].agg(["mean", "std", "count"])
    aggregate.columns = ["trigger_method", factor, "mean", "std", "count"]
    for policy in POLICIES:
        series = aggregate.loc[aggregate.trigger_method == policy].sort_values(factor)
        errors = 1.96 * series["std"] / np.sqrt(series["count"]) if ci else None
        ax.errorbar(series[factor], series["mean"], yerr=errors, marker="o", markersize=3, linewidth=1.4, capsize=2, color=COLORS[policy], label=policy)
    labels = {"incoming_rate": "Arrival rate (orders/min)", "num_pickers": "Pickers", "cart_capacity": "Cart capacity"}
    ax.set(xlabel=labels[factor], ylabel=ylabel)
    ax.grid(alpha=0.25)


def figure_1(output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    for aisle in range(12):
        x_pos = aisle * 1.55
        ax.add_patch(Rectangle((x_pos, 0), 1, 16, facecolor="#eef2f4", edgecolor="#4b5d67"))
        for position in range(16):
            sku = aisle * 32 + position * 2 + 1
            color = "#f3c34c" if sku <= 77 else "#80b9a2" if sku <= 192 else "#a9bdd2"
            ax.add_patch(Rectangle((x_pos + 0.08, position + 0.1), 0.84, 0.8, facecolor=color, edgecolor="white", linewidth=0.3))
    for y_pos, label in [(-1.1, "Front cross aisle"), (16.35, "Rear cross aisle")]:
        ax.add_patch(Rectangle((-0.55, y_pos), 18, 0.75, facecolor="#d7dde2", edgecolor="#4b5d67"))
        ax.text(8.5, y_pos + 0.37, label, ha="center", va="center")
    ax.scatter(-0.15, -0.72, marker="s", s=80, color="#b5453d", zorder=3)
    ax.annotate("I/O", (-0.15, -0.72), xytext=(0.35, -2.2), arrowprops={"arrowstyle": "-", "color": "#b5453d"})
    ax.set(xlim=(-1, 18), ylim=(-2.6, 18), aspect="equal", xlabel="12 parallel aisles", ylabel="16 shelf positions")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.legend(handles=[Patch(facecolor=color, label=label) for color, label in [("#f3c34c", "A: SKU 1-77"), ("#80b9a2", "B: SKU 78-192"), ("#a9bdd2", "C: SKU 193-384")]], loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, output_dir, 1, "warehouse_layout")


def figures_2_to_4(data: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5)); boxplot(ax, data, "total_late_orders", "Censoring-aware total late orders"); save(fig, output_dir, 2, "total_late_orders_distribution")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    boxplot(axes[0], data, "throughput_per_hour", "Throughput (orders/hour)"); boxplot(axes[1], data, "on_time_rate_percent", "Non-late-at-horizon rate (%)")
    fig.tight_layout(); save(fig, output_dir, 3, "throughput_and_service_distribution")
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    for ax, column, label in zip(axes, ["picker_utility_percent", "mean_cart_utilization_percent", "trip_count"], ["Picker utilisation (%)", "Cart utilisation (%)", "Completed trip count"], strict=True): boxplot(ax, data, column, label)
    fig.tight_layout(); save(fig, output_dir, 4, "service_efficiency_distribution")


def figure_5(output_dir: Path) -> None:
    partition = pd.read_csv(STATUS_PARTITION_PATH)
    required_partition_columns = {
        "trigger_method",
        "weighting",
        "share_comp_ontime",
        "share_out_notdue",
        "sum_check",
    }
    missing_columns = required_partition_columns.difference(partition.columns)
    if missing_columns:
        raise ValueError(f"{STATUS_PARTITION_PATH} is missing columns: {sorted(missing_columns)}")
    order_weighted = partition.loc[partition["weighting"] == "order_weighted"].copy()
    if order_weighted["trigger_method"].duplicated().any():
        raise ValueError("The order-weighted status partition has duplicate policies.")
    if set(order_weighted["trigger_method"]) != set(POLICIES):
        raise ValueError("The order-weighted status partition must contain exactly the eight policies.")
    if not np.allclose(order_weighted["sum_check"], 1.0, atol=1e-10):
        raise ValueError("The order-weighted status partition does not sum to one.")
    order_weighted["service_percent"] = 100 * (
        order_weighted["share_comp_ontime"] + order_weighted["share_out_notdue"]
    )

    results = pd.read_csv(
        FULL_FACTORIAL_RESULTS_PATH,
        usecols=["status", "trigger_method", "throughput_per_hour", "picker_utility_percent"],
    )
    successful = results.loc[results["status"] == "success"]
    aggregate = successful.groupby("trigger_method", as_index=False).agg(
        mean_throughput=("throughput_per_hour", "mean"),
        picker_utility_percent=("picker_utility_percent", "mean"),
    )
    if set(aggregate["trigger_method"]) != set(POLICIES):
        raise ValueError(f"{FULL_FACTORIAL_RESULTS_PATH} must contain successful runs for all eight policies.")

    points = order_weighted.merge(aggregate, on="trigger_method", validate="one_to_one")
    if len(points) != len(POLICIES):
        raise ValueError("Figure 05 requires exactly one point for each policy.")

    # Match the project's global Pareto definition: maximize service, throughput, and picker utilization.
    metrics = points[["service_percent", "mean_throughput", "picker_utility_percent"]].to_numpy()
    dominated = np.zeros(len(points), dtype=bool)
    for i, candidate in enumerate(metrics):
        for j, challenger in enumerate(metrics):
            if i != j and np.all(challenger >= candidate) and np.any(challenger > candidate):
                dominated[i] = True
                break
    frontier = points.loc[~dominated].sort_values("mean_throughput")

    max_cart = points.set_index("trigger_method").loc[["MaxCart", "UrgentCart"]]
    if not np.allclose(
        max_cart[["service_percent", "mean_throughput"]].iloc[0],
        max_cart[["service_percent", "mean_throughput"]].iloc[1],
        rtol=0,
        atol=1e-10,
    ):
        raise ValueError("MaxCart and UrgentCart must share coordinates to use a combined label.")

    fig, ax = plt.subplots(figsize=(10, 6))
    label_offsets = {
        "FTWB": (6, 8),
        "MPBH": (7, 8),
        "MaxCart": (-82, -18),
        "MaxPicker": (8, 10),
        "SNH": (7, 8),
        "UrgentPicker": (-75, -16),
        "VTWB": (-4, 12),
    }
    for _, row in points.iterrows():
        policy = row["trigger_method"]
        if policy == "UrgentCart":
            continue
        label = "MaxCart / UrgentCart" if policy == "MaxCart" else policy
        ax.scatter(
            row["mean_throughput"],
            row["service_percent"],
            color=COLORS[policy],
            s=70,
            zorder=3,
        )
        ax.annotate(
            label,
            (row["mean_throughput"], row["service_percent"]),
            xytext=label_offsets[policy],
            textcoords="offset points",
        )
    ax.plot(
        frontier["mean_throughput"],
        frontier["service_percent"],
        color="#20252b",
        linestyle="--",
        marker="o",
        linewidth=1.6,
        markersize=5,
        label="Global Pareto frontier",
        zorder=2,
    )
    ax.set(
        xlabel="Mean throughput (orders/h)",
        ylabel="Order-weighted non-late-at-horizon rate (%)",
    )
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout(); save(fig, output_dir, 5, "service_throughput_pareto")


def figures_6_to_14(data: pd.DataFrame, output_dir: Path) -> None:
    definitions = [(6, "incoming_rate", "Mean total late orders", True, "tlo_by_arrival_rate"), (7, "num_pickers", "Mean total late orders", True, "tlo_by_pickers"), (8, "cart_capacity", "Mean total late orders", False, "tlo_by_cart_capacity")]
    for number, factor, ylabel, ci, name in definitions:
        fig, ax = plt.subplots(figsize=(10, 5.5)); profile(ax, data, factor, "total_late_orders", ylabel, ci); ax.legend(ncol=4, fontsize=8, frameon=False); fig.tight_layout(); save(fig, output_dir, number, name)
    for number, factor, kind, ylabel, name in [(10, "incoming_rate", "std", "SD of total late orders", "tlo_sd_by_arrival_rate"), (11, "incoming_rate", "cv", "CV of total late orders (%)", "tlo_cv_by_arrival_rate"), (12, "num_pickers", "std", "SD of total late orders", "tlo_sd_by_pickers"), (13, "num_pickers", "cv", "CV of total late orders (%)", "tlo_cv_by_pickers")]:
        grouped = data.groupby(["trigger_method", factor], as_index=False).total_late_orders.agg(["mean", "std"]).reset_index()
        grouped["metric"] = grouped["std"] if kind == "std" else 100 * grouped["std"] / grouped["mean"].replace(0, np.nan)
        fig, ax = plt.subplots(figsize=(10, 5.5))
        for policy in POLICIES:
            series = grouped.loc[grouped.trigger_method == policy].sort_values(factor); ax.plot(series[factor], series.metric, marker="o", markersize=3, linewidth=1.4, color=COLORS[policy], label=policy)
        ax.set(xlabel="Arrival rate (orders/min)" if factor == "incoming_rate" else "Pickers", ylabel=ylabel); ax.grid(alpha=0.25); ax.legend(ncol=4, fontsize=8, frameon=False); fig.tight_layout(); save(fig, output_dir, number, name)
    rates = sorted(data.incoming_rate.unique()); fig, axes = plt.subplots(2, 3, figsize=(15, 9), sharex=True, sharey=True)
    for ax, rate in zip(axes.flat, rates, strict=True): profile(ax, data.loc[data.incoming_rate == rate], "num_pickers", "total_late_orders", "Mean total late orders"); ax.set_title(f"Arrival rate = {rate:g} orders/min")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    for ax in axes.flat:
        legend = ax.get_legend()
        if legend is not None: legend.remove()
    fig.legend(handles, labels, ncol=4, fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.01))
    fig.tight_layout(rect=(0, 0, 1, 0.93)); save(fig, output_dir, 14, "policy_picker_interaction")


def figure_10_wp4_panel_b(output_dir: Path) -> None:
    effects = pd.read_csv(WP4_SIMPLE_EFFECTS_PATH)
    interactions = pd.read_csv(WP4_INTERACTIONS_PATH)
    estimate_columns = {"estimate", "ci95_low", "ci95_high"}
    if not estimate_columns.issubset(effects.columns) or "contrast" not in effects.columns:
        raise ValueError(f"{WP4_SIMPLE_EFFECTS_PATH} is missing required effect columns.")
    if not estimate_columns.issubset(interactions.columns) or "interaction" not in interactions.columns:
        raise ValueError(f"{WP4_INTERACTIONS_PATH} is missing required interaction columns.")
    if len(effects) != 9 or len(interactions) != 2:
        raise ValueError("Figure 10 WP4 Panel B requires exactly 9 conditional effects and 2 interactions.")

    interaction_labels = {
        "inter_MPBH_FCFS": "Interaction: (MPBH - FCFS), IMM vs FTWB",
        "inter_EDT_FCFS": "Interaction: (EDT - FCFS), IMM vs FTWB",
    }
    if set(interactions["interaction"]) != set(interaction_labels):
        raise ValueError(f"{WP4_INTERACTIONS_PATH} contains unexpected interaction names.")

    effects = effects.assign(label=effects["contrast"], kind="Conditional effect")
    interactions = interactions.assign(
        label=interactions["interaction"].map(interaction_labels),
        kind="Interaction",
    )
    estimates = pd.concat([effects, interactions], ignore_index=True)
    values = estimates[["estimate", "ci95_low", "ci95_high"]].to_numpy(dtype=float)
    if not np.isfinite(values).all() or np.any(values[:, 1] > values[:, 0]) or np.any(values[:, 0] > values[:, 2]):
        raise ValueError("Figure 10 WP4 Panel B has invalid estimates or confidence intervals.")

    positions = np.arange(len(estimates))[::-1]
    fig, ax = plt.subplots(figsize=(12.5, 7.2))
    colors = {"Conditional effect": "#245b7a", "Interaction": "#c56624"}
    markers = {"Conditional effect": "o", "Interaction": "D"}
    for kind in ("Conditional effect", "Interaction"):
        mask = estimates["kind"].to_numpy() == kind
        selected = estimates.loc[mask]
        selected_positions = positions[mask]
        ax.errorbar(
            selected["estimate"],
            selected_positions,
            xerr=[
                selected["estimate"] - selected["ci95_low"],
                selected["ci95_high"] - selected["estimate"],
            ],
            fmt=markers[kind],
            color=colors[kind],
            ecolor=colors[kind],
            markersize=5,
            capsize=3,
            linewidth=1.2,
            label=kind,
            zorder=3,
        )
    for position, row in zip(positions, estimates.itertuples(), strict=True):
        ax.annotate(
            f"{row.estimate:.2f} [{row.ci95_low:.2f}, {row.ci95_high:.2f}]",
            (8, position),
            xytext=(4, 0),
            textcoords="offset points",
            va="center",
            fontsize=7.5,
        )

    ax.axvline(0, color="#4b5563", linewidth=1, linestyle="--", zorder=1)
    ax.axhline(1.5, color="#aeb7bf", linewidth=0.8, zorder=1)
    ax.set(
        xlabel="Difference in total late orders (95% CI)",
        xlim=(-205, 65),
        yticks=positions,
        yticklabels=estimates["label"],
    )
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="x", alpha=0.25)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="upper center", bbox_to_anchor=(0.75, 0.98), ncol=2)
    fig.subplots_adjust(left=0.39, right=0.99, top=0.86, bottom=0.12)
    save(fig, output_dir, 10, "wp4_panel_b_conditional_effects")


def figure_11_wp5_calibration(output_dir: Path) -> None:
    global_tuning = pd.read_csv(WP5_GLOBAL_TUNING_PATH)
    tuning = {
        method: global_tuning.loc[global_tuning["method"] == method]
        .rename(columns={"mean_throughput": "mean_tp", "mean_utilization": "mean_ut"})
        .copy()
        for method in ("FTWB", "VTWB")
    }
    grids = {"FTWB": (18, 5, 1200), "VTWB": (16, 1, 32)}
    for method, (expected_count, minimum, maximum) in grids.items():
        series = tuning[method]
        required = {"parameter_value", "mean_tlo", "mean_tp", "mean_ut"}
        missing = required.difference(series.columns)
        if missing:
            raise ValueError(f"{method} tuning data is missing columns: {sorted(missing)}")
        if (
            len(series) != expected_count
            or series["parameter_value"].duplicated().any()
            or series["parameter_value"].min() != minimum
            or series["parameter_value"].max() != maximum
        ):
            raise ValueError(f"{method} tuning data does not cover the expected expanded grid.")

    selected = pd.read_csv(WP5_SELECTED_PARAMETERS_PATH)
    selected_values = {
        "FTWB": [
            int(
                selected.loc[
                    (selected["benchmark"] == "FTWB")
                    & (selected["criterion"] == "S1 (Minimum TLO)"),
                    "selected_value",
                ].item()
            )
        ],
        "VTWB": [
            int(
                selected.loc[
                    (selected["benchmark"] == "VTWB")
                    & (selected["criterion"] == criterion),
                    "selected_value",
                ].item()
            )
            for criterion in ("S1 (Minimum TLO)", "S2 (Maximum Composite Score)")
        ],
    }
    canonical_values = {
        method: int(selected.loc[selected["benchmark"] == method, "canonical_value"].iloc[0])
        for method in ("FTWB", "VTWB")
    }
    for method, values in selected_values.items():
        if not set(values + [canonical_values[method]]).issubset(
            set(tuning[method]["parameter_value"])
        ):
            raise ValueError(f"{method} selected or canonical values are absent from its tuning grid.")

    scenario_columns = [
        "incoming_rate",
        "num_pickers",
        "cart_capacity",
        "routing_policy",
        "batching_method",
    ]
    scenarios = pd.read_csv(WP5_TUNING_SAMPLE_PATH)[scenario_columns].drop_duplicates()
    if len(scenarios) != 144:
        raise ValueError(f"{WP5_TUNING_SAMPLE_PATH} must contain exactly 144 unique cells.")

    raw_metrics = {
        "mean_tlo": "total_late_orders",
        "mean_throughput": "throughput_per_hour",
        "mean_utilization": "picker_utility_percent",
    }

    def summarize_held_out(frame: pd.DataFrame, label: str) -> pd.Series:
        if len(frame) != 144 * 15:
            raise ValueError(f"{label} must contain 15 held-out replications for all 144 cells.")
        return frame[list(raw_metrics.values())].mean().rename(
            {source: target for target, source in raw_metrics.items()}
        )

    held_out_raw = pd.read_csv(WP5_HELD_OUT_PATH)
    held_out_curves: dict[str, list[tuple[int, pd.Series]]] = {"FTWB": [], "VTWB": []}
    for method, values in selected_values.items():
        for value in values:
            variant = f"{method}_tuned_F{value}" if method == "FTWB" else f"{method}_tuned_V{value}"
            rows = held_out_raw.loc[held_out_raw["experiment_type"] == variant].merge(
                scenarios, on=scenario_columns, validate="many_to_one"
            )
            held_out_curves[method].append((value, summarize_held_out(rows, variant)))

    full_columns = [
        *scenario_columns,
        "repetition",
        "trigger_method",
        "status",
        "sampled_ftwb_interval_seconds",
        "sampled_vtwb_threshold_orders",
        *raw_metrics.values(),
    ]
    full = pd.read_csv(FULL_FACTORIAL_RESULTS_PATH, usecols=full_columns)
    held_out_full = full.loc[
        (full["status"] == "success") & (full["repetition"] >= 15)
    ].merge(scenarios, on=scenario_columns, validate="many_to_one")

    def canonical_summary(method: str, column: str, value: int) -> pd.Series:
        rows = held_out_full.loc[
            (held_out_full["trigger_method"] == method) & (held_out_full[column] == value)
        ]
        return summarize_held_out(rows, f"{method} canonical value {value}")

    for method, parameter_column in (
        ("FTWB", "sampled_ftwb_interval_seconds"),
        ("VTWB", "sampled_vtwb_threshold_orders"),
    ):
        held_out_curves[method].append(
            (
                canonical_values[method],
                canonical_summary(method, parameter_column, canonical_values[method]),
            )
        )
    maxpicker_held_out = summarize_held_out(
        held_out_full.loc[held_out_full["trigger_method"] == "MaxPicker"],
        "MaxPicker held-out reference",
    )

    maxpicker_tuning_rows = global_tuning.loc[
        global_tuning["method"] == "MaxPicker (F->0 ref)"
    ]
    if len(maxpicker_tuning_rows) != 1:
        raise ValueError(f"{WP5_GLOBAL_TUNING_PATH} must contain one MaxPicker reference row.")
    maxpicker_tuning = maxpicker_tuning_rows.iloc[0]

    metrics = [
        ("mean_tlo", "mean_tlo", "Mean total late orders"),
        ("mean_throughput", "mean_tp", "Mean throughput (orders/hour)"),
        ("mean_utilization", "mean_ut", "Mean picker utilisation (%)"),
    ]
    parameter_axes = {
        "FTWB": {
            "xlabel": "FTWB interval F (seconds)",
            "scale": "log",
            "ticks": [5, 10, 20, 60, 120, 240, 600, 1200],
        },
        "VTWB": {
            "xlabel": "VTWB order threshold V (orders)",
            "scale": "linear",
            "ticks": [1, 4, 6, 8, 12, 16, 24, 32],
        },
    }
    fig, axes = plt.subplots(3, 2, figsize=(14, 10), sharey="row")
    tuning_color = "#245b7a"
    held_out_color = "#c56624"
    reference_color = "#68727c"
    for column, method in enumerate(("FTWB", "VTWB")):
        series = tuning[method].sort_values("parameter_value")
        axes[0, column].set_title(method)
        for row, (metric, tuning_metric, ylabel) in enumerate(metrics):
            ax = axes[row, column]
            ax.plot(
                series["parameter_value"],
                series[tuning_metric],
                color=tuning_color,
                marker="o",
                markersize=3,
                linewidth=1.4,
                label="Tuning (15 reps)",
            )
            held_out = sorted(held_out_curves[method], key=lambda item: item[0])
            ax.plot(
                [value for value, _ in held_out],
                [summary[metric] for _, summary in held_out],
                color=held_out_color,
                marker="s",
                markersize=4,
                linestyle="--",
                linewidth=1.2,
                label="Held-out (selected/canonical)",
            )
            selected_rows = series.loc[series["parameter_value"].isin(selected_values[method])]
            ax.scatter(
                selected_rows["parameter_value"],
                selected_rows[tuning_metric],
                marker="*",
                s=105,
                color="#e5a72e",
                edgecolor="#333333",
                linewidth=0.6,
                zorder=4,
                label="Selected tuning value",
            )
            ax.axhline(
                maxpicker_tuning[metric],
                color=reference_color,
                linestyle=":",
                linewidth=1.2,
                label="MaxPicker reference (tuning)",
            )
            ax.axhline(
                maxpicker_held_out[metric],
                color=reference_color,
                linestyle="-.",
                linewidth=1.2,
                label="MaxPicker reference (held-out)",
            )
            ax.set_xscale(parameter_axes[method]["scale"])
            ticks = parameter_axes[method]["ticks"]
            ax.set_xticks(ticks, labels=[str(value) for value in ticks])
            ax.set_xlabel(parameter_axes[method]["xlabel"] if row == 2 else "")
            if column == 0:
                ax.set_ylabel(ylabel)
            ax.grid(alpha=0.25)
            if row == 0 and column == 0:
                ax.set_xlim(5, 1200)
            if row == 0 and column == 1:
                ax.set_xlim(1, 32)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="upper center", ncol=3)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.90, bottom=0.09, hspace=0.25, wspace=0.14)
    save(fig, output_dir, 11, "wp5_benchmark_calibration_sensitivity")


def figure_s5_latency(output_dir: Path) -> None:
    data = pd.read_csv(WP7_LATENCY_PATH)
    required = {
        "policy",
        "order_pool_size",
        "median_latency_ms",
        "q25_latency_ms",
        "q75_latency_ms",
        "repeats",
        "core_pinned",
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{WP7_LATENCY_PATH} is missing columns: {sorted(missing)}")

    pool_sizes = [10, 50, 100, 250, 500, 1000, 2500, 5000]
    if set(data["policy"]) != set(POLICIES) or sorted(data["order_pool_size"].unique()) != pool_sizes:
        raise ValueError(f"{WP7_LATENCY_PATH} must contain all eight policies at the expected pool sizes.")
    if data.duplicated(["policy", "order_pool_size"]).any():
        raise ValueError(f"{WP7_LATENCY_PATH} contains duplicate policy/pool-size rows.")
    if data["core_pinned"].nunique() != 1 or data["core_pinned"].iloc[0] != 0:
        raise ValueError(f"{WP7_LATENCY_PATH} must contain measurements pinned to CPU core 0.")
    latency_values = data[["median_latency_ms", "q25_latency_ms", "q75_latency_ms"]].to_numpy(
        dtype=float
    )
    if (
        not np.isfinite(latency_values).all()
        or np.any(latency_values <= 0)
        or np.any(latency_values[:, 1] > latency_values[:, 0])
        or np.any(latency_values[:, 0] > latency_values[:, 2])
    ):
        raise ValueError(f"{WP7_LATENCY_PATH} contains invalid latency summaries.")

    fig, ax = plt.subplots(figsize=(11, 6.5))
    for policy in POLICIES:
        series = data.loc[data["policy"] == policy].sort_values("order_pool_size")
        ax.errorbar(
            series["order_pool_size"],
            series["median_latency_ms"],
            yerr=[
                series["median_latency_ms"] - series["q25_latency_ms"],
                series["q75_latency_ms"] - series["median_latency_ms"],
            ],
            fmt="o-",
            markersize=3.5,
            linewidth=1.4,
            capsize=2,
            color=COLORS[policy],
            label=policy,
        )

    ax.set(
        xlabel="Order-pool size (orders)",
        ylabel="Median decision-kernel latency (ms; IQR bars)",
        xticks=pool_sizes,
        xticklabels=[f"{size:,}" for size in pool_sizes],
        xlim=(pool_sizes[0] * 0.8, pool_sizes[-1] * 1.25),
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.grid(which="major", alpha=0.25)
    ax.grid(which="minor", axis="y", alpha=0.12)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.02), ncol=4, fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / "Figure_S5_latency_scaling_pinned_core.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def figures_15_to_18(output_dir: Path) -> None:
    crossed = pd.read_csv(ASSET_DIR / "Figure_15_source_crossed_timing_composition.csv"); fig, ax = plt.subplots(figsize=(10, 4.5)); positions = np.arange(len(crossed))
    ax.errorbar(crossed.mean_difference_total_late, positions, xerr=1.96 * crossed.standard_error, fmt="o", color="#245b7a", capsize=4); ax.axvline(0, color="#4b5563", linewidth=1); ax.set(yticks=positions, yticklabels=crossed.contrast, xlabel="Paired mean difference in total late orders", ylabel="Contrast"); ax.grid(axis="x", alpha=0.25); fig.tight_layout(); save(fig, output_dir, 15, "timing_composition_contrasts")
    calibration = pd.read_csv(ASSET_DIR / "Figure_16_source_calibration_sensitivity.csv"); metrics = [("mean_total_late_orders", "Mean total late orders"), ("mean_throughput_per_hour", "Mean throughput (orders/hour)"), ("mean_picker_utilization_percent", "Picker utilisation (%)"), ("mean_composite_score", "Matched composite score")]; fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, (metric, label) in zip(axes.flat, metrics, strict=True):
        for (method, split), series in calibration.groupby(["method", "split"]): ax.plot(series.parameter_value, series[metric], marker="o", markersize=3, linestyle="-" if split == "tuning" else "--", label=f"{method} ({split})")
        ax.set(xlabel="Parameter value", ylabel=label); ax.grid(alpha=0.25)
    axes[0, 0].legend(fontsize=7, frameon=False); fig.tight_layout(); save(fig, output_dir, 16, "calibration_sensitivity")
    beta = pd.read_csv(ASSET_DIR / "Figure_17_source_beta_sensitivity.csv"); metrics = [("total_late_mean", "Mean total late orders"), ("trips_mean", "Mean trip count"), ("throughput_mean_per_hour", "Mean throughput (orders/hour)"), ("cart_utilization_mean_percent", "Mean cart utilisation (%)")]; fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, (metric, label) in zip(axes.flat, metrics, strict=True):
        for method, series in beta.groupby("trigger_method"): ax.plot(series.beta, series[metric], marker="o", markersize=3, linewidth=1.4, label=method, color=COLORS.get(method))
        ax.axvline(2, color="#4b5563", linestyle="--", linewidth=1); ax.set(xlabel="Urgency threshold beta", ylabel=label, xticks=[1, 2, 3, 4]); ax.grid(alpha=0.25)
    axes[0, 0].legend(ncol=2, fontsize=7, frameon=False); fig.tight_layout(); save(fig, output_dir, 17, "beta_sensitivity")
    latency = pd.read_csv(ASSET_DIR / "Figure_18_source_decision_latency.csv"); summary = latency.groupby(["trigger_method", "pool_size_n"], as_index=False).adjusted_microseconds_per_call.median()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for method, series in summary.groupby("trigger_method"): ax.plot(series.pool_size_n, series.adjusted_microseconds_per_call, marker="o", markersize=3, linewidth=1.4, label=method, color=COLORS.get(method))
    ax.set(xscale="log", xlabel="Order-pool size", ylabel="Median overhead-adjusted latency (microseconds/call)"); ax.grid(alpha=0.25); ax.legend(ncol=2, fontsize=8, frameon=False); fig.tight_layout(); save(fig, output_dir, 18, "decision_latency")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--output-dir", type=Path, default=ASSET_DIR / "generated"); parser.add_argument("--figures", default="all"); parser.add_argument("--wp4-panel-b", action="store_true", help="Generate the WP4 Panel B conditional-effects figure."); parser.add_argument("--wp5-figure-11", action="store_true", help="Generate the expanded WP5 benchmark-calibration figure."); parser.add_argument("--supplement-s5-latency", action="store_true", help="Generate Supplementary Figure S5 latency curves.")
    args = parser.parse_args(); requested = set(range(1, 19)) if args.figures == "all" else {int(value) for value in args.figures.split(",")}; args.output_dir.mkdir(parents=True, exist_ok=True)
    if 1 in requested: figure_1(args.output_dir)
    raw_figures = {2, 3, 4, 6, 7, 8, 10, 11, 12, 13, 14}
    if requested & raw_figures:
        raw = pd.read_csv(ASSET_DIR / "Figure_06_to_08_source_final_results.csv", usecols=RAW_COLUMNS)
        if requested & {2, 3, 4}: figures_2_to_4(raw, args.output_dir)
        if requested & {6, 7, 8, 10, 11, 12, 13, 14}: figures_6_to_14(raw, args.output_dir)
    if 5 in requested: figure_5(args.output_dir)
    if 9 in requested: shutil.copy2(ASSET_DIR / "Figure_09_Pareto_Service_Throughput.png", args.output_dir / "Figure_09_pareto_service_throughput.png")
    if requested & {15, 16, 17, 18}: figures_15_to_18(args.output_dir)
    if args.wp4_panel_b: figure_10_wp4_panel_b(args.output_dir)
    if args.wp5_figure_11: figure_11_wp5_calibration(args.output_dir)
    if args.supplement_s5_latency: figure_s5_latency(SUPPLEMENT_DIR)
    return 0


if __name__ == "__main__": raise SystemExit(main())