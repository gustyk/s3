# trigger_method.py
from typing import List, Dict, Any
import simpy
from datetime import datetime, timedelta
from order_pool import OrderPool
from batching_method import batching_method
from io_pool import IOPool

def ftwb_trigger(env, order_pool, cart_capacity, IOPool, time_window, batching_type):
    """
    Fixed Time Window Batching trigger method
    """
    while True:
        yield env.timeout(time_window)
        if order_pool.orders:
            try:
                orders_to_process = order_pool.get_all_orders()
                batching_method(orders_to_process, cart_capacity, IOPool, batching_type)
                order_pool.clear()  # Clear all orders as they've been processed
            except Exception as e:
                print(f"Error in ftwb_trigger: {e}")

def vtwb_trigger(env, order_pool, cart_capacity, IOPool, order_threshold, batching_type):
    """
    Variable Time Window Batching trigger method
    """
    while True:
        if len(order_pool.orders) >= order_threshold:
            try:
                orders_to_process = order_pool.get_orders(order_threshold)
                batching_method(orders_to_process, cart_capacity, IOPool, batching_type)
                order_pool.remove_orders(orders_to_process)  # Remove only processed orders
            except Exception as e:
                print(f"Error in vtwb_trigger: {e}")
        yield env.timeout(1)  # Check every time unit

def dtwb_trigger(env, order_pool, cart_capacity, IOPool, due_window, batching_type):
    """
    Due Time Window Batching trigger method
    """
    while True:
        current_time = env.now
        try:
            urgent_orders = order_pool.get_urgent_orders(current_time + due_window)
            if urgent_orders:
                batching_method(urgent_orders, cart_capacity, IOPool, batching_type)
                order_pool.remove_orders(urgent_orders)  # Remove only urgent orders
        except Exception as e:
            print(f"Error in dtwb_trigger: {e}")
        
        yield env.timeout(1)  # Check every time unit


def trigger_method(env, order_pool, cart_capacity, IOPool, trigger_type, batching_type, **kwargs):
    """
    Select and run the appropriate trigger method
    Args:
        env: SimPy environment
        order_pool: OrderPool instance
        cart_capacity: Maximum items capacity per batch
        IOPool: List to store the batched orders
        trigger_type: Type of trigger method ("FTWB", "VTWB", or "DTWB")
        batching_type: Type of batching method ("FCFS" or "EDT")
        **kwargs: Additional arguments for specific trigger methods
    """
    if trigger_type == "FTWB":
        return ftwb_trigger(env, order_pool, cart_capacity, IOPool, kwargs.get('time_window', 60), batching_type)
    elif trigger_type == "VTWB":
        return vtwb_trigger(env, order_pool, cart_capacity, IOPool, kwargs.get('order_threshold', 10), batching_type)
    elif trigger_type == "DTWB":
        return dtwb_trigger(env, order_pool, cart_capacity, IOPool, kwargs.get('due_window', 30), batching_type)
    else:
        raise ValueError(f"Unknown trigger type: {trigger_type}")
