#routing.py
import yaml
import math
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

# Read YAML configuration
with open("config/parameters.yaml", "r") as file:
    params = yaml.safe_load(file)

# Access variables
SHELVES_PER_AISLE = params["warehouse_structure"]["shelves_per_aisle"]
HALF_SHELVES = params["warehouse_structure"]["half_shelves"]
DEPOT_TO_FIRST_AISLE = params["walking_times"]["depot_to_first_aisle"]
BETWEEN_AISLES = params["walking_times"]["between_aisles"]
PICKING_TIME_PER_ITEM = params["picking_time_per_item"]
BETWEEN_SHELVES = params["walking_times"]["between_shelves"]
SETUP_TIME = params["setup_time"]

# Add at the beginning of routing.py after loading parameters
# Precompute all item positions
ITEM_POSITIONS = {}
for item in range(1, params["warehouse_items"] + 1):
    aisle = math.ceil(item / SHELVES_PER_AISLE)
    shelf = (math.ceil(item / 2) - 1) % HALF_SHELVES + 1
    ITEM_POSITIONS[item] = (aisle, shelf)

# Modify translate_items_to_positions
def translate_items_to_positions(items):
    """Use precomputed positions"""
    return [ITEM_POSITIONS[item] for item in items]

"""
def translate_items_to_positions(items):
    
    Translate item numbers to aisle and shelf positions.
    
    Args:
        items: List of item numbers
        
    Returns:
        List of (aisle, shelf) position tuples
    
    positions = []
    for item in items:
        aisle = math.ceil(item / SHELVES_PER_AISLE)
        shelf = (math.ceil(item / 2) - 1) % HALF_SHELVES + 1
        positions.append((aisle, shelf))
    return positions
"""

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

from functools import lru_cache

# Cache for translated positions
position_cache = {}

@lru_cache(maxsize=1024)
def calculate_total_time_cached(items_tuple, routing_strategy):
    """
    Cached version of calculate_total_time.
    """
    items = [list(item) for item in items_tuple]
    return calculate_total_time(items, routing_strategy)

def calculate_total_time(items, routing_strategy):
    """
    Simulate the picking process and calculate total trip time based on routing strategy.
    
    Args:
        items: List of (item number, quantity) tuples to pick.
        routing_strategy: Strategy for routing (1: Traversal, 2: Largest Gap).
        
    Returns:
        Total trip time in seconds.
    """
    # Expand items by quantity
    item_numbers = [item for item, quantity in items for _ in range(quantity)]
    positions = translate_items_to_positions(item_numbers)
    aisles = sorted(set(pos[0] for pos in positions))  # Unique aisles with picks
    
    total_walking_time = 0
    total_picking_time = len(item_numbers) * PICKING_TIME_PER_ITEM
    
    if routing_strategy == 1:  # Traversal strategy
        # Initialize components of walking time
        depot_time = DEPOT_TO_FIRST_AISLE + (aisles[0] - 1) * BETWEEN_AISLES
        
        # Calculate traverse_time
        traverse_time = 0
        if len(aisles) > 1:
            traverse_time = HALF_SHELVES * BETWEEN_SHELVES * (len(aisles) - 1)
        
        # Calculate aisles_time
        aisles_time = 0
        if len(aisles) == 1:
            aisles_time = 0
        elif len(aisles) % 2 != 0:  # Odd number of aisles > 1
            aisles_time = (aisles[-2] - aisles[0]) * BETWEEN_AISLES
        else:  # Even number of aisles
            aisles_time = (aisles[-1] - aisles[0]) * BETWEEN_AISLES
        
        # Calculate last_aisle_time
        last_aisle = aisles[-1]
        farthest_shelf = max(pos[1] for pos in positions if pos[0] == last_aisle)
        
        if len(aisles) % 2 != 0:  # Odd number of aisles
            last_aisle_time = (farthest_shelf * BETWEEN_SHELVES) * 2
        else:  # Even number of aisles
            last_aisle_time = HALF_SHELVES * BETWEEN_SHELVES
        
        # Calculate return_time
        return_time = last_aisle * BETWEEN_AISLES
        
        # Total walking time
        total_walking_time = depot_time + traverse_time + aisles_time + last_aisle_time + return_time
        
        logger.debug(f"Traversal strategy - Walking components: depot={depot_time}, traverse={traverse_time}, "
                     f"aisles={aisles_time}, last_aisle={last_aisle_time}, return={return_time}")
    
    elif routing_strategy == 2:  # Largest Gap strategy
        # Initialize components of walking time
        depot_time = DEPOT_TO_FIRST_AISLE + (aisles[0] - 1) * BETWEEN_AISLES
        
        # Calculate traverse_time
        traverse_time = 0
        if len(aisles) > 1:
            traverse_time = HALF_SHELVES * BETWEEN_SHELVES * 2
        
        # Calculate aisles_time
        aisles_time = 0
        if len(aisles) == 1:
            aisles_time = 0
        else:
            aisles_time = (aisles[-1] - aisles[0]) * BETWEEN_AISLES
        
        # Calculate gap_time
        gap_time = 0
        if len(aisles) >= 3:
            for aisle in aisles[1:-1]:  # Exclude first and last aisles
                shelves_in_aisle = sorted([pos[1] for pos in positions if pos[0] == aisle])
                if shelves_in_aisle:
                    # Calculate gaps within the aisle
                    gaps = [
                        (HALF_SHELVES + 1) - shelves_in_aisle[-1],  # Gap from last shelf to end
                        *[shelves_in_aisle[i+1] - shelves_in_aisle[i] for i in range(len(shelves_in_aisle)-1)],  # Gaps between shelves
                        shelves_in_aisle[0] - 0  # Gap from start to first shelf
                    ]
                    largest_gap = max(gaps)
                    gap_time += (HALF_SHELVES - largest_gap + 1) * BETWEEN_SHELVES
        
        # Calculate last_aisle_time
        last_aisle = aisles[-1]
        farthest_shelf = max(pos[1] for pos in positions if pos[0] == last_aisle)
        
        last_aisle_time = 0
        if len(aisles) == 1:
            last_aisle_time = (farthest_shelf * BETWEEN_SHELVES) * 2
        
        # Calculate return_time
        return_time = last_aisle * BETWEEN_AISLES
        
        # Total walking time
        total_walking_time = depot_time + traverse_time + aisles_time + gap_time + last_aisle_time + return_time
        
        logger.debug(f"Largest Gap strategy - Walking components: depot={depot_time}, traverse={traverse_time}, "
                     f"aisles={aisles_time}, gap={gap_time}, last_aisle={last_aisle_time}, return={return_time}")
    
    # Add setup time and picking time to get total trip time
    total_trip_time = SETUP_TIME + total_walking_time + total_picking_time
    
    logger.debug(f"Total trip time: setup={SETUP_TIME}, walking={total_walking_time}, "
                 f"picking={total_picking_time}, total={total_trip_time}")
    
    return total_trip_time