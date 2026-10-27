import sys
import copy
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd

from src.configuration import load_config, DEFAULT_CONFIG
from src.experiment import Scenario, run_simulation
from src.routing import calculate_total_time
import src.trigger_method as tm
import src.travel_surrogate as ts

def run_single_task(args):
    factor_name, policy, lam, m, rep, p, scen, use_exact_routing, config_hash = args
    if use_exact_routing:
        orig_est = ts.estimate_trip_seconds
        def exact_trip(orders, r_name, params):
            items = [(int(item), int(qty)) for o in orders for item, qty in o['Order List']]
            strat = 1 if r_name in {'Traversal', 'S-shape'} else 2
            return calculate_total_time(items, strat, params)
        ts.estimate_trip_seconds = exact_trip
        try:
            res = run_simulation(p, scen, rep, config_hash)
        finally:
            ts.estimate_trip_seconds = orig_est
    else:
        res = run_simulation(p, scen, rep, config_hash)
        
    return {
        'factor': factor_name,
        'policy': policy,
        'incoming_rate': lam,
        'num_pickers': m,
        'repetition': rep,
        'total_late_orders': res['total_late_orders'],
        'late_completed_orders': res.get('late_completed_orders', 0),
        'completed_orders': res.get('completed_orders', 0),
        'generated_orders': res.get('generated_orders', 0)
    }

def main():
    config = load_config(DEFAULT_CONFIG)
    base_params = copy.deepcopy(config.values)

    lambdas = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
    pickers = [2, 6, 12]
    cart_cap = 150
    routing = 'S-shape'
    batching = 'FCFS'
    policies = ['FTWB', 'VTWB', 'MPBH', 'MaxPicker']

    rate_map = {float(v): k for k, v in base_params['incoming_rate'].items()}
    cart_map = {int(v): k for k, v in base_params['cart_capacity'].items()}
    rout_map = {str(v): k for k, v in base_params['routing_policy'].items()}
    batch_map = {str(v): k for k, v in base_params['batching_method'].items()}
    trig_map = {str(v): k for k, v in base_params['trigger_method'].items()}

    # 1. Assert bitwise match of baseline from stored full factorial
    df_fact = pd.read_csv('outputs/final-q1-v1/full-factorial/results.csv')
    sub_base = df_fact[
        (df_fact['incoming_rate'].isin(lambdas)) &
        (df_fact['num_pickers'].isin(pickers)) &
        (df_fact['cart_capacity'] == cart_cap) &
        (df_fact['routing_policy'] == routing) &
        (df_fact['batching_method'] == batching) &
        (df_fact['repetition'] < 10) &
        (df_fact['trigger_method'].isin(policies))
    ]
    assert len(sub_base) == 720, f"Expected 720 stored baseline rows, got {len(sub_base)}"
    print("Asserted stored factorial slice has 720 rows.")

    # Spot-check bitwise reproducibility on a sample
    for check_rep in [0, 4, 9]:
        scen_chk = Scenario(rate_map[0.5], trig_map['MPBH'], 2, batch_map['FCFS'], cart_map[150], rout_map['S-shape'])
        res_chk = run_simulation(base_params, scen_chk, check_rep, config.sha256)
        stored_chk = sub_base[
            (sub_base['incoming_rate'] == 0.5) &
            (sub_base['num_pickers'] == 2) &
            (sub_base['trigger_method'] == 'MPBH') &
            (sub_base['repetition'] == check_rep)
        ]['total_late_orders'].values[0]
        assert res_chk['total_late_orders'] == stored_chk, f"Bitwise mismatch: {res_chk['total_late_orders']} != {stored_chk}"
    print("Bitwise regression check PASSED (replications 0, 4, 9 bitwise identical).")

    # Build tasks for the OFAT ladder
    tasks = []
    
    # Factor 1: revert beta -> 1 (MPBH only, 18 cells x 10 reps = 180 runs)
    for lam in lambdas:
        for m in pickers:
            for rep in range(10):
                p = copy.deepcopy(base_params)
                p['urgency_beta'] = 1
                scen = Scenario(rate_map[lam], trig_map['MPBH'], m, batch_map[batching], cart_map[cart_cap], rout_map[routing])
                tasks.append(('revert_beta', 'MPBH', lam, m, rep, p, scen, False, config.sha256))

    # Factor 2: revert pick time -> 3 s (all 4 policies, 180 x 4 = 720 runs)
    for pol in policies:
        for lam in lambdas:
            for m in pickers:
                for rep in range(10):
                    p = copy.deepcopy(base_params)
                    p['picking_time_per_item'] = 3
                    scen = Scenario(rate_map[lam], trig_map[pol], m, batch_map[batching], cart_map[cart_cap], rout_map[routing])
                    tasks.append(('revert_pick_time', pol, lam, m, rep, p, scen, False, config.sha256))

    # Factor 3: revert warm-up W -> 0 (all 4 policies, 720 runs)
    for pol in policies:
        for lam in lambdas:
            for m in pickers:
                for rep in range(10):
                    p = copy.deepcopy(base_params)
                    p['warmup_seconds'] = 0
                    scen = Scenario(rate_map[lam], trig_map[pol], m, batch_map[batching], cart_map[cart_cap], rout_map[routing])
                    tasks.append(('revert_warmup', pol, lam, m, rep, p, scen, False, config.sha256))

    # Factor 4: revert horizon H -> 3,600 s (all 4 policies, 720 runs)
    for pol in policies:
        for lam in lambdas:
            for m in pickers:
                for rep in range(10):
                    p = copy.deepcopy(base_params)
                    p['simulation_time'] = 3600
                    scen = Scenario(rate_map[lam], trig_map[pol], m, batch_map[batching], cart_map[cart_cap], rout_map[routing])
                    tasks.append(('revert_horizon', pol, lam, m, rep, p, scen, False, config.sha256))

    # Factor 5: revert travel surrogate -> exact S-shape routing (MPBH only, 180 runs; competitors do not use travel surrogate)
    for lam in lambdas:
        for m in pickers:
            for rep in range(10):
                p = copy.deepcopy(base_params)
                scen = Scenario(rate_map[lam], trig_map['MPBH'], m, batch_map[batching], cart_map[cart_cap], rout_map[routing])
                tasks.append(('revert_exact_routing', 'MPBH', lam, m, rep, p, scen, True, config.sha256))

    print(f"Launching {len(tasks)} OFAT simulation runs with 7 workers...")
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=7) as executor:
        futures = [executor.submit(run_single_task, t) for t in tasks]
        done = 0
        for f in as_completed(futures):
            results.append(f.result())
            done += 1
            if done % 500 == 0 or done == len(tasks):
                print(f"Progress: {done}/{len(tasks)} ({done/len(tasks)*100:.1f}%) in {time.time()-t0:.1f} s")

    df_ofat_runs = pd.DataFrame(results)
    
    # Print the legacy rule from analysis.py at 50c4298:
    legacy_rule = "Rule in analysis.py at commit 50c4298: df.groupby(factor)['total_late_orders'].mean() where total_late_orders was evaluated without cohort censoring and due allowance [1800, 7200]"
    print("\n" + "="*80)
    print(legacy_rule)
    print("="*80 + "\n")

    # Aggregate the ladder steps:
    # 0. Baseline (Current canonical model from stored factorial)
    canon_base = sub_base[sub_base['trigger_method'].isin(['FTWB', 'VTWB', 'MaxPicker'])]['total_late_orders'].mean()
    mpbh_base = sub_base[sub_base['trigger_method'] == 'MPBH']['total_late_orders'].mean()
    
    # 1. Revert beta -> 1 (MPBH under beta=1, canonical pool unchanged)
    mpbh_beta1 = df_ofat_runs[(df_ofat_runs['factor'] == 'revert_beta') & (df_ofat_runs['policy'] == 'MPBH')]['total_late_orders'].mean()
    canon_beta1 = canon_base

    # 2. Revert pick time -> 3s
    sub_pick = df_ofat_runs[df_ofat_runs['factor'] == 'revert_pick_time']
    canon_pick = sub_pick[sub_pick['policy'].isin(['FTWB', 'VTWB', 'MaxPicker'])]['total_late_orders'].mean()
    mpbh_pick = sub_pick[sub_pick['policy'] == 'MPBH']['total_late_orders'].mean()

    # 3. Revert warmup -> 0s
    sub_warm = df_ofat_runs[df_ofat_runs['factor'] == 'revert_warmup']
    canon_warm = sub_warm[sub_warm['policy'].isin(['FTWB', 'VTWB', 'MaxPicker'])]['total_late_orders'].mean()
    mpbh_warm = sub_warm[sub_warm['policy'] == 'MPBH']['total_late_orders'].mean()

    # 4. Revert horizon -> 3600s
    sub_horiz = df_ofat_runs[df_ofat_runs['factor'] == 'revert_horizon']
    canon_horiz = sub_horiz[sub_horiz['policy'].isin(['FTWB', 'VTWB', 'MaxPicker'])]['total_late_orders'].mean()
    mpbh_horiz = sub_horiz[sub_horiz['policy'] == 'MPBH']['total_late_orders'].mean()

    # 5. Revert travel surrogate -> exact routing
    sub_exact = df_ofat_runs[df_ofat_runs['factor'] == 'revert_exact_routing']
    canon_exact = canon_base
    mpbh_exact = sub_exact[sub_exact['policy'] == 'MPBH']['total_late_orders'].mean()

    # 6. Legacy TLO definition: re-aggregating per-order completed late data (late_completed_orders only)
    canon_legacy = sub_base[sub_base['trigger_method'].isin(['FTWB', 'VTWB', 'MaxPicker'])]['late_completed_orders'].mean()
    mpbh_legacy = sub_base[sub_base['trigger_method'] == 'MPBH']['late_completed_orders'].mean()

    ladder = [
        {
            'step': 0,
            'factor': 'Baseline (current canonical model)',
            'commit': '2846f9a',
            'design': '6 lambdas x 3 m x 1 C (150) x S-shape x FCFS x 10 reps (reps 0-9)',
            'run_count': 720,
            'canonical_pool_TLO': round(canon_base, 2),
            'mpbh_TLO': round(mpbh_base, 2),
            'delta_TLO': round(mpbh_base - canon_base, 2),
            'relative_reduction_pct': round((canon_base - mpbh_base) / canon_base * 100, 2),
            'notes': 'Bitwise verified against outputs/final-q1-v1/full-factorial/results.csv'
        },
        {
            'step': 1,
            'factor': 'Revert beta -> 1',
            'commit': '2846f9a',
            'design': '18 cells x 10 reps MPBH (reps 0-9)',
            'run_count': 180,
            'canonical_pool_TLO': round(canon_beta1, 2),
            'mpbh_TLO': round(mpbh_beta1, 2),
            'delta_TLO': round(mpbh_beta1 - canon_beta1, 2),
            'relative_reduction_pct': round((canon_beta1 - mpbh_beta1) / canon_beta1 * 100, 2),
            'notes': 'Holding canonical pool constant; MPBH evaluated with urgency_beta=1'
        },
        {
            'step': 2,
            'factor': 'Revert pick time -> 3 s',
            'commit': '2846f9a',
            'design': '18 cells x 10 reps x 4 policies',
            'run_count': 720,
            'canonical_pool_TLO': round(canon_pick, 2),
            'mpbh_TLO': round(mpbh_pick, 2),
            'delta_TLO': round(mpbh_pick - canon_pick, 2),
            'relative_reduction_pct': round((canon_pick - mpbh_pick) / canon_pick * 100, 2),
            'notes': 'Item pick service time reverted from 5s to legacy 3s'
        },
        {
            'step': 3,
            'factor': 'Revert warm-up W -> 0 s',
            'commit': '2846f9a',
            'design': '18 cells x 10 reps x 4 policies',
            'run_count': 720,
            'canonical_pool_TLO': round(canon_warm, 2),
            'mpbh_TLO': round(mpbh_warm, 2),
            'delta_TLO': round(mpbh_warm - canon_warm, 2),
            'relative_reduction_pct': round((canon_warm - mpbh_warm) / canon_warm * 100, 2),
            'notes': 'Starting from empty warehouse without Welch transient purge (W=0)'
        },
        {
            'step': 4,
            'factor': 'Revert horizon H -> 3,600 s',
            'commit': '2846f9a',
            'design': '18 cells x 10 reps x 4 policies',
            'run_count': 720,
            'canonical_pool_TLO': round(canon_horiz, 2),
            'mpbh_TLO': round(mpbh_horiz, 2),
            'delta_TLO': round(mpbh_horiz - canon_horiz, 2),
            'relative_reduction_pct': round((canon_horiz - mpbh_horiz) / canon_horiz * 100, 2),
            'notes': 'Simulation horizon truncated to 1 hour (3600s)'
        },
        {
            'step': 5,
            'factor': 'Revert travel surrogate -> exact routing',
            'commit': '2846f9a',
            'design': '18 cells x 10 reps MPBH',
            'run_count': 180,
            'canonical_pool_TLO': round(canon_exact, 2),
            'mpbh_TLO': round(mpbh_exact, 2),
            'delta_TLO': round(mpbh_exact - canon_exact, 2),
            'relative_reduction_pct': round((canon_exact - mpbh_exact) / canon_exact * 100, 2),
            'notes': 'MPBH decision filter using exact S-shape routing tour calculation'
        },
        {
            'step': 6,
            'factor': 'Revert TLO definition -> legacy (analysis.py at 50c4298)',
            'commit': '50c4298',
            'design': 'Re-aggregated baseline (720 runs) using late_completed_orders only',
            'run_count': 720,
            'canonical_pool_TLO': round(canon_legacy, 2),
            'mpbh_TLO': round(mpbh_legacy, 2),
            'delta_TLO': round(mpbh_legacy - canon_legacy, 2),
            'relative_reduction_pct': round((canon_legacy - mpbh_legacy) / canon_legacy * 100, 2),
            'notes': 'Rule: total_late_orders aggregated only over completed orders (late_completed_orders)'
        }
    ]

    out_df = pd.DataFrame(ladder)
    Path("results/WP0").mkdir(parents=True, exist_ok=True)
    out_df.to_csv("results/WP0/change_ladder_ofat.csv", index=False)
    print("Successfully wrote results/WP0/change_ladder_ofat.csv")
    print(out_df.to_string())

if __name__ == '__main__':
    main()
