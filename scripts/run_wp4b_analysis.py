import subprocess
from pathlib import Path
import pandas as pd
import numpy as np

def get_git_revision_hash() -> str:
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        return "unknown"

def main():
    crossed_file = Path("results/WP4/ftwb_mpbh_raw.csv")
    if not crossed_file.exists():
        print(f"Error: {crossed_file} does not exist.")
        return

    print("Loading simulated FTWB x MPBH results...")
    crossed_df = pd.read_csv(crossed_file)
    print(f"Loaded {len(crossed_df)} rows from crossed execution.")

    print("Loading full-factorial dataset...")
    ff_df = pd.read_csv("outputs/final-q1-v1/full-factorial/results.csv")

    commit_hash = get_git_revision_hash()

    # The 6 cells in the 2 (Timing: FTWB, IMM/MPBH) x 3 (Composition: FCFS, EDT, MPBH) design:
    # 1. FTWB x FCFS
    # 2. FTWB x EDT
    # 3. FTWB x MPBH (newly simulated)
    # 4. IMM x FCFS (MaxPicker / immediate release with FCFS)
    # 5. IMM x EDT (UrgentPicker / immediate release with EDT)
    # 6. IMM x MPBH (canonical MPBH)

    # Note: In full factorial, trigger_method = 'FTWB', 'MaxPicker', 'MPBH', etc.
    # We filter and align each of the 6 cells across all 432 scenarios x 30 replications (12,960 runs per cell)
    
    # Check policies in ff_df
    # 1. FTWB x FCFS
    c1 = ff_df[(ff_df["trigger_method"] == "FTWB") & (ff_df["batching_method"] == "FCFS")].copy()
    c1["cell_label"] = "FTWB x FCFS"
    c1["timing"] = "FTWB"
    c1["composition"] = "FCFS"

    # 2. FTWB x EDT
    c2 = ff_df[(ff_df["trigger_method"] == "FTWB") & (ff_df["batching_method"] == "EDT")].copy()
    c2["cell_label"] = "FTWB x EDT"
    c2["timing"] = "FTWB"
    c2["composition"] = "EDT"

    # 3. FTWB x MPBH
    c3 = crossed_df.copy()
    c3["cell_label"] = "FTWB x MPBH"
    c3["timing"] = "FTWB"
    c3["composition"] = "MPBH"

    # 4. IMM x FCFS
    c4 = ff_df[(ff_df["trigger_method"] == "MaxPicker") & (ff_df["batching_method"] == "FCFS")].copy()
    c4["cell_label"] = "IMM x FCFS"
    c4["timing"] = "IMM"
    c4["composition"] = "FCFS"

    # 5. IMM x EDT
    c5 = ff_df[(ff_df["trigger_method"] == "UrgentPicker") & (ff_df["batching_method"] == "EDT")].copy()
    c5["cell_label"] = "IMM x EDT"
    c5["timing"] = "IMM"
    c5["composition"] = "EDT"

    # 6. IMM x MPBH
    # In full factorial, MPBH runs are present under both FCFS and EDT dummy tags (they are identical)
    # Filter to one batching_method to get exact 432 x 30 = 12,960 runs
    c6 = ff_df[(ff_df["trigger_method"] == "MPBH") & (ff_df["batching_method"] == "FCFS")].copy()
    c6["cell_label"] = "IMM x MPBH"
    c6["timing"] = "IMM"
    c6["composition"] = "MPBH"

    all_cells = pd.concat([c1, c2, c3, c4, c5, c6], ignore_index=True)
    print(f"Combined 6 cells total rows: {len(all_cells)} (expected 6 x 12,960 = 77,760)")

    # 1. Six Cells Table
    six_cells_list = []
    for (label, timing, comp), grp in all_cells.groupby(["cell_label", "timing", "composition"]):
        six_cells_list.append({
            "cell_label": label,
            "timing_policy": timing,
            "composition_rule": comp,
            "mean_tlo": grp["total_late_orders"].mean(),
            "std_tlo": grp["total_late_orders"].std(),
            "median_tlo": grp["total_late_orders"].median(),
            "total_runs": len(grp),
            "commit_hash": commit_hash
        })
    six_df = pd.DataFrame(six_cells_list)
    six_df = six_df.sort_values("mean_tlo")
    six_df.to_csv("results/WP4/six_cells_full.csv", index=False)
    print("Saved results/WP4/six_cells_full.csv")

    # 2. ANOVA and Simple Effects / Interactions
    # Group by (scenario, repetition) block to do exact paired contrasts
    pivot = all_cells.pivot_table(
        index=["incoming_rate", "num_pickers", "cart_capacity", "routing_policy", "repetition"],
        columns="cell_label",
        values="total_late_orders"
    ).reset_index()

    # Simple timing effect at each composition:
    # Timing effect = FTWB - IMM (positive means IMM is better, i.e. lower TLO)
    diff_fcfs = pivot["FTWB x FCFS"] - pivot["IMM x FCFS"]
    diff_edt = pivot["FTWB x EDT"] - pivot["IMM x EDT"]
    diff_mpbh = pivot["FTWB x MPBH"] - pivot["IMM x MPBH"]

    # Simple composition effect at each timing:
    # FCFS -> MPBH:
    comp_at_ftwb = pivot["FTWB x FCFS"] - pivot["FTWB x MPBH"]
    comp_at_imm = pivot["IMM x FCFS"] - pivot["IMM x MPBH"]

    # Two-path decomposition:
    # Path A: Start at FTWB x FCFS -> change timing to IMM (IMM x FCFS) -> change composition to MPBH (IMM x MPBH)
    step1_A = pivot["FTWB x FCFS"] - pivot["IMM x FCFS"]
    step2_A = pivot["IMM x FCFS"] - pivot["IMM x MPBH"]

    # Path B: Start at FTWB x FCFS -> change composition to MPBH (FTWB x MPBH) -> change timing to IMM (IMM x MPBH)
    step1_B = pivot["FTWB x FCFS"] - pivot["FTWB x MPBH"]
    step2_B = pivot["FTWB x MPBH"] - pivot["IMM x MPBH"]

    total_delta = pivot["FTWB x FCFS"] - pivot["IMM x MPBH"]

    path_df = pd.DataFrame([
        {
            "path": "Path A (Timing First)",
            "step1_timing_diff": step1_A.mean(),
            "step2_composition_diff": step2_A.mean(),
            "total_reduction": total_delta.mean(),
            "timing_share_pct": (step1_A.mean() / total_delta.mean()) * 100.0,
            "composition_share_pct": (step2_A.mean() / total_delta.mean()) * 100.0
        },
        {
            "path": "Path B (Composition First)",
            "step1_composition_diff": step1_B.mean(),
            "step2_timing_diff": step2_B.mean(),
            "total_reduction": total_delta.mean(),
            "composition_share_pct": (step1_B.mean() / total_delta.mean()) * 100.0,
            "timing_share_pct": (step2_B.mean() / total_delta.mean()) * 100.0
        }
    ])
    path_df.to_csv("results/WP4/two_path_full.csv", index=False)
    print("Saved results/WP4/two_path_full.csv")

    # Shapley attribution (average of orderings):
    shapley_timing = (step1_A.mean() + step2_B.mean()) / 2.0
    shapley_comp = (step2_A.mean() + step1_B.mean()) / 2.0
    shapley_df = pd.DataFrame([{
        "shapley_timing_reduction": shapley_timing,
        "shapley_composition_reduction": shapley_comp,
        "shapley_timing_share_pct": (shapley_timing / total_delta.mean()) * 100.0,
        "shapley_comp_share_pct": (shapley_comp / total_delta.mean()) * 100.0,
        "shapley_ratio_timing_to_comp": shapley_timing / shapley_comp if shapley_comp > 0 else np.nan,
        "commit_hash": commit_hash
    }])
    shapley_df.to_csv("results/WP4/shapley_full.csv", index=False)
    print("Saved results/WP4/shapley_full.csv")

    print("\n--- Full Crossed Attribution Summary ---")
    print(six_df[["cell_label", "mean_tlo", "std_tlo"]])
    print(path_df)
    print(shapley_df)

if __name__ == "__main__":
    main()
