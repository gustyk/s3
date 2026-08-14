"""Stochastic order generation with an injected random stream."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

import numpy as np

from src.models import Order

LOGGER = logging.getLogger(__name__)
LINE_COUNT_VALUES = np.arange(1, 11)


def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{remaining:02}"


def generate_orders(
    env: Any,
    order_pool: Any,
    arrival_rate: float,
    end_time: float,
    rng: np.random.Generator | None = None,
    *,
    due_time_min_seconds: int = 1800,
    due_time_max_seconds: int = 7200,
    due_time_resolution_seconds: int = 60,
    measurement_start_seconds: float = 0.0,
    item_probabilities: Sequence[float] | None = None,
):
    if arrival_rate <= 0:
        raise ValueError("arrival_rate must be positive")
    if end_time <= 0:
        raise ValueError("end_time must be positive")
    if not 0 < due_time_min_seconds <= due_time_max_seconds:
        raise ValueError("due-time bounds must satisfy 0 < min <= max")
    if due_time_resolution_seconds <= 0:
        raise ValueError("due_time_resolution_seconds must be positive")
    if due_time_min_seconds % due_time_resolution_seconds or due_time_max_seconds % due_time_resolution_seconds:
        raise ValueError("due-time bounds must be multiples of due_time_resolution_seconds")
    probabilities = np.asarray(
        item_probabilities if item_probabilities is not None else [1 / 384] * 384
    )
    if (
        len(probabilities) == 0
        or np.any(probabilities < 0)
        or not np.isclose(probabilities.sum(), 1)
    ):
        raise ValueError("item_probabilities must be non-negative and sum to one")

    rng = rng or np.random.default_rng()
    customer_id = 1
    while True:
        yield env.timeout(rng.exponential(scale=60 / arrival_rate))
        if env.now > end_time:
            break
        allowance_steps = rng.integers(
            due_time_min_seconds // due_time_resolution_seconds,
            due_time_max_seconds // due_time_resolution_seconds + 1,
        )
        due_time = env.now + int(allowance_steps) * due_time_resolution_seconds
        line_count = int(rng.integers(1, 11))
        if line_count > len(probabilities):
            raise ValueError("Order line count exceeds warehouse item count")
        items = rng.choice(
            np.arange(1, len(probabilities) + 1), size=line_count, replace=False, p=probabilities
        )
        quantities = rng.integers(1, 11, size=line_count)
        order_list = [
            (int(item), int(quantity)) for item, quantity in zip(items, quantities, strict=True)
        ]
        order: Order = {
            "Order ID": f"Cust{customer_id:05}",
            "Created Time": format_time(env.now),
            "Created Time Seconds": float(env.now),
            "Order List": order_list,
            "Total Item": sum(quantity for _, quantity in order_list),
            "Due Time": format_time(due_time),
            "Due Time Seconds": float(due_time),
            "Measurement Eligible": bool(env.now >= measurement_start_seconds),
        }
        order_pool.add_order(order)
        customer_id += 1
    LOGGER.info("Order generation completed: %s orders", customer_id - 1)
