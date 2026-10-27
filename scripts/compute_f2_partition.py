import pandas as pd
import numpy as np
from pathlib import Path

df = pd.read_csv("outputs/final-q1-v1/full-factorial/results.csv")
df["n_cohort"] = df["generated_orders"]
df["n_comp_ontime"] = df["completed_orders"] - df["late_completed_orders"]
df["n_comp_late"] = df["late_completed_orders"]
df["n_out_overdue"] = df["late_outstanding_orders"]
df["n_out_notdue"] = df["outstanding_orders"] - df["late_outstanding_orders"]

# 1. Run-mean shares
df["share_comp_ontime_run"] = df["n_comp_ontime"] / df["n_cohort"]
df["share_comp_late_run"] = df["n_comp_late"] / df["n_cohort"]
df["share_out_overdue_run"] = df["n_out_overdue"] / df["n_cohort"]
df["share_out_notdue_run"] = df["n_out_notdue"] / df["n_cohort"]

run_means = df.groupby("trigger_method").agg(
    share_comp_ontime=("share_comp_ontime_run", "mean"),
    share_comp_late=("share_comp_late_run", "mean"),
    share_out_overdue=("share_out_overdue_run", "mean"),
    share_out_notdue=("share_out_notdue_run", "mean")
).reset_index()
run_means.insert(1, "weighting", "run_mean")

# 2. Order-weighted shares
pooled = df.groupby("trigger_method").agg(
    total_N=("n_cohort", "sum"),
    total_comp_ontime=("n_comp_ontime", "sum"),
    total_comp_late=("n_comp_late", "sum"),
    total_out_overdue=("n_out_overdue", "sum"),
    total_out_notdue=("n_out_notdue", "sum")
).reset_index()

order_weighted = pd.DataFrame({
    "trigger_method": pooled["trigger_method"],
    "weighting": "order_weighted",
    "share_comp_ontime": pooled["total_comp_ontime"] / pooled["total_N"],
    "share_comp_late": pooled["total_comp_late"] / pooled["total_N"],
    "share_out_overdue": pooled["total_out_overdue"] / pooled["total_N"],
    "share_out_notdue": pooled["total_out_notdue"] / pooled["total_N"]
})

combined = pd.concat([run_means, order_weighted], ignore_index=True)
combined["sum_check"] = combined["share_comp_ontime"] + combined["share_comp_late"] + combined["share_out_overdue"] + combined["share_out_notdue"]

print("=== RUN-MEAN SHARES ===")
print(run_means.to_string())
print("\n=== ORDER-WEIGHTED SHARES ===")
print(order_weighted.to_string())

out_path = Path("results/WP3/table4d_status_partition_exact.csv")
combined.to_csv(out_path, index=False)
print(f"\nSaved {out_path} successfully.")
