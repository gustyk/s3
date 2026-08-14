from __future__ import annotations

import copy

import pandas as pd
import pytest
import simpy

from src.composite_score import REFERENCE_METHODS, score_blocks
from src.io_pool import IOPool
from src.order_pool import OrderPool
from src.travel_surrogate import estimate_travel_seconds, estimate_trip_seconds, travel_features
from src.trigger_method import (
    _capacity_fill,
    _mpbh_batch,
    _snh_batch,
    calculate_urgent_orders,
    crossed_timing_composition_trigger,
    mpbh_trigger,
    snh_trigger,
    trigger_method,
)
from src.welch import recommend_warmup
from tests.conftest import make_order


def test_travel_surrogate_features_and_validation(small_params):
    order = make_order(total=3, item=33)
    assert travel_features([order], small_params) == (1.0, 1.0, 3.0, 2.0, 1.0)
    assert estimate_trip_seconds([order], "S-shape", small_params) > small_params["setup_time"]
    with pytest.raises(ValueError, match="Unknown"):
        estimate_trip_seconds([order], "unknown", small_params)
    assert travel_features([], small_params) == (1.0, 0.0, 0.0, 0.0, 0.0)
    broken = copy.deepcopy(small_params)
    broken["travel_time_surrogate"]["Traversal"] = [1]
    with pytest.raises(ValueError, match="counts differ"):
        estimate_travel_seconds([order], "S-shape", broken)


def test_paper_canonical_urgency_is_single_order_and_strict(small_params):
    env = simpy.Environment(initial_time=10)
    pool = OrderPool()
    trip = estimate_trip_seconds([make_order()], "S-shape", small_params)
    on_time = make_order("on-time", due=10 + trip)
    late = make_order("late", due=10 + trip - 1)
    pool.add_order(on_time)
    pool.add_order(late)
    urgent, count = calculate_urgent_orders(env, pool, "S-shape", None, small_params)
    assert count == 1
    assert [order["Order ID"] for order in urgent] == ["late"]
    with pytest.raises(ValueError, match="routing_config"):
        calculate_urgent_orders(env, pool)


def test_snh_and_mpbh_return_capacity_feasible_deterministic_batches(small_params):
    env = simpy.Environment(initial_time=0)
    pool = OrderPool()
    for order in [
        make_order("a", due=1000, total=60, item=1),
        make_order("b", due=1100, total=50, item=2),
        make_order("c", due=1200, total=40, item=3),
    ]:
        pool.add_order(order)
    io_pool = IOPool(env, 1)
    snh, reason = _snh_batch(env, pool, 100, io_pool, 2, "S-shape", small_params)
    assert reason in {"urgency", "full-urgency-fit", "capacity", "hybrid-fallback"}
    assert sum(order["Total Item"] for order in snh) <= 100
    mpbh = _mpbh_batch(env, pool.get_all_orders(), 100, 2, "S-shape", small_params)
    assert sum(order["Total Item"] for order in mpbh) <= 100
    assert mpbh == _mpbh_batch(env, pool.get_all_orders(), 100, 2, "S-shape", small_params)
    assert _capacity_fill(pool.get_all_orders(), 100, skip_non_fitting=False) == [
        pool.get_all_orders()[0]
    ]
    empty_pool = OrderPool()
    assert _snh_batch(env, empty_pool, 100, io_pool, 2, "S-shape", small_params) == (
        [],
        "empty",
    )


def test_canonical_policy_guards_and_dispatch_errors(small_params):
    env = simpy.Environment()
    pool = OrderPool()
    io_pool = IOPool(env, 1)
    with pytest.raises(ValueError, match="base variant"):
        next(snh_trigger(env, pool, 100, io_pool, 1, 2, "FCFS", algorithm_variant="old"))
    with pytest.raises(ValueError, match="routing_config"):
        next(snh_trigger(env, pool, 100, io_pool, 1, 2, "FCFS"))
    with pytest.raises(ValueError, match="base variant"):
        next(mpbh_trigger(env, pool, 100, io_pool, "FCFS", algorithm_variant="old"))
    with pytest.raises(ValueError, match="routing_config"):
        next(mpbh_trigger(env, pool, 100, io_pool, "FCFS"))
    with pytest.raises(ValueError, match="routing policy"):
        trigger_method(env, pool, 100, io_pool, "FTWB", "FCFS", routing_policy="bad")
    with pytest.raises(ValueError, match="Unknown trigger"):
        trigger_method(
            env,
            pool,
            100,
            io_pool,
            "bad",
            "FCFS",
            routing_policy="S-shape",
            routing_config=small_params,
        )


@pytest.mark.parametrize("timing", ["FTWB", "MPBH"])
@pytest.mark.parametrize("composition", ["FCFS", "EDT", "MPBH"])
def test_crossed_reviewer_ablation_releases_capacity_feasible_batch(
    small_params, timing, composition
):
    env = simpy.Environment()
    pool = OrderPool()
    pool.add_order(make_order("late", created=1, due=20, total=1, item=1))
    pool.add_order(make_order("early", created=0, due=500, total=1, item=2))
    pool.add_order(make_order("third", created=2, due=700, total=1, item=3))
    io_pool = IOPool(env, 1)
    process = crossed_timing_composition_trigger(
        env,
        pool,
        2,
        io_pool,
        timing_policy=timing,
        composition_rule=composition,
        batching_type="FCFS",
        time_window=5,
        urgent_threshold=2,
        routing_policy="S-shape",
        routing_config=small_params,
    )
    env.process(process)
    env.run(until=6)
    assert len(io_pool.batches) == 1
    assert sum(order["Total Item"] for order in io_pool.batches[0]["orders"]) <= 2
    assert pool.get_order_count() >= 1


def test_crossed_reviewer_ablation_guards_and_dispatch(small_params):
    env = simpy.Environment()
    pool = OrderPool()
    io_pool = IOPool(env, 1)
    with pytest.raises(ValueError, match="timing"):
        next(
            crossed_timing_composition_trigger(
                env,
                pool,
                2,
                io_pool,
                timing_policy="bad",
                composition_rule="FCFS",
                batching_type="FCFS",
                time_window=5,
                urgent_threshold=2,
                routing_policy="S-shape",
                routing_config=small_params,
            )
        )
    with pytest.raises(ValueError, match="composition"):
        next(
            crossed_timing_composition_trigger(
                env,
                pool,
                2,
                io_pool,
                timing_policy="FTWB",
                composition_rule="bad",
                batching_type="FCFS",
                time_window=5,
                urgent_threshold=2,
                routing_policy="S-shape",
                routing_config=small_params,
            )
        )
    with pytest.raises(ValueError, match="Both timing"):
        trigger_method(
            env,
            pool,
            2,
            io_pool,
            "MPBH",
            "FCFS",
            routing_policy="S-shape",
            routing_config=small_params,
            timing_policy_override="FTWB",
        )
    with pytest.raises(ValueError, match="routing_config"):
        trigger_method(
            env,
            pool,
            2,
            io_pool,
            "MPBH",
            "FCFS",
            timing_policy_override="FTWB",
            composition_rule_override="FCFS",
        )
    generated = trigger_method(
        env,
        pool,
        2,
        io_pool,
        "MPBH",
        "FCFS",
        routing_policy="S-shape",
        routing_config=small_params,
        timing_policy_override="MPBH",
        composition_rule_override="EDT",
    )
    assert generated is not None


def test_io_pool_late_and_pending_paths():
    env = simpy.Environment()
    io_pool = IOPool(env, 1)
    late = make_order("late", due=1)
    io_pool.add_batch([late])
    with pytest.raises(ValueError, match="Unknown picker"):
        io_pool.assign_batch_to_picker("X")
    assert io_pool.assign_batch_to_picker("Picker1") is not None
    env.run(until=2)
    assert io_pool.complete_batch("Picker1", 2)
    assert io_pool.get_stats()["total_late_orders"] == 1
    pending = make_order("pending", due=1)
    io_pool.add_batch([pending])
    assert io_pool.check_late_pending_orders(2) == 1


def test_composite_uses_matched_blocks_and_constant_ties():
    rows = []
    for index, method in enumerate(REFERENCE_METHODS):
        rows.append(
            {
                "incoming_rate": 1,
                "num_pickers": 1,
                "batching_method": "FCFS",
                "cart_capacity": 100,
                "routing_policy": "S-shape",
                "repetition": 0,
                "seed": 7,
                "trigger_method": method,
                "total_late_orders": index,
                "throughput_per_hour": 10 + index,
                "picker_utility_percent": 50,
            }
        )
    scored = score_blocks(pd.DataFrame(rows))
    assert set(scored["utilisation_normalized"]) == {0.5}
    assert scored.loc[scored.trigger_method == "FTWB", "tlo_normalized"].iloc[0] == 1
    assert scored["composite_score"].between(0, 1).all()
    with pytest.raises(ValueError, match="methods"):
        score_blocks(pd.DataFrame(rows[:-1]))


def test_welch_recommender_handles_stable_trace():
    rows = []
    for method in ["FTWB", "MPBH"]:
        for repetition in range(3):
            for point in range(60):
                rows.append(
                    {
                        "trigger_method": method,
                        "repetition": repetition,
                        "time_seconds": point * 60,
                        "backlog_orders": 10 + min(point, 10) * 0.1,
                        "active_pickers": 2,
                    }
                )
    diagnostics, summary = recommend_warmup(
        pd.DataFrame(rows), interval_seconds=60, consecutive_points=5
    )
    assert not diagnostics["nonstationary_tail"].any()
    assert summary["status"] == "recommendation_available"
    assert summary["recommended_warmup_seconds"] is not None


def test_warmup_cohort_and_raw_outstanding_records(small_params):
    from src.experiment import Scenario, run_simulation

    params = copy.deepcopy(small_params)
    params["warmup_seconds"] = 120
    params["simulation_time"] = 180
    params["incoming_rate"][4] = 4
    records: list[dict] = []
    result = run_simulation(params, Scenario(4, 3, 1, 1, 1, 1), 0, "warmup", records)
    eligible = [row for row in records if row["measurement_eligible"]]
    assert result["generated_orders"] == len(eligible)
    assert result["total_late_orders"] == (
        result["late_completed_orders"] + result["late_outstanding_orders"]
    )
    assert all(row["horizon_state"] in {"waiting", "pending", "assigned", "completed"} for row in records)
    for row in records:
        if row["completion_seconds"] == "":
            assert row["censor_seconds"] == 300
            assert row["tardiness_lower_bound_seconds"] != ""
