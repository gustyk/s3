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


def figures_2_to_5(data: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5)); boxplot(ax, data, "total_late_orders", "Censoring-aware total late orders"); save(fig, output_dir, 2, "total_late_orders_distribution")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    boxplot(axes[0], data, "throughput_per_hour", "Throughput (orders/hour)"); boxplot(axes[1], data, "on_time_rate_percent", "Non-late-at-horizon rate (%)")
    fig.tight_layout(); save(fig, output_dir, 3, "throughput_and_service_distribution")
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    for ax, column, label in zip(axes, ["picker_utility_percent", "mean_cart_utilization_percent", "trip_count"], ["Picker utilisation (%)", "Cart utilisation (%)", "Completed trip count"], strict=True): boxplot(ax, data, column, label)
    fig.tight_layout(); save(fig, output_dir, 4, "service_efficiency_distribution")
    aggregate = data.groupby("trigger_method", as_index=False).agg(late=("total_late_orders", "sum"), generated=("generated_orders", "sum"), throughput=("throughput_per_hour", "mean"), utilisation=("picker_utility_percent", "mean"))
    aggregate["service"] = 100 * (1 - aggregate.late / aggregate.generated)
    fig, ax = plt.subplots(figsize=(10, 6))
    for _, row in aggregate.iterrows():
        ax.scatter(row.throughput, row.service, color=COLORS[row.trigger_method], s=70); ax.annotate(row.trigger_method, (row.throughput, row.service), xytext=(4, 4), textcoords="offset points")
    ax.set(xlabel="Mean throughput (orders/hour)", ylabel="Non-late-at-horizon rate (%)"); ax.grid(alpha=0.25)
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
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--output-dir", type=Path, default=ASSET_DIR / "generated"); parser.add_argument("--figures", default="all")
    args = parser.parse_args(); requested = set(range(1, 19)) if args.figures == "all" else {int(value) for value in args.figures.split(",")}; args.output_dir.mkdir(parents=True, exist_ok=True)
    if 1 in requested: figure_1(args.output_dir)
    raw_figures = {2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14}
    if requested & raw_figures:
        raw = pd.read_csv(ASSET_DIR / "Figure_06_to_08_source_final_results.csv", usecols=RAW_COLUMNS)
        if requested & {2, 3, 4, 5}: figures_2_to_5(raw, args.output_dir)
        if requested & {6, 7, 8, 10, 11, 12, 13, 14}: figures_6_to_14(raw, args.output_dir)
    if 9 in requested: shutil.copy2(ASSET_DIR / "Figure_09_Pareto_Service_Throughput.png", args.output_dir / "Figure_09_pareto_service_throughput.png")
    if requested & {15, 16, 17, 18}: figures_15_to_18(args.output_dir)
    return 0


if __name__ == "__main__": raise SystemExit(main())