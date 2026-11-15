"""Regenerate selected supplementary result tables from the per-run data in the repository
and compare them with the committed files (the committed files are never overwritten).

Inputs (all tracked in the repository):
  data/results_full_factorial.csv.gz         207,360 canonical full-factorial runs
  results/WP8/per_run_triage.csv             per-run cohort / all-arrivals counts (joined on run_uuid)

Usage:
  python scripts/regenerate_supplement_tables.py [--out outputs/regenerated] [--only NAME ...]

For every table the script writes <out>/<name>.csv and prints IDENTICAL if all values agree
with the committed file within a relative tolerance of 1e-9, otherwise DIFFERENT with details.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
KEYS = ["incoming_rate", "num_pickers", "cart_capacity", "routing_policy", "repetition"]
E_Q = 30.25  # mean items per order used for the utilisation lower bound (scripts/run_t5_classification.py)


def load_runs():
    cols = ["run_uuid"] + KEYS + ["trigger_method", "batching_method", "total_late_orders"]
    f = pd.read_csv(ROOT / "data/results_full_factorial.csv.gz", usecols=cols)
    tri = pd.read_csv(ROOT / "results/WP8/per_run_triage.csv")
    f = f.merge(tri, on="run_uuid", how="left", validate="1:1")
    # MPBH is stored under both batching tags (identical runs); keep one copy
    f = f[~((f.trigger_method == "MPBH") & (f.batching_method == "EDT"))].copy()
    f["m_group"] = pd.cut(f.num_pickers, [0, 4, 8, 12], labels=["scarce (1-4)", "mid (5-8)", "abundant (9-12)"]).astype(str)
    rho = f.incoming_rate / 60.0 * 5.0 * E_Q / f.num_pickers
    f["band"] = np.where(rho < 0.7, "light", np.where(rho <= 1.0, "heavy", "overloaded"))
    return f


def t_interval(x):
    """Two-sided 95% t interval for the mean of x (one value per replication)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    se = x.std(ddof=1) / np.sqrt(n)
    q = stats.t.ppf(0.975, n - 1)
    return x.mean() - q * se, x.mean() + q * se


def pooled_diff(f, value, a, b):
    """Per (scenario, replication) mean of `value` for policy set a minus policy set b."""
    ma = f[f.trigger_method.isin(a)].groupby(KEYS)[value].mean().rename("a")
    mb = f[f.trigger_method.isin(b)].groupby(KEYS)[value].mean().rename("b")
    return pd.concat([ma, mb], axis=1).reset_index().assign(diff=lambda d: d.a - d.b)


CANON = ["FTWB", "VTWB"]


def table10_v3(f):
    rows = []
    for (lam, grp), g in f.groupby(["incoming_rate", "m_group"], sort=False):
        mp = g[g.trigger_method == "MPBH"]
        can = g[g.trigger_method.isin(CANON)]
        mx = g[g.trigger_method == "MaxPicker"]
        d = pooled_diff(g, "cohort_late", CANON, ["MPBH"])
        lo, hi = t_interval((-d["diff"]).groupby(d.repetition).mean())
        n_mean = mp.cohort_N.mean()
        tc, tx, tm = can.cohort_late.mean(), mx.cohort_late.mean(), mp.cohort_late.mean()
        delta = tm - tc
        rows.append({
            "lam": lam, "m_group": grp, "mean_N": n_mean,
            "mpbh_ontime_orders_per_run": mp.cohort_ontime_completed.mean(),
            "mpbh_ontime_pct_of_N": mp.cohort_ontime_completed.mean() / n_mean * 100,
            "canonical_ontime_orders_per_run": can.cohort_ontime_completed.mean(),
            "canonical_ontime_pct_of_N": can.cohort_ontime_completed.mean() / n_mean * 100,
            "maxpicker_ontime_orders_per_run": mx.cohort_ontime_completed.mean(),
            "maxpicker_ontime_pct_of_N": mx.cohort_ontime_completed.mean() / n_mean * 100,
            "mean_canonical_TLO": tc, "mean_maxpicker_TLO": tx, "mean_mpbh_TLO": tm,
            "delta_vs_canonical": delta, "delta_vs_canonical_ci95_low": lo, "delta_vs_canonical_ci95_high": hi,
            "rel_reduction_canonical_pct": -delta / tc * 100 if tc else 0.0,
            "delta_as_pct_of_N": delta / n_mean * 100,
            "practical_sig_flag_prespec": abs(delta / n_mean * 100) >= 2.0,
            "delta_vs_maxpicker": tm - tx,
            "rel_reduction_maxpicker_pct": -(tm - tx) / tx * 100 if tx else 0.0,
        })
    out = pd.DataFrame(rows)
    return out.sort_values(["lam"], kind="stable").reset_index(drop=True)


def all_arrivals_tlo_v4(f):
    def row(g, st, sv):
        mp = g[g.trigger_method == "MPBH"].all_arrivals_late.mean()
        can = g[g.trigger_method.isin(CANON)].all_arrivals_late.mean()
        mx = g[g.trigger_method == "MaxPicker"].all_arrivals_late.mean()
        d = pooled_diff(g, "all_arrivals_late", CANON, ["MPBH"])
        lo, hi = t_interval(d["diff"].groupby(d.repetition).mean())
        return {"slice_type": st, "slice_value": sv, "mpbh_all_arrivals_tlo": mp,
                "canonical_pooled_all_arrivals_tlo": can, "maxpicker_all_arrivals_tlo": mx,
                "delta_vs_canonical_abs": can - mp, "ci95_vs_canonical_low": lo, "ci95_vs_canonical_high": hi,
                "rel_reduction_vs_canonical_pct": (can - mp) / can * 100,
                "delta_vs_maxpicker_abs": mx - mp, "rel_reduction_vs_maxpicker_pct": (mx - mp) / mx * 100}
    rows = [row(f, "overall", "all")]
    rows += [row(g, "lambda", lam) for lam, g in f.groupby("incoming_rate")]
    rows += [row(f[f.band == b], "band", b) for b in ["light", "heavy", "overloaded"]]
    return pd.DataFrame(rows)


def backlog_triage_v4(f):
    metrics = ["backlog_at_W", "pre_completed_by_H", "pre_outstanding_at_H", "mean_age_outstanding_inherited_s",
               "p95_age_outstanding_inherited_s", "max_age_outstanding_inherited_s",
               "cohort_N", "cohort_late", "cohort_ontime_completed"]
    rows = []

    def add(g, pol, level, lam, grp):
        r = {"trigger_method": pol, "group_level": level, "incoming_rate": lam, "picker_group": grp}
        r.update({m: g[m].mean() for m in metrics})
        r["cohort_ontime_pct_of_N"] = r["cohort_ontime_completed"] / r["cohort_N"] * 100
        rows.append(r)

    for pol, p in f.groupby("trigger_method"):
        for (lam, grp), g in p.groupby(["incoming_rate", "m_group"]):
            add(g, pol, "picker_group", lam, grp)
        for lam, g in p.groupby("incoming_rate"):
            add(g, pol, "per_lambda", lam, "all")
        for b in ["heavy", "light", "overloaded"]:
            add(p[p.band == b], pol, "band", -1.0, b)
    return pd.DataFrame(rows)



# ---------------------------------------------------------------- crossed timing x composition
def _cells(f, tuned):
    """Six-cell (timing x composition) table per scenario and replication; returns wide frame."""
    def s(d, n):
        return d.set_index(KEYS).total_late_orders.rename(n)
    imm = {
        "IF": f[(f.trigger_method == "MaxPicker") & (f.batching_method == "FCFS")],
        "IE": f[(f.trigger_method == "MaxPicker") & (f.batching_method == "EDT")],
        "IM": f[f.trigger_method == "MPBH"],
    }
    if tuned:
        h = pd.read_csv(ROOT / "results/WP5/held_out_evaluation_raw.csv.gz")
        t5 = h[h.experiment_type == "FTWB_tuned_F5"]
        ftwb = {"FF": t5[t5.batching_method == "FCFS"], "FE": t5[t5.batching_method == "EDT"],
                "FM": h[h.experiment_type == "FTWB_F5_x_MPBH_comp"]}
        imm = {k: v[v.repetition.between(15, 29)] for k, v in imm.items()}
    else:
        c = pd.read_csv(ROOT / "results/WP4/ftwb_mpbh_raw.csv", usecols=KEYS + ["total_late_orders"])
        ftwb = {"FF": f[(f.trigger_method == "FTWB") & (f.batching_method == "FCFS")],
                "FE": f[(f.trigger_method == "FTWB") & (f.batching_method == "EDT")], "FM": c}
    cells = {**ftwb, **imm}
    p = pd.concat([s(v, k) for k, v in cells.items()], axis=1).reset_index()
    assert not p.isna().any().any()
    p["tF"], p["tE"], p["tM"] = p.FF - p.IF, p.FE - p.IE, p.FM - p.IM
    p["cI"], p["cF"] = p.IM - p.IF, p.FM - p.FF
    p["inter"] = p.tM - p.tF
    p["sh_t"], p["sh_c"] = (p.tF + p.tM) / 2, (p.cI + p.cF) / 2 * -1
    p["tot"] = p.FF - p.IM
    return p


def _share(p):
    """Timing share: pooled ratio of means; 95% t interval (df = n-1) from the SD of per-replication shares."""
    g = p.groupby("repetition")[["sh_t", "tot"]].mean()
    n = len(g)
    point = g.sh_t.mean() / g.tot.mean() * 100
    hw = stats.t.ppf(0.975, n - 1) * (g.sh_t / g.tot).std(ddof=1) / np.sqrt(n) * 100
    return point, point - hw, point + hw


def _rep_ci(p, col):
    return t_interval(p.groupby("repetition")[col].mean())


def crossed_effects_by_lambda_ci(f):
    p = _cells(f, tuned=False)
    rows = []
    for lam, g in p.groupby("incoming_rate"):
        lo, hi = _rep_ci(g, "inter")
        n = g.repetition.nunique()
        rows.append({"incoming_rate": lam, "simple_effect_timing_at_FCFS": g.tF.mean(),
                     "simple_effect_timing_at_EDT": g.tE.mean(), "simple_effect_timing_at_MPBH": g.tM.mean(),
                     "simple_effect_comp_MPBH_vs_FCFS_at_IMM": g.cI.mean(),
                     "simple_effect_comp_MPBH_vs_FCFS_at_FTWB": g.cF.mean(),
                     "interaction_timing_x_comp": g.inter.mean(),
                     "interaction_ci95_low": lo, "interaction_ci95_high": hi, "clusters": n, "df": n - 1})
    return pd.DataFrame(rows)


def shapley_by_lambda(f):
    p = _cells(f, tuned=False)
    rows = []
    for lam, g in p.groupby("incoming_rate"):
        pt, lo, hi = _share(g)
        rows.append({"incoming_rate": lam, "total_reduction": g.tot.mean(), "shapley_timing": g.sh_t.mean(),
                     "shapley_composition": g.tot.mean() - g.sh_t.mean(), "timing_share_pct": pt,
                     "timing_share_ci_low": lo, "timing_share_ci_high": hi})
    return pd.DataFrame(rows)


def crossed_tuned_timing_shapley(f):
    p = _cells(f, tuned=True)
    rows = []
    for label, g in [("overall", p)] + [(f"lambda={lam}", g) for lam, g in p.groupby("incoming_rate")]:
        pt, lo, hi = _share(g)
        rows.append({"stratum": label, "total_reduction_orders": g.tot.mean(), "shapley_timing_orders": g.sh_t.mean(),
                     "shapley_composition_orders": g.tot.mean() - g.sh_t.mean(), "timing_share_pct": pt,
                     "timing_share_ci95_low": lo, "timing_share_ci95_high": hi})
    return pd.DataFrame(rows)


def crossed_tuned_timing_effects_by_lambda_ci(f):
    p = _cells(f, tuned=True)
    spec = [("timing_at_FCFS", "tF", "simple_effect_timing_at_FCFS"), ("timing_at_EDT", "tE", "simple_effect_timing_at_EDT"),
            ("timing_at_MPBH", "tM", "simple_effect_timing_at_MPBH"),
            ("comp_at_IMM", "cI", "simple_effect_comp_MPBH_vs_FCFS_at_IMM"),
            ("comp_at_FTWB", "cF", "simple_effect_comp_MPBH_vs_FCFS_at_FTWB")]
    rows = []
    for lam, g in p.groupby("incoming_rate"):
        r = {"incoming_rate": lam}
        for short, col, name in spec:
            lo, hi = _rep_ci(g, col)
            r.update({name: g[col].mean(), f"{short}_ci_low": lo, f"{short}_ci_high": hi})
        lo, hi = _rep_ci(g, "inter")
        n = g.repetition.nunique()
        r.update({"interaction_timing_x_comp": g.inter.mean(), "interaction_ci95_low": lo,
                  "interaction_ci95_high": hi, "clusters": n, "df": n - 1})
        rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ setup-time sensitivity (36-cell subset)
def setup_sensitivity_with_tuned_and_cis(_f):
    raw = pd.read_csv(ROOT / "results/WP6/setup_simulation_raw.csv")
    tun = pd.read_csv(ROOT / "results/WP6/setup_simulation_tuned_raw.csv")
    key = ["setup_time", "incoming_rate", "cart_capacity", "num_pickers", "repetition"]

    def cell_mean(d, names, col="trigger_method"):
        return d[d[col].isin(names)].groupby(key).total_late_orders.mean()

    series = {"mp": cell_mean(raw, ["MPBH"]), "can": cell_mean(raw, ["FTWB", "VTWB"]),
              "tun": cell_mean(tun, ["FTWB_tuned_F5", "VTWB_tuned_V8"]), "f5": cell_mean(tun, ["FTWB_tuned_F5"]),
              "v8": cell_mean(tun, ["VTWB_tuned_V8"]), "v6": cell_mean(tun, ["VTWB_tuned_V6"]),
              "mx": cell_mean(raw, ["MaxPicker"])}
    p = pd.concat(series, axis=1).reset_index()
    rows = []
    for st, g in p.groupby("setup_time"):
        r = {"setup_time": st, "mpbh_mean_tlo": g.mp.mean(), "canonical_pooled_mean_tlo": g.can.mean(),
             "tuned_pooled_mean_tlo": g.tun.mean(), "tuned_ftwb_f5_mean_tlo": g.f5.mean(),
             "tuned_vtwb_v8_mean_tlo": g.v8.mean(), "tuned_vtwb_v6_mean_tlo": g.v6.mean(),
             "maxpicker_mean_tlo": g.mx.mean()}
        for short, col in [("canonical_pooled", "can"), ("tuned_ftwb", "f5"), ("maxpicker", "mx")]:
            d = (g[col] - g.mp).groupby(g.repetition).mean()
            lo, hi = t_interval(d)
            r.update({f"advantage_vs_{short}": d.mean(), f"ci95_vs_{short}_low": lo, f"ci95_vs_{short}_high": hi,
                      f"rel_red_vs_{short}_pct": d.mean() / g[col].mean() * 100})
        rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ tardiness summary (partial)
def tardiness_run_mean_columns():
    """Regenerates only the run-level columns of results/WP3/tardiness_all_policies_summary.csv.
    The order-weighted and horizon lower-bound columns need order-level data (orders.csv.gz),
    which is not distributed with the repository, so they cannot be regenerated here."""
    cols = ["trigger_method", "batching_method", "completed_orders", "mean_tardiness_seconds",
            "mean_late_tardiness_seconds", "p95_tardiness_seconds"]
    f = pd.read_csv(ROOT / "data/results_full_factorial.csv.gz", usecols=cols)
    f = f[~((f.trigger_method == "MPBH") & (f.batching_method == "EDT"))]
    c = f[f.completed_orders > 0]
    new = c.groupby("trigger_method").agg(run_mean_completed_only_s=("mean_tardiness_seconds", "mean"),
                                          run_mean_conditional_late_s=("mean_late_tardiness_seconds", "mean"),
                                          run_mean_p95_s=("p95_tardiness_seconds", "mean"))
    ref = pd.read_csv(ROOT / "results/WP3/tardiness_all_policies_summary.csv", comment="#").dropna(how="all")
    ref = ref.set_index("policy")
    ok = all(np.allclose(new.loc[ref.index, c_], ref[c_], rtol=1e-9) for c_ in new.columns)
    print(f"tardiness_all_policies_summary (run-mean columns only): {'IDENTICAL' if ok else 'DIFFERENT'}; "
          "order-weighted and horizon lower-bound columns NOT regenerable (no order-level data in the repository)")


TABLES = {
    "table10_v3": (table10_v3, "results/WP9/table10_v3.csv"),
    "all_arrivals_tlo_v4": (all_arrivals_tlo_v4, "results/WP8/all_arrivals_tlo_v4.csv"),
    "setup_sensitivity_with_tuned_and_cis": (setup_sensitivity_with_tuned_and_cis,
                                             "results/WP6/setup_sensitivity_with_tuned_and_cis.csv"),
    "backlog_triage_v4": (backlog_triage_v4, "results/WP8/backlog_triage_v4.csv"),
    "crossed_effects_by_lambda_ci": (crossed_effects_by_lambda_ci, "results/WP4/crossed_effects_by_lambda_ci.csv"),
    "shapley_by_lambda": (shapley_by_lambda, "results/WP4/shapley_by_lambda.csv"),
    "crossed_tuned_timing_shapley": (crossed_tuned_timing_shapley, "results/WP5/crossed_tuned_timing_shapley.csv"),
    "crossed_tuned_timing_effects_by_lambda_ci": (crossed_tuned_timing_effects_by_lambda_ci,
                                                  "results/WP5/crossed_tuned_timing_effects_by_lambda_ci.csv"),
}


def compare(new, ref_path):
    ref = pd.read_csv(ROOT / ref_path)
    if list(new.columns) != list(ref.columns):
        return False, f"columns differ: {list(new.columns)} vs {list(ref.columns)}"
    if len(new) != len(ref):
        return False, f"row count {len(new)} vs {len(ref)}"
    # align rows on the non-numeric key columns where possible
    keys = [c for c in ref.columns if ref[c].dtype == object or str(ref[c].dtype).startswith("str")]
    if "incoming_rate" in ref.columns and "incoming_rate" not in keys:
        keys.append("incoming_rate")
    if "lam" in ref.columns:
        keys.append("lam")
    if "slice_value" in ref.columns and "slice_value" not in keys:
        keys.append("slice_value")
    keys = list(dict.fromkeys(keys))
    a = new.copy()
    b = ref.copy()
    for k in keys:
        a[k] = a[k].astype(str)
        b[k] = b[k].astype(str)
    a = a.sort_values(keys).reset_index(drop=True)
    b = b.sort_values(keys).reset_index(drop=True)
    bad = []
    for c in ref.columns:
        if c in keys:
            if not (a[c] == b[c]).all():
                bad.append((c, "key mismatch"))
        elif ref[c].dtype == bool:
            if not (a[c].astype(bool) == b[c]).all():
                bad.append((c, "bool mismatch"))
        else:
            diff = ~np.isclose(a[c].astype(float), b[c].astype(float), rtol=1e-9, atol=1e-9, equal_nan=True)
            if diff.any():
                bad.append((c, f"{diff.sum()} cells, max abs diff "
                               f"{np.nanmax(np.abs(a[c].astype(float) - b[c].astype(float))):.3g}"))
    return (not bad), bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="outputs/regenerated")
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    f = load_runs()
    for name, (fn, ref) in TABLES.items():
        if args.only and name not in args.only:
            continue
        df = fn(f)
        df.to_csv(out / f"{name}.csv", index=False)
        ok, info = compare(df, ref)
        print(f"{name}: {'IDENTICAL' if ok else 'DIFFERENT'} to {ref}" + ("" if ok else f" -> {info}"))
    if not args.only or "tardiness" in args.only:
        tardiness_run_mean_columns()


if __name__ == "__main__":
    main()
