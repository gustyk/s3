# main.py - Modified with crash recovery capabilities
import simpy
import yaml
import csv
import os
import logging
import sys
import itertools
import time
from collections import Counter

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

# Function to find the highest run_id in the CSV file
def get_highest_run_id(csv_file):
    if not os.path.exists(csv_file):
        return 0
    
    try:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            run_ids = [int(row['run_id']) for row in reader if row['run_id'].isdigit()]
            return max(run_ids) if run_ids else 0
    except Exception as e:
        print(f"Error reading run_ids from CSV: {e}")
        return 0

# Function to get completed combinations from the CSV
def get_completed_combinations(csv_file, expected_run_id_start):
    # Use Counter instead of set to count occurrences
    completed = Counter()
    if not os.path.exists(csv_file):
        return completed
    
    try:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row['run_id']) >= expected_run_id_start:
                    key = (
                        row['trigger_method'],
                        int(row['cart_capacity']),
                        row['batching_method'],
                        row['routing_policy'],
                        int(row['num_pickers'])
                    )
                    completed[key] += 1
    except Exception as e:
        print(f"Error reading completed combinations: {e}")
    
    return completed

# Function to save checkpoint
def save_checkpoint(checkpoint_file, current_run_id):
    with open(checkpoint_file, 'w') as f:
        f.write(str(current_run_id))

# Function to load checkpoint
def load_checkpoint(checkpoint_file):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            try:
                return int(f.read().strip())
            except:
                return None
    return None

# Main function to run only the specified combinations
def main():
    # Load parameters from config file
    with open("config/parameters.yaml", "r") as file:
        params = yaml.safe_load(file)
    
    # Simulation output file
    output_file = "simulation_results.csv"
    
    # Checkpoint file
    checkpoint_file = "simulation_checkpoint.txt"
    
    # Get the base run_id (expected starting point)
    base_run_id = 172801  # Starting point from the original analysis
    
    # Try to load the checkpoint
    checkpoint_run_id = load_checkpoint(checkpoint_file)
    
    # Get the highest run_id from the CSV file
    highest_run_id = get_highest_run_id(output_file)
    
    # Determine the current run_id to start from
    if checkpoint_run_id and checkpoint_run_id > base_run_id:
        # Use checkpoint if it exists and is valid
        current_run_id = checkpoint_run_id
        print(f"Resuming from checkpoint at run_id: {current_run_id}")
    elif highest_run_id >= base_run_id:
        # If there's data in the CSV with higher run_id than our base, start from there
        current_run_id = highest_run_id + 1
        print(f"Resuming from highest CSV run_id: {current_run_id}")
    else:
        # Otherwise start from the base run_id
        current_run_id = base_run_id
        print(f"Starting from base run_id: {current_run_id}")
    
    # Get completed combinations to avoid duplicates
    completed_combinations = get_completed_combinations(output_file, base_run_id)
    print(f"Found {sum(completed_combinations.values())} already completed runs")
    
    # Prepare output file
    file_exists = os.path.isfile(output_file)
    
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
        
        # Get all parameter options for the combinations
        cart_capacity_keys = list(params["cart_capacity"].keys())  # [1, 2, 3]
        batching_method_keys = list(params["batching_method"].keys())  # [1, 2]
        routing_policy_keys = list(params["routing_policy"].keys())  # [1, 2]
        num_pickers_options = params["num_pickers_options"]  # [1, 2, ..., 12]
        
        # We'll run only for incoming_rate_key = 6 and trigger_method_keys = [6, 7]
        incoming_rate_key = 6  # Fixed to 16 orders/min
        trigger_method_keys = [6, 7]  # UrgentCart and DVNS
        
        # Calculate total combinations to run
        combinations_per_trigger = (
            len(cart_capacity_keys) * len(batching_method_keys) * 
            len(routing_policy_keys) * len(num_pickers_options)
        )
        total_combinations = combinations_per_trigger * len(trigger_method_keys) * 30  # 30 repetitions per combination
        
        # Calculate how many rows will be added
        remaining_combinations = total_combinations - sum(completed_combinations.values())
        print(f"Total combinations to run: {total_combinations / 30} (with 30 repetitions each)")
        print(f"Remaining rows to be added: {remaining_combinations}")
        print(f"Starting run_id: {current_run_id}")
        print(f"Expected final run_id: {base_run_id + total_combinations - 1}")
        
        total_runs = 0
        checkpoint_frequency = 100  # Save checkpoint every 100 runs
        
        # Generate and run all combinations
        all_parameter_combinations = list(itertools.product(
            trigger_method_keys,
            cart_capacity_keys, 
            batching_method_keys, 
            routing_policy_keys, 
            num_pickers_options
        ))
        
        # Track time for estimating completion
        start_time = time.time()
        
        # For each combination
        for trigger_method_key, cart_capacity_key, batching_method_key, routing_policy_key, num_pickers in all_parameter_combinations:
            # Get actual parameter values
            arrival_rate = params["incoming_rate"][incoming_rate_key]
            trigger_type = params["trigger_method"][trigger_method_key]
            batching_type = params["batching_method"][batching_method_key]
            cart_capacity = params["cart_capacity"][cart_capacity_key]
            routing_policy = params["routing_policy"][routing_policy_key]
            
            # Check if this combination was already completed
            combo_key = (
                trigger_type,
                cart_capacity,
                batching_type,
                routing_policy,
                num_pickers
            )
            
            # Check if we already have all 30 repetitions for this combo
            if completed_combinations[combo_key] >= 30:
                print(f"Skipping already completed combination: {combo_key}")
                continue
            
            # Calculate how many more repetitions we need
            remaining_repetitions = 30 - completed_combinations[combo_key]
            
            # Run remaining repetitions for this combination
            for repetition in range(remaining_repetitions):
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
                    'run_id': current_run_id,
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
                
                # Update the counter for this combination
                completed_combinations[combo_key] += 1
                
                # Increment run_id
                current_run_id += 1
                total_runs += 1
                
                # Force write to disk
                csvfile.flush()
                os.fsync(csvfile.fileno())
                
                # Save checkpoint at regular intervals
                if total_runs % checkpoint_frequency == 0:
                    save_checkpoint(checkpoint_file, current_run_id)
                    
                    # Calculate and show estimated time remaining
                    elapsed_time = time.time() - start_time
                    runs_per_second = total_runs / elapsed_time
                    remaining_runs = remaining_combinations - total_runs
                    estimated_seconds_remaining = remaining_runs / runs_per_second if runs_per_second > 0 else 0
                    
                    hours, remainder = divmod(estimated_seconds_remaining, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    print(f"Progress: {total_runs}/{remaining_combinations} runs completed ({(total_runs/remaining_combinations)*100:.1f}%)")
                    print(f"Current run_id: {current_run_id}")
                    print(f"Estimated time remaining: {int(hours)}h {int(minutes)}m {int(seconds)}s")
    
    # Final checkpoint
    save_checkpoint(checkpoint_file, current_run_id)
    
    print(f"DONE! Generated {total_runs} additional simulation results rows.")
    print(f"Final run_id: {current_run_id - 1}")
    
    # Remove checkpoint file if completed successfully
    if os.path.exists(checkpoint_file) and current_run_id >= base_run_id + total_combinations:
        os.remove(checkpoint_file)
        print("Checkpoint file removed as simulation completed successfully.")

if __name__ == "__main__":
    main()