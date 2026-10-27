import sys
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

def compute_cluster_cis_by_setup(df, pool_policies=['FTWB', 'VTWB'], setup_times=[30.0, 60.0]):
    t_crit = stats.t.ppf(0.975, df=29)
    rows = []
    for st in setup_times:
        sub = df[df['setup_time'] == st]
        diffs = []
        c_means = []
        m_means = []
        for r in range(30):
            rep_df = sub[sub['repetition'] == r]
            c_val = rep_df[rep_df['trigger_method'].isin(pool_policies)]['total_late_orders'].mean()
            m_val = rep_df[rep_df['trigger_method'] == 'MPBH']['total_late_orders'].mean()
            diffs.append(c_val - m_val)
            c_means.append(c_val)
            m_means.append(m_val)
        mean_diff = np.mean(diffs)
        se_diff = np.std(diffs, ddof=1) / np.sqrt(30)
        ci_low = mean_diff - t_crit * se_diff
        ci_high = mean_diff + t_crit * se_diff
        mean_c = np.mean(c_means)
        mean_m = np.mean(m_means)
        rel_red = mean_diff / mean_c * 100 if mean_c > 0 else 0
        rows.append({
            'setup_time': st,
            'canonical_pool_mean_tlo': mean_c,
            'mpbh_mean_tlo': mean_m,
            'advantage_diff': mean_diff,
            'ci95_low': ci_low,
            'ci95_high': ci_high,
            'relative_reduction_pct': rel_red
        })
    return pd.DataFrame(rows)

def compute_cluster_cis_by_lambda(df, pool_policies=['FTWB', 'VTWB'], setup_times=[30.0, 60.0]):
    t_crit = stats.t.ppf(0.975, df=29)
    rows = []
    lambdas = sorted(df['incoming_rate'].unique())
    for st in setup_times:
        st_df = df[df['setup_time'] == st]
        for lam in lambdas:
            sub = st_df[st_df['incoming_rate'] == lam]
            diffs = []
            c_means = []
            m_means = []
            for r in range(30):
                rep_df = sub[sub['repetition'] == r]
                c_val = rep_df[rep_df['trigger_method'].isin(pool_policies)]['total_late_orders'].mean()
                m_val = rep_df[rep_df['trigger_method'] == 'MPBH']['total_late_orders'].mean()
                diffs.append(c_val - m_val)
                c_means.append(c_val)
                m_means.append(m_val)
            mean_diff = np.mean(diffs)
            se_diff = np.std(diffs, ddof=1) / np.sqrt(30)
            ci_low = mean_diff - t_crit * se_diff
            ci_high = mean_diff + t_crit * se_diff
            mean_c = np.mean(c_means)
            mean_m = np.mean(m_means)
            rel_red = mean_diff / mean_c * 100 if mean_c > 0 else 0
            rows.append({
                'setup_time': st,
                'incoming_rate': lam,
                'canonical_pool_mean_tlo': mean_c,
                'mpbh_mean_tlo': mean_m,
                'advantage_diff': mean_diff,
                'ci95_low': ci_low,
                'ci95_high': ci_high,
                'relative_reduction_pct': rel_red
            })
    return pd.DataFrame(rows)

def main():
    path_5k = Path('results/WP6/setup_simulation_raw.csv')
    path_11k = Path('results/WP6/setup_simulation_raw_w11k.csv')

    raw_5k = pd.read_csv(path_5k)
    res_st_5k = compute_cluster_cis_by_setup(raw_5k)
    res_lam_5k = compute_cluster_cis_by_lambda(raw_5k)

    if not path_11k.exists():
        print(f"File {path_11k} does not exist yet. Simulation is still running in background.")
        return

    raw_11k = pd.read_csv(path_11k)
    print(f"Loaded {path_11k}: {len(raw_11k):,} rows.")
    res_st_11k = compute_cluster_cis_by_setup(raw_11k)
    res_lam_11k = compute_cluster_cis_by_lambda(raw_11k)

    # Merge by setup time side by side
    st_merged = res_st_5k.merge(res_st_11k, on='setup_time', suffixes=('_w5k', '_w11k'))
    print("\n" + "=" * 90)
    print("SIDE-BY-SIDE SETUP SENSITIVITY: W = 5,460 s vs W = 11,000 s")
    print("Canonical Pool Definition: FTWB and VTWB only (pooled canonical benchmark)")
    print("Cluster CIs: clustered over 30 replications (df = 29)")
    print("=" * 90)
    for _, r in st_merged.iterrows():
        st = r['setup_time']
        print(f"Setup {st:.0f} s:")
        print(f"  W = 5,460 s : Canonical = {r['canonical_pool_mean_tlo_w5k']:.2f}, MPBH = {r['mpbh_mean_tlo_w5k']:.2f}, Advantage = +{r['advantage_diff_w5k']:.2f} [{r['ci95_low_w5k']:.2f}, {r['ci95_high_w5k']:.2f}] ({r['relative_reduction_pct_w5k']:.2f}%)")
        print(f"  W = 11,000 s: Canonical = {r['canonical_pool_mean_tlo_w11k']:.2f}, MPBH = {r['mpbh_mean_tlo_w11k']:.2f}, Advantage = +{r['advantage_diff_w11k']:.2f} [{r['ci95_low_w11k']:.2f}, {r['ci95_high_w11k']:.2f}] ({r['relative_reduction_pct_w11k']:.2f}%)")
        diff_adv = r['advantage_diff_w11k'] - r['advantage_diff_w5k']
        print(f"  Delta Advantage (W=11k - W=5.4k): {diff_adv:+.2f}")

    lam_merged = res_lam_5k.merge(res_lam_11k, on=['setup_time', 'incoming_rate'], suffixes=('_w5k', '_w11k'))
    print("\n" + "=" * 90)
    print("SIDE-BY-SIDE BY ARRIVAL RATE (LAMBDA): W = 5,460 s vs W = 11,000 s")
    print("Canonical Pool Definition: FTWB and VTWB only")
    print("Cluster CIs: clustered over 30 replications (df = 29)")
    print("=" * 90)
    for _, r in lam_merged.iterrows():
        st = r['setup_time']
        lam = r['incoming_rate']
        print(f"Setup {st:.0f} s, Lambda = {lam:4.1f}:")
        print(f"  W = 5,460 s : Adv = +{r['advantage_diff_w5k']:.2f} [{r['ci95_low_w5k']:.2f}, {r['ci95_high_w5k']:.2f}] ({r['relative_reduction_pct_w5k']:.2f}%)")
        print(f"  W = 11,000 s: Adv = +{r['advantage_diff_w11k']:.2f} [{r['ci95_low_w11k']:.2f}, {r['ci95_high_w11k']:.2f}] ({r['relative_reduction_pct_w11k']:.2f}%)")

    # Save to CSV for reporting artifacts
    st_merged.to_csv('results/WP6/warmup_11k_vs_5k_by_setup.csv', index=False)
    lam_merged.to_csv('results/WP6/warmup_11k_vs_5k_by_lambda.csv', index=False)
    print("\nSaved comparison CSVs to results/WP6/warmup_11k_vs_5k_by_setup.csv and by_lambda.csv")

if __name__ == '__main__':
    main()
