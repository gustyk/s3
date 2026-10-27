import sys
import copy
import time
from pathlib import Path
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.configuration import load_config, DEFAULT_CONFIG
from src.experiment import Scenario, run_simulation
from src.routing import calculate_total_time
import src.trigger_method as tm

def exact_trip(orders, r_name, params):
    items = [(int(item), int(qty)) for o in orders for item, qty in o['Order List']]
    strat = 1 if r_name in {'Traversal', 'S-shape'} else 2
    return calculate_total_time(items, strat, params)

def run_single_combined_run(args):
    pol, lam, m, rep, base_params, config_hash = args
    
    # Configure combined revert parameters:
    # W = 0 s, H = 3600 s (observation 0 to 3600), pick time = 3 s, beta = 1
    p = copy.deepcopy(base_params)
    p['simulation_time'] = 3600.0
    p['warmup_seconds'] = 0.0
    p['picking_time_per_item'] = 3.0
    p['trigger_parameters']['Urgent_threshold'] = 1

    rate_map = {float(v): k for k, v in p['incoming_rate'].items()}
    cart_map = {int(v): k for k, v in p['cart_capacity'].items()}
    rout_map = {str(v): k for k, v in p['routing_policy'].items()}
    batch_map = {str(v): k for k, v in p['batching_method'].items()}
    trig_map = {str(v): k for k, v in p['trigger_method'].items()}

    scen = Scenario(rate_map[lam], trig_map[pol], m, batch_map['FCFS'], cart_map[150], rout_map['S-shape'])

    # Patch exact routing for MPBH surrogate
    orig_est = tm.estimate_trip_seconds
    tm.estimate_trip_seconds = exact_trip
    try:
        res = run_simulation(p, scen, rep, config_hash)
    finally:
        tm.estimate_trip_seconds = orig_est

    # Legacy TLO rule: late_completed_orders
    legacy_tlo = res.get('late_completed_orders', 0)
    canonical_tlo = res.get('total_late_orders', 0)

    return {
        'policy': pol,
        'incoming_rate': lam,
        'num_pickers': m,
        'cart_capacity': 150,
        'routing_policy': 'S-shape',
        'batching_method': 'FCFS',
        'repetition': rep,
        'warmup_seconds': 0.0,
        'simulation_time': 3600.0,
        'picking_time_per_item': 3.0,
        'urgency_beta': 1,
        'exact_routing': True,
        'canonical_tlo': canonical_tlo,
        'legacy_tlo': legacy_tlo,
        'completed_orders': res.get('completed_orders', 0),
        'generated_orders': res.get('generated_orders', 0),
        'late_outstanding_orders': res.get('late_outstanding_orders', 0)
    }

def main():
    t0 = time.time()
    print("=" * 70)
    print("STARTING COMBINED REVERT EXPERIMENT")
    print("Configuration: W=0 s, H=3,600 s, pick=3 s, beta=1, exact routing, legacy TLO")
    print("Design: 18 cells x 10 reps x 4 policies = 720 runs")
    print("=" * 70)

    config = load_config(DEFAULT_CONFIG)
    base_params = copy.deepcopy(config.values)

    lambdas = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
    pickers = [2, 6, 12]
    policies = ['FTWB', 'VTWB', 'MaxPicker', 'MPBH']

    tasks = []
    for pol in policies:
        for lam in lambdas:
            for m in pickers:
                for rep in range(10):
                    tasks.append((pol, lam, m, rep, base_params, config.sha256))

    assert len(tasks) == 720, f"Expected 720 tasks, got {len(tasks)}"
    print(f"Prepared {len(tasks)} tasks across 4 policies.")

    out_dir = Path("results/WP0")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "combined_revert_results.csv"

    results = []
    workers = 7
    print(f"Running with {workers} worker processes...")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(run_single_combined_run, t) for t in tasks]
        done = 0
        for f in as_completed(futures):
            res = f.result()
            results.append(res)
            done += 1
            if done % 100 == 0 or done == len(tasks):
                elapsed = time.time() - t0
                print(f"[{done:3d}/{len(tasks)}] runs completed ({done/len(tasks)*100:.1f}%) in {elapsed:.1f} s")

    df = pd.DataFrame(results)
    # Sort for deterministic reporting
    df.sort_values(by=['policy', 'incoming_rate', 'num_pickers', 'repetition'], inplace=True)
    df.to_csv(out_csv, index=False)
    print(f"\nSaved combined revert results to {out_csv}")

    # Analyze and report from output CSV only
    df_out = pd.read_csv(out_csv)
    canon_pool = df_out[df_out['policy'].isin(['FTWB', 'VTWB', 'MaxPicker'])]
    mpbh_pool = df_out[df_out['policy'] == 'MPBH']

    # 1. Under Legacy TLO Rule (late_completed_orders)
    c_leg = canon_pool['legacy_tlo'].mean()
    m_leg = mpbh_pool['legacy_tlo'].mean()
    d_leg = m_leg - c_leg
    rel_leg = (c_leg - m_leg) / c_leg * 100 if c_leg > 0 else 0

    print("\n" + "=" * 70)
    print("REPORT FROM OUTPUT CSV: COMBINED REVERT (LEGACY TLO RULE)")
    print("=" * 70)
    print(f"Canonical Pool Runs:        {len(canon_pool)}")
    print(f"MPBH Runs:                  {len(mpbh_pool)}")
    print(f"Canonical Pool Mean Legacy TLO: {c_leg:.4f}")
    print(f"MPBH Mean Legacy TLO:           {m_leg:.4f}")
    print(f"Delta (MPBH - Canonical):       {d_leg:+.4f}")
    print(f"Relative Reduction:             {rel_leg:.2f}%")

    # By-policy breakdown under Legacy TLO
    print("\nBy-Policy Legacy TLO Mean:")
    for pol in ['FTWB', 'VTWB', 'MaxPicker', 'MPBH']:
        sub = df_out[df_out['policy'] == pol]
        print(f"  {pol:12s}: {sub['legacy_tlo'].mean():.4f}")

    # 2. Under Canonical TLO Definition (total_late_orders = completed late + outstanding overdue)
    c_can = canon_pool['canonical_tlo'].mean()
    m_can = mpbh_pool['canonical_tlo'].mean()
    d_can = m_can - c_can
    rel_can = (c_can - m_can) / c_can * 100 if c_can > 0 else 0

    print("\n" + "=" * 70)
    print("REPORT FROM OUTPUT CSV: COMBINED REVERT (CANONICAL TLO DEFINITION)")
    print("=" * 70)
    print(f"Canonical Pool Mean Canonical TLO: {c_can:.4f}")
    print(f"MPBH Mean Canonical TLO:           {m_can:.4f}")
    print(f"Delta (MPBH - Canonical):          {d_can:+.4f}")
    print(f"Relative Reduction:                {rel_can:.2f}%")

    print("\nBy-Policy Canonical TLO Mean:")
    for pol in ['FTWB', 'VTWB', 'MaxPicker', 'MPBH']:
        sub = df_out[df_out['policy'] == pol]
        print(f"  {pol:12s}: {sub['canonical_tlo'].mean():.4f}")

    print("\nElapsed total time: {:.1f} s".format(time.time() - t0))
    print("=" * 70)

if __name__ == '__main__':
    main()
