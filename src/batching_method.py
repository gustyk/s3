# batching_method.py
import logging

# Configure logging
logger = logging.getLogger(__name__)

def fcfs_batching(orders_to_process, cart_capacity, io_pool):
    """
    Batch orders using the First Come First Serve (FCFS) method.
    Args:
        orders_to_process: List of orders to be processed
        cart_capacity: Maximum items capacity per batch
        io_pool: List to store the batched orders
    """
    logger.info("\n--- FCFS Batching ---")
    current_batch = []
    current_batch_quantity = 0

    logger.info(f"Orders entering FCFS batching: {len(orders_to_process)} orders")
    for order in orders_to_process:
        order_quantity = order["Total Item"]
        logger.debug(f"Processing Order ID: {order['Order ID']}, Total Item: {order_quantity}")

        if current_batch_quantity + order_quantity <= cart_capacity:
            current_batch.append(order)
            current_batch_quantity += order_quantity
        else:
            logger.info(f"Batch completed with {len(current_batch)} orders, Total Items: {current_batch_quantity}")
            io_pool.append(current_batch)
            current_batch = [order]
            current_batch_quantity = order_quantity

    if current_batch:
        logger.info(f"Final batch completed with {len(current_batch)} orders, Total Items: {current_batch_quantity}")
        io_pool.append(current_batch)
    
    return io_pool

def edt_batching(orders_to_process, cart_capacity, io_pool):
    """
    Batch orders using the Earliest Due Time (EDT) method.
    Args:
        orders_to_process: List of orders to be processed
        cart_capacity: Maximum items capacity per batch
        io_pool: List to store the batched orders
    """
    logger.info("\n--- EDT Batching ---")

    # Sort orders by Due Time (earliest first)
    sorted_orders = sorted(orders_to_process, key=lambda x: x["Due Time"])

    logger.info(f"Orders entering EDT batching: {len(sorted_orders)} orders")
    current_batch = []
    current_batch_quantity = 0

    for order in sorted_orders:
        order_quantity = order["Total Item"]
        logger.debug(f"Processing Order ID: {order['Order ID']}, Total Item: {order_quantity}")

        if current_batch_quantity + order_quantity <= cart_capacity:
            current_batch.append(order)
            current_batch_quantity += order_quantity
        else:
            logger.info(f"Batch completed with {len(current_batch)} orders, Total Items: {current_batch_quantity}")
            io_pool.append(current_batch)
            current_batch = [order]
            current_batch_quantity = order_quantity

    if current_batch:
        logger.info(f"Final batch completed with {len(current_batch)} orders, Total Items: {current_batch_quantity}")
        io_pool.append(current_batch)
    
    return io_pool

def batching_method(orders_to_process, cart_capacity, io_pool, batching_type):
    """
    Select and run the appropriate batching method.
    Args:
        orders_to_process: List of orders to be processed
        cart_capacity: Maximum items capacity per batch
        io_pool: List to store the batched orders
        batching_type: Type of batching method to use ("FCFS" or "EDT")
    """
    try:
        if batching_type == "FCFS":
            return fcfs_batching(orders_to_process, cart_capacity, io_pool)
        elif batching_type == "EDT":
            return edt_batching(orders_to_process, cart_capacity, io_pool)
        else:
            raise ValueError(f"Unknown batching type: {batching_type}")
    except Exception as e:
        logger.error(f"Error occurred during {batching_type} batching: {str(e)}")
        raise