"""Rerun positive control across 36 cells with proper trigger_method module patching."""
import pandas as pd
import numpy as np
from src.configuration import load_config
from src.experiment import Scenario, run_simulation
import src.trigger_method as tm

def main():
    config = load_config()
    base_params = config.values
    
    routings = [('S-shape', 1), ('Largest Gap', 2)]
    ctrl_records = []
    
    tasks = []
    for lam in [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]:
        for m in [2, 6, 12]:
            for c in [150]:
                for r_name, r_key in routings:
                    tasks.append((lam, m, c, r_name, r_key))
                    
    print(f"Total positive control tasks: {len(tasks)}")
    
    rate_map = {float(v): k for k, v in base_params['incoming_rate'].items()}
    cart_map = {int(v): k for k, v in base_params['cart_capacity'].items()}
    
    orig_est = tm.estimate_trip_seconds
    for i, (lam, m, c, r_name, r_key) in enumerate(tasks):
        scen = Scenario(rate_map[lam], 8, m, 1, cart_map[c], r_key)
        
        # Unbiased
        res_base = run_simulation(base_params, scen, 0, config.sha256)
        
        # +60s bias
        tm.estimate_trip_seconds = lambda orders, r, p: orig_est(orders, r, p) + 60.0
        res_plus = run_simulation(base_params, scen, 0, config.sha256)
        
        # -60s bias
        tm.estimate_trip_seconds = lambda orders, r, p: max(0.0, orig_est(orders, r, p) - 60.0)
        res_minus = run_simulation(base_params, scen, 0, config.sha256)
        tm.estimate_trip_seconds = orig_est
        
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
        if (i + 1) % 6 == 0:
            print(f"Completed {i+1}/{len(tasks)} positive control cells")

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
