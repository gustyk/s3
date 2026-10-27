import copy
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
from src.configuration import load_config, DEFAULT_CONFIG
from src.experiment import run_simulation, Scenario

def run_task(item):
    p, scen, rep, chash = item
    res = run_simulation(p, scen, rep, chash)
    return {
        'setup_time': p['setup_time'],
        'incoming_rate': float(p['incoming_rate'][scen.incoming_rate_key]),
        'cart_capacity': int(p['cart_capacity'][scen.cart_key]),
        'routing_policy': p['routing_policy'][scen.routing_key],
        'batching_method': p['batching_method'][scen.batching_key],
        'num_pickers': scen.num_pickers,
        'trigger_method': p['trigger_method'][scen.trigger_key],
        'repetition': 0,
        'total_late_orders': res['total_late_orders'],
        'throughput_per_hour': res['throughput_per_hour'],
        'picker_utility_percent': res['picker_utility_percent'],
        'mean_cart_utilization_percent': res['mean_cart_utilization_percent'],
        'trip_count': res['trip_count'],
        'generated_orders': res['generated_orders'],
        'completed_orders': res['completed_orders'],
        'late_completed_orders': res['late_completed_orders'],
        'late_outstanding_orders': res['late_outstanding_orders']
    }

def main():
    config = load_config(DEFAULT_CONFIG)
    base_params = copy.deepcopy(config.values)

    rate_keys = [1, 2, 3, 4, 5, 6]
    m_vals = [2, 6, 12]
    c_keys = [1, 3] # 100, 200
    trig_keys = [1, 2, 3, 4, 5, 6, 7, 8]
    setups = [30.0, 60.0, 120.0, 300.0]

    tasks = []
    for st in setups:
        p_dict = copy.deepcopy(base_params)
        p_dict['setup_time'] = st
        for rk in rate_keys:
            for m in m_vals:
                for ck in c_keys:
                    for tk in trig_keys:
                        scen = Scenario(incoming_rate_key=rk, trigger_key=tk, num_pickers=m, batching_key=1, cart_key=ck, routing_key=1)
                        tasks.append((p_dict, scen, 0, config.sha256))

    print('Total rep 0 tasks to run for setups 30, 60, 120, 300:', len(tasks))

    results = []
    with ProcessPoolExecutor(max_workers=8) as executor:
        for r in executor.map(run_task, tasks):
            results.append(r)

    df0 = pd.DataFrame(results)
    df0.to_csv('results/WP6/setup_rep0.csv', index=False)
    print('Successfully finished rep 0 for all 4 setups!')

if __name__ == '__main__':
    main()
