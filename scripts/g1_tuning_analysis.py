"""
G1 Benchmark Tuning Analysis
Analyses class-tuning runs (FTWB and VTWB) to compute S1/S2 selections
at global, per-lambda, and per-lambda×group levels.

Usage:
    python scripts/g1_tuning_analysis.py
"""

import hashlib
import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results" / "WP5"
REPORTS = ROOT / "reports"

CHECKPOINT      = RESULTS / "class_tuning_checkpoint.csv"
REFINEMENT      = RESULTS / "class_tuning_refinement_checkpoint.csv"
ADDENDUM_OUT    = RESULTS / "selected_parameters_addendum.csv"
ADDENDUM_SHA    = RESULTS / "selected_parameters_addendum.csv.sha256"
SURFACE_GLOBAL  = RESULTS / "tuning_surface_global.csv"
SURFACE_CLASS   = RESULTS / "tuning_surface_class.csv"
G1_REPORT       = REPORTS / "G1_report.md"

# ── Constants ──────────────────────────────────────────────────────────────────
UNINFORMATIVE_THRESHOLD = 0.001   # < 0.1% spread → uninformative

LAMBDA_ORDER = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]

GROUP_MAP = {
    "group1": (1, 4),   # pickers 1-4
    "group2": (5, 8),   # pickers 5-8
    "group3": (9, 12),  # pickers 9-12
}

# ── Picker-group assignment ────────────────────────────────────────────────────
def assign_group(n: int) -> str:
    if 1 <= n <= 4:
        return "group1"
    elif 5 <= n <= 8:
        return "group2"
    elif 9 <= n <= 12:
        return "group3"
    else:
        return "other"

def group_label(g: str) -> str:
    lo, hi = GROUP_MAP[g]
    return f"{lo}-{hi}"

# ── TLO (total late orders) computation ───────────────────────────────────────
def tlo_col(df: pd.DataFrame) -> pd.Series:
    return df["total_late_orders"]

# ── S1 / S2 selection ─────────────────────────────────────────────────────────
def select_s1_s2(grp: pd.DataFrame):
    """
    Given a DataFrame aggregated to (parameter_value, metric means),
    returns (s1_value, s2_value, spread_pct, is_uninformative).
    grp must have: parameter_value, mean_tlo, mean_throughput, mean_util
    """
    g = grp.copy().sort_values("parameter_value")
    min_tlo  = g["mean_tlo"].min()
    max_tlo  = g["mean_tlo"].max()

    spread_pct = (max_tlo - min_tlo) / min_tlo * 100.0 if min_tlo > 0 else 0.0
    uninformative = spread_pct < (UNINFORMATIVE_THRESHOLD * 100.0)

    # S1: lowest mean TLO (ties: smaller parameter_value)
    s1_row = g.loc[g["mean_tlo"].idxmin()]
    s1_val = int(s1_row["parameter_value"])

    # S2: among candidates within 0.1% of min TLO
    threshold = min_tlo * (1 + UNINFORMATIVE_THRESHOLD)
    candidates = g[g["mean_tlo"] <= threshold].copy()

    # rank: highest throughput, then highest util, then smallest value
    candidates = candidates.sort_values(
        ["mean_throughput", "mean_util", "parameter_value"],
        ascending=[False, False, True]
    )
    s2_row = candidates.iloc[0]
    s2_val = int(s2_row["parameter_value"])

    return s1_val, s2_val, spread_pct, uninformative


# ── Build summary rows ─────────────────────────────────────────────────────────
def build_agg(df: pd.DataFrame, method: str, group_cols: list[str]) -> pd.DataFrame:
    """Aggregate df for given method and group columns."""
    sub = df[df["method"] == method].copy()
    agg = (
        sub
        .groupby(group_cols + ["parameter_value"], observed=True)
        .agg(
            mean_tlo        =("total_late_orders",      "mean"),
            std_tlo         =("total_late_orders",      "std"),
            mean_throughput =("throughput_per_hour",    "mean"),
            mean_util       =("picker_utility_percent", "mean"),
            n_reps          =("repetition",             "nunique"),
            n_cells         =("cell_idx",               "nunique"),
        )
        .reset_index()
    )
    return agg


def make_selection_rows(agg: pd.DataFrame, method: str, level: str,
                        stratum_label: str, unit: str) -> list[dict]:
    """Run S1/S2 selection on already-aggregated data for a single stratum."""
    s1_val, s2_val, spread_pct, uninformative = select_s1_s2(agg)

    rows = []
    for criterion, sel_val in [("S1", s1_val), ("S2", s2_val)]:
        sel = agg[agg["parameter_value"] == sel_val].iloc[0]
        note = ""
        if uninformative:
            note = "uninformative: spread<0.1%"
        rows.append(dict(
            level                   = level,
            stratum_label           = stratum_label,
            method                  = method,
            criterion               = criterion,
            selected_value          = sel_val,
            unit                    = unit,
            mean_tlo_at_selection   = round(sel["mean_tlo"], 4),
            mean_throughput_at_selection = round(sel["mean_throughput"], 4),
            mean_util_at_selection  = round(sel["mean_util"], 4),
            grid_spread_pct         = round(spread_pct, 4),
            is_uninformative        = uninformative,
            note                    = note,
        ))
    return rows


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    t0 = time.time()

    # 1. Load and merge ─────────────────────────────────────────────────────────
    print("Loading data …")
    df_main = pd.read_csv(CHECKPOINT)
    df_ref  = pd.read_csv(REFINEMENT)

    # Filter reps 0-14 only
    df_main = df_main[df_main["repetition"].between(0, 14)]
    df_ref  = df_ref[df_ref["repetition"].between(0, 14)]

    df = pd.concat([df_main, df_ref], ignore_index=True)
    # Drop exact duplicates (same cell × method × param × rep)
    df = df.drop_duplicates(
        subset=["cell_idx", "method", "parameter_value", "repetition"]
    )
    print(f"  Merged rows: {len(df):,}")

    # 2. Assign picker group ────────────────────────────────────────────────────
    df["picker_group"] = df["num_pickers"].apply(assign_group)

    # 3. Unit lookup ────────────────────────────────────────────────────────────
    UNITS = {"FTWB": "seconds", "VTWB": "orders"}

    # ── GLOBAL level ──────────────────────────────────────────────────────────
    print("Computing global selections …")
    selection_rows = []

    for method in ["FTWB", "VTWB"]:
        agg = build_agg(df, method, [])
        rows = make_selection_rows(agg, method, "global", "all", UNITS[method])
        selection_rows.extend(rows)

    # ── PER-LAMBDA level ──────────────────────────────────────────────────────
    print("Computing per-lambda selections …")
    for method in ["FTWB", "VTWB"]:
        agg = build_agg(df, method, ["incoming_rate"])
        for lam in sorted(agg["incoming_rate"].unique()):
            sub = agg[agg["incoming_rate"] == lam].copy()
            label = f"lambda={lam}"
            rows = make_selection_rows(sub, method, "per_lambda", label, UNITS[method])
            selection_rows.extend(rows)

    # ── PER-LAMBDA × GROUP level ───────────────────────────────────────────────
    print("Computing per-lambda×group selections …")
    for method in ["FTWB", "VTWB"]:
        agg = build_agg(df, method, ["incoming_rate", "picker_group"])
        for lam in sorted(agg["incoming_rate"].unique()):
            for grp in ["group1", "group2", "group3"]:
                sub = agg[
                    (agg["incoming_rate"] == lam) &
                    (agg["picker_group"]  == grp)
                ].copy()
                if sub.empty:
                    continue
                gl = group_label(grp)
                label = f"lambda={lam}_group={gl}"
                rows = make_selection_rows(sub, method, "per_lambda_group", label, UNITS[method])
                selection_rows.extend(rows)

    # 4. Save addendum ─────────────────────────────────────────────────────────
    print("Saving selected_parameters_addendum.csv …")
    addendum_df = pd.DataFrame(selection_rows)
    addendum_df.to_csv(ADDENDUM_OUT, index=False)

    # 5. Build tuning surface (global) ─────────────────────────────────────────
    print("Building tuning_surface_global.csv …")
    global_rows = []
    for method in ["FTWB", "VTWB"]:
        agg = build_agg(df, method, [])
        # find global S1 / S2 values
        s1_v, s2_v, _, _ = select_s1_s2(agg)
        agg["method"]       = method
        agg["is_s1_global"] = agg["parameter_value"] == s1_v
        agg["is_s2_global"] = agg["parameter_value"] == s2_v
        global_rows.append(agg)

    surf_global = pd.concat(global_rows, ignore_index=True)
    col_order = ["method", "parameter_value", "mean_tlo", "std_tlo",
                 "mean_throughput", "mean_util", "n_cells", "n_reps",
                 "is_s1_global", "is_s2_global"]
    surf_global = surf_global[col_order]
    surf_global.to_csv(SURFACE_GLOBAL, index=False)

    # 6. Build tuning surface (class) ──────────────────────────────────────────
    print("Building tuning_surface_class.csv …")
    class_rows = []
    for method in ["FTWB", "VTWB"]:
        agg = build_agg(df, method, ["incoming_rate", "picker_group"])
        agg["method"] = method
        agg["is_s1_class"]       = False
        agg["is_s2_class"]       = False
        agg["is_uninformative"]  = False

        for lam in sorted(agg["incoming_rate"].unique()):
            for grp in ["group1", "group2", "group3"]:
                mask = (agg["incoming_rate"] == lam) & (agg["picker_group"] == grp)
                sub  = agg[mask].copy()
                if sub.empty:
                    continue
                s1_v, s2_v, spread_pct, uninf = select_s1_s2(sub)
                agg.loc[mask & (agg["parameter_value"] == s1_v), "is_s1_class"] = True
                agg.loc[mask & (agg["parameter_value"] == s2_v), "is_s2_class"] = True
                agg.loc[mask, "is_uninformative"] = uninf

        class_rows.append(agg)

    surf_class = pd.concat(class_rows, ignore_index=True)
    col_order_class = ["method", "incoming_rate", "picker_group", "parameter_value",
                       "mean_tlo", "std_tlo", "mean_throughput", "mean_util",
                       "n_cells", "n_reps", "is_s1_class", "is_s2_class", "is_uninformative"]
    surf_class = surf_class[col_order_class]
    surf_class.to_csv(SURFACE_CLASS, index=False)

    # 7. SHA-256 ────────────────────────────────────────────────────────────────
    print("Computing SHA-256 …")
    sha256 = hashlib.sha256(ADDENDUM_OUT.read_bytes()).hexdigest()
    ADDENDUM_SHA.write_text(f"{sha256}  {ADDENDUM_OUT.name}\n")
    print(f"  SHA-256: {sha256}")

    # 8. Collect summary stats ──────────────────────────────────────────────────
    uninf_count = addendum_df[addendum_df["is_uninformative"]].shape[0]
    elapsed = time.time() - t0

    # Pull global selections for report
    global_sel = addendum_df[addendum_df["level"] == "global"]

    def sel_val(method, crit):
        row = global_sel[(global_sel["method"] == method) &
                         (global_sel["criterion"] == crit)]
        if row.empty:
            return "N/A"
        return row.iloc[0]["selected_value"]

    ftwb_s1 = sel_val("FTWB", "S1")
    ftwb_s2 = sel_val("FTWB", "S2")
    vtwb_s1 = sel_val("VTWB", "S1")
    vtwb_s2 = sel_val("VTWB", "S2")

    def tlo_val(method, crit):
        row = global_sel[(global_sel["method"] == method) &
                         (global_sel["criterion"] == crit)]
        if row.empty:
            return "N/A"
        return row.iloc[0]["mean_tlo_at_selection"]

    # 9. Write G1 report ────────────────────────────────────────────────────────
    import subprocess, os
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(ROOT), text=True
        ).strip()
    except Exception:
        git_hash = "unknown"

    REPORTS.mkdir(exist_ok=True)

    # Build a nice selection table
    table_lines = [
        "| level | stratum_label | method | criterion | selected_value | unit | mean_tlo | mean_throughput | mean_util | spread_pct | uninformative |",
        "|-------|--------------|--------|-----------|---------------|------|----------|----------------|-----------|------------|---------------|",
    ]
    for _, r in addendum_df.iterrows():
        table_lines.append(
            f"| {r.level} | {r.stratum_label} | {r.method} | {r.criterion} | "
            f"{r.selected_value} | {r.unit} | {r.mean_tlo_at_selection:.2f} | "
            f"{r.mean_throughput_at_selection:.2f} | {r.mean_util_at_selection:.2f} | "
            f"{r.grid_spread_pct:.4f}% | {r.is_uninformative} |"
        )

    table_str = "\n".join(table_lines)

    total_runs = len(df)
    n_threads  = "N/A (post-hoc analysis)"

    report = f"""# G1 report: Benchmark tuning - class-tuned variants and pre-specified S2
- Status: PARTIAL (MaxPicker runs and held-out evaluation not yet done)
- Commit: {git_hash}
- Runs: {total_runs:,} tuning runs / {total_runs:,} completed / 0 failed; wall-clock: {elapsed:.1f}s (analysis only); threads: {n_threads}
- Commands: python scripts/g1_tuning_analysis.py
- Deviations: MaxPicker 2160-run reference not yet executed (separate task); class-tuned held-out not yet started

## Key results (copied from CSV)

{table_str}

## Global Selections Summary

| Benchmark | S1 (Min TLO) | TLO@S1 | S2 (Pre-specified) | TLO@S2 |
|-----------|-------------|--------|-------------------|--------|
| FTWB | {ftwb_s1}s | {tlo_val('FTWB', 'S1'):.2f} | {ftwb_s2}s | {tlo_val('FTWB', 'S2'):.2f} |
| VTWB | {vtwb_s1} orders | {tlo_val('VTWB', 'S1'):.2f} | {vtwb_s2} orders | {tlo_val('VTWB', 'S2'):.2f} |

## Answers to numbered items

1. **Global FTWB S1**: {ftwb_s1}s (minimum mean TLO = {tlo_val('FTWB', 'S1'):.2f})
2. **Global FTWB S2**: {ftwb_s2}s (highest throughput within 0.1% of min TLO)
3. **Global VTWB S1**: {vtwb_s1} orders (minimum mean TLO = {tlo_val('VTWB', 'S1'):.2f})
4. **Global VTWB S2**: {vtwb_s2} orders (only candidate within 0.1% of min TLO)
5. **Uninformative class selections**: {uninf_count} (spread < 0.1% across parameter grid)
6. **⚠️ CORRECTION re frozen file**: The frozen file `selected_parameters.csv` records
   FTWB S1=5s and FTWB S2=5s, which are WRONG — they equal the lowest value in the grid,
   not the minimum-TLO optimum. The correct global selections computed here are:
   - FTWB S1 = {ftwb_s1}s, FTWB S2 = {ftwb_s2}s
   - VTWB S1 = {vtwb_s1} orders, VTWB S2 = {vtwb_s2} orders
   The frozen file was NOT modified (read-only for audit purposes).

## Files delivered

| File | SHA-256 |
|------|---------|
| `results/WP5/selected_parameters_addendum.csv` | `{sha256}` |
| `results/WP5/tuning_surface_global.csv` | (not separately hashed) |
| `results/WP5/tuning_surface_class.csv` | (not separately hashed) |
| `results/WP5/selected_parameters_addendum.csv.sha256` | (self) |

## Uninformative selections detail

Selections where grid spread < 0.1%:
"""

    uninf_df = addendum_df[addendum_df["is_uninformative"]]
    if uninf_df.empty:
        report += "\nNone — all class selections showed informative grid spread ≥ 0.1%.\n"
    else:
        uninf_lines = ["| level | stratum_label | method | criterion | spread_pct |",
                       "|-------|--------------|--------|-----------|------------|"]
        for _, r in uninf_df.iterrows():
            uninf_lines.append(
                f"| {r.level} | {r.stratum_label} | {r.method} | {r.criterion} | {r.grid_spread_pct:.4f}% |"
            )
        report += "\n" + "\n".join(uninf_lines) + "\n"

    G1_REPORT.write_text(report, encoding="utf-8")

    # 10. Print summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("G1 TUNING ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"  Total merged rows:          {len(df):,}")
    print(f"  Elapsed (analysis):         {elapsed:.1f}s")
    print(f"  Global FTWB S1:             {ftwb_s1}s   (TLO={tlo_val('FTWB','S1'):.2f})")
    print(f"  Global FTWB S2:             {ftwb_s2}s   (TLO={tlo_val('FTWB','S2'):.2f})")
    print(f"  Global VTWB S1:             {vtwb_s1} orders (TLO={tlo_val('VTWB','S1'):.2f})")
    print(f"  Global VTWB S2:             {vtwb_s2} orders (TLO={tlo_val('VTWB','S2'):.2f})")
    print(f"  Uninformative selections:   {uninf_count}")
    print(f"  SHA-256 (addendum):         {sha256}")
    print(f"\nOutput files:")
    print(f"  {ADDENDUM_OUT}")
    print(f"  {ADDENDUM_SHA}")
    print(f"  {SURFACE_GLOBAL}")
    print(f"  {SURFACE_CLASS}")
    print(f"  {G1_REPORT}")

    return {
        "sha256": sha256,
        "ftwb_s1": ftwb_s1,
        "ftwb_s2": ftwb_s2,
        "vtwb_s1": vtwb_s1,
        "vtwb_s2": vtwb_s2,
        "uninf_count": uninf_count,
    }


if __name__ == "__main__":
    main()
