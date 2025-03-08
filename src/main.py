# main.py
import simpy
import yaml
import csv
import os
import logging
import numpy as np
from datetime import datetime, timedelta

# Import components
from src.order_pool import OrderPool
from src.io_pool import IOPool  # Using the improved IOPool class
from src.order_generator import generate_orders
from src.trigger_method import trigger_method
from src.batching_method import batching_method
from src.routing import calculate_total_time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    
    # Get selected configuration
    selected_config = params["SELECTED_CONFIGURATION"]
    arrival_rate = params["incoming_rate"][selected_config["incoming_rate"]]
    cart_capacity = params["cart_capacity"][selected_config["cart_capacity"]]
    trigger_type = params["trigger_method"][selected_config["trigger_method"]]
    batching_type = params["batching_method"][selected_config["batching_method"]]
    routing_policy = params["routing_policy"][selected_config["routing_policy"]]
    
    # Get number of pickers
    num_pickers = selected_config["num_pickers_options"]
    simulation_time = params["simulation_time"]
    
    # Set up trigger parameters
    trigger_params = {
        'time_window': params['trigger_parameters']['FTWB_interval'],
        'order_threshold': params['trigger_parameters']['VTWB_threshold'],
        'urgent_threshold': params['trigger_parameters']['Urgent_threshold'],
        'num_pickers': num_pickers,
        'due_window': 30  # Default value for DTWB trigger
    }
    
    # Set up CSV output file
    output_file = "simulation_results.csv"
    file_exists = os.path.isfile(output_file)
    
    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['incoming_rate', 'cart_capacity', 'trigger_method', 'batching_method', 
                      'routing_policy', 'num_pickers', 'total_orders', 'total_late_orders', 'picker_utility']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        # Run simulation with selected parameters
        logger.info(f"Starting simulation with: AR={arrival_rate}, CC={cart_capacity}, TM={trigger_type}, BM={batching_type}, RP={routing_policy}, NP={num_pickers}")
        
        # Initialize SimPy environment
        env = simpy.Environment()  # Starting at time 0 (00:00:00)
        order_pool = OrderPool()
        io_pool_instance = IOPool(env, num_pickers)  # Pass env and picker capacity
        
        # Run simulation
        results = run_simulation(
            env, order_pool, io_pool_instance, arrival_rate, cart_capacity, 
            trigger_type, batching_type, routing_policy, num_pickers, simulation_time,
            trigger_params
        )
        
        if results:
            # Write results to CSV
            writer.writerow({
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
            
            # Print results
            logger.info(f"Simulation completed with parameters:")
            logger.info(f"  Arrival Rate: {arrival_rate} orders/min")
            logger.info(f"  Cart Capacity: {cart_capacity}")
            logger.info(f"  Trigger Method: {trigger_type}")
            logger.info(f"  Batching Method: {batching_type}")
            logger.info(f"  Routing Policy: {routing_policy}")
            logger.info(f"  Number of Pickers: {num_pickers}")
            logger.info(f"Results:")
            logger.info(f"  Total Orders: {results['total_orders']}")
            logger.info(f"  Total Late Orders: {results['total_late_orders']}")
            logger.info(f"  Picker Utility: {results['picker_utility']:.2f}%")
        else:
            logger.error("Simulation failed to produce results")

if __name__ == "__main__":
    main()
