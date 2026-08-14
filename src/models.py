"""Typed contracts shared by the simulation components."""

from __future__ import annotations

from typing import NotRequired, TypedDict

Order = TypedDict(
    "Order",
    {
        "Order ID": str,
        "Created Time": str,
        "Created Time Seconds": float,
        "Order List": list[tuple[int, int]],
        "Total Item": int,
        "Due Time": str,
        "Due Time Seconds": float,
        "Measurement Eligible": NotRequired[bool],
        "Batch ID": NotRequired[int],
        "Picker ID": NotRequired[str],
        "Picking Start Time Seconds": NotRequired[float],
        "Completion Time Seconds": NotRequired[float],
        "Censor Time Seconds": NotRequired[float],
        "Horizon State": NotRequired[str],
        "Waiting Time Seconds": NotRequired[float],
        "Flow Time Seconds": NotRequired[float],
        "Tardiness Seconds": NotRequired[float],
        "Tardiness Lower Bound Seconds": NotRequired[float],
    },
)
