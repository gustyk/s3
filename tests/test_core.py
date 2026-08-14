from __future__ import annotations

import numpy as np
import pytest
import simpy

from src.batching_method import batching_method
from src.io_pool import IOPool
from src.order_generator import format_time, generate_orders
from src.order_pool import OrderPool
from src.routing import calculate_total_time
from tests.conftest import make_order


def test_routing_single_item_golden_case():
    assert calculate_total_time([(1, 1)], 1) == 195
    assert calculate_total_time([(1, 1)], 2) == 195
    assert calculate_total_time([], 1) == 0


def test_routing_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        calculate_total_time([(1, 0)], 1)
    with pytest.raises(ValueError):
        calculate_total_time([(999, 1)], 1)
    with pytest.raises(ValueError):
        calculate_total_time([(1, 1)], 99)


def test_order_pool_contract_and_duplicate_protection():
    pool = OrderPool()
    order = make_order()
    pool.add_order(order)
    assert pool.get_generated_count() == 1
    assert pool.get_all_orders() == [order]
    with pytest.raises(ValueError, match="Duplicate"):
        pool.add_order(order)
    with pytest.raises(ValueError, match="missing"):
        pool.add_order({"Order ID": "bad"})


def test_order_pool_operations_and_validation():
    pool = OrderPool()
    later = make_order("later", created=2, due=20)
    earlier = make_order("earlier", created=1, due=10)
    pool.add_order(later)
    pool.add_order(earlier)
    assert pool.sort_orders("Due Time")[0]["Order ID"] == "earlier"
    assert pool.sort_orders("Created Time", reverse=True)[0]["Order ID"] == "later"
    assert pool.get_order_by_id("earlier") == earlier
    assert pool.remove_order("earlier") == [earlier]
    assert pool.remove_orders(["later"]) == [later]
    assert pool.get_order_count() == 0
    with pytest.raises(ValueError, match="Sort key"):
        pool.sort_orders("invalid")
    with pytest.raises(ValueError, match="timestamps"):
        pool.add_order(make_order("bad-time", created=10, due=10))
    bad_total = make_order("bad-total")
    bad_total["Total Item"] = 2
    with pytest.raises(ValueError, match="Total Item"):
        pool.add_order(bad_total)


def test_batching_respects_capacity_and_edt():
    late = make_order("late", due=200, total=60)
    early = make_order("early", due=100, total=40)
    batches = batching_method([late, early], 100, [], "EDT")
    assert [[o["Order ID"] for o in batch] for batch in batches] == [["early", "late"]]
    assert all(sum(o["Total Item"] for o in batch) <= 100 for batch in batches)
    with pytest.raises(ValueError, match="exceed"):
        batching_method([make_order(total=101)], 100, [], "FCFS")
    fcfs = batching_method([make_order("a", total=70), make_order("b", total=40)], 100, [], "FCFS")
    assert len(fcfs) == 2
    with pytest.raises(ValueError, match="positive"):
        batching_method([], 0, [], "EDT")
    with pytest.raises(ValueError, match="Unknown"):
        batching_method([], 100, [], "unknown")


def test_io_pool_due_time_equality_is_on_time():
    env = simpy.Environment(initial_time=0)
    io_pool = IOPool(env, 1)
    order = make_order(due=10)
    io_pool.add_batch([order])
    assert io_pool.assign_batch_to_picker("Picker1") is not None
    env.run(until=10)
    assert io_pool.complete_batch("Picker1", 10)
    stats = io_pool.get_stats()
    assert stats["total_late_orders"] == 0
    assert order["Tardiness Seconds"] == 0
    assert stats["picker_utility"] == 100


def test_picker_cannot_hold_two_batches():
    env = simpy.Environment()
    io_pool = IOPool(env, 1)
    io_pool.add_batch([make_order("A")])
    io_pool.add_batch([make_order("B")])
    first = io_pool.assign_batch_to_picker("Picker1")
    assert first is not None
    assert io_pool.assign_batch_to_picker("Picker1") is None
    assert io_pool.get_picker_batch("Picker1") == first
    assert len(io_pool.get_active_batches()) == 1
    assert len(io_pool.get_pending_batches()) == 1
    assert io_pool.get_available_pickers() == 0
    assert io_pool.complete_batch("unknown", 1) is False
    assert io_pool.complete_batch("Picker1", 1) is True
    assert len(io_pool.get_completed_batches()) == 1
    io_pool.clear_completed_batches()
    assert len(io_pool.get_completed_batches()) == 0


@pytest.mark.parametrize(
    ("arrival", "end", "due_min", "due_max", "message"),
    [(0, 10, 1, 2, "arrival"), (1, 0, 1, 2, "end_time"), (1, 10, 2, 2, "due-time")],
)
def test_generator_rejects_invalid_controls(arrival, end, due_min, due_max, message):
    process = generate_orders(
        simpy.Environment(),
        OrderPool(),
        arrival,
        end,
        np.random.default_rng(1),
        due_time_min_seconds=due_min,
        due_time_max_seconds=due_max,
    )
    with pytest.raises(ValueError, match=message):
        next(process)


def test_generator_rejects_invalid_item_profile():
    process = generate_orders(
        simpy.Environment(),
        OrderPool(),
        1,
        10,
        np.random.default_rng(1),
        item_probabilities=[0.2, 0.2],
    )
    with pytest.raises(ValueError, match="sum to one"):
        next(process)


def test_generator_rejects_invalid_due_resolution():
    process = generate_orders(
        simpy.Environment(),
        OrderPool(),
        1,
        10,
        np.random.default_rng(1),
        due_time_min_seconds=61,
        due_time_max_seconds=120,
        due_time_resolution_seconds=60,
    )
    with pytest.raises(ValueError, match="multiples"):
        next(process)


def test_routing_multiple_aisles_and_cache():
    traversal = calculate_total_time([(1, 1), (33, 1), (65, 1)], 1)
    largest_gap = calculate_total_time([(1, 1), (33, 1), (65, 1)], 2)
    assert traversal > 0 and largest_gap > 0
    from src.routing import calculate_total_time_cached

    assert calculate_total_time_cached(((1, 1),), 1) == 195


def test_longest_idle_picker_and_release_slot_reservation():
    env = simpy.Environment()
    io_pool = IOPool(env, 2)
    io_pool.add_batch([make_order("A")])
    assert io_pool.get_release_slots() == 1
    assert io_pool.assign_batch_to_picker("Picker2") is None
    assert io_pool.assign_batch_to_picker("Picker1") is not None
    env.run(until=5)
    assert io_pool.complete_batch("Picker1", 5)
    io_pool.add_batch([make_order("B")])
    # Picker2 has been idle since t=0 and must be assigned before Picker1.
    assert io_pool.assign_batch_to_picker("Picker1") is None
    assert io_pool.assign_batch_to_picker("Picker2") is not None


def test_routing_uses_scenario_specific_productivity(small_params):
    baseline = calculate_total_time([(1, 1)], 1, small_params)
    changed = dict(small_params)
    changed["setup_time"] = small_params["setup_time"] + 100
    assert calculate_total_time([(1, 1)], 1, changed) == baseline + 100


def test_display_time_supports_day_rollover_without_model_arithmetic():
    assert format_time(24 * 3600 + 1) == "24:00:01"
    order = make_order("next-day", created=86_390, due=86_410)
    pool = OrderPool()
    pool.add_order(order)
    assert pool.sort_orders("Due Time")[0]["Due Time Seconds"] == 86_410
