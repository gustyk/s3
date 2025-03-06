# io_pool.py
from datetime import datetime
from typing import List, Dict, Optional

class IOPool:
    def __init__(self):
        """
        Initialize the IO Pool to manage batches and picker assignments
        """
        self.batches = []  # List of batches with their arrival timestamps
        self.assigned_batches = {}  # Dictionary to track picker assignments {picker_id: batch}
        self.current_batch_id = 0  # Counter for generating unique batch IDs

    def add_batch(self, batch: List[dict]) -> None:
        """
        Add a new batch to the IO Pool with timestamp
        Args:
            batch: List of orders forming a batch from batching_method
        """
        batch_info = {
            'batch_id': self.current_batch_id,
            'orders': batch,
            'timestamp': datetime.now(),
            'total_items': sum(order['Total Item'] for order in batch),
            'assigned_to': None,
            'status': 'pending'  # pending, assigned, completed
        }
        self.batches.append(batch_info)
        self.current_batch_id += 1
        print(f"Added batch {batch_info['batch_id']} with {len(batch)} orders")

    def sort_batches(self) -> None:
        """
        Sort batches based on their incoming timestamp
        """
        self.batches.sort(key=lambda x: x['timestamp'])

    def assign_batch_to_picker(self, picker_id: str) -> Optional[dict]:
        """
        Assign the earliest available batch to a picker
        Args:
            picker_id: Unique identifier for the picker
        Returns:
            Batch information if assignment successful, None if no batches available
        """
        # Check if picker already has an assigned batch
        if picker_id in self.assigned_batches:
            print(f"Picker {picker_id} already has an assigned batch")
            return None
        
        # Sort batches before assignment
        self.sort_batches()

        # Find the earliest unassigned batch
        with self.lock:  # import threading
            for batch in self.batches:
                if batch['status'] == 'pending':
                    batch['status'] = 'assigned'
                    batch['assigned_to'] = picker_id
                    self.assigned_batches[picker_id] = batch
                    print(f"Assigned batch {batch['batch_id']} to picker {picker_id}")
                    return batch

        print(f"No available batches for picker {picker_id}")
        return None

    def complete_batch(self, picker_id: str) -> bool:
        """
        Mark a batch as completed and remove picker assignment
        Args:
            picker_id: Unique identifier for the picker
        Returns:
            Boolean indicating success of operation
        """
        if picker_id not in self.assigned_batches:
            print(f"No batch assigned to picker {picker_id}")
            return False

        with self.lock:  # import threading
            batch = self.assigned_batches[picker_id]
            batch['status'] = 'completed'
        del self.assigned_batches[picker_id]
        print(f"Completed batch {batch['batch_id']} by picker {picker_id}")
        return True

    def get_picker_batch(self, picker_id: str) -> Optional[dict]:
        """
        Get the currently assigned batch for a picker
        Args:
            picker_id: Unique identifier for the picker
        Returns:
            Batch information if exists, None otherwise
        """
        return self.assigned_batches.get(picker_id)

    def get_pending_batches(self) -> List[dict]:
        """
        Get all pending batches
        Returns:
            List of unassigned batch information
        """
        return [batch for batch in self.batches if batch['status'] == 'pending']

    def get_active_batches(self) -> List[dict]:
        """
        Get all currently assigned batches
        Returns:
            List of assigned batch information
        """
        return [batch for batch in self.batches if batch['status'] == 'assigned']

    def get_completed_batches(self) -> List[dict]:
        """
        Get all completed batches
        Returns:
            List of completed batch information
        """
        return [batch for batch in self.batches if batch['status'] == 'completed']

    def get_stats(self) -> Dict:
        """
        Get statistics about the current state of batches
        Returns:
            Dictionary containing batch statistics
        """
        return {
            'total_batches': len(self.batches),
            'pending_batches': len(self.get_pending_batches()),
            'active_batches': len(self.get_active_batches()),
            'completed_batches': len(self.get_completed_batches()),
            'active_pickers': len(self.assigned_batches)
        }

    def clear_completed_batches(self) -> None:
        """
        Remove all completed batches from the pool
        """
        self.batches = [batch for batch in self.batches if batch['status'] != 'completed']
        logging.info("Cleared all completed batches") # import logging
