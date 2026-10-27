import sys
import copy
import time
from pathlib import Path
import pandas as pd
import numpy as np

from src.configuration import load_config, DEFAULT_CONFIG
from src.experiment import Scenario, run_simulation
from src.routing import calculate_total_time
import src.trigger_method as tm

def exact_trip(orders, r_name, params):
    items = [(int(item), int(qty)) for o in orders for item, qty in o['Order List']]
    strat = 1 if r_name in {'Traversal', 'S-shape'} else 2
    return calculate_total_time(items, strat, params)

def main():
    config = load_config(DEFAULT_CONFIG)
    base_params = copy.deepcopy(config.values)

    orig_est = tm.estimate_trip_seconds
    rate_map = {float(v): k for k, v in base_params['incoming_rate'].items()}
    cart_map = {int(v): k for k, v in base_params['cart_capacity'].items()}
    rout_map = {str(v): k for k, v in base_params['routing_policy'].items()}
    batch_map = {str(v): k for k, v in base_params['batching_method'].items()}
    trig_map = {str(v): k for k, v in base_params['trigger_method'].items()}

    lambdas = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
    pickers = [2, 6, 12]
    cart_cap = 150
    routing = 'S-shape'
    batching = 'FCFS'

    print("====================================================================")
    print("1. RUNNING OFAT STEP 1 (beta = 1, 180 runs)...")
    print("====================================================================")
    step1_records = []
    first_print_s1 = False
    for lam in lambdas:
        for m in pickers:
            for rep in range(10):
                p = copy.deepcopy(base_params)
                p['trigger_parameters']['Urgent_threshold'] = 1  # Correct parameter name patched!
                scen = Scenario(rate_map[lam], trig_map['MPBH'], m, batch_map[batching], cart_map[cart_cap], rout_map[routing])
                
                if not first_print_s1:
                    def pred_time_logger(orders, r_name, params):
                        val = orig_est(orders, r_name, params)
                        print(f"  [Step 1 Verified Predicted-Completion] {len(orders)} orders, policy={r_name}, predicted_completion_time={val:.2f} s")
                        return val
                    tm.estimate_trip_seconds = pred_time_logger
                    res = run_simulation(p, scen, rep, config.sha256)
                    tm.estimate_trip_seconds = orig_est
                    first_print_s1 = True
                else:
                    res = run_simulation(p, scen, rep, config.sha256)

                step1_records.append({
                    'factor': 'revert_beta',
                    'incoming_rate': lam,
                    'num_pickers': m,
                    'repetition': rep,
                    'total_late_orders': res['total_late_orders']
                })

    df_step1 = pd.DataFrame(step1_records)
    Path("results/WP0").mkdir(parents=True, exist_ok=True)
    df_step1.to_csv("results/WP0/ofat_step1_beta1_results.csv", index=False)
    print(f"Step 1 (beta=1) 180 runs completed. Saved to results/WP0/ofat_step1_beta1_results.csv. Mean MPBH TLO = {df_step1['total_late_orders'].mean():.2f}")

    print("\n====================================================================")
    print("2. RUNNING OFAT STEP 5 (Exact Routing, 180 runs)...")
    print("====================================================================")
    step5_records = []
    first_print_s5 = False
    for lam in lambdas:
        for m in pickers:
            for rep in range(10):
                p = copy.deepcopy(base_params)
                scen = Scenario(rate_map[lam], trig_map['MPBH'], m, batch_map[batching], cart_map[cart_cap], rout_map[routing])
                
                if not first_print_s5:
                    def exact_time_logger(orders, r_name, params):
                        val = exact_trip(orders, r_name, params)
                        print(f"  [Step 5 Verified Predicted-Completion (Exact)] {len(orders)} orders, policy={r_name}, predicted_completion_time={val:.2f} s")
                        return val
                    tm.estimate_trip_seconds = exact_time_logger
                    res = run_simulation(p, scen, rep, config.sha256)
                    tm.estimate_trip_seconds = orig_est
                    first_print_s5 = True
                else:
                    tm.estimate_trip_seconds = exact_trip
                    res = run_simulation(p, scen, rep, config.sha256)
                    tm.estimate_trip_seconds = orig_est

                step5_records.append({
                    'factor': 'revert_exact_routing',
                    'incoming_rate': lam,
                    'num_pickers': m,
                    'repetition': rep,
                    'total_late_orders': res['total_late_orders']
                })

    df_step5 = pd.DataFrame(step5_records)
    Path("results/WP0").mkdir(parents=True, exist_ok=True)
    df_step5.to_csv("results/WP0/ofat_step5_exact_routing_results.csv", index=False)
    print(f"Step 5 (Exact routing) 180 runs completed. Saved to results/WP0/ofat_step5_exact_routing_results.csv. Mean MPBH TLO = {df_step5['total_late_orders'].mean():.2f}")

    print("\n====================================================================")
    print("3. RUNNING ORACLE CHECK (360 runs: S-shape and Largest Gap, surrogate vs oracle)...")
    print("====================================================================")
    oracle_records = []
    first_print_oracle = False
    
    for r_name in ['S-shape', 'Largest Gap']:
        for lam in lambdas:
            for m in pickers:
                for rep in range(10):
                    scen = Scenario(rate_map[lam], trig_map['MPBH'], m, batch_map['FCFS'], cart_map[150], rout_map[r_name])
                    
                    # 1. Surrogate run
                    res_surr = run_simulation(base_params, scen, rep, config.sha256)
                    
                    # 2. Oracle run
                    if not first_print_oracle and r_name == 'Largest Gap':
                        def oracle_time_logger(orders, rn, params):
                            val = exact_trip(orders, rn, params)
                            print(f"  [Oracle Check Verified Predicted-Completion ({r_name})] {len(orders)} orders, policy={rn}, predicted_completion_time={val:.2f} s")
                            return val
                        tm.estimate_trip_seconds = oracle_time_logger
                        res_oracle = run_simulation(base_params, scen, rep, config.sha256)
                        tm.estimate_trip_seconds = orig_est
                        first_print_oracle = True
                    else:
                        tm.estimate_trip_seconds = exact_trip
                        res_oracle = run_simulation(base_params, scen, rep, config.sha256)
                        tm.estimate_trip_seconds = orig_est
                    
                    oracle_records.append({
                        'routing_policy': r_name,
                        'incoming_rate': lam,
                        'num_pickers': m,
                        'repetition': rep,
                        'surrogate_tlo': res_surr['total_late_orders'],
                        'oracle_tlo': res_oracle['total_late_orders'],
                        'delta_tlo': res_oracle['total_late_orders'] - res_surr['total_late_orders']
                    })

    df_oracle = pd.DataFrame(oracle_records)
    Path("results/WP7").mkdir(parents=True, exist_ok=True)
    df_oracle.to_csv("results/WP7/oracle_check_results_rerun.csv", index=False)
    print(f"Oracle check 360 runs completed. Saved to results/WP7/oracle_check_results_rerun.csv")
    for r_name, grp in df_oracle.groupby('routing_policy'):
        mean_d = grp['delta_tlo'].mean()
        identical = (grp['delta_tlo'] == 0).sum()
        print(f"  Policy {r_name:12s}: Mean Delta TLO = {mean_d:+.4f}, Identical runs = {identical}/{len(grp)} ({identical/len(grp)*100:.1f}%)")

    print("\n====================================================================")
    print("4. RUNNING COMBINED REVERT (720 runs: W=0, H=3,600s, pick 3s, beta=1, legacy TLO)...")
    print("====================================================================")
    policies = ['FTWB', 'VTWB', 'MPBH', 'MaxPicker']
    combined_records = []
    
    p_comb = copy.deepcopy(base_params)
    p_comb['simulation_time'] = 3600.0
    p_comb['warmup_time'] = 0.0
    p_comb['observation_start_time'] = 0.0
    p_comb['observation_end_time'] = 3600.0
    p_comb['picking_time_per_item'] = 3.0
    p_comb['trigger_parameters']['Urgent_threshold'] = 1

    for pol in policies:
        for lam in lambdas:
            for m in pickers:
                for rep in range(10):
                    scen = Scenario(rate_map[lam], trig_map[pol], m, batch_map[batching], cart_map[cart_cap], rout_map[routing])
                    res = run_simulation(p_comb, scen, rep, config.sha256)
                    
                    combined_records.append({
                        'policy': pol,
                        'incoming_rate': lam,
                        'num_pickers': m,
                        'repetition': rep,
                        'total_late_orders': res['total_late_orders'],
                        'late_completed_orders': res.get('late_completed_orders', 0),
                        'completed_orders': res.get('completed_orders', 0),
                        'generated_orders': res.get('generated_orders', 0)
                    })

    df_comb = pd.DataFrame(combined_records)
    Path("results/WP0").mkdir(parents=True, exist_ok=True)
    df_comb.to_csv("results/WP0/combined_revert_results.csv", index=False)
    print(f"Combined revert 720 runs completed. Saved to results/WP0/combined_revert_results.csv")
    
    canon_pool = df_comb[df_comb['policy'].isin(['FTWB', 'VTWB', 'MaxPicker'])]
    mpbh_pool = df_comb[df_comb['policy'] == 'MPBH']
    
    # 1. Under Canonical TLO
    c_tlo = canon_pool['total_late_orders'].mean()
    m_tlo = mpbh_pool['total_late_orders'].mean()
    d_tlo = m_tlo - c_tlo
    rel_tlo = (c_tlo - m_tlo) / c_tlo * 100 if c_tlo > 0 else 0
    print(f"\n[Combined Revert - Canonical TLO Definition]")
    print(f"  Canonical Pool Mean TLO: {c_tlo:.2f}")
    print(f"  MPBH Mean TLO:           {m_tlo:.2f}")
    print(f"  Delta TLO:               {d_tlo:.2f}")
    print(f"  Relative Reduction:      {rel_tlo:.2f}%")

    # 2. Under Legacy TLO Mapping (late_completed_orders)
    c_leg = canon_pool['late_completed_orders'].mean()
    m_leg = mpbh_pool['late_completed_orders'].mean()
    d_leg = m_leg - c_leg
    rel_leg = (c_leg - m_leg) / c_leg * 100 if c_leg > 0 else 0
    print(f"\n[Combined Revert - Legacy TLO Mapping (`late_completed_orders`)]")
    print(f"  Canonical Pool Mean TLO: {c_leg:.2f}")
    print(f"  MPBH Mean TLO:           {m_leg:.2f}")
    print(f"  Delta TLO:               {d_leg:.2f}")
    print(f"  Relative Reduction:      {rel_leg:.2f}%")

if __name__ == '__main__':
    main()
