"""Canonical release-trigger and intrinsic-composition policies.

The implementation follows the 2026-08-14 decision freeze for EJIE-337519.
Simple methods open a batching cycle that releases at most one batch per
currently available picker slot. SNH and MPBH build one intrinsic,
capacity-feasible batch per slot. Addresses R1-Mayor #1/#10 and R2-Mayor #4.
"""

from __future__ import annotations

import logging
from contextlib import suppress
from typing import Any

from src.batching_method import batching_method
from src.travel_surrogate import estimate_trip_seconds

LOGGER = logging.getLogger(__name__)


def _wait_for_state_change(env: Any, order_pool: Any, io_pool: Any, timeout: float | None = None):
    """Wake on an arrival/pool mutation, picker-state change, or deadline."""
    events = []
    for source in (order_pool, io_pool):
        wait = getattr(source, "wait_for_change", None)
        if wait is not None:
            with suppress(RuntimeError):
                events.append(wait())
    if timeout is not None:
        events.append(env.timeout(max(float(timeout), 1e-9)))
    if not events:
        return env.timeout(1)
    return events[0] if len(events) == 1 else env.any_of(events)


def _due_seconds(order: dict[str, Any]) -> float:
    return float(order["Due Time Seconds"])


def _arrival_key(order: dict[str, Any]) -> tuple[float, str]:
    return float(order["Created Time Seconds"]), str(order["Order ID"])


def _edt_key(order: dict[str, Any]) -> tuple[float, float, str]:
    return _due_seconds(order), *_arrival_key(order)


def _single_order_trip_seconds(
    order: dict[str, Any], routing_name: str, params: dict[str, Any]
) -> float:
    """Cache the immutable single-order surrogate within one simulation run."""
    cache_key = f"_Urgency Trip Seconds:{routing_name}"
    cached = order.get(cache_key)
    if cached is None:
        cached = estimate_trip_seconds([order], routing_name, params)
        order[cache_key] = float(cached)
    return float(cached)


def _capacity_fill(
    orders: list[dict[str, Any]], capacity: int, *, skip_non_fitting: bool = True
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    used = 0
    for order in orders:
        quantity = int(order["Total Item"])
        if used + quantity <= capacity:
            selected.append(order)
            used += quantity
        elif not skip_non_fitting:
            break
    return selected


def calculate_urgent_orders(
    env: Any,
    order_pool: Any,
    routing_policy: str | int = "S-shape",
    io_pool: Any | None = None,
    routing_config: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Return orders whose conservative single-order completion exceeds due.

    Paper-canonical urgency is evaluated independently for each order as
    ``now + setup + pick + O(1) travel surrogate > due``. ``io_pool`` remains
    in the signature for API compatibility but does not alter this criterion.
    """
    del io_pool
    if routing_config is None:
        raise ValueError("routing_config is required for canonical urgency prediction")
    routing_name = (
        "S-shape" if routing_policy in {1, "Traversal", "S-shape"} else "Largest Gap"
    )
    urgent = [
        order
        for order in sorted(order_pool.get_all_orders(), key=_edt_key)
        if float(env.now) + _single_order_trip_seconds(order, routing_name, routing_config)
        > _due_seconds(order)
    ]
    return urgent, len(urgent)


def _seconds_to_next_urgency(
    env: Any,
    orders: list[dict[str, Any]],
    routing_name: str,
    params: dict[str, Any],
) -> float | None:
    transitions = [
        _due_seconds(order) - _single_order_trip_seconds(order, routing_name, params)
        for order in orders
    ]
    future = [instant for instant in transitions if instant >= float(env.now)]
    if not future:
        return None
    # Urgency is strict (> due), hence the tiny epsilon after equality.
    return min(future) - float(env.now) + 1e-9


def _enqueue_composed_cycle(
    order_pool: Any,
    io_pool: Any,
    candidates: list[dict[str, Any]],
    cart_capacity: int,
    batching_type: str,
) -> int:
    """Compose and enqueue no more batches than unreserved picker slots."""
    slots = io_pool.get_release_slots()
    if slots <= 0 or not candidates:
        return 0
    batches = batching_method(candidates, cart_capacity, [], batching_type)[:slots]
    released = [order for batch in batches for order in batch]
    for batch in batches:
        io_pool.add_batch(batch)
    order_pool.remove_orders([str(order["Order ID"]) for order in released])
    return len(batches)


def ftwb_trigger(env, order_pool, cart_capacity, io_pool, time_window, batching_type):
    while True:
        yield env.timeout(time_window)
        _enqueue_composed_cycle(
            order_pool,
            io_pool,
            sorted(order_pool.get_all_orders(), key=_arrival_key),
            cart_capacity,
            batching_type,
        )


def vtwb_trigger(env, order_pool, cart_capacity, io_pool, order_threshold, batching_type):
    while True:
        if order_pool.get_order_count() >= order_threshold and io_pool.get_release_slots() > 0:
            first_v = sorted(order_pool.get_all_orders(), key=_arrival_key)[:order_threshold]
            _enqueue_composed_cycle(
                order_pool, io_pool, first_v, cart_capacity, batching_type
            )
        yield _wait_for_state_change(env, order_pool, io_pool)


def max_picker_trigger(env, order_pool, cart_capacity, io_pool, num_pickers, batching_type):
    del num_pickers
    while True:
        if order_pool.get_order_count() and io_pool.get_release_slots() > 0:
            _enqueue_composed_cycle(
                order_pool,
                io_pool,
                sorted(order_pool.get_all_orders(), key=_arrival_key),
                cart_capacity,
                batching_type,
            )
        yield _wait_for_state_change(env, order_pool, io_pool)


def max_cart_trigger(env, order_pool, cart_capacity, io_pool, batching_type):
    while True:
        waiting = order_pool.get_all_orders()
        if (
            io_pool.get_release_slots() > 0
            and sum(int(order["Total Item"]) for order in waiting) >= cart_capacity
        ):
            _enqueue_composed_cycle(
                order_pool,
                io_pool,
                sorted(waiting, key=_arrival_key),
                cart_capacity,
                batching_type,
            )
        yield _wait_for_state_change(env, order_pool, io_pool)


def urgent_picker_trigger(
    env,
    order_pool,
    cart_capacity,
    io_pool,
    num_pickers,
    urgent_threshold,
    batching_type,
    routing_policy="S-shape",
    routing_config=None,
):
    while True:
        waiting = order_pool.get_all_orders()
        if waiting and io_pool.get_release_slots() > 0:
            _, urgent_count = calculate_urgent_orders(
                env, order_pool, routing_policy, io_pool, routing_config
            )
            all_idle = io_pool.get_available_pickers() == num_pickers
            if io_pool.get_release_slots() > 0 and (
                urgent_count >= urgent_threshold or all_idle
            ):
                _enqueue_composed_cycle(
                    order_pool,
                    io_pool,
                    sorted(waiting, key=_arrival_key),
                    cart_capacity,
                    batching_type,
                )
        remaining = order_pool.get_all_orders()
        yield _wait_for_state_change(
            env,
            order_pool,
            io_pool,
            _seconds_to_next_urgency(env, remaining, routing_policy, routing_config)
            if remaining
            and io_pool.get_release_slots() > 0
            and routing_config is not None
            else None,
        )


def urgent_cart_trigger(
    env,
    order_pool,
    cart_capacity,
    io_pool,
    urgent_threshold,
    batching_type,
    routing_policy="S-shape",
    routing_config=None,
):
    while True:
        waiting = order_pool.get_all_orders()
        if waiting and io_pool.get_release_slots() > 0:
            _, urgent_count = calculate_urgent_orders(
                env, order_pool, routing_policy, io_pool, routing_config
            )
            capacity_ready = (
                sum(int(order["Total Item"]) for order in waiting) >= cart_capacity
            )
            if urgent_count >= urgent_threshold or capacity_ready:
                _enqueue_composed_cycle(
                    order_pool,
                    io_pool,
                    sorted(waiting, key=_arrival_key),
                    cart_capacity,
                    batching_type,
                )
        remaining = order_pool.get_all_orders()
        yield _wait_for_state_change(
            env,
            order_pool,
            io_pool,
            _seconds_to_next_urgency(env, remaining, routing_policy, routing_config)
            if remaining
            and io_pool.get_release_slots() > 0
            and routing_config is not None
            else None,
        )


def _snh_batch(
    env: Any,
    order_pool: Any,
    cart_capacity: int,
    io_pool: Any,
    urgent_threshold: int,
    routing_name: str,
    params: dict[str, Any],
) -> tuple[list[dict[str, Any]], str]:
    waiting = order_pool.get_all_orders()
    if not waiting:
        return [], "empty"
    urgent, urgent_count = calculate_urgent_orders(
        env, order_pool, routing_name, io_pool, params
    )
    if urgent_count >= urgent_threshold:
        return _capacity_fill(sorted(urgent, key=_edt_key), cart_capacity), "urgency"

    urgency_order = sorted(waiting, key=_edt_key)
    if sum(int(order["Total Item"]) for order in urgency_order) <= cart_capacity:
        return urgency_order, "full-urgency-fit"

    capacity_order = sorted(
        waiting,
        key=lambda order: (-int(order["Total Item"]), *_edt_key(order)),
    )
    capacity_batch = _capacity_fill(capacity_order, cart_capacity)
    if capacity_batch:
        return capacity_batch, "capacity"

    hybrid_order = sorted(
        waiting,
        key=lambda order: (
            order not in urgent,
            _due_seconds(order),
            -int(order["Total Item"]),
            *_arrival_key(order),
        ),
    )
    return _capacity_fill(hybrid_order, cart_capacity), "hybrid-fallback"


def snh_trigger(
    env,
    order_pool,
    cart_capacity,
    io_pool,
    num_pickers,
    urgent_threshold,
    batching_type,
    routing_policy="S-shape",
    routing_config=None,
    algorithm_variant="base",
):
    del num_pickers, batching_type
    if algorithm_variant != "base":
        raise ValueError("Canonical SNH supports only the base variant")
    if routing_config is None:
        raise ValueError("routing_config is required for SNH")
    while True:
        while order_pool.get_order_count() and io_pool.get_release_slots() > 0:
            batch, reason = _snh_batch(
                env,
                order_pool,
                cart_capacity,
                io_pool,
                urgent_threshold,
                routing_policy,
                routing_config,
            )
            if not batch:
                break
            io_pool.add_batch(batch, release_reason=f"SNH:{reason}")
            order_pool.remove_orders([str(order["Order ID"]) for order in batch])
        yield _wait_for_state_change(env, order_pool, io_pool)


def _predicted_late_count(
    env: Any,
    orders: list[dict[str, Any]],
    routing_name: str,
    params: dict[str, Any],
) -> int:
    completion = float(env.now) + estimate_trip_seconds(orders, routing_name, params)
    return sum(completion > _due_seconds(order) for order in orders)


def _mpbh_batch(
    env: Any,
    waiting: list[dict[str, Any]],
    cart_capacity: int,
    urgent_threshold: int,
    routing_name: str,
    params: dict[str, Any],
) -> list[dict[str, Any]]:
    temporary: list[dict[str, Any]] = []
    for order in sorted(waiting, key=_edt_key):
        temporary.append(order)
        while temporary and (
            sum(int(candidate["Total Item"]) for candidate in temporary) > cart_capacity
            or _predicted_late_count(env, temporary, routing_name, params) > urgent_threshold
        ):
            latest = max(temporary, key=_edt_key)
            temporary.remove(latest)
            if latest is not order:
                continue
            break
    if temporary:
        return temporary
    # A tight due date must not deadlock the system: dispatch the earliest
    # individually capacity-feasible order and report its lateness downstream.
    return _capacity_fill(sorted(waiting, key=_edt_key), cart_capacity)[:1]


def mpbh_trigger(
    env,
    order_pool,
    cart_capacity,
    io_pool,
    batching_type,
    routing_policy="S-shape",
    routing_config=None,
    urgent_threshold=2,
    algorithm_variant="base",
):
    del batching_type
    if algorithm_variant != "base":
        raise ValueError("Canonical MPBH supports only the base variant")
    if routing_config is None:
        raise ValueError("routing_config is required for MPBH")
    while True:
        while order_pool.get_order_count() and io_pool.get_release_slots() > 0:
            batch = _mpbh_batch(
                env,
                order_pool.get_all_orders(),
                cart_capacity,
                urgent_threshold,
                routing_policy,
                routing_config,
            )
            if not batch:
                break
            io_pool.add_batch(batch, release_reason="MPBH")
            order_pool.remove_orders([str(order["Order ID"]) for order in batch])
        yield _wait_for_state_change(env, order_pool, io_pool)


def crossed_timing_composition_trigger(
    env,
    order_pool,
    cart_capacity,
    io_pool,
    *,
    timing_policy: str,
    composition_rule: str,
    batching_type: str,
    time_window: float,
    urgent_threshold: int,
    routing_policy: str,
    routing_config: dict[str, Any],
):
    """Reviewer ablation adapter with independently crossed policies.

    Addresses R1-Mayor #1. ``MPBH`` timing means state-adaptive immediate
    release whenever an unreserved picker slot and waiting order exist; its
    intrinsic batch builder is selected independently by ``composition_rule``.
    """
    if timing_policy not in {"FTWB", "MPBH"}:
        raise ValueError(f"Unsupported crossed timing policy: {timing_policy}")
    if composition_rule not in {"FCFS", "EDT", "MPBH"}:
        raise ValueError(f"Unsupported crossed composition rule: {composition_rule}")
    while True:
        if timing_policy == "FTWB":
            yield env.timeout(time_window)
        if order_pool.get_order_count() and io_pool.get_release_slots() > 0:
            if composition_rule in {"FCFS", "EDT"}:
                _enqueue_composed_cycle(
                    order_pool,
                    io_pool,
                    order_pool.get_all_orders(),
                    cart_capacity,
                    composition_rule,
                )
            else:
                while order_pool.get_order_count() and io_pool.get_release_slots() > 0:
                    batch = _mpbh_batch(
                        env,
                        order_pool.get_all_orders(),
                        cart_capacity,
                        urgent_threshold,
                        routing_policy,
                        routing_config,
                    )
                    if not batch:
                        break
                    io_pool.add_batch(batch, release_reason=f"{timing_policy}+MPBH")
                    order_pool.remove_orders([str(order["Order ID"]) for order in batch])
        if timing_policy != "FTWB":
            yield _wait_for_state_change(env, order_pool, io_pool)


SUPPORTED_TRIGGER_METHODS = {
    "FTWB",
    "VTWB",
    "MaxPicker",
    "MaxCart",
    "UrgentPicker",
    "UrgentCart",
    "SNH",
    "MPBH",
}
SUPPORTED_ROUTING_POLICIES = {"S-shape": 1, "Traversal": 1, "Largest Gap": 2}


def trigger_method(
    env, order_pool, cart_capacity, io_pool, trigger_type, batching_type, **kwargs
):
    routing_name = kwargs.get("routing_policy", "S-shape")
    if routing_name not in SUPPORTED_ROUTING_POLICIES:
        raise ValueError(f"Unknown routing policy: {routing_name}")
    common = {
        "routing_policy": routing_name,
        "routing_config": kwargs.get("routing_config"),
    }
    timing_override = kwargs.get("timing_policy_override")
    composition_override = kwargs.get("composition_rule_override")
    if timing_override or composition_override:
        if not timing_override or not composition_override:
            raise ValueError("Both timing and composition overrides are required")
        routing_config = kwargs.get("routing_config")
        if routing_config is None:
            raise ValueError("routing_config is required for crossed ablation")
        return crossed_timing_composition_trigger(
            env,
            order_pool,
            cart_capacity,
            io_pool,
            timing_policy=timing_override,
            composition_rule=composition_override,
            batching_type=batching_type,
            time_window=kwargs.get("time_window", 720),
            urgent_threshold=kwargs.get("urgent_threshold", 2),
            routing_policy=routing_name,
            routing_config=routing_config,
        )
    if trigger_type == "FTWB":
        return ftwb_trigger(
            env, order_pool, cart_capacity, io_pool, kwargs.get("time_window", 720), batching_type
        )
    if trigger_type == "VTWB":
        return vtwb_trigger(
            env,
            order_pool,
            cart_capacity,
            io_pool,
            kwargs.get("order_threshold", 12),
            batching_type,
        )
    if trigger_type == "MaxPicker":
        return max_picker_trigger(
            env, order_pool, cart_capacity, io_pool, kwargs.get("num_pickers", 1), batching_type
        )
    if trigger_type == "MaxCart":
        return max_cart_trigger(env, order_pool, cart_capacity, io_pool, batching_type)
    if trigger_type == "UrgentPicker":
        return urgent_picker_trigger(
            env,
            order_pool,
            cart_capacity,
            io_pool,
            kwargs.get("num_pickers", 1),
            kwargs.get("urgent_threshold", 2),
            batching_type,
            **common,
        )
    if trigger_type == "UrgentCart":
        return urgent_cart_trigger(
            env,
            order_pool,
            cart_capacity,
            io_pool,
            kwargs.get("urgent_threshold", 2),
            batching_type,
            **common,
        )
    if trigger_type == "SNH":
        return snh_trigger(
            env,
            order_pool,
            cart_capacity,
            io_pool,
            kwargs.get("num_pickers", 1),
            kwargs.get("urgent_threshold", 2),
            batching_type,
            algorithm_variant=kwargs.get("algorithm_variant", "base"),
            **common,
        )
    if trigger_type == "MPBH":
        return mpbh_trigger(
            env,
            order_pool,
            cart_capacity,
            io_pool,
            batching_type,
            urgent_threshold=kwargs.get("urgent_threshold", 2),
            algorithm_variant=kwargs.get("algorithm_variant", "base"),
            **common,
        )
    raise ValueError(f"Unknown trigger type: {trigger_type}")
