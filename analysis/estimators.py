"""Standard statistical estimators for stratified cluster designs in S3 simulation."""

from __future__ import annotations
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from scipy import stats

def stratified_cluster_ci(
    blocks: pd.DataFrame,
    value_col: str,
    stratum_col: str = "lam",
    rep_col: str = "rep",
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    blocks: one row per (scenario, replication) with the paired contrast in value_col.
    Returns estimate, lo, hi, se, df, n_clusters.
    Equal stratum weighting across strata with Welch-Satterthwaite df.
    """
    cl = blocks.groupby([stratum_col, rep_col])[value_col].mean().reset_index()
    g = cl.groupby(stratum_col)[value_col]
    n = g.size().to_numpy(float)
    mu = g.mean().to_numpy()
    s2 = g.var(ddof=1).to_numpy()
    S = len(n)

    # Variance contribution of each stratum (equal weight 1/S)
    v = s2 / n / (S**2)
    est = float(mu.mean())
    se = float(np.sqrt(v.sum()))

    # Welch-Satterthwaite degrees of freedom
    denom = np.sum((v**2) / (n - 1))
    dof = float((v.sum()**2) / denom) if denom > 0 else float("inf")
    t = float(stats.t.ppf(1.0 - alpha / 2.0, dof))

    return {
        "est": est,
        "lo": est - t * se,
        "hi": est + t * se,
        "se": se,
        "df": dof,
        "n_clusters": int(n.sum())
    }

def stratified_boot_ratio(
    cl: pd.DataFrame,
    num_col: str,
    den_col: str,
    stratum_col: str = "lam",
    B: int = 10000,
    seed: int = 20261020
) -> Tuple[float, Tuple[float, float]]:
    """
    cl: cluster-level table (one row per stratum x rep) with cluster-mean numerator and denominator.
    Returns (point_estimate, (ci_low, ci_high)) based on B bootstrap resamples within each stratum.
    """
    rng = np.random.default_rng(seed)
    groups = {s: d[[num_col, den_col]].to_numpy() for s, d in cl.groupby(stratum_col)}
    out = np.empty(B)
    for b in range(B):
        num = 0.0
        den = 0.0
        for arr in groups.values():
            idx = rng.integers(0, len(arr), len(arr))
            num += arr[idx, 0].mean()
            den += arr[idx, 1].mean()
        out[b] = num / den if den != 0 else np.nan

    point = sum(a[:, 0].mean() for a in groups.values()) / sum(a[:, 1].mean() for a in groups.values())
    ci = np.percentile(out, [2.5, 97.5])
    return float(point), (float(ci[0]), float(ci[1]))
