# order_pool.py
from typing import List, Dict, Union
from datetime import datetime

class OrderPool:
    def __init__(self):
        self.orders: List[Dict] = []

    def add_order(self, order: Dict) -> None:
        """
        Add a new order to the pool
        
        Args:
            order (Dict): Order dictionary containing order details
        """
        required_fields = ["Order ID", "Created Time"]
        if all(field in order for field in required_fields):
            self.orders.append(order)
        else:
            raise ValueError("Order is missing required fields")

    def remove_order(self, order_ids: Union[str, List[str]]) -> List[Dict]:
        """
        Remove one or multiple orders from the pool based on Order IDs
        
        Args:

            order_ids: Single Order ID string or list of Order IDs to remove
            
        Returns:
            List of removed orders. Empty list if no orders were found.
        """
        if isinstance(order_ids, str):
            order_ids = [order_ids]
            
        removed_orders = []
        remaining_orders = []
        
        for order in self.orders:
            if order["Order ID"] in order_ids:
                removed_orders.append(order)
            else:
                remaining_orders.append(order)
                
        self.orders = remaining_orders
        return removed_orders

    def sort_orders(self, key: str = "Created Time", reverse: bool = False) -> List[Dict]:
        """
        Sort orders based on Created Time or Due Time
        
        Args:
            key: Sorting key - either "Created Time" or "Due Time"
            reverse: If True, sort in descending order
            
        Returns:
            Sorted list of orders
            
        Raises:
            ValueError: If invalid key is provided
        """
        if key not in ["Created Time", "Due Time"]:
            raise ValueError("Sort key must be either 'Created Time' or 'Due Time'")
        
        def time_to_seconds(time_str: str) -> int:
            """Convert HH:MM:SS to seconds for comparison"""
            time_obj = datetime.strptime(time_str, "%H:%M:%S")
            return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
        
        self.orders.sort(
            key=lambda x: time_to_seconds(x[key]),
            reverse=reverse
        )
        return self.orders

    def clear_orders(self) -> None:
        """
        Remove all orders from the pool
        """
        self.orders.clear()

    def get_all_orders(self) -> List[Dict]:
        """
        Get all orders in the pool
        
        Returns:
            List of all orders
        """
        return self.orders

    def get_order_count(self) -> int:
        """
        Get the number of orders in the pool
        
        Returns:
            Number of orders
        """
        return len(self.orders)

    def get_order_by_id(self, order_id: str) -> Union[Dict, None]:
        """
        Get a specific order by its ID
        
        Args:
            order_id: Order ID to search for
            
        Returns:
            Order dictionary if found, None otherwise
        """
        for order in self.orders:
            if order["Order ID"] == order_id:
                return order
        return None

    # Add this method to the OrderPool class in src/order_pool.py

    def shuffle_orders(self) -> None:
        """
        Shuffle the orders in the pool to escape local optima in search algorithms
        """
        import random
        random.shuffle(self.orders)
        
    def remove_orders(self, order_ids: list) -> List[Dict]:
        """
        Remove multiple orders from the pool based on Order IDs
        
        Args:
            order_ids: List of Order IDs to remove
                
        Returns:
            List of removed orders. Empty list if no orders were found.
        """
        removed_orders = []
        remaining_orders = []
        
        for order in self.orders:
            if order["Order ID"] in order_ids:
                removed_orders.append(order)
            else:
                remaining_orders.append(order)
                
        self.orders = remaining_orders
        return removed_orders