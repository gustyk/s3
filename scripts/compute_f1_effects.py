import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path('.')))
from analysis.estimators import stratified_cluster_ci

crossed_df = pd.read_csv('results/WP4/ftwb_mpbh_raw.csv')
ff_df = pd.read_csv('outputs/final-q1-v1/full-factorial/results.csv')

c1 = ff_df[(ff_df['trigger_method'] == 'FTWB') & (ff_df['batching_method'] == 'FCFS')].copy()
c1['cell_label'] = 'FTWB_FCFS'

c2 = ff_df[(ff_df['trigger_method'] == 'FTWB') & (ff_df['batching_method'] == 'EDT')].copy()
c2['cell_label'] = 'FTWB_EDT'

c3 = crossed_df.copy()
c3['cell_label'] = 'FTWB_MPBH'

c4 = ff_df[(ff_df['trigger_method'] == 'MaxPicker') & (ff_df['batching_method'] == 'FCFS')].copy()
c4['cell_label'] = 'IMM_FCFS'

c5 = ff_df[(ff_df['trigger_method'] == 'MaxPicker') & (ff_df['batching_method'] == 'EDT')].copy()
c5['cell_label'] = 'IMM_EDT'

c6 = ff_df[(ff_df['trigger_method'] == 'MPBH') & (ff_df['batching_method'] == 'FCFS')].copy()
c6['cell_label'] = 'IMM_MPBH'

all_cells = pd.concat([c1, c2, c3, c4, c5, c6], ignore_index=True)

pivot = all_cells.pivot_table(
    index=['incoming_rate', 'num_pickers', 'cart_capacity', 'routing_policy', 'repetition'],
    columns='cell_label',
    values='total_late_orders'
).reset_index()

# 1. Timing within composition (IMM - FTWB)
pivot['timing_FCFS'] = pivot['IMM_FCFS'] - pivot['FTWB_FCFS']
pivot['timing_EDT'] = pivot['IMM_EDT'] - pivot['FTWB_EDT']
pivot['timing_MPBH'] = pivot['IMM_MPBH'] - pivot['FTWB_MPBH']

# 2. Composition within timing: at IMM
pivot['comp_IMM_MPBH_FCFS'] = pivot['IMM_MPBH'] - pivot['IMM_FCFS']
pivot['comp_IMM_MPBH_EDT'] = pivot['IMM_MPBH'] - pivot['IMM_EDT']
pivot['comp_IMM_EDT_FCFS'] = pivot['IMM_EDT'] - pivot['IMM_FCFS']

# 3. Composition within timing: at FTWB
pivot['comp_FTWB_MPBH_FCFS'] = pivot['FTWB_MPBH'] - pivot['FTWB_FCFS']
pivot['comp_FTWB_MPBH_EDT'] = pivot['FTWB_MPBH'] - pivot['FTWB_EDT']
pivot['comp_FTWB_EDT_FCFS'] = pivot['FTWB_EDT'] - pivot['FTWB_FCFS']

# 4. Interactions
pivot['inter_MPBH_FCFS'] = pivot['comp_IMM_MPBH_FCFS'] - pivot['comp_FTWB_MPBH_FCFS']
pivot['inter_EDT_FCFS'] = pivot['comp_IMM_EDT_FCFS'] - pivot['comp_FTWB_EDT_FCFS']

cols = [
    ('timing_within_composition', 'FCFS', 'IMM - FTWB | FCFS', 'timing_FCFS'),
    ('timing_within_composition', 'EDT', 'IMM - FTWB | EDT', 'timing_EDT'),
    ('timing_within_composition', 'MPBH', 'IMM - FTWB | MPBH', 'timing_MPBH'),
    ('composition_within_timing', 'IMM', 'MPBH - FCFS | IMM', 'comp_IMM_MPBH_FCFS'),
    ('composition_within_timing', 'IMM', 'MPBH - EDT | IMM', 'comp_IMM_MPBH_EDT'),
    ('composition_within_timing', 'IMM', 'EDT - FCFS | IMM', 'comp_IMM_EDT_FCFS'),
    ('composition_within_timing', 'FTWB', 'MPBH - FCFS | FTWB', 'comp_FTWB_MPBH_FCFS'),
    ('composition_within_timing', 'FTWB', 'MPBH - EDT | FTWB', 'comp_FTWB_MPBH_EDT'),
    ('composition_within_timing', 'FTWB', 'EDT - FCFS | FTWB', 'comp_FTWB_EDT_FCFS'),
]

simple_effects_v2 = []
for effect_type, cond, contrast, col in cols:
    ci = stratified_cluster_ci(pivot, col, stratum_col='incoming_rate', rep_col='repetition')
    est_val = ci['est']
    lo_val = ci['lo']
    hi_val = ci['hi']
    se_val = ci['se']
    df_val = ci['df']
    mean_val = pivot[col].mean()
    print(f"{contrast:25s}: mean={mean_val:.2f}, est={est_val:.2f} [{lo_val:.2f}, {hi_val:.2f}], se={se_val:.4f}, df={df_val:.1f}")
    simple_effects_v2.append({
        'type': effect_type,
        'condition': cond,
        'contrast': contrast,
        'estimate': est_val,
        'ci95_low': lo_val,
        'ci95_high': hi_val,
        'se': se_val,
        'df': df_val
    })

interactions_v2 = []
for name, col in [('inter_MPBH_FCFS', 'inter_MPBH_FCFS'), ('inter_EDT_FCFS', 'inter_EDT_FCFS')]:
    ci = stratified_cluster_ci(pivot, col, stratum_col='incoming_rate', rep_col='repetition')
    est_val = ci['est']
    lo_val = ci['lo']
    hi_val = ci['hi']
    se_val = ci['se']
    df_val = ci['df']
    mean_val = pivot[col].mean()
    print(f"{name:25s}: mean={mean_val:.2f}, est={est_val:.2f} [{lo_val:.2f}, {hi_val:.2f}], se={se_val:.4f}, df={df_val:.1f}")
    interactions_v2.append({
        'interaction': name,
        'estimate': est_val,
        'ci95_low': lo_val,
        'ci95_high': hi_val,
        'se': se_val,
        'df': df_val
    })

Path('results/WP4').mkdir(parents=True, exist_ok=True)
pd.DataFrame(simple_effects_v2).to_csv('results/WP4/simple_effects_v2.csv', index=False)
pd.DataFrame(interactions_v2).to_csv('results/WP4/interactions_v2.csv', index=False)
print("Saved results/WP4/simple_effects_v2.csv and results/WP4/interactions_v2.csv successfully.")
