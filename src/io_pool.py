# io_pool.py
import logging
import statistics

# Configure logging
logger = logging.getLogger(__name__)


def _percentile(values: list[float], probability: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = index - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


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
        # self.lock = threading.Lock()  # Lock for thread safety
        self.num_pickers = num_pickers  # Maximum number of pickers available
        self.picker_utilization = 0.0  # Total time pickers spent working
        self.picker_busy_time = {f"Picker{i + 1}": 0.0 for i in range(num_pickers)}
        self.picker_idle_since = {f"Picker{i + 1}": float(env.now) for i in range(num_pickers)}
        self.total_completed_orders = 0  # Total number of orders completed
        self.total_late_orders = 0  # Total number of orders completed late
        self.completed_orders = []
        self._change_event = env.event()

    def _notify_change(self) -> None:
        if not self._change_event.triggered:
            self._change_event.succeed()
        self._change_event = self.env.event()

    def wait_for_change(self):
        """Return an event fired by the next batch or picker-state change."""
        return self._change_event

    def add_batch(self, batch: list[dict], release_reason: str = "configured-batching") -> int:
        """
        Add a new batch to the IO Pool with timestamp

        Args:
            batch: List of orders forming a batch from batching_method

        Returns:
            Batch ID of the new batch
        """
        # with self.lock:
        batch_info = {
            "batch_id": self.current_batch_id,
            "orders": batch,
            "timestamp": self.env.now,  # Use simulation time instead of system time
            "total_items": sum(order["Total Item"] for order in batch),
            "assigned_to": None,
            "status": "pending",  # pending, assigned, completed
            "start_time": None,  # Time when picking started
            "completion_time": None,  # Time when picking completed
            "picking_time": None,  # Total time spent picking
            "release_reason": release_reason,
        }
        for order in batch:
            order["Batch ID"] = self.current_batch_id
            order["Batch Release Reason"] = release_reason
            order["Batch Release Time Seconds"] = float(self.env.now)
            order["Batch Order Count"] = len(batch)
            order["Batch Total Pieces"] = int(batch_info["total_items"])
        self.batches.append(batch_info)
        batch_id = self.current_batch_id
        self.current_batch_id += 1
        self._notify_change()

        logger.info(
            f"Added batch {batch_id} with {len(batch)} orders, {batch_info['total_items']} items"
        )

        return batch_id

    def sort_batches(self) -> None:
        """
        Sort batches based on their incoming timestamp
        This should be called with the lock held by the caller
        """
        self.batches.sort(key=lambda x: x["timestamp"])

    def assign_batch_to_picker(self, picker_id: str) -> dict | None:
        """
        Assign the earliest available batch to a picker

        Args:
            picker_id: Unique identifier for the picker

        Returns:
            Batch information if assignment successful, None if no batches available or picker already has batch
        """
        # with self.lock:
        if picker_id not in self.picker_idle_since:
            raise ValueError(f"Unknown picker ID: {picker_id}")
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

        available = [
            candidate
            for candidate in self.picker_idle_since
            if candidate not in self.assigned_batches
        ]
        longest_idle = min(
            available,
            key=lambda candidate: (
                self.picker_idle_since[candidate],
                int(candidate.removeprefix("Picker")),
            ),
        )
        if picker_id != longest_idle:
            return None

        # Find the earliest unassigned batch
        for batch in self.batches:
            if batch["status"] == "pending":
                batch["status"] = "assigned"
                batch["assigned_to"] = picker_id
                batch["start_time"] = self.env.now  # Record start time
                self.assigned_batches[picker_id] = batch
                for order in batch["orders"]:
                    order["Picker ID"] = picker_id
                    order["Picking Start Time Seconds"] = float(self.env.now)
                self._notify_change()
                logger.info(
                    f"Assigned batch {batch['batch_id']} to picker {picker_id} at time {self.env.now}"
                )
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
        # with self.lock:
        if picker_id not in self.assigned_batches:
            logger.info(f"No batch assigned to picker {picker_id}")
            return False

        batch = self.assigned_batches[picker_id]
        batch["status"] = "completed"
        batch["completion_time"] = self.env.now
        batch["picking_time"] = picking_time

        # Update metrics
        self.picker_utilization += picking_time
        self.picker_busy_time[picker_id] = self.picker_busy_time.get(picker_id, 0.0) + picking_time
        self.total_completed_orders += len(batch["orders"])

        # Check for late orders
        for order in batch["orders"]:
            due_time_seconds = float(order["Due Time Seconds"])
            order["Picking Start Time Seconds"] = float(batch["start_time"])
            order["Completion Time Seconds"] = float(self.env.now)
            order["Waiting Time Seconds"] = float(
                batch["start_time"] - order["Created Time Seconds"]
            )
            order["Flow Time Seconds"] = float(self.env.now - order["Created Time Seconds"])
            order["Tardiness Seconds"] = max(0.0, float(self.env.now - due_time_seconds))
            order["Tour Time Seconds"] = float(picking_time)
            self.completed_orders.append(order)
            if self.env.now > due_time_seconds:
                self.total_late_orders += 1
                logger.debug(
                    f"Order {order['Order ID']} completed late: due at {due_time_seconds}, completed at {self.env.now}"
                )

        # Remove from assigned batches
        del self.assigned_batches[picker_id]
        self.picker_idle_since[picker_id] = float(self.env.now)
        self._notify_change()

        logger.info(
            f"Completed batch {batch['batch_id']} by picker {picker_id} at time {self.env.now}"
        )
        return True

    def get_picker_batch(self, picker_id: str) -> dict | None:
        """
        Get the currently assigned batch for a picker

        Args:
            picker_id: Unique identifier for the picker

        Returns:
            Batch information if exists, None otherwise
        """
        # with self.lock:
        return self.assigned_batches.get(picker_id)

    def get_available_pickers(self) -> int:
        """
        Get the number of available pickers

        Returns:
            Number of available pickers
        """
        # with self.lock:
        return self.num_pickers - len(self.assigned_batches)

    def get_release_slots(self) -> int:
        """Idle picker capacity not already reserved by a pending batch."""
        pending = sum(batch["status"] == "pending" for batch in self.batches)
        return max(0, self.get_available_pickers() - pending)

    def get_pending_batches(self) -> list[dict]:
        """
        Get all pending batches

        Returns:
            List of unassigned batch information
        """
        # with self.lock:
        return [batch.copy() for batch in self.batches if batch["status"] == "pending"]

    def get_active_batches(self) -> list[dict]:
        """
        Get all currently assigned batches

        Returns:
            List of assigned batch information
        """
        # with self.lock:
        return [batch.copy() for batch in self.batches if batch["status"] == "assigned"]

    def get_completed_batches(self) -> list[dict]:
        """
        Get all completed batches

        Returns:
            List of completed batch information
        """
        # with self.lock:
        return [batch.copy() for batch in self.batches if batch["status"] == "completed"]

    def get_stats(
        self, observation_start: float = 0.0, observation_end: float | None = None
    ) -> dict:
        """Return observation-window statistics.

        Orders are eligible when their arrival is on/after ``observation_start``.
        Picker utilization is the overlap of assigned work with the observation
        window, so batches crossing the Welch boundary are handled correctly.
        """
        end = float(self.env.now if observation_end is None else observation_end)
        duration = max(0.0, end - float(observation_start))
        completed = [
            order
            for order in self.completed_orders
            if float(order["Created Time Seconds"]) >= observation_start
            and float(order["Completion Time Seconds"]) <= end
        ]
        late_completed = sum(
            float(order["Completion Time Seconds"]) > float(order["Due Time Seconds"])
            for order in completed
        )
        tardiness = [float(order["Tardiness Seconds"]) for order in completed]
        late_tardiness = [value for value in tardiness if value > 0]
        flow_times = [float(order["Flow Time Seconds"]) for order in completed]
        waiting_times = [float(order["Waiting Time Seconds"]) for order in completed]

        busy_by_picker = {picker_id: 0.0 for picker_id in self.picker_idle_since}
        for batch in self.batches:
            if batch["start_time"] is None or batch["assigned_to"] is None:
                continue
            batch_end = end if batch["completion_time"] is None else min(
                end, float(batch["completion_time"])
            )
            overlap = max(0.0, batch_end - max(float(batch["start_time"]), observation_start))
            busy_by_picker[str(batch["assigned_to"])] += overlap
        picker_utilization_by_picker = {
            picker_id: (busy / duration * 100 if duration else 0.0)
            for picker_id, busy in busy_by_picker.items()
        }
        picker_utility = (
            statistics.fmean(picker_utilization_by_picker.values())
            if picker_utilization_by_picker
            else 0.0
        )

        return {
            "total_batches": len(self.batches),
            "pending_batches": sum(b["status"] == "pending" for b in self.batches),
            "active_batches": sum(b["status"] == "assigned" for b in self.batches),
            "completed_batches": sum(b["status"] == "completed" for b in self.batches),
            "active_pickers": len(self.assigned_batches),
            "available_pickers": self.num_pickers - len(self.assigned_batches),
            "total_completed_orders": len(completed),
            "total_late_orders": late_completed,
            "picker_utility": picker_utility,
            "picker_utilization_by_picker": picker_utilization_by_picker,
            "mean_tardiness_seconds": statistics.fmean(tardiness) if tardiness else 0.0,
            "mean_late_tardiness_seconds": (
                statistics.fmean(late_tardiness) if late_tardiness else 0.0
            ),
            "median_tardiness_seconds": statistics.median(tardiness) if tardiness else 0.0,
            "max_tardiness_seconds": max(tardiness, default=0.0),
            "p95_tardiness_seconds": _percentile(tardiness, 0.95),
            "mean_flow_time_seconds": statistics.fmean(flow_times) if flow_times else 0.0,
            "p95_flow_time_seconds": _percentile(flow_times, 0.95),
            "mean_waiting_time_seconds": statistics.fmean(waiting_times) if waiting_times else 0.0,
            "p95_waiting_time_seconds": _percentile(waiting_times, 0.95),
            "completed_order_ids": [order["Order ID"] for order in completed],
        }

    def clear_completed_batches(self) -> None:
        """
        Remove all completed batches from the pool
        """
        # with self.lock:
        self.batches = [batch for batch in self.batches if batch["status"] != "completed"]
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
        # with self.lock:
        for batch in self.batches:
            if batch["status"] == "pending" or batch["status"] == "assigned":
                for order in batch["orders"]:
                    due_time_seconds = float(order["Due Time Seconds"])

                    if current_time > due_time_seconds:
                        late_count += 1

        return late_count
