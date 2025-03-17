# trigger_method.py
from typing import List, Dict, Any
import simpy
import logging
import random
from datetime import datetime, timedelta
from src.order_pool import OrderPool
from src.batching_method import batching_method
from src.io_pool import IOPool
from src.routing import calculate_total_time

# Set up logging
logger = logging.getLogger(__name__)

# Helper function to calculate urgent orders
def calculate_urgent_orders(env, order_pool, routing_policy=1):
    """
    Calculate which orders would be late if processed now.
    
    Args:
        env: SimPy environment for current time
        order_pool: OrderPool instance
        routing_policy: Routing policy (1: Traversal, 2: Largest Gap)
        
    Returns:
        List of urgent orders and count of urgent orders
    """
    all_orders = order_pool.get_all_orders()
    if not all_orders:
        return [], 0
    
    # Combine all orders into a single batch for completion time estimation
    all_items = []
    for order in all_orders:
        all_items.extend([(item, qty) for item, qty in order['Order List']])
    
    # Calculate the total time it would take to pick all orders
    current_time = env.now
    processing_time = calculate_total_time(all_items, routing_policy)
    completion_time = current_time + processing_time
    
    # Check which orders would be late
    urgent_orders = []
    for order in all_orders:
        due_time_str = order['Due Time']
        due_time_parts = list(map(int, due_time_str.split(':')))
        due_time_seconds = due_time_parts[0] * 3600 + due_time_parts[1] * 60 + due_time_parts[2]
        
        if completion_time > due_time_seconds:
            urgent_orders.append(order)
    
    return urgent_orders, len(urgent_orders)

def ftwb_trigger(env, order_pool, cart_capacity, io_pool, time_window, batching_type):
    """
    Fixed Time Window Batching trigger method
    """
    while True:
        yield env.timeout(time_window)
        if order_pool.get_order_count() > 0:
            try:
                orders_to_process = order_pool.get_all_orders()
                batch_list = []
                batch_list = batching_method(orders_to_process, cart_capacity, batch_list, batching_type)
                
                # Add batches to IOPool
                for batch in batch_list:
                    io_pool.add_batch(batch)
                
                order_pool.clear_orders()  # Clear all orders as they've been processed
            except Exception as e:
                logger.error(f"Error in ftwb_trigger: {e}")

def vtwb_trigger(env, order_pool, cart_capacity, io_pool, order_threshold, batching_type):
    """
    Variable Time Window Batching trigger method
    Only process order_threshold number of orders when threshold is met
    """
    while True:
        if order_pool.get_order_count() >= order_threshold:
            try:
                # Get only order_threshold orders from the pool
                all_orders = order_pool.get_all_orders()
                orders_to_process = all_orders[:order_threshold]
                
                # Create batches from the selected orders
                batch_list = []
                batch_list = batching_method(orders_to_process, cart_capacity, batch_list, batching_type)
                
                # Add batches to IOPool
                for batch in batch_list:
                    io_pool.add_batch(batch)
                
                # Remove only the processed orders
                for order in orders_to_process:
                    order_pool.remove_order(order["Order ID"])
                
                logger.info(f"VTWB processed {len(orders_to_process)} orders, {order_pool.get_order_count()} orders remaining")
            except Exception as e:
                logger.error(f"Error in vtwb_trigger: {e}")
        yield env.timeout(1)  # Check every time unit

def max_picker_trigger(env, order_pool, cart_capacity, io_pool, num_pickers, batching_type):
    """
    Maximize Picker utilization trigger method
    Process orders whenever there are idle pickers
    """
    while True:
        # Check if there are orders and at least one picker is available
        if order_pool.get_order_count() > 0 and io_pool.get_available_pickers() > 0:
            try:
                # Process all orders in the pool
                orders_to_process = order_pool.get_all_orders()
                batch_list = []
                batch_list = batching_method(orders_to_process, cart_capacity, batch_list, batching_type)
                
                # Add batches to IOPool
                for batch in batch_list:
                    io_pool.add_batch(batch)
                
                # Clear processed orders
                order_pool.clear_orders()
                
                logger.info(f"MaxPicker processed {len(orders_to_process)} orders")
            except Exception as e:
                logger.error(f"Error in MaxPicker trigger: {e}")
        
        yield env.timeout(1)  # Check every time unit

def max_cart_trigger(env, order_pool, cart_capacity, io_pool, batching_type):
    """
    Maximize Cart utilization trigger method
    Process orders when total items exceed cart capacity, excluding the overflow order
    """
    while True:
        # Get all orders from the pool
        all_orders = order_pool.get_all_orders()
        
        # Calculate total items in all orders
        if all_orders:
            total_items_in_pool = sum(order['Total Item'] for order in all_orders)
            
            # Only process if total items in pool exceeds cart capacity
            if total_items_in_pool > cart_capacity:
                try:
                    # Find orders that fit within cart capacity
                    total_items = 0
                    orders_to_process = []
                    
                    for order in all_orders:
                        order_quantity = order['Total Item']
                        
                        # If adding this order would exceed capacity, stop
                        # This is the overflow order we want to exclude
                        if total_items + order_quantity > cart_capacity:
                            break
                        
                        # Otherwise, add it to the orders to process
                        total_items += order_quantity
                        orders_to_process.append(order)
                    
                    # Only process if we have orders that fit in the cart
                    if orders_to_process:
                        # Create batches
                        batch_list = []
                        batch_list = batching_method(orders_to_process, cart_capacity, batch_list, batching_type)
                        
                        # Add batches to IOPool
                        for batch in batch_list:
                            io_pool.add_batch(batch)
                        
                        # Remove only the processed orders
                        for order in orders_to_process:
                            order_pool.remove_order(order["Order ID"])
                        
                        logger.info(f"MaxCart processed {len(orders_to_process)} orders with {total_items} items, excluding overflow order")
                except Exception as e:
                    logger.error(f"Error in MaxCart trigger: {e}")
        
        yield env.timeout(1)  # Check every time unit

def urgent_picker_trigger(env, order_pool, cart_capacity, io_pool, num_pickers, urgent_threshold, batching_type, routing_policy=1):
    """
    UrgentPicker trigger method
    Activates if all pickers are idle OR urgent order count >= urgent_threshold
    """
    while True:
        # Check if there are orders in the pool
        if order_pool.get_order_count() > 0:
            # Calculate urgent orders
            urgent_orders, urgent_count = calculate_urgent_orders(env, order_pool, routing_policy)
            
            # Check activation conditions
            all_pickers_idle = io_pool.get_available_pickers() == num_pickers
            urgent_threshold_met = urgent_count >= urgent_threshold
            
            if all_pickers_idle or urgent_threshold_met:
                try:
                    # Process all orders in order_pool
                    orders_to_process = order_pool.get_all_orders()
                    batch_list = []
                    batch_list = batching_method(orders_to_process, cart_capacity, batch_list, batching_type)
                    
                    # Add batches to IOPool
                    for batch in batch_list:
                        io_pool.add_batch(batch)
                    
                    # Clear processed orders
                    order_pool.clear_orders()
                    
                    if urgent_threshold_met:
                        logger.info(f"UrgentPicker triggered by {urgent_count} urgent orders")
                    else:
                        logger.info(f"UrgentPicker triggered by all pickers being idle")
                    
                except Exception as e:
                    logger.error(f"Error in UrgentPicker trigger: {e}")
        
        yield env.timeout(1)  # Check every time unit

def urgent_cart_trigger(env, order_pool, cart_capacity, io_pool, urgent_threshold, batching_type, routing_policy=1):
    """
    UrgentCart trigger method
    Activates if total items in IOPool >= cart_capacity OR urgent order count >= urgent_threshold
    """
    while True:
        # Check if there are orders in the pool
        if order_pool.get_order_count() > 0:
            # Calculate urgent orders
            urgent_orders, urgent_count = calculate_urgent_orders(env, order_pool, routing_policy)
            
            # Calculate total items in active batches
            active_batches = io_pool.get_active_batches()
            total_items_in_io_pool = sum(batch['total_items'] for batch in active_batches) if active_batches else 0
            
            # Check activation conditions
            cart_capacity_met = total_items_in_io_pool >= cart_capacity
            urgent_threshold_met = urgent_count >= urgent_threshold
            
            if cart_capacity_met or urgent_threshold_met:
                try:
                    # Process all orders in order_pool
                    orders_to_process = order_pool.get_all_orders()
                    batch_list = []
                    batch_list = batching_method(orders_to_process, cart_capacity, batch_list, batching_type)
                    
                    # Add batches to IOPool
                    for batch in batch_list:
                        io_pool.add_batch(batch)
                    
                    # Clear processed orders
                    order_pool.clear_orders()
                    
                    if urgent_threshold_met:
                        logger.info(f"UrgentCart triggered by {urgent_count} urgent orders")
                    else:
                        logger.info(f"UrgentCart triggered by total items in IOPool >= cart_capacity")
                    
                except Exception as e:
                    logger.error(f"Error in UrgentCart trigger: {e}")
        
        yield env.timeout(1)  # Check every time unit

def dvns_trigger(env, order_pool, cart_capacity, io_pool, num_pickers, urgent_threshold, routing_policy=1):
    """
    Dynamic Variable Neighborhood Search (DVNS) trigger
    Prioritizes: 1. Minimize late orders 2. Maximize picker utilization 3. Maximize cart utilization
    """
    while True:
        # --- Step 1: Generate Neighborhoods ---
        all_orders = order_pool.get_all_orders()
        if not all_orders:
            yield env.timeout(1)
            continue
        
        # Neighborhood 1: Urgency-based (earliest due_time)
        n1 = sorted(all_orders, key=lambda x: x['Due Time'])
        
        # Neighborhood 2: Max cart utilization (largest orders first)
        n2 = sorted(all_orders, key=lambda x: -x['Total Item'])
        
        # Neighborhood 3: Hybrid (urgent + cart optimization)
        urgent_orders, _ = calculate_urgent_orders(env, order_pool, routing_policy)
        n3 = urgent_orders + [o for o in n2 if o not in urgent_orders]
        
        # --- Step 2: Evaluate Neighborhoods ---
        best_solution = None
        
        # Check N1 (Urgent orders take precedence)
        if len(urgent_orders) >= urgent_threshold:
            best_solution = urgent_orders  # Process all urgent orders
            logger.info(f"DVNS selected urgent solution with {len(urgent_orders)} urgent orders")
        else:
            # Check if N1 can fill the cart
            total_n1 = sum(o['Total Item'] for o in n1)
            if total_n1 <= cart_capacity and io_pool.get_available_pickers() > 0:
                best_solution = n1
                logger.info(f"DVNS selected due time solution with {len(n1)} orders")
        
        # Check N2 (Max cart fill)
        if not best_solution:
            total_n2 = 0
            selected_n2 = []
            for order in n2:
                if total_n2 + order['Total Item'] > cart_capacity:
                    break
                total_n2 += order['Total Item']
                selected_n2.append(order)
            if selected_n2 and io_pool.get_available_pickers() > 0:
                best_solution = selected_n2
                logger.info(f"DVNS selected cart fill solution with {len(selected_n2)} orders")
        
        # Check N3 (Hybrid)
        if not best_solution:
            total_n3 = 0
            selected_n3 = []
            for order in n3:
                if total_n3 + order['Total Item'] > cart_capacity:
                    break
                total_n3 += order['Total Item']
                selected_n3.append(order)
            if selected_n3 and io_pool.get_available_pickers() > 0:
                best_solution = selected_n3
                logger.info(f"DVNS selected hybrid solution with {len(selected_n3)} orders")
        
        # --- Step 3: Process Best Solution ---
        if best_solution:
            try:
                batch_list = []
                batch_list = batching_method(best_solution, cart_capacity, batch_list, "EDT")  # Use EDT for consistency
                for batch in batch_list:
                    io_pool.add_batch(batch)
                
                # Remove processed orders
                for order in best_solution:
                    order_pool.remove_order(order["Order ID"])
                
                logger.info(f"DVNS processed {len(best_solution)} orders")
            except Exception as e:
                logger.error(f"Error in DVNS trigger: {e}")
        else:
            # Shake: Shuffle orders to escape local optima
            # Since we don't have direct access to shuffle_orders in OrderPool,
            # we'll log that a shuffle would happen here
            logger.info("DVNS: No solution found this round, would shuffle orders")
        
        yield env.timeout(1)  # Check every time unit

def trigger_method(env, order_pool, cart_capacity, io_pool, trigger_type, batching_type, **kwargs):
    """
    Select and run the appropriate trigger method
    Args:
        env: SimPy environment
        order_pool: OrderPool instance
        cart_capacity: Maximum items capacity per batch
        io_pool: IOPool instance to store the batched orders
        trigger_type: Type of trigger method ("FTWB", "VTWB", "MaxPicker", "MaxCart", 
                                              "UrgentPicker", "UrgentCart", "DVNS")
        batching_type: Type of batching method ("FCFS" or "EDT")
        **kwargs: Additional arguments for specific trigger methods
    """
    # Extract routing policy for urgent order calculations
    routing_policy = 1  # Default to Traversal
    if 'routing_policy' in kwargs:
        routing_policy = 2 if kwargs['routing_policy'] == "Largest Gap" else 1
    
    if trigger_type == "FTWB":
        return ftwb_trigger(env, order_pool, cart_capacity, io_pool, kwargs.get('time_window', 60), batching_type)
    elif trigger_type == "VTWB":
        return vtwb_trigger(env, order_pool, cart_capacity, io_pool, kwargs.get('order_threshold', 10), batching_type)
    elif trigger_type == "MaxPicker":
        return max_picker_trigger(env, order_pool, cart_capacity, io_pool, kwargs.get('num_pickers', 1), batching_type)
    elif trigger_type == "MaxCart":
        return max_cart_trigger(env, order_pool, cart_capacity, io_pool, batching_type)
    elif trigger_type == "UrgentPicker":
        return urgent_picker_trigger(env, order_pool, cart_capacity, io_pool, 
                                    kwargs.get('num_pickers', 1), 
                                    kwargs.get('urgent_threshold', 1), 
                                    batching_type,
                                    routing_policy)
    elif trigger_type == "UrgentCart":
        return urgent_cart_trigger(env, order_pool, cart_capacity, io_pool, 
                                  kwargs.get('urgent_threshold', 1), 
                                  batching_type,
                                  routing_policy)
    elif trigger_type == "DVNS":
        return dvns_trigger(env, order_pool, cart_capacity, io_pool, 
                           kwargs.get('num_pickers', 1),
                           kwargs.get('urgent_threshold', 1),
                           routing_policy)
    else:
        raise ValueError(f"Unknown trigger type: {trigger_type}")