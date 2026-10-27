import gzip
import pandas as pd

W = 5460.0
H = 34260.0

with gzip.open('outputs/final-q1-v1/full-factorial/orders.csv.gz', 'rt') as f:
    header = f.readline().strip().split(',')
    run_idx = header.index('run_uuid')
    arr_idx = header.index('arrival_seconds')
    due_idx = header.index('due_seconds')
    comp_idx = header.index('completion_seconds')
    meas_idx = header.index('measurement_eligible')
    late_idx = header.index('late_completed')
    over_idx = header.index('overdue_outstanding')
    pol_idx = header.index('trigger_method')
    rate_idx = header.index('incoming_rate')
    
    selected_runs = {}
    # Scan only first 300,000 lines (contains ~50 complete runs)
    for idx, line in enumerate(f):
        if idx >= 300000:
            break
        parts = line.strip().split(',')
        ruid = parts[run_idx]
        if ruid not in selected_runs:
            if len(selected_runs) < 24:
                selected_runs[ruid] = {
                    'policy': parts[pol_idx],
                    'rate': float(parts[rate_idx]),
                    'all_eligible': 0,
                    'all_late': 0,
                    'cohort_orders': 0,
                    'cohort_late': 0
                }
        
        if ruid in selected_runs:
            entry = selected_runs[ruid]
            arr = float(parts[arr_idx])
            due = float(parts[due_idx])
            comp = parts[comp_idx]
            meas = parts[meas_idx] == 'True'
            is_late = (parts[late_idx] == 'True') or (parts[over_idx] == 'True')
            
            # All arrivals in [0, H) with due < H:
            if arr < H and due < H:
                entry['all_eligible'] += 1
                if not comp or float(comp) > due:
                    entry['all_late'] += 1
                    
            # Cohort orders:
            if meas:
                entry['cohort_orders'] += 1
                if is_late:
                    entry['cohort_late'] += 1

rows = []
for ruid, d in selected_runs.items():
    ratio = d['all_late'] / d['cohort_late'] if d['cohort_late'] > 0 else None
    rows.append({
        'run_uuid': ruid,
        'policy': d['policy'],
        'rate': d['rate'],
        'cohort_N': d['cohort_orders'],
        'cohort_late': d['cohort_late'],
        'all_eligible': d['all_eligible'],
        'all_late': d['all_late'],
        'ratio_all_to_cohort': ratio
    })

df_sample = pd.DataFrame(rows)
df_sample.to_csv('results/WP8/sample_24_runs_check.csv', index=False)
print("=== STRATIFIED SAMPLE OF 24 RUNS AUDIT ===")
print(df_sample.to_string())
