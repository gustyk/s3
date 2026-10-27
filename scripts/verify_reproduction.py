import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from analysis.estimators import stratified_cluster_ci, stratified_boot_ratio

print("Loading full factorial results...")
df = pd.read_csv("outputs/final-q1-v1/full-factorial/results.csv")

# 1. Mean TLO by policy (Table 4a)
print("\n--- 1. Mean TLO by Policy (Table 4a Target vs Computed) ---")
policy_means = df.groupby("trigger_method")["total_late_orders"].mean().round(2).to_dict()
targets_4a = {
    "FTWB": 2023.15,
    "VTWB": 1981.45,
    "MaxPicker": 1977.70,
    "MaxCart": 1978.41,
    "UrgentCart": 1978.41,
    "UrgentPicker": 1998.91,
    "SNH": 1992.06,
    "MPBH": 1788.83
}
all_4a_pass = True
for pol, tgt in targets_4a.items():
    actual = policy_means.get(pol, np.nan)
    match = np.isclose(actual, tgt, atol=0.01)
    if not match:
        all_4a_pass = False
    print(f"  {pol:12s}: Target={tgt:8.2f}, Actual={actual:8.2f}, Match={match}")

# 2. Pooled canonical benchmark TLO
pooled_canonical = (policy_means["FTWB"] + policy_means["VTWB"]) / 2.0
target_pooled = 2002.30
print(f"\nPooled Canonical Benchmark: Target={target_pooled:.2f}, Actual={pooled_canonical:.2f}, Match={np.isclose(pooled_canonical, target_pooled, atol=0.01)}")

# 3. Paired Contrasts vs Pooled Canonical (Table 5)
print("\n--- 2. Paired Contrasts vs Canonical Benchmark (Table 5) ---")
p = df.pivot_table(
    index=["incoming_rate", "num_pickers", "cart_capacity", "routing_policy", "batching_method", "repetition"],
    columns="trigger_method",
    values="total_late_orders"
).reset_index()

p["canonical_pool"] = (p["FTWB"] + p["VTWB"]) / 2.0

table5_targets = {
    "MPBH": {"est": -213.47, "lo": -214.53, "hi": -212.40, "rel": 10.66},
    "MaxPicker": {"est": -24.59, "lo": -25.10, "hi": -24.09, "rel": 1.23},
    "MaxCart": {"est": -23.88, "lo": -24.38, "hi": -23.39, "rel": 1.19},
    "UrgentCart": {"est": -23.88, "lo": -24.38, "hi": -23.39, "rel": 1.19},
    "UrgentPicker": {"est": -3.39, "lo": -3.66, "hi": -3.11, "rel": 0.17},
    "SNH": {"est": -10.24, "lo": -10.58, "hi": -9.89, "rel": 0.51}
}

t5_results = {}
for pol, tgt in table5_targets.items():
    p["diff"] = p[pol] - p["canonical_pool"]
    res = stratified_cluster_ci(p, "diff", stratum_col="incoming_rate", rep_col="repetition")
    rel_pct = abs(res["est"]) / pooled_canonical * 100.0
    t5_results[pol] = {
        "est": res["est"], "lo": res["lo"], "hi": res["hi"], "se": res["se"], "df": res["df"], "rel": rel_pct
    }
    print(f"  {pol:12s}: Target={tgt['est']:8.2f} [{tgt['lo']:7.2f}, {tgt['hi']:7.2f}] ({tgt['rel']}%) | Actual={res['est']:8.2f} [{res['lo']:7.2f}, {res['hi']:7.2f}] ({rel_pct:.2f}%)")

# 4. Cell winners decomposition
print("\n--- 3. Cell Winners Reproduction (864 cells) ---")
# Each cell is (incoming_rate, num_pickers, cart_capacity, routing_policy, batching_method)
cell_means = df.groupby(["incoming_rate", "num_pickers", "cart_capacity", "routing_policy", "batching_method", "trigger_method"])[["total_late_orders", "throughput_per_hour"]].mean().reset_index()

# Find winner per cell: lowest total_late_orders, tie broken by highest throughput_per_hour
winners = []
for cell_id, g in cell_means.groupby(["incoming_rate", "num_pickers", "cart_capacity", "routing_policy", "batching_method"]):
    best_tlo = g["total_late_orders"].min()
    cand = g[g["total_late_orders"] == best_tlo]
    if len(cand) > 1:
        best_tp = cand["throughput_per_hour"].max()
        cand = cand[cand["throughput_per_hour"] == best_tp]
    winner_pol = cand.iloc[0]["trigger_method"]
    winners.append(winner_pol)

win_counts = pd.Series(winners).value_counts().to_dict()
print(f"Cell winners counts: {win_counts}")
target_wins = {"MPBH": 770, "MaxPicker": 59, "SNH": 31, "MaxCart": 4}
print(f"Target winners:      {target_wins}")
wins_pass = (win_counts == target_wins)
print(f"Winners match exactly: {wins_pass}")

# 5. Beta sweep reproduction (beta=1 vs beta=2)
# Check if beta sweep data exists
beta_results_path = Path("docs/revised-paper-assets/Figure_14_source_final_results.csv")
# Or from outputs/beta-smoke or outputs/beta-sensitivity-pilot-v1
print("\nReproduction summary completed.")
