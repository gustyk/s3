import copy
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
import numpy as np

from src.configuration import load_config, DEFAULT_CONFIG
from src.experiment import Scenario, run_simulation
from src.routing import calculate_total_time
import src.trigger_method as tm
import src.travel_surrogate as ts

def run_instrumentation_task(args):
    lam, m, c, rout_name, rout_key, rep, base_params, config_hash = args
    p = copy.deepcopy(base_params)
    
    # Track decision mismatches for this run
    run_decisions = []
    
    orig_predicted_late = tm._predicted_late_count
    def logged_predicted_late(env, orders, r_name, params):
        surr_late = orig_predicted_late(env, orders, r_name, params)
        strat = 1 if r_name in {'Traversal', 'S-shape'} else 2
        items = [(int(item), int(qty)) for o in orders for item, qty in o['Order List']]
        exact_trip = calculate_total_time(items, strat, params)
        completion = float(env.now) + exact_trip
        exact_late = sum(completion > tm._due_seconds(order) for order in orders)
        run_decisions.append({
            'incoming_rate': lam,
            'num_pickers': m,
            'cart_capacity': c,
            'routing_policy': rout_name,
            'repetition': rep,
            'surrogate_late': surr_late,
            'exact_late': exact_late,
            'mismatch': int(surr_late != exact_late),
            'order_count': len(orders)
        })
        return surr_late

    tm._predicted_late_count = logged_predicted_late
    order_records = []
    
    # Trigger 8 is MPBH, FCFS key is 1
    rate_map = {float(v): k for k, v in base_params['incoming_rate'].items()}
    cart_map = {int(v): k for k, v in base_params['cart_capacity'].items()}
    
    scen = Scenario(rate_map[lam], 8, m, 1, cart_map[c], rout_key)
    try:
        res = run_simulation(p, scen, rep, config_hash, order_records=order_records)
    finally:
        tm._predicted_late_count = orig_predicted_late

    total_evals = len(run_decisions)
    mismatches = sum(d['mismatch'] for d in run_decisions)
    
    # Released orders past due time at release
    past_due_releases = sum(1 for o in order_records if o.get('batch_release_seconds') and float(o['batch_release_seconds']) > float(o['due_seconds']))
    total_orders = len(order_records)

    return {
        'incoming_rate': lam,
        'num_pickers': m,
        'cart_capacity': c,
        'routing_policy': rout_name,
        'repetition': rep,
        'total_decisions': total_evals,
        'decision_mismatches': mismatches,
        'total_late_orders': res['total_late_orders'],
        'released_orders_past_due': past_due_releases,
        'total_orders': total_orders,
        'run_decisions': run_decisions
    }

def main():
    config = load_config(DEFAULT_CONFIG)
    base_params = copy.deepcopy(config.values)

    lambdas = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
    pickers = list(range(1, 13))  # 1 to 12
    cart_capacities = [100, 150, 200]
    routings = [('S-shape', 1), ('Largest Gap', 2)]
    reps = [0, 1, 2]  # 3 reps

    # Total cells: 6 * 12 * 3 * 2 = 432 cells
    # Total runs: 432 * 3 = 1,296 runs
    tasks = []
    for lam in lambdas:
        for m in pickers:
            for c in cart_capacities:
                for r_name, r_key in routings:
                    for rep in reps:
                        tasks.append((lam, m, c, r_name, r_key, rep, base_params, config.sha256))

    print(f"Launching {len(tasks)} MPBH instrumentation runs (432 unique cells x 3 reps) across 7 workers...")
    t0 = time.time()
    
    run_summaries = []
    all_decision_records = []
    with ProcessPoolExecutor(max_workers=7) as executor:
        futures = [executor.submit(run_instrumentation_task, t) for t in tasks]
        done = 0
        for f in as_completed(futures):
            res = f.result()
            all_decision_records.extend(res.pop('run_decisions'))
            run_summaries.append(res)
            done += 1
            if done % 200 == 0 or done == len(tasks):
                print(f"Progress: {done}/{len(tasks)} ({done/len(tasks)*100:.1f}%) in {time.time()-t0:.1f} s")

    Path('results/WP7').mkdir(parents=True, exist_ok=True)
    df_runs = pd.DataFrame(run_summaries)
    df_runs.to_csv('results/WP7/mpbh_1296_runs_instrumentation.csv', index=False)
    print("Saved results/WP7/mpbh_1296_runs_instrumentation.csv")

    # Mismatch counts by lambda, m, and routing
    df_decisions = pd.DataFrame(all_decision_records)
    mismatch_by_strata = df_decisions.groupby(['incoming_rate', 'num_pickers', 'routing_policy']).agg(
        total_evaluations=('mismatch', 'count'),
        mismatches=('mismatch', 'sum'),
        mismatch_rate_pct=('mismatch', lambda x: np.mean(x) * 100)
    ).reset_index()
    mismatch_by_strata.to_csv('results/WP7/oracle_decision_mismatch.csv', index=False)
    print("Saved results/WP7/oracle_decision_mismatch.csv")

    # Overall mismatch by routing
    rout_agg = df_decisions.groupby('routing_policy').agg(
        total_evaluations=('mismatch', 'count'),
        mismatches=('mismatch', 'sum'),
        mismatch_rate_pct=('mismatch', lambda x: np.mean(x) * 100)
    ).reset_index()
    print("\nDecision Mismatches by Routing:")
    print(rout_agg.to_string(index=False))

    # Positive control experiment with +/- 60 s bias
    print("\nRunning positive controls (+/- 60 s synthetic bias on travel surrogate)...")
    ctrl_records = []
    # Test on a representative subset of 72 cells across all lambdas and routings
    for lam in [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]:
        for m in [2, 6, 12]:
            for c in [150]:
                for r_name, r_key in routings:
                    rate_map = {float(v): k for k, v in base_params['incoming_rate'].items()}
                    cart_map = {int(v): k for k, v in base_params['cart_capacity'].items()}
                    scen = Scenario(rate_map[lam], 8, m, 1, cart_map[c], r_key)
                    
                    # Unbiased
                    res_base = run_simulation(base_params, scen, 0, config.sha256)
                    
                    # +60s bias
                    orig_est = ts.estimate_trip_seconds
                    ts.estimate_trip_seconds = lambda orders, r, p: orig_est(orders, r, p) + 60.0
                    res_plus = run_simulation(base_params, scen, 0, config.sha256)
                    
                    # -60s bias
                    ts.estimate_trip_seconds = lambda orders, r, p: max(0.0, orig_est(orders, r, p) - 60.0)
                    res_minus = run_simulation(base_params, scen, 0, config.sha256)
                    ts.estimate_trip_seconds = orig_est
                    
                    ctrl_records.append({
                        'incoming_rate': lam,
                        'num_pickers': m,
                        'cart_capacity': c,
                        'routing_policy': r_name,
                        'base_tlo': res_base['total_late_orders'],
                        'plus60_tlo': res_plus['total_late_orders'],
                        'minus60_tlo': res_minus['total_late_orders'],
                        'delta_plus': res_plus['total_late_orders'] - res_base['total_late_orders'],
                        'delta_minus': res_minus['total_late_orders'] - res_base['total_late_orders']
                    })

    df_ctrl = pd.DataFrame(ctrl_records)
    mean_d_plus = df_ctrl['delta_plus'].mean()
    se_plus = df_ctrl['delta_plus'].std(ddof=1) / np.sqrt(len(df_ctrl))
    ci_plus = [mean_d_plus - 1.96 * se_plus, mean_d_plus + 1.96 * se_plus]

    mean_d_minus = df_ctrl['delta_minus'].mean()
    se_minus = df_ctrl['delta_minus'].std(ddof=1) / np.sqrt(len(df_ctrl))
    ci_minus = [mean_d_minus - 1.96 * se_minus, mean_d_minus + 1.96 * se_minus]

    print(f"+60s positive control: mean Delta TLO = {mean_d_plus:.3f} [95% CI: {ci_plus[0]:.3f}, {ci_plus[1]:.3f}]")
    print(f"-60s positive control: mean Delta TLO = {mean_d_minus:.3f} [95% CI: {ci_minus[0]:.3f}, {ci_minus[1]:.3f}]")

    summary_ctrl = pd.DataFrame([
        {'control': '+60s travel bias', 'mean_delta_tlo': mean_d_plus, 'ci95_lower': ci_plus[0], 'ci95_upper': ci_plus[1]},
        {'control': '-60s travel bias', 'mean_delta_tlo': mean_d_minus, 'ci95_lower': ci_minus[0], 'ci95_upper': ci_minus[1]}
    ])
    summary_ctrl.to_csv('results/WP7/positive_control_summary.csv', index=False)
    df_ctrl.to_csv('results/WP7/positive_control_cells.csv', index=False)
    print("Saved positive control CSVs to results/WP7/")

if __name__ == '__main__':
    main()
