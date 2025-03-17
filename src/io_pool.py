# io_pool.py
from typing import List, Dict, Optional
import threading
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class IOPool:
    def __init__(self, env, num_pickers=1):
        """
        Initialize the IO Pool to manage batches and picker assignments

        Args:
            env: SimPy environment for time tracking
            num_pickers: Maximum number of pickers available (from config)
        """
        self.env = env  # Store SimPy environment for time tracking
        self.batches = []  # List of batches with their arrival timestamps
        self.assigned_batches = {}  # Dictionary to track picker assignments {picker_id: batch}
        self.current_batch_id = 0  # Counter for generating unique batch IDs
        #self.lock = threading.Lock()  # Lock for thread safety
        self.num_pickers = num_pickers  # Maximum number of pickers available
        self.picker_utilization = 0  # Total time pickers spent working
        self.total_completed_orders = 0  # Total number of orders completed
        self.total_late_orders = 0  # Total number of orders completed late

    def add_batch(self, batch: List[dict]) -> int:
        """
        Add a new batch to the IO Pool with timestamp
        
        Args:
            batch: List of orders forming a batch from batching_method
            
        Returns:
            Batch ID of the new batch
        """
        #with self.lock:
        batch_info = {
            'batch_id': self.current_batch_id,
            'orders': batch,
            'timestamp': self.env.now,  # Use simulation time instead of system time
            'total_items': sum(order['Total Item'] for order in batch),
            'assigned_to': None,
            'status': 'pending',  # pending, assigned, completed
            'start_time': None,   # Time when picking started
            'completion_time': None,  # Time when picking completed
            'picking_time': None  # Total time spent picking
        }
        self.batches.append(batch_info)
        batch_id = self.current_batch_id
        self.current_batch_id += 1
        
        logger.info(f"Added batch {batch_id} with {len(batch)} orders, {batch_info['total_items']} items")
        
        return batch_id

    def sort_batches(self) -> None:
        """
        Sort batches based on their incoming timestamp
        This should be called with the lock held by the caller
        """
        self.batches.sort(key=lambda x: x['timestamp'])

    def assign_batch_to_picker(self, picker_id: str) -> Optional[dict]:
        """
        Assign the earliest available batch to a picker
        
        Args:
            picker_id: Unique identifier for the picker
            
        Returns:
            Batch information if assignment successful, None if no batches available or picker already has batch
        """
        #with self.lock:
        # Check if picker already has an assigned batch
        if picker_id in self.assigned_batches:
            logger.info(f"Picker {picker_id} already has an assigned batch")
            return None
        
        # Check if we've reached the picker capacity limit
        if len(self.assigned_batches) >= self.num_pickers:
            logger.info(f"Maximum number of pickers ({self.num_pickers}) already assigned")
            return None
        
        # Sort batches before assignment (inside the lock)
        self.sort_batches()
        
        # Find the earliest unassigned batch
        for batch in self.batches:
            if batch['status'] == 'pending':
                batch['status'] = 'assigned'
                batch['assigned_to'] = picker_id
                batch['start_time'] = self.env.now  # Record start time
                self.assigned_batches[picker_id] = batch
                logger.info(f"Assigned batch {batch['batch_id']} to picker {picker_id} at time {self.env.now}")
                return batch
        
        logger.info(f"No available batches for picker {picker_id}")
        return None

    def complete_batch(self, picker_id: str, picking_time: float) -> bool:
        """
        Mark a batch as completed and remove picker assignment
        
        Args:
            picker_id: Unique identifier for the picker
            picking_time: Time it took to complete the batch (from routing.py)
            
        Returns:
            Boolean indicating success of operation
        """
        #with self.lock:
        if picker_id not in self.assigned_batches:
            logger.info(f"No batch assigned to picker {picker_id}")
            return False
        
        batch = self.assigned_batches[picker_id]
        batch['status'] = 'completed'
        batch['completion_time'] = self.env.now
        batch['picking_time'] = picking_time
        
        # Update metrics
        self.picker_utilization += picking_time
        self.total_completed_orders += len(batch['orders'])
        
        # Check for late orders
        for order in batch['orders']:
            due_time_str = order['Due Time']
            due_time_parts = list(map(int, due_time_str.split(':')))
            due_time_seconds = due_time_parts[0] * 3600 + due_time_parts[1] * 60 + due_time_parts[2]
            
            if self.env.now > due_time_seconds:
                self.total_late_orders += 1
                logger.debug(f"Order {order['Order ID']} completed late: due at {due_time_str}, completed at {self.env.now}")
        
        # Remove from assigned batches
        del self.assigned_batches[picker_id]
        
        logger.info(f"Completed batch {batch['batch_id']} by picker {picker_id} at time {self.env.now}")
        return True

    def get_picker_batch(self, picker_id: str) -> Optional[dict]:
        """
        Get the currently assigned batch for a picker
        
        Args:
            picker_id: Unique identifier for the picker
            
        Returns:
            Batch information if exists, None otherwise
        """
        #with self.lock:
        return self.assigned_batches.get(picker_id)

    def get_available_pickers(self) -> int:
        """
        Get the number of available pickers
        
        Returns:
            Number of available pickers
        """
        #with self.lock:
        return self.num_pickers - len(self.assigned_batches)

    def get_pending_batches(self) -> List[dict]:
        """
        Get all pending batches
        
        Returns:
            List of unassigned batch information
        """
        #with self.lock:
        return [batch.copy() for batch in self.batches if batch['status'] == 'pending']

    def get_active_batches(self) -> List[dict]:
        """
        Get all currently assigned batches
        
        Returns:
            List of assigned batch information
        """
        #with self.lock:
        return [batch.copy() for batch in self.batches if batch['status'] == 'assigned']

    def get_completed_batches(self) -> List[dict]:
        """
        Get all completed batches
        
        Returns:
            List of completed batch information
        """
        #with self.lock:
        return [batch.copy() for batch in self.batches if batch['status'] == 'completed']

    def get_stats(self) -> Dict:
        """
        Get statistics about the current state of batches and performance metrics
        
        Returns:
            Dictionary containing batch statistics and performance metrics
        """
        #with self.lock:
        # Calculate picker utility as percentage of time pickers were busy
        total_simulation_time = self.env.now * self.num_pickers
        picker_utility = (self.picker_utilization / total_simulation_time * 100) if total_simulation_time > 0 else 0
        
        return {
            'total_batches': len(self.batches),
            'pending_batches': len([b for b in self.batches if b['status'] == 'pending']),
            'active_batches': len([b for b in self.batches if b['status'] == 'assigned']),
            'completed_batches': len([b for b in self.batches if b['status'] == 'completed']),
            'active_pickers': len(self.assigned_batches),
            'available_pickers': self.num_pickers - len(self.assigned_batches),
            'total_completed_orders': self.total_completed_orders,
            'total_late_orders': self.total_late_orders, 
            'picker_utility': picker_utility
        }

    def clear_completed_batches(self) -> None:
        """
        Remove all completed batches from the pool
        """
        #with self.lock:
        self.batches = [batch for batch in self.batches if batch['status'] != 'completed']
        logger.info("Cleared all completed batches")

    def check_late_pending_orders(self, current_time: float) -> int:
        """
        Check and count orders in pending batches that are already late
        
        Args:
            current_time: Current simulation time
            
        Returns:
            Number of late pending orders
        """
        late_count = 0
        #with self.lock:
        for batch in self.batches:
            if batch['status'] == 'pending' or batch['status'] == 'assigned':
                for order in batch['orders']:
                    due_time_str = order['Due Time']
                    due_time_parts = list(map(int, due_time_str.split(':')))
                    due_time_seconds = due_time_parts[0] * 3600 + due_time_parts[1] * 60 + due_time_parts[2]
                    
                    if current_time > due_time_seconds:
                        late_count += 1
        
        return late_count