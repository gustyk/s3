"""
Update Scope B Head-to-Head tables with class-tuned VTWB variants:
- VTWB class-tuned by lambda (VTWB_class_lambda)
- VTWB class-tuned by lambda x group (VTWB_class_lam_grp)
- Also compute pooled class-tuned variant (or class-tuned pooled with FTWB F5)
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

def compute_row(slice_val, var_name, comp_df, mpbh_df, slice_col=None):
    if slice_col is not None:
        c_sub = comp_df[comp_df[slice_col] == slice_val].sort_values(['incoming_rate', 'num_pickers', 'cart_capacity', 'routing_policy', 'batching_method', 'repetition']).reset_index(drop=True)
        m_sub = mpbh_df[mpbh_df[slice_col] == slice_val].sort_values(['incoming_rate', 'num_pickers', 'cart_capacity', 'routing_policy', 'batching_method', 'repetition']).reset_index(drop=True)
    else:
        c_sub = comp_df.sort_values(['incoming_rate', 'num_pickers', 'cart_capacity', 'routing_policy', 'batching_method', 'repetition']).reset_index(drop=True)
        m_sub = mpbh_df.sort_values(['incoming_rate', 'num_pickers', 'cart_capacity', 'routing_policy', 'batching_method', 'repetition']).reset_index(drop=True)

    assert len(c_sub) == len(m_sub), f"Length mismatch: {len(c_sub)} vs {len(m_sub)}"

    mpbh_mean_tlo = m_sub['total_late_orders'].mean()
    comp_mean_tlo = c_sub['total_late_orders'].mean()
    delta_tlo = comp_mean_tlo - mpbh_mean_tlo

    # Clustered CI over repetitions (15 clusters: reps 15..29, df=14)
    d = c_sub['total_late_orders'].values - m_sub['total_late_orders'].values
    reps = c_sub['repetition'].values
    rep_means = [d[reps == r].mean() for r in range(15, 30)]
    se = np.std(rep_means, ddof=1) / np.sqrt(15)
    t_val = stats.t.ppf(0.975, df=14)
    ci_low = delta_tlo - t_val * se
    ci_high = delta_tlo + t_val * se

    rel_red = (delta_tlo / comp_mean_tlo * 100) if comp_mean_tlo != 0 else 0.0
    delta_thru = m_sub['throughput_per_hour'].mean() - c_sub['throughput_per_hour'].mean()
    delta_util = m_sub['picker_utility_percent'].mean() - c_sub['picker_utility_percent'].mean()

    # Cohort on-time orders
    m_on_time = (m_sub['generated_orders'] - m_sub['total_late_orders']).mean()
    m_on_time_pct = (m_on_time / m_sub['generated_orders'].mean() * 100)

    return {
        'slice': slice_val,
        'competitor_variant': var_name,
        'mpbh_mean_tlo': mpbh_mean_tlo,
        'competitor_mean_tlo': comp_mean_tlo,
        'delta_tlo_abs (comp - mpbh)': delta_tlo,
        'ci95_low': ci_low,
        'ci95_high': ci_high,
        'mpbh_relative_reduction_pct': rel_red,
        'delta_throughput (mpbh - comp)': delta_thru,
        'delta_utility_pp (mpbh - comp)': delta_util,
        'mpbh_on_time_orders_per_run': m_on_time,
        'mpbh_on_time_pct_of_N': m_on_time_pct
    }

def main():
    print("Loading datasets...")
    fact = pd.read_csv('outputs/final-q1-v1/full-factorial/results.csv')
    scen_cols = ['incoming_rate', 'num_pickers', 'cart_capacity', 'routing_policy', 'batching_method', 'repetition']
    
    mpbh = fact[(fact['trigger_method'] == 'MPBH') & (fact['repetition'] >= 15)].drop_duplicates(subset=scen_cols).copy()
    
    # Load regimes to map band and cleared
    regimes = pd.read_csv('results/WP2/cell_regimes_v2.csv')
    cell_cols = ['incoming_rate', 'num_pickers', 'cart_capacity', 'routing_policy', 'batching_method']
    band_map = dict(zip(zip(regimes['incoming_rate'], regimes['num_pickers'], regimes['cart_capacity'], regimes['routing_policy']), regimes['rho_lb_band']))
    cleared_map = dict(zip(zip(regimes['incoming_rate'], regimes['num_pickers'], regimes['cart_capacity'], regimes['routing_policy'], regimes['batching_method']), regimes['cleared']))

    def add_meta(df):
        # Add picker group
        def get_grp(m):
            if m <= 4: return '1-4'
            elif m <= 8: return '5-8'
            else: return '9-12'
        df['m_group'] = df['num_pickers'].apply(get_grp)
        # Add band
        keys_band = list(zip(df['incoming_rate'], df['num_pickers'], df['cart_capacity'], df['routing_policy']))
        df['rho_lb_band'] = [band_map.get(k, '<0.7') for k in keys_band]
        # Cleared flag from cell_regimes_v2
        keys_cleared = list(zip(df['incoming_rate'], df['num_pickers'], df['cart_capacity'], df['routing_policy'], df['batching_method']))
        df['is_cleared'] = [cleared_map.get(k, False) for k in keys_cleared]
        return df

    mpbh = add_meta(mpbh)

    class_vtwb = pd.read_csv('results/WP5/held_out_class_tuned_vtwb_raw.csv')
    v_lam = add_meta(class_vtwb[class_vtwb['variant'] == 'VTWB_class_lambda'].copy())
    v_grp = add_meta(class_vtwb[class_vtwb['variant'] == 'VTWB_class_lam_grp'].copy())

    new_variants = [
        ('VTWB class-tuned by lambda', v_lam),
        ('VTWB class-tuned by lambda x group', v_grp)
    ]

    # 1. Update overall
    print("Updating overall...")
    df_overall = pd.read_csv('results/WP5/head_to_head_scopeB_overall.csv')
    # Filter out existing if re-running
    df_overall = df_overall[~df_overall['competitor_variant'].isin([v[0] for v in new_variants])]
    rows = []
    for vname, vdf in new_variants:
        rows.append(compute_row('overall', vname, vdf, mpbh))
    df_overall = pd.concat([df_overall, pd.DataFrame(rows)], ignore_index=True)
    df_overall.to_csv('results/WP5/head_to_head_scopeB_overall.csv', index=False)

    # 2. Update by_lambda
    print("Updating by_lambda...")
    df_lambda = pd.read_csv('results/WP5/head_to_head_scopeB_by_lambda.csv')
    df_lambda = df_lambda[~df_lambda['competitor_variant'].isin([v[0] for v in new_variants])]
    rows = []
    for l in [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]:
        for vname, vdf in new_variants:
            rows.append(compute_row(l, vname, vdf, mpbh, slice_col='incoming_rate'))
    df_lambda = pd.concat([df_lambda, pd.DataFrame(rows)], ignore_index=True)
    df_lambda = df_lambda.sort_values(['slice', 'competitor_variant']).reset_index(drop=True)
    df_lambda.to_csv('results/WP5/head_to_head_scopeB_by_lambda.csv', index=False)

    # 3. Update by_group
    print("Updating by_group...")
    df_group = pd.read_csv('results/WP5/head_to_head_scopeB_by_group.csv')
    df_group = df_group[~df_group['competitor_variant'].isin([v[0] for v in new_variants])]
    rows = []
    for g in ['1-4', '5-8', '9-12']:
        for vname, vdf in new_variants:
            rows.append(compute_row(g, vname, vdf, mpbh, slice_col='m_group'))
    df_group = pd.concat([df_group, pd.DataFrame(rows)], ignore_index=True)
    df_group = df_group.sort_values(['slice', 'competitor_variant']).reset_index(drop=True)
    df_group.to_csv('results/WP5/head_to_head_scopeB_by_group.csv', index=False)

    # 4. Update by_band
    print("Updating by_band...")
    df_band = pd.read_csv('results/WP5/head_to_head_scopeB_by_band.csv')
    df_band = df_band[~df_band['competitor_variant'].isin([v[0] for v in new_variants])]
    rows = []
    for b in ['<0.7', '0.7-1', '>=1']:
        for vname, vdf in new_variants:
            rows.append(compute_row(b, vname, vdf, mpbh, slice_col='rho_lb_band'))
    df_band = pd.concat([df_band, pd.DataFrame(rows)], ignore_index=True)
    df_band = df_band.sort_values(['slice', 'competitor_variant']).reset_index(drop=True)
    df_band.to_csv('results/WP5/head_to_head_scopeB_by_band.csv', index=False)

    # 5. Update by_cleared
    print("Updating by_cleared...")
    df_cleared = pd.read_csv('results/WP5/head_to_head_scopeB_by_cleared.csv')
    df_cleared = df_cleared[~df_cleared['competitor_variant'].isin([v[0] for v in new_variants])]
    rows = []
    for c in [False, True]:
        for vname, vdf in new_variants:
            rows.append(compute_row(c, vname, vdf, mpbh, slice_col='is_cleared'))
    df_cleared = pd.concat([df_cleared, pd.DataFrame(rows)], ignore_index=True)
    df_cleared = df_cleared.sort_values(['slice', 'competitor_variant']).reset_index(drop=True)
    df_cleared.to_csv('results/WP5/head_to_head_scopeB_by_cleared.csv', index=False)

    print("All Scope B head-to-head files successfully updated!")

if __name__ == '__main__':
    main()
