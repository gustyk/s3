"""Appendix A Policy Rule Verification Tests.

Exercises each trigger / batching rule directly according to specification:
1. Empty pool guard (no dispatch, r_t unaffected, no crashes).
2. Release slot reservation exhaustion (r_t = 0 implies no dispatch).
3. VTWB first-V subset selection (V_first = SortByArrival(W)[:V]).
4. UrgentPicker all-idle with urgency false (fires when available pickers == M even if U(t) < beta).
5. UrgentCart capacity-only and urgency-only trigger cases.
6. SNH 4-step execution logic (Urgency dominance, Full fit, Capacity fill, Hybrid fallback).
7. MaxCart waiting pieces >= C trigger.
8. MPBH beta = 1 and beta = 2 with late-count trim cases.
9. Property test: a single-order candidate within capacity is never trimmed for beta >= 1.
"""

from __future__ import annotations

import copy
import random
import pytest
import simpy

from src.io_pool import IOPool
from src.order_pool import OrderPool
from src.travel_surrogate import estimate_trip_seconds
from src.trigger_method import (
    _capacity_fill,
    _enqueue_composed_cycle,
    _mpbh_batch,
    _predicted_late_count,
    _snh_batch,
    calculate_urgent_orders,
    ftwb_trigger,
    max_cart_trigger,
    max_picker_trigger,
    mpbh_trigger,
    snh_trigger,
    urgent_cart_trigger,
    urgent_picker_trigger,
    vtwb_trigger,
)
from tests.conftest import make_order


# 1. Empty pool guard
def test_empty_pool_guard(small_params):
    """Empty pool should yield 0 dispatches and not mutate IO pool or raise errors."""
    env = simpy.Environment(initial_time=0)
    order_pool = OrderPool()
    io_pool = IOPool(env, 2)
    initial_slots = io_pool.get_release_slots()
    assert initial_slots == 2

    # Test direct _enqueue_composed_cycle
    batches_released = _enqueue_composed_cycle(order_pool, io_pool, [], 100, "FCFS")
    assert batches_released == 0
    assert io_pool.get_release_slots() == initial_slots
    assert len(io_pool.batches) == 0

    # Test _snh_batch with empty pool
    batch, reason = _snh_batch(env, order_pool, 100, io_pool, 2, "S-shape", small_params)
    assert batch == []
    assert reason == "empty"

    # Test _mpbh_batch with empty waiting list
    mpbh_b = _mpbh_batch(env, order_pool.get_all_orders(), 100, 2, "S-shape", small_params)
    assert mpbh_b == []


# 2. Release slot reservation exhaustion (r_t = 0 implies no dispatch)
def test_release_slot_exhaustion(small_params):
    """When r_t = 0 (no unreserved picker slots), no batches should be dispatched."""
    env = simpy.Environment(initial_time=0)
    order_pool = OrderPool()
    order1 = make_order("O1", created=10, due=1000, total=5)
    order_pool.add_order(order1)

    # IOPool with 1 picker; add a pending batch so release slots become 0
    io_pool = IOPool(env, 1)
    io_pool.add_batch([make_order("DUMMY", created=0, due=1000, total=1)])
    assert io_pool.get_release_slots() == 0

    # Attempt composition and dispatch
    candidates = order_pool.get_all_orders()
    released_count = _enqueue_composed_cycle(order_pool, io_pool, candidates, 100, "FCFS")
    assert released_count == 0
    assert order_pool.get_order_count() == 1
    assert len(io_pool.batches) == 1  # Only the dummy batch exists


# 3. VTWB first-V subset selection (V_first = SortByArrival(W)[:V])
def test_vtwb_first_v_subset(small_params):
    """VTWB selects exactly the first V orders sorted by arrival time."""
    env = simpy.Environment(initial_time=0)
    order_pool = OrderPool()
    o1 = make_order("O1", created=10.0, due=1000, total=10)
    o2 = make_order("O2", created=30.0, due=1000, total=10)
    o3 = make_order("O3", created=20.0, due=1000, total=10)
    o4 = make_order("O4", created=5.0, due=1000, total=10)
    for o in [o1, o2, o3, o4]:
        order_pool.add_order(o)

    io_pool = IOPool(env, 2)
    threshold_v = 3

    # Run VTWB trigger process
    env.process(vtwb_trigger(env, order_pool, 100, io_pool, threshold_v, "FCFS"))
    env.step()

    # The first 3 orders by arrival time are: O4 (5.0), O1 (10.0), O3 (20.0)
    # They should have been dispatched in batch
    assert len(io_pool.batches) == 1
    batch = io_pool.batches[0]["orders"]
    batch_ids = [o["Order ID"] for o in batch]
    assert batch_ids == ["O4", "O1", "O3"]
    # O2 (30.0) remains in order pool
    assert order_pool.get_order_count() == 1
    assert order_pool.get_all_orders()[0]["Order ID"] == "O2"


# 4. UrgentPicker all-idle with urgency false
def test_urgent_picker_all_idle_without_urgency(small_params):
    """UrgentPicker fires when available pickers == M even if U(t) < beta."""
    env = simpy.Environment(initial_time=0)
    order_pool = OrderPool()
    # Create non-urgent order (due date far in future)
    order = make_order("O1", created=0.0, due=999999.0, total=10)
    order_pool.add_order(order)

    num_pickers = 3
    io_pool = IOPool(env, num_pickers)
    # Check initial conditions: all pickers idle, urgency = 0
    assert io_pool.get_available_pickers() == num_pickers
    _, u_count = calculate_urgent_orders(env, order_pool, "S-shape", io_pool, small_params)
    assert u_count == 0  # U(t) = 0 < beta (where beta = 2)

    # Launch urgent picker trigger with beta = 2
    env.process(
        urgent_picker_trigger(
            env, order_pool, 100, io_pool, num_pickers, 2, "FCFS", "S-shape", small_params
        )
    )
    env.step()

    # Should have fired and dispatched the order because all pickers were idle
    assert len(io_pool.batches) == 1
    assert order_pool.get_order_count() == 0


# 5. UrgentCart capacity-only and urgency-only cases
def test_urgent_cart_capacity_only_and_urgency_only(small_params):
    """UrgentCart fires when capacity is reached (without urgency) OR when urgency threshold is reached (below capacity)."""
    # Case A: Capacity-only (Total items >= C, U(t) = 0)
    env_a = simpy.Environment(initial_time=0)
    pool_a = OrderPool()
    o_far1 = make_order("OA1", created=0.0, due=999999.0, total=15)
    o_far2 = make_order("OA2", created=1.0, due=999999.0, total=15)
    pool_a.add_order(o_far1)
    pool_a.add_order(o_far2)
    io_a = IOPool(env_a, 2)
    env_a.process(
        urgent_cart_trigger(
            env_a, pool_a, 30, io_a, 2, "FCFS", "S-shape", small_params
        )
    )
    env_a.step()
    # Fired due to capacity (15 + 15 = 30 >= 30)
    assert len(io_a.batches) == 1
    assert pool_a.get_order_count() == 0

    # Case B: Urgency-only (U(t) >= beta, Total items < C)
    env_b = simpy.Environment(initial_time=0)
    pool_b = OrderPool()
    # Create 2 urgent orders with small total items (1 item each, cart capacity = 50)
    # due must satisfy created < due
    o_urg1 = make_order("OB1", created=0.0, due=5.0, total=1)
    o_urg2 = make_order("OB2", created=1.0, due=6.0, total=1)
    pool_b.add_order(o_urg1)
    pool_b.add_order(o_urg2)
    io_b = IOPool(env_b, 2)
    env_b.process(
        urgent_cart_trigger(
            env_b, pool_b, 50, io_b, 2, "FCFS", "S-shape", small_params
        )
    )
    env_b.step()
    # Fired due to urgency (2 urgent orders >= beta=2) even though total items = 2 << 50
    assert len(io_b.batches) == 1
    assert pool_b.get_order_count() == 0


# 6. SNH 4-step execution logic (Urgency dominance, Full fit, Capacity fill, Hybrid fallback)
def test_snh_four_step_logic(small_params):
    """Test all 4 branches of SNH batching:
    Step 1: Urgency dominance (urgent >= beta).
    Step 2: Full-urgency fit (total waiting items <= C).
    Step 3: Capacity fill (largest items first).
    Step 4: Hybrid fallback.
    """
    env = simpy.Environment(initial_time=0)
    io = IOPool(env, 1)

    # Step 1: Urgency dominance
    pool1 = OrderPool()
    u1 = make_order("U1", created=0.0, due=5.0, total=10)
    u2 = make_order("U2", created=1.0, due=6.0, total=10)
    non_u = make_order("NU", created=2.0, due=999999.0, total=10)
    pool1.add_order(u1)
    pool1.add_order(u2)
    pool1.add_order(non_u)
    batch1, reason1 = _snh_batch(env, pool1, 50, io, 2, "S-shape", small_params)
    assert reason1 == "urgency"
    assert {o["Order ID"] for o in batch1} == {"U1", "U2"}

    # Step 2: Full-urgency fit (urgent < beta, total items <= C)
    pool2 = OrderPool()
    o1 = make_order("O1", created=0.0, due=999999.0, total=15)
    o2 = make_order("O2", created=1.0, due=999999.0, total=15)
    pool2.add_order(o1)
    pool2.add_order(o2)
    batch2, reason2 = _snh_batch(env, pool2, 50, io, 2, "S-shape", small_params)
    assert reason2 == "full-urgency-fit"
    assert len(batch2) == 2

    # Step 3: Capacity fill (urgent < beta, total items > C, capacity order fits)
    pool3 = OrderPool()
    # Items: 40, 20, 20 with C=50 -> largest item 40 + none or fits within 50
    # capacity_order sorts by -quantity: 40, then 20, then 20
    # _capacity_fill will take 40. Next 20 exceeds 50 (40+20=60>50). Returns [40].
    c1 = make_order("C1", created=0.0, due=999999.0, total=40)
    c2 = make_order("C2", created=1.0, due=999999.0, total=20)
    c3 = make_order("C3", created=2.0, due=999999.0, total=20)
    pool3.add_order(c1)
    pool3.add_order(c2)
    pool3.add_order(c3)
    batch3, reason3 = _snh_batch(env, pool3, 50, io, 2, "S-shape", small_params)
    assert reason3 == "capacity"
    assert [o["Order ID"] for o in batch3] == ["C1"]

    # Step 4: Hybrid fallback
    # When capacity_order does not fit even 1 item (e.g. all orders > C, or mocked edge case)
    pool4 = OrderPool()
    h1 = make_order("H1", created=0.0, due=1000.0, total=60)
    pool4.add_order(h1)
    batch4, reason4 = _snh_batch(env, pool4, 50, io, 2, "S-shape", small_params)
    assert reason4 == "hybrid-fallback"
    assert batch4 == []


# 7. MaxCart pieces >= C trigger
def test_max_cart_pieces_trigger():
    """MaxCart triggers if and only if sum(Total Item) >= cart_capacity and release slots > 0."""
    env = simpy.Environment(initial_time=0)
    pool = OrderPool(env)
    io = IOPool(env, 1)

    o1 = make_order("O1", created=0, due=1000, total=15)
    pool.add_order(o1)

    # Cart capacity is 30. o1 has 15 (< 30), so should not trigger yet.
    env.process(max_cart_trigger(env, pool, 30, io, "FCFS"))
    env.step()
    assert len(io.batches) == 0

    # Add second order with 15 pieces. Total = 30 >= 30.
    o2 = make_order("O2", created=1, due=1000, total=15)
    pool.add_order(o2)
    # Step through triggered events until batch is created
    for _ in range(5):
        if len(io.batches) > 0:
            break
        if env._queue:
            env.step()
    assert len(io.batches) == 1
    assert pool.get_order_count() == 0


# 8. MPBH beta = 1 and beta = 2 with late-count trim cases
def test_mpbh_beta_trimming(small_params):
    """MPBH trims candidates when predicted_late_count > beta."""
    env = simpy.Environment(initial_time=0)

    # Create 3 orders with tight due dates such that:
    # 1 order alone is on time, 2 orders together has 1 late, 3 orders together has 2 late
    trip_single = estimate_trip_seconds([make_order()], "S-shape", small_params)
    
    # Order A: due after single trip
    oA = make_order("OA", created=0.0, due=trip_single + 10.0, total=10, item=1)
    # Order B: due at trip_single + 15
    oB = make_order("OB", created=1.0, due=trip_single + 15.0, total=10, item=10)
    # Order C: due at trip_single + 15
    oC = make_order("OC", created=2.0, due=trip_single + 15.0, total=10, item=20)

    waiting = [oA, oB, oC]

    # For beta = 1:
    batch_beta1 = _mpbh_batch(env, waiting, 100, urgent_threshold=1, routing_name="S-shape", params=small_params)
    late_beta1 = _predicted_late_count(env, batch_beta1, "S-shape", small_params)
    assert late_beta1 <= 1

    # For beta = 2:
    batch_beta2 = _mpbh_batch(env, waiting, 100, urgent_threshold=2, routing_name="S-shape", params=small_params)
    late_beta2 = _predicted_late_count(env, batch_beta2, "S-shape", small_params)
    assert late_beta2 <= 2


# 9. Property test: one-order candidate is never trimmed for beta >= 1
def test_property_single_order_never_trimmed(small_params):
    """A single order with quantity <= cart_capacity must NEVER be trimmed/dropped by MPBH for beta >= 1."""
    rng = random.Random(42)
    for _ in range(100):
        created = rng.uniform(0.0, 1000.0)
        due_offset = rng.uniform(1.0, 5000.0)  # Ensure due > created
        total_items = rng.randint(1, 50)
        beta = rng.randint(1, 10)
        env = simpy.Environment(initial_time=created)
        order = make_order("P1", created=created, due=created + due_offset, total=total_items, item=5)
        cart_capacity = 50  # >= total_items

        batch = _mpbh_batch(env, [order], cart_capacity, urgent_threshold=beta, routing_name="S-shape", params=small_params)
        assert len(batch) == 1
        assert batch[0]["Order ID"] == "P1"


# --- Additional Dedicated Rule Tests (Reviewer Revision F7) ---
import simpy
from src.io_pool import IOPool
from src.order_pool import OrderPool
from src.trigger_method import _mpbh_batch, ftwb_trigger, max_picker_trigger
from tests.conftest import make_order


# F7a. Dedicated test of MPBH fallback branch
def test_mpbh_fallback_branch(small_params):
    """When beta=0 and all orders are predicted late, candidate empties and fallback dispatches earliest-due order."""
    env = simpy.Environment(initial_time=100.0)
    # Orders with past due dates: predicted late count is always > 0
    o1 = make_order("O_LATE_1", created=10.0, due=50.0, total=5, item=1)
    o2 = make_order("O_LATE_2", created=15.0, due=60.0, total=5, item=2)
    o3 = make_order("O_LATE_3", created=20.0, due=40.0, total=5, item=3)  # Earliest due: 40.0

    waiting = [o1, o2, o3]
    # With urgent_threshold=0, any predicted late count > 0 triggers trimming
    batch = _mpbh_batch(env, waiting, cart_capacity=100, urgent_threshold=0, routing_name="S-shape", params=small_params)
    assert len(batch) == 1
    # Must dispatch the earliest-due waiting order (O_LATE_3 with due=40.0)
    assert batch[0]["Order ID"] == "O_LATE_3"


# F7b. Dedicated FTWB periodic epoch test
def test_ftwb_periodic_epoch_trigger(small_params):
    """FTWB must NOT release between epochs; releases only at periodic interval F when release slots > 0."""
    env = simpy.Environment(initial_time=0)
    order_pool = OrderPool(env)
    io_pool = IOPool(env, num_pickers=1)
    
    o1 = make_order("O1", created=0.0, due=1000.0, total=5, item=1)
    order_pool.add_order(o1)
    
    F = 720.0
    env.process(ftwb_trigger(env, order_pool, cart_capacity=100, io_pool=io_pool, time_window=F, batching_type="FCFS"))

    # Advance time to before epoch F
    env.run(until=719.0)
    assert order_pool.get_order_count() == 1
    assert len(io_pool.batches) == 0

    # Step into epoch F (env.step or until > 720.0)
    env.run(until=720.001)
    assert order_pool.get_order_count() == 0
    assert len(io_pool.batches) == 1


# F7b. Dedicated MaxPicker immediate release test
def test_max_picker_immediate_release(small_params):
    """MaxPicker must trigger immediately as soon as pool is non-empty and release slots > 0."""
    env = simpy.Environment(initial_time=0)
    order_pool = OrderPool(env)
    io_pool = IOPool(env, num_pickers=1)

    env.process(max_picker_trigger(env, order_pool, cart_capacity=100, io_pool=io_pool, num_pickers=1, batching_type="FCFS"))

    env.run(until=10.0)
    assert len(io_pool.batches) == 0

    # Add order at t=10
    o1 = make_order("O1", created=10.0, due=1000.0, total=5, item=1)
    order_pool.add_order(o1)

    # MaxPicker should fire immediately without waiting for an epoch
    env.run(until=10.001)
    assert order_pool.get_order_count() == 0
    assert len(io_pool.batches) == 1
