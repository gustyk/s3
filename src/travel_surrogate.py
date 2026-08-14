"""Calibrated linear travel-time surrogate used by urgency policies.

Addresses R1-Mayor #1/#10 and R2-Mayor #3/#4. The feature vector is bounded
for a single order (at most ten distinct lines), so one order prediction is O(1)
with respect to waiting-pool size. Final coefficients require a frozen
calibration report; unvalidated coefficients fail unless explicitly allowed by
the caller's configuration workflow.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def travel_features(orders: Iterable[dict[str, Any]], params: dict[str, Any]) -> tuple[float, ...]:
    lines: list[tuple[int, int]] = [
        (int(item), int(quantity))
        for order in orders
        for item, quantity in order["Order List"]
    ]
    if not lines:
        return (1.0, 0.0, 0.0, 0.0, 0.0)
    shelves_per_aisle = int(params["warehouse_structure"]["shelves_per_aisle"])
    aisles = {(item - 1) // shelves_per_aisle + 1 for item, _ in lines}
    return (
        1.0,
        float(len(lines)),
        float(sum(quantity for _, quantity in lines)),
        float(max(aisles)),
        float(len(aisles)),
    )


def estimate_travel_seconds(
    orders: Iterable[dict[str, Any]], routing_name: str, params: dict[str, Any]
) -> float:
    specification = params["travel_time_surrogate"]
    if routing_name not in {"Traversal", "S-shape", "Largest Gap"}:
        raise ValueError(f"Unknown routing policy for surrogate: {routing_name}")
    coefficient_key = "Traversal" if routing_name in {"Traversal", "S-shape"} else routing_name
    coefficients = tuple(float(value) for value in specification[coefficient_key])
    features = travel_features(orders, params)
    if len(coefficients) != len(features):
        raise ValueError("Travel-surrogate coefficient and feature counts differ")
    return max(
        0.0,
        sum(
            coefficient * feature
            for coefficient, feature in zip(coefficients, features, strict=True)
        ),
    )


def estimate_trip_seconds(
    orders: Iterable[dict[str, Any]], routing_name: str, params: dict[str, Any]
) -> float:
    materialized = list(orders)
    pieces = sum(int(order["Total Item"]) for order in materialized)
    return (
        float(params["setup_time"])
        + pieces * float(params["picking_time_per_item"])
        + estimate_travel_seconds(materialized, routing_name, params)
    )
