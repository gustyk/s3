# trigger_method.py
from typing import List, Dict, Any
import simpy
import logging
from datetime import datetime, timedelta
from src.order_pool import OrderPool
from src.batching_method import batching_method
from src.io_pool import IOPool

# Set up logging
logger = logging.getLogger(__name__)

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
    """
    while True:
        if order_pool.get_order_count() >= order_threshold:
            try:
                orders_to_process = order_pool.get_all_orders()
                batch_list = []
                batch_list = batching_method(orders_to_process, cart_capacity, batch_list, batching_type)
                
                # Add batches to IOPool
                for batch in batch_list:
                    io_pool.add_batch(batch)
                
                order_pool.clear_orders()  # Clear all orders as they've been processed
            except Exception as e:
                logger.error(f"Error in vtwb_trigger: {e}")
        yield env.timeout(1)  # Check every time unit

def dtwb_trigger(env, order_pool, cart_capacity, io_pool, due_window, batching_type):
    """
    Due Time Window Batching trigger method
    """
    while True:
        current_time = env.now
        urgent_orders = []
        
        # Identify urgent orders
        for order in order_pool.get_all_orders():
            due_time_str = order['Due Time']
            due_time_parts = list(map(int, due_time_str.split(':')))
            due_time_seconds = due_time_parts[0] * 3600 + due_time_parts[1] * 60 + due_time_parts[2]
            
            if due_time_seconds - current_time <= due_window * 60:
                urgent_orders.append(order)
        
        if urgent_orders:
            try:
                batch_list = []
                batch_list = batching_method(urgent_orders, cart_capacity, batch_list, batching_type)
                
                # Add batches to IOPool
                for batch in batch_list:
                    io_pool.add_batch(batch)
                
                # Remove processed orders
                for order in urgent_orders:
                    order_pool.remove_order(order['Order ID'])
            except Exception as e:
                logger.error(f"Error in dtwb_trigger: {e}")
        
        yield env.timeout(1)  # Check every time unit

def max_picker_trigger(env, order_pool, cart_capacity, io_pool, num_pickers, batching_type):
    """
    Maximize Picker utilization trigger method
    """
    while True:
        if order_pool.get_order_count() > 0 and len(io_pool.get_active_batches()) < num_pickers:
            try:
                orders_to_process = order_pool.get_all_orders()
                batch_list = []
                batch_list = batching_method(orders_to_process, cart_capacity, batch_list, batching_type)
                
                # Add batches to IOPool
                for batch in batch_list:
                    io_pool.add_batch(batch)
                
                # Clear processed orders
                order_pool.clear_orders()
            except Exception as e:
                logger.error(f"Error in MaxPicker trigger: {e}")
        
        yield env.timeout(1)  # Check every time unit

def max_cart_trigger(env, order_pool, cart_capacity, io_pool, batching_type):
    """
    Maximize Cart utilization trigger method
    """
    while True:
        if order_pool.get_order_count() > 0:
            try:
                total_items = sum(order['Total Item'] for order in order_pool.get_all_orders())
                
                if total_items >= cart_capacity * 0.8:  # Try to fill cart to at least 80%
                    orders_to_process = order_pool.get_all_orders()
                    batch_list = []
                    batch_list = batching_method(orders_to_process, cart_capacity, batch_list, batching_type)
                    
                    # Add batches to IOPool
                    for batch in batch_list:
                        io_pool.add_batch(batch)
                    
                    # Clear processed orders
                    order_pool.clear_orders()
            except Exception as e:
                logger.error(f"Error in MaxCart trigger: {e}")
        
        yield env.timeout(1)  # Check every time unit

def urgent_picker_trigger(env, order_pool, cart_capacity, io_pool, num_pickers, urgent_threshold, batching_type):
    """
    Prioritize urgent orders, then maximize picker utilization
    """
    while True:
        current_time = env.now
        urgent_orders = []
        
        # Check for urgent orders (due within urgent_threshold minutes)
        for order in order_pool.get_all_orders():
            due_time_str = order['Due Time']
            due_time_parts = list(map(int, due_time_str.split(':')))
            due_time_seconds = due_time_parts[0] * 3600 + due_time_parts[1] * 60 + due_time_parts[2]
            
            if due_time_seconds - current_time <= urgent_threshold * 60:
                urgent_orders.append(order)
        
        # Process urgent orders first
        if urgent_orders and len(io_pool.get_active_batches()) < num_pickers:
            try:
                batch_list = []
                batch_list = batching_method(urgent_orders, cart_capacity, batch_list, batching_type)
                
                # Add batches to IOPool
                for batch in batch_list:
                    io_pool.add_batch(batch)
                
                # Remove processed orders
                for order in urgent_orders:
                    order_pool.remove_order(order['Order ID'])
            except Exception as e:
                logger.error(f"Error processing urgent orders: {e}")
        
        # Then process regular orders if pickers are available
        elif order_pool.get_order_count() > 0 and len(io_pool.get_active_batches()) < num_pickers:
            try:
                orders_to_process = order_pool.get_all_orders()
                batch_list = []
                batch_list = batching_method(orders_to_process, cart_capacity, batch_list, batching_type)
                
                # Add batches to IOPool
                for batch in batch_list:
                    io_pool.add_batch(batch)
                
                # Clear processed orders
                order_pool.clear_orders()
            except Exception as e:
                logger.error(f"Error in regular order processing: {e}")
        
        yield env.timeout(1)  # Check every time unit

def urgent_cart_trigger(env, order_pool, cart_capacity, io_pool, urgent_threshold, batching_type):
    """
    Prioritize urgent orders, then maximize cart utilization
    """
    while True:
        current_time = env.now
        urgent_orders = []
        
        # Check for urgent orders (due within urgent_threshold minutes)
        for order in order_pool.get_all_orders():
            due_time_str = order['Due Time']
            due_time_parts = list(map(int, due_time_str.split(':')))
            due_time_seconds = due_time_parts[0] * 3600 + due_time_parts[1] * 60 + due_time_parts[2]
            
            if due_time_seconds - current_time <= urgent_threshold * 60:
                urgent_orders.append(order)
        
        # Process urgent orders first
        if urgent_orders:
            try:
                batch_list = []
                batch_list = batching_method(urgent_orders, cart_capacity, batch_list, batching_type)
                
                # Add batches to IOPool
                for batch in batch_list:
                    io_pool.add_batch(batch)
                
                # Remove processed orders
                for order in urgent_orders:
                    order_pool.remove_order(order['Order ID'])
            except Exception as e:
                logger.error(f"Error processing urgent orders: {e}")
        
        # Then check if we can maximize cart capacity
        else:
            total_items = sum(order['Total Item'] for order in order_pool.get_all_orders())
            
            if total_items >= cart_capacity * 0.8:  # Try to fill cart to at least 80%
                try:
                    orders_to_process = order_pool.get_all_orders()
                    batch_list = []
                    batch_list = batching_method(orders_to_process, cart_capacity, batch_list, batching_type)
                    
                    # Add batches to IOPool
                    for batch in batch_list:
                        io_pool.add_batch(batch)
                    
                    # Clear processed orders
                    order_pool.clear_orders()
                except Exception as e:
                    logger.error(f"Error in regular order processing: {e}")
        
        yield env.timeout(1)  # Check every time unit

def vnd_trigger(env, order_pool, cart_capacity, io_pool, batching_type):
    """
    Variable Neighborhood Descent trigger method
    """
    while True:
        if order_pool.get_order_count() > 0:
            try:
                # Get all orders
                orders = order_pool.get_all_orders()
                
                # Use EDT batching for VND which sorts by due time
                batch_list = []
                batch_list = batching_method(orders, cart_capacity, batch_list, "EDT")
                
                # Add batches to IOPool
                for batch in batch_list:
                    io_pool.add_batch(batch)
                
                # Clear processed orders
                order_pool.clear_orders()
            except Exception as e:
                logger.error(f"Error in VND trigger: {e}")
        
        yield env.timeout(1)  # Check every time unit

def trigger_method(env, order_pool, cart_capacity, io_pool, trigger_type, batching_type, **kwargs):
    """
    Select and run the appropriate trigger method
    Args:
        env: SimPy environment
        order_pool: OrderPool instance
        cart_capacity: Maximum items capacity per batch
        io_pool: IOPool instance to store the batched orders
        trigger_type: Type of trigger method ("FTWB", "VTWB", "DTWB", "MaxPicker", "MaxCart", "UrgentPicker", "UrgentCart", "VND")
        batching_type: Type of batching method ("FCFS" or "EDT")
        **kwargs: Additional arguments for specific trigger methods
    """
    if trigger_type == "FTWB":
        return ftwb_trigger(env, order_pool, cart_capacity, io_pool, kwargs.get('time_window', 60), batching_type)
    elif trigger_type == "VTWB":
        return vtwb_trigger(env, order_pool, cart_capacity, io_pool, kwargs.get('order_threshold', 10), batching_type)
    elif trigger_type == "DTWB":
        return dtwb_trigger(env, order_pool, cart_capacity, io_pool, kwargs.get('due_window', 30), batching_type)
    elif trigger_type == "MaxPicker":
        return max_picker_trigger(env, order_pool, cart_capacity, io_pool, kwargs.get('num_pickers', 1), batching_type)
    elif trigger_type == "MaxCart":
        return max_cart_trigger(env, order_pool, cart_capacity, io_pool, batching_type)
    elif trigger_type == "UrgentPicker":
        return urgent_picker_trigger(env, order_pool, cart_capacity, io_pool, kwargs.get('num_pickers', 1), kwargs.get('urgent_threshold', 30), batching_type)
    elif trigger_type == "UrgentCart":
        return urgent_cart_trigger(env, order_pool, cart_capacity, io_pool, kwargs.get('urgent_threshold', 30), batching_type)
    elif trigger_type == "VND":
        return vnd_trigger(env, order_pool, cart_capacity, io_pool, batching_type)
    else:
        raise ValueError(f"Unknown trigger type: {trigger_type}")
