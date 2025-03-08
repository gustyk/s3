# main.py
import simpy
import yaml
import csv
import os
import logging
import itertools
import sys

# Import components
from src.order_pool import OrderPool
from src.io_pool import IOPool
from src.order_generator import generate_orders
from src.trigger_method import trigger_method
from src.batching_method import batching_method
from src.routing import calculate_total_time

# Suppress logging
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)

# Function to run a single simulation with specific parameters
def run_simulation(
    env, 
    order_pool, 
    io_pool_instance, 
    arrival_rate, 
    cart_capacity, 
    trigger_type, 
    batching_type, 
    routing_policy, 
    num_pickers, 
    simulation_time,
    trigger_params
):
    # Start order generator process
    env.process(generate_orders(env, order_pool, arrival_rate, simulation_time))
    
    # Start trigger process
    env.process(trigger_method(env, order_pool, cart_capacity, io_pool_instance, trigger_type, batching_type, **trigger_params))
    
    # Process to simulate pickers
    def picker_process(env, picker_id):
        while True:
            # Try to get a batch from io_pool
            batch = io_pool_instance.assign_batch_to_picker(picker_id)
            
            if batch is None:
                # No batch available, wait and try again
                yield env.timeout(1)
                continue
            
            # Calculate picking time based on routing policy
            order_list = []
            for order in batch['orders']:
                order_list.extend([(item, qty) for item, qty in order['Order List']])
            
            route_strategy = 1 if routing_policy == "Traversal" else 2
            trip_time = calculate_total_time(order_list, route_strategy)
            
            # Simulate picking
            yield env.timeout(trip_time)
            
            # Mark batch as completed
            io_pool_instance.complete_batch(picker_id, trip_time)
    
    # Start picker processes
    for i in range(num_pickers):
        picker_id = f"Picker{i+1}"
        env.process(picker_process(env, picker_id))
    
    # Run the simulation
    env.run(until=simulation_time)
    
    # Process remaining orders in order pool for late orders
    for order in order_pool.get_all_orders():
        due_time_str = order['Due Time']
        due_time_parts = list(map(int, due_time_str.split(':')))
        due_time_seconds = due_time_parts[0] * 3600 + due_time_parts[1] * 60 + due_time_parts[2]
        
        if due_time_seconds < simulation_time:
            io_pool_instance.total_late_orders += 1
    
    # Get performance metrics
    stats = io_pool_instance.get_stats()
    
    return {
        'total_orders': stats['total_completed_orders'],
        'total_late_orders': stats['total_late_orders'] + io_pool_instance.check_late_pending_orders(simulation_time),
        'picker_utility': stats['picker_utility']
    }

# Main function to run all simulations
def main():
    # Load parameters from config file
    with open("config/parameters.yaml", "r") as file:
        params = yaml.safe_load(file)
    
    # Prepare output file
    output_file = "simulation_results.csv"
    file_exists = os.path.isfile(output_file)
    
    # Get all possible configurations
    incoming_rates = list(params["incoming_rate"].keys())
    trigger_methods = list(params["trigger_method"].keys())
    num_pickers_options = params["num_pickers_options"]
    batching_methods = list(params["batching_method"].keys())
    cart_capacities = list(params["cart_capacity"].keys())
    routing_policies = list(params["routing_policy"].keys())
    
    # Prepare CSV output
    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['run_id', 'incoming_rate', 'cart_capacity', 'trigger_method', 
                      'batching_method', 'routing_policy', 'num_pickers', 
                      'total_orders', 'total_late_orders', 'picker_utility']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        # Simulation parameters
        simulation_time = params["simulation_time"]
        
        # Set up trigger parameters
        trigger_params = {
            'time_window': params['trigger_parameters']['FTWB_interval'],
            'order_threshold': params['trigger_parameters']['VTWB_threshold'],
            'urgent_threshold': params['trigger_parameters']['Urgent_threshold'],
            'due_window': 30
        }
        
        # Generate all combinations
        total_runs = 0
        total_combinations = (
            len(incoming_rates) * len(trigger_methods) * len(num_pickers_options) * 
            len(batching_methods) * len(cart_capacities) * len(routing_policies) * 30
        )
        
        # Track unique runs to ensure reproducibility
        run_id = 0
        
        # Iterate through all parameter combinations
        for (
            incoming_rate_key, trigger_method_key, num_pickers, 
            batching_method_key, cart_capacity_key, routing_policy_key
        ) in itertools.product(
            incoming_rates, trigger_methods, num_pickers_options, 
            batching_methods, cart_capacities, routing_policies
        ):
            # Run 30 times for each combination
            for repetition in range(30):
                run_id += 1
                
                # Get parameter values
                arrival_rate = params["incoming_rate"][incoming_rate_key]
                trigger_type = params["trigger_method"][trigger_method_key]
                batching_type = params["batching_method"][batching_method_key]
                cart_capacity = params["cart_capacity"][cart_capacity_key]
                routing_policy = params["routing_policy"][routing_policy_key]
                
                # Update trigger parameters
                trigger_params['num_pickers'] = num_pickers
                
                # Initialize SimPy environment
                env = simpy.Environment()
                order_pool = OrderPool()
                io_pool_instance = IOPool(env, num_pickers)
                
                # Run simulation
                results = run_simulation(
                    env, order_pool, io_pool_instance, arrival_rate, cart_capacity, 
                    trigger_type, batching_type, routing_policy, num_pickers, 
                    simulation_time, trigger_params
                )
                
                # Write results to CSV
                writer.writerow({
                    'run_id': run_id,
                    'incoming_rate': arrival_rate,
                    'cart_capacity': cart_capacity,
                    'trigger_method': trigger_type,
                    'batching_method': batching_type,
                    'routing_policy': routing_policy,
                    'num_pickers': num_pickers,
                    'total_orders': results['total_orders'],
                    'total_late_orders': results['total_late_orders'],
                    'picker_utility': results['picker_utility']
                })
                
                # Update and print progress
                total_runs += 1
                if total_runs % 100 == 0:
                    print(f"Progress: {total_runs}/{total_combinations} runs completed")
    
    print("DONE!")

if __name__ == "__main__":
    main()
