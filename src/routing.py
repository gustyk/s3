# routing.py
import logging
import math
from functools import lru_cache
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def _default_params():
    """Load defaults lazily so importing this module has no file-system side effect."""
    with (PROJECT_ROOT / "config" / "parameters.yaml").open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@lru_cache(maxsize=32)
def _position_map(item_count: int, shelves_per_aisle: int, half_shelves: int):
    return {
        item: (
            math.ceil(item / shelves_per_aisle),
            (math.ceil(item / 2) - 1) % half_shelves + 1,
        )
        for item in range(1, item_count + 1)
    }


def translate_items_to_positions(items, model_params=None):
    """Translate item IDs using default or scenario-specific warehouse structure."""
    source = _default_params() if model_params is None else model_params
    shelves_per_aisle = int(source["warehouse_structure"]["shelves_per_aisle"])
    half_shelves = int(source["warehouse_structure"]["half_shelves"])
    positions_by_item = _position_map(
        int(source["warehouse_items"]), shelves_per_aisle, half_shelves
    )
    invalid = [item for item in items if item not in positions_by_item]
    if invalid:
        raise ValueError(f"Unknown warehouse item IDs: {invalid[:5]}")
    return [positions_by_item[item] for item in items]


def calculate_largest_gap(positions):
    """
    Find the largest gap in shelf positions for an aisle.

    Args:
        positions: List of shelf positions

    Returns:
        Tuple of (start_of_gap, end_of_gap)
    """
    if len(positions) < 2:
        return positions[0], positions[0]  # No gap if only one position

    positions.sort()
    largest_gap = max(positions[i + 1] - positions[i] for i in range(len(positions) - 1))
    start_of_gap = positions[0]
    return start_of_gap, start_of_gap + largest_gap


@lru_cache(maxsize=1024)
def calculate_total_time_cached(items_tuple, routing_strategy):
    """
    Cached version of calculate_total_time.
    """
    items = [list(item) for item in items_tuple]
    return calculate_total_time(items, routing_strategy)


def calculate_total_time(items, routing_strategy, model_params=None):
    """
    Simulate the picking process and calculate total trip time based on routing strategy.

    Args:
        items: List of (item number, quantity) tuples to pick.
        routing_strategy: Strategy for routing (1: Traversal, 2: Largest Gap).

    Returns:
        Total trip time in seconds.
    """
    if routing_strategy not in {1, 2}:
        raise ValueError(f"Unknown routing strategy: {routing_strategy}")
    if not items:
        return 0.0
    if any(quantity <= 0 for _, quantity in items):
        raise ValueError("Item quantities must be positive")
    source = _default_params() if model_params is None else model_params
    half_shelves = float(source["warehouse_structure"]["half_shelves"])
    depot_to_first_aisle = float(source["walking_times"]["depot_to_first_aisle"])
    between_aisles = float(source["walking_times"]["between_aisles"])
    between_shelves = float(source["walking_times"]["between_shelves"])
    picking_time_per_item = float(source["picking_time_per_item"])
    setup_time = float(source["setup_time"])

    # Expand items by quantity
    item_numbers = [item for item, quantity in items for _ in range(quantity)]
    positions = translate_items_to_positions(item_numbers, model_params)
    aisles = sorted(set(pos[0] for pos in positions))  # Unique aisles with picks

    total_walking_time = 0
    total_picking_time = len(item_numbers) * picking_time_per_item

    if routing_strategy == 1:  # Traversal strategy
        # Initialize components of walking time
        depot_time = depot_to_first_aisle + (aisles[0] - 1) * between_aisles

        # Calculate traverse_time
        traverse_time = 0.0
        if len(aisles) > 1:
            traverse_time = half_shelves * between_shelves * (len(aisles) - 1)

        # Calculate aisles_time
        aisles_time = 0.0
        if len(aisles) == 1:
            aisles_time = 0.0
        elif len(aisles) % 2 != 0:  # Odd number of aisles > 1
            aisles_time = (aisles[-2] - aisles[0]) * between_aisles
        else:  # Even number of aisles
            aisles_time = (aisles[-1] - aisles[0]) * between_aisles

        # Calculate last_aisle_time
        last_aisle = aisles[-1]
        farthest_shelf = max(pos[1] for pos in positions if pos[0] == last_aisle)

        if len(aisles) % 2 != 0:  # Odd number of aisles
            last_aisle_time = (farthest_shelf * between_shelves) * 2
        else:  # Even number of aisles
            last_aisle_time = half_shelves * between_shelves

        # Calculate return_time
        return_time = last_aisle * between_aisles

        # Total walking time
        total_walking_time = (
            depot_time + traverse_time + aisles_time + last_aisle_time + return_time
        )

        logger.debug(
            f"Traversal strategy - Walking components: depot={depot_time}, traverse={traverse_time}, "
            f"aisles={aisles_time}, last_aisle={last_aisle_time}, return={return_time}"
        )

    elif routing_strategy == 2:  # Largest Gap strategy
        # Initialize components of walking time
        depot_time = depot_to_first_aisle + (aisles[0] - 1) * between_aisles

        # Calculate traverse_time
        traverse_time = 0.0
        if len(aisles) > 1:
            traverse_time = half_shelves * between_shelves * 2

        # Calculate aisles_time
        aisles_time = 0.0 if len(aisles) == 1 else (aisles[-1] - aisles[0]) * between_aisles

        # Calculate gap_time
        gap_time = 0
        if len(aisles) >= 3:
            for aisle in aisles[1:-1]:  # Exclude first and last aisles
                shelves_in_aisle = sorted([pos[1] for pos in positions if pos[0] == aisle])
                if shelves_in_aisle:
                    # Calculate gaps within the aisle
                    gaps = [
                        (half_shelves + 1) - shelves_in_aisle[-1],  # Gap from last shelf to end
                        *[
                            shelves_in_aisle[i + 1] - shelves_in_aisle[i]
                            for i in range(len(shelves_in_aisle) - 1)
                        ],  # Gaps between shelves
                        shelves_in_aisle[0] - 0,  # Gap from start to first shelf
                    ]
                    largest_gap = max(gaps)
                    gap_time += (half_shelves - largest_gap + 1) * between_shelves

        # Calculate last_aisle_time
        last_aisle = aisles[-1]
        farthest_shelf = max(pos[1] for pos in positions if pos[0] == last_aisle)

        last_aisle_time = 0
        if len(aisles) == 1:
            last_aisle_time = (farthest_shelf * between_shelves) * 2

        # Calculate return_time
        return_time = last_aisle * between_aisles

        # Total walking time
        total_walking_time = (
            depot_time + traverse_time + aisles_time + gap_time + last_aisle_time + return_time
        )

        logger.debug(
            f"Largest Gap strategy - Walking components: depot={depot_time}, traverse={traverse_time}, "
            f"aisles={aisles_time}, gap={gap_time}, last_aisle={last_aisle_time}, return={return_time}"
        )

    # Add setup time and picking time to get total trip time
    total_trip_time = setup_time + total_walking_time + total_picking_time

    logger.debug(
        f"Total trip time: setup={setup_time}, walking={total_walking_time}, "
        f"picking={total_picking_time}, total={total_trip_time}"
    )

    return total_trip_time
