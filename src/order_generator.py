#order_generator.py
import simpy
import numpy as np
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Helper function to format time in HH:MM:SS
def format_time(seconds):
    """
    Format time in seconds to HH:MM:SS format
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string (HH:MM:SS)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Order Generator Process
def generate_orders(env, order_pool, arrival_rate, end_time):
    """
    Generate orders at a specified arrival rate
    
    Args:
        env: SimPy environment
        order_pool: OrderPool to store generated orders
        arrival_rate: Average number of orders per minute
        end_time: Simulation end time in seconds
    """
    customer_id = 1
    total_orders_generated = 0
    
    while True:
        # Generate interarrival time (in seconds)
        interarrival_time = np.random.exponential(scale=60 / arrival_rate)  # Convert rate to seconds
        yield env.timeout(interarrival_time)
        
        # Check if the current time exceeds the simulation end time
        if env.now > end_time:
            break
        
        # Generate due time for the order (30 to 120 minutes from now)
        due_time = env.now + np.random.randint(30 * 60, 120 * 60)  # Convert minutes to seconds
        
        # Format created time and due time
        created_time_str = format_time(env.now)
        due_time_str = format_time(due_time)
        
        # Randomly select the number of items in the order (1 to 10)
        num_items_order = np.random.choice(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            p=[0.3, 0.25, 0.22, 0.17, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]
        )
        
        # Randomly select the items in the order (from 1 to 384)
        items = np.random.choice(
            range(1, 385),
            size=num_items_order,
            replace=False,
            p=[0.007125,0.007125,0.007125,0.007125,0.007125,0.007125,0.007125,0.007125,0.007125,0.007125,0.007125,0.007125,0.007125,0.007125,0.007125,0.007125,0.00475,0.00475,0.00475,0.00475,0.00475,0.00475,0.00475,0.00475,0.00475,0.00475,0.00475,0.00475,0.00475,0.00475,0.00475,0.00475,0.006375,0.006375,0.006375,0.006375,0.006375,0.006375,0.006375,0.006375,0.006375,0.006375,0.006375,0.006375,0.006375,0.006375,0.006375,0.006375,0.00425,0.00425,0.00425,0.00425,0.00425,0.00425,0.00425,0.00425,0.00425,0.00425,0.00425,0.00425,0.00425,0.00425,0.00425,0.00425,0.005625,0.005625,0.005625,0.005625,0.005625,0.005625,0.005625,0.005625,0.005625,0.005625,0.005625,0.005625,0.005625,0.005625,0.005625,0.005625,0.00375,0.00375,0.00375,0.00375,0.00375,0.00375,0.00375,0.00375,0.00375,0.00375,0.00375,0.00375,0.00375,0.00375,0.00375,0.00375,0.0045,0.0045,0.0045,0.0045,0.0045,0.0045,0.0045,0.0045,0.0045,0.0045,0.0045,0.0045,0.0045,0.0045,0.0045,0.0045,0.003,0.003,0.003,0.003,0.003,0.003,0.003,0.003,0.003,0.003,0.003,0.003,0.003,0.003,0.003,0.003,0.003375,0.003375,0.003375,0.003375,0.003375,0.003375,0.003375,0.003375,0.003375,0.003375,0.003375,0.003375,0.003375,0.003375,0.003375,0.003375,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.002625,0.002625,0.002625,0.002625,0.002625,0.002625,0.002625,0.002625,0.002625,0.002625,0.002625,0.002625,0.002625,0.002625,0.002625,0.002625,0.00175,0.00175,0.00175,0.00175,0.00175,0.00175,0.00175,0.00175,0.00175,0.00175,0.00175,0.00175,0.00175,0.00175,0.00175,0.00175,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.00225,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.001875,0.001875,0.001875,0.001875,0.001875,0.001875,0.001875,0.001875,0.001875,0.001875,0.001875,0.001875,0.001875,0.001875,0.001875,0.001875,0.00125,0.00125,0.00125,0.00125,0.00125,0.00125,0.00125,0.00125,0.00125,0.00125,0.00125,0.00125,0.00125,0.00125,0.00125,0.00125,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.0015,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001,0.001125,0.001125,0.001125,0.001125,0.001125,0.001125,0.001125,0.001125,0.001125,0.001125,0.001125,0.001125,0.001125,0.001125,0.001125,0.001125,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.00075,0.0005,0.0005,0.0005,0.0005,0.0005,0.0005,0.0005,0.0005,0.0005,0.0005,0.0005,0.0005,0.0005,0.0005,0.0005,0.0005,0.000375,0.000375,0.000375,0.000375,0.000375,0.000375,0.000375,0.000375,0.000375,0.000375,0.000375,0.000375,0.000375,0.000375,0.000375,0.000375,0.00025,0.00025,0.00025,0.00025,0.00025,0.00025,0.00025,0.00025,0.00025,0.00025,0.00025,0.00025,0.00025,0.00025,0.00025,0.00025]
        )
        
        # Randomly select the quantity of each item (1 to 10)
        quantities = np.random.choice(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            size=num_items_order,
            p=[0.3, 0.25, 0.22, 0.17, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01]
        )
        
        # Create the order as a list of (item ID, quantity) tuples
        order_list = [(item, quantity) for item, quantity in zip(items, quantities)]
        
        # Calculate the total order quantity
        total_quantity = sum(quantity for _, quantity in order_list)
        
        # Add the order to the order pool
        order = {
            "Order ID": f"Cust{customer_id:05}",
            "Created Time": created_time_str,
            "Order List": order_list,
            "Total Item": total_quantity,
            "Due Time": due_time_str,
        }
        
        order_pool.add_order(order)
        total_orders_generated += 1
        
        # Log the order generation
        logger.debug(f"Generated Order ID: {order['Order ID']}, Items: {total_quantity}, Due: {due_time_str}")
        
        # Increment the customer ID
        customer_id += 1
    
    logger.info(f"Order generation completed. Total orders generated: {total_orders_generated}")
