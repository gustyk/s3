import copy
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd

from src.configuration import load_config, DEFAULT_CONFIG
from src.experiment import Scenario, run_simulation
from src.welch import recommend_warmup

def run_welch_task(args):
    setup_val, trig_key, pol_name, rep, p, scen, config_hash = args
    trace = []
    run_simulation(p, scen, rep, config_hash, trace_records=trace)
    for row in trace:
        row['setup_time'] = setup_val
        row['trigger_method'] = pol_name
        row['repetition'] = rep
    return trace

def main():
    config = load_config(DEFAULT_CONFIG)
    base_params = copy.deepcopy(config.values)
    base_params['warmup_seconds'] = 0
    base_params['simulation_time'] = 86400  # 24-h

    setups = [30, 60, 120, 180, 300]
    policies = ['FTWB', 'VTWB', 'MaxPicker', 'MaxCart', 'UrgentPicker', 'UrgentCart', 'SNH', 'MPBH']
    trig_map = {str(v): k for k, v in base_params['trigger_method'].items()}

    tasks = []
    for s in setups:
        for pol in policies:
            t_key = trig_map[pol]
            for rep in range(10):
                p = copy.deepcopy(base_params)
                p['setup_time'] = s
                # lambda = 0.5 (key 1), m = 12, FCFS (key 1), C = 100 (key 1), S-shape (key 1)
                scen = Scenario(1, t_key, 12, 1, 1, 1)
                tasks.append((s, t_key, pol, rep, p, scen, config.sha256))

    print(f'Launching {len(tasks)} Welch simulation runs across 7 workers...')
    t0 = time.time()
    all_traces = []
    with ProcessPoolExecutor(max_workers=7) as executor:
        futures = [executor.submit(run_welch_task, t) for t in tasks]
        done = 0
        for f in as_completed(futures):
            all_traces.extend(f.result())
            done += 1
            if done % 100 == 0 or done == len(tasks):
                print(f'Progress: {done}/{len(tasks)} ({done/len(tasks)*100:.1f}%) in {time.time()-t0:.1f} s')

    df_traces = pd.DataFrame(all_traces)
    
    # Save separate curves by setup time
    Path('results/WP6').mkdir(parents=True, exist_ok=True)
    for s in setups:
        sub_s = df_traces[df_traces['setup_time'] == s]
        sub_s.to_csv(f'results/WP6/welch_curves_{s}s.csv', index=False)
        print(f'Saved results/WP6/welch_curves_{s}s.csv ({len(sub_s)} rows)')

    # Save full combined welch curves with explicit setup column
    df_traces.to_csv('results/WP6/welch_curves_all_setups.csv', index=False)
    print(f'Saved results/WP6/welch_curves_all_setups.csv ({len(df_traces)} rows)')

    # Compute stabilization points per setup x policy
    stab_rows = []
    for s in setups:
        sub_s = df_traces[df_traces['setup_time'] == s]
        diag, summ = recommend_warmup(sub_s, interval_seconds=60.0)
        for _, row in diag.iterrows():
            d = dict(row)
            d['setup_time'] = s
            stab_rows.append(d)

    df_stab = pd.DataFrame(stab_rows)
    cols = ['setup_time'] + [c for c in df_stab.columns if c != 'setup_time']
    df_stab = df_stab[cols]
    df_stab.to_csv('results/WP6/welch_stabilization_points_by_setup.csv', index=False)
    print('Saved results/WP6/welch_stabilization_points_by_setup.csv')
    print(df_stab[['setup_time', 'trigger_method', 'metric', 'recommended_warmup_seconds']].head(16).to_string())

if __name__ == '__main__':
    main()
