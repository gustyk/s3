"""Deterministic, auditable experiment runner."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.metadata
import itertools
import json
import logging
import os
import platform
import subprocess
import sys
import time
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import simpy

from src.configuration import DEFAULT_CONFIG, LoadedConfig, load_config, load_item_probabilities
from src.io_pool import IOPool
from src.models import Order
from src.order_generator import generate_orders
from src.order_pool import OrderPool
from src.routing import calculate_total_time
from src.trigger_method import trigger_method

LOGGER = logging.getLogger(__name__)
MODEL_VERSION = "0.2.0-reviewer-canonical"
RESULT_FIELDS = [
    "run_uuid",
    "run_id",
    "repetition",
    "seed",
    "status",
    "wall_seconds",
    "error_type",
    "error_message",
    "incoming_rate",
    "cart_capacity",
    "trigger_method",
    "batching_method",
    "routing_policy",
    "algorithm_variant",
    "timing_policy",
    "composition_rule",
    "num_pickers",
    "generated_orders",
    "completed_orders",
    "outstanding_orders",
    "total_late_orders",
    "late_order_ratio",
    "on_time_rate_percent",
    "throughput_per_hour",
    "late_completed_orders",
    "late_outstanding_orders",
    "service_level_percent",
    "mean_tardiness_seconds",
    "mean_late_tardiness_seconds",
    "median_tardiness_seconds",
    "max_tardiness_seconds",
    "p95_tardiness_seconds",
    "mean_flow_time_seconds",
    "p95_flow_time_seconds",
    "mean_waiting_time_seconds",
    "p95_waiting_time_seconds",
    "picker_utility_percent",
    "picker_utilization_spread_pp",
    "mean_cart_utilization_percent",
    "trip_count",
    "warmup_seconds",
    "observation_start_seconds",
    "observation_end_seconds",
    "conservation_ok",
    "config_sha256",
    "git_commit",
    "git_dirty",
    "source_tree_sha256",
    "model_version",
    "input_sample_id",
    "sampled_due_time_min_seconds",
    "sampled_due_time_max_seconds",
    "sampled_picking_time_per_item",
    "sampled_setup_time",
    "sampled_walking_time_multiplier",
    "sampled_ftwb_interval_seconds",
    "sampled_vtwb_threshold_orders",
    "sampled_urgency_beta",
    "surrogate_calibration_id",
]

ORDER_RESULT_FIELDS = [
    "run_uuid",
    "repetition",
    "seed",
    "incoming_rate",
    "cart_capacity",
    "trigger_method",
    "batching_method",
    "routing_policy",
    "algorithm_variant",
    "num_pickers",
    "timing_policy",
    "composition_rule",
    "order_id",
    "measurement_eligible",
    "arrival_seconds",
    "due_seconds",
    "line_count",
    "total_pieces",
    "batch_id",
    "batch_release_reason",
    "batch_release_seconds",
    "batch_order_count",
    "batch_total_pieces",
    "picker_id",
    "start_seconds",
    "completion_seconds",
    "tour_time_seconds",
    "censor_seconds",
    "horizon_state",
    "waiting_observed_seconds",
    "flow_observed_seconds",
    "late_completed",
    "overdue_outstanding",
    "tardiness_seconds",
    "tardiness_lower_bound_seconds",
    "config_sha256",
    "source_tree_sha256",
    "model_version",
    "ftwb_interval_seconds",
    "vtwb_threshold_orders",
    "urgency_beta",
    "observation_start_seconds",
    "observation_end_seconds",
]


@dataclass(frozen=True)
class Scenario:
    incoming_rate_key: int
    trigger_key: int
    num_pickers: int
    batching_key: int
    cart_key: int
    routing_key: int


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _order_row_count(path: Path, compression: str) -> int:
    opener = gzip.open if compression == "gzip" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        return max(0, sum(1 for _ in handle) - 1)


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


@lru_cache(maxsize=1)
def _source_provenance() -> tuple[str, bool]:
    root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    candidates = [root / "pyproject.toml", root / "requirements.lock"]
    candidates.extend((root / "src").rglob("*.py"))
    candidates.extend((root / "config").rglob("*.yaml"))
    for path in sorted(candidates, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        content = path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    try:
        dirty = bool(
            subprocess.check_output(
                [
                    "git",
                    "status",
                    "--porcelain",
                    "--",
                    "src",
                    "config",
                    "pyproject.toml",
                    "requirements.lock",
                ],
                text=True,
                stderr=subprocess.DEVNULL,
                cwd=root,
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        dirty = True
    return digest.hexdigest(), dirty


def deterministic_seed(master_seed: int, incoming_rate_key: int, repetition: int) -> int:
    """Create CRN seed: policy choices share the same demand stream."""
    material = f"{master_seed}|arrival={incoming_rate_key}|rep={repetition}".encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def _run_uuid(config_hash: str, scenario: Scenario, repetition: int) -> str:
    material = f"{config_hash}|{scenario}|{repetition}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, material))


def _all_order_locations(order_pool: OrderPool, io_pool: IOPool) -> list[str]:
    waiting = [order["Order ID"] for order in order_pool.get_all_orders()]
    batched = [order["Order ID"] for batch in io_pool.batches for order in batch["orders"]]
    return waiting + batched


def run_simulation(
    params: dict[str, Any],
    scenario: Scenario,
    repetition: int,
    config_hash: str,
    order_records: list[dict[str, Any]] | None = None,
    trace_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    arrival_rate = float(params["incoming_rate"][scenario.incoming_rate_key])
    trigger_name = params["trigger_method"][scenario.trigger_key]
    batching_name = params["batching_method"][scenario.batching_key]
    cart_capacity = int(params["cart_capacity"][scenario.cart_key])
    routing_name = params["routing_policy"][scenario.routing_key]
    routing_strategy = 1 if routing_name in {"Traversal", "S-shape"} else 2
    observation_duration = float(params["simulation_time"])
    observation_start = float(params.get("warmup_seconds", 0.0))
    horizon = observation_start + observation_duration
    seed = deterministic_seed(int(params["master_seed"]), scenario.incoming_rate_key, repetition)
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    order_pool = OrderPool(env)
    io_pool = IOPool(env, scenario.num_pickers)

    env.process(
        generate_orders(
            env,
            order_pool,
            arrival_rate,
            horizon,
            rng,
            due_time_min_seconds=int(params["due_time_min_seconds"]),
            due_time_max_seconds=int(params["due_time_max_seconds"]),
            due_time_resolution_seconds=int(params.get("due_time_resolution_seconds", 60)),
            measurement_start_seconds=observation_start,
            item_probabilities=load_item_probabilities(params),
        )
    )

    if trace_records is not None:
        trace_interval = float(params.get("welch_observation_interval_seconds", 60))
        if trace_interval <= 0:
            raise ValueError("welch_observation_interval_seconds must be positive")

        def monitor_process():
            while True:
                pending_orders = sum(
                    len(batch["orders"])
                    for batch in io_pool.batches
                    if batch["status"] == "pending"
                )
                active_orders = sum(
                    len(batch["orders"])
                    for batch in io_pool.batches
                    if batch["status"] == "assigned"
                )
                trace_records.append(
                    {
                        "time_seconds": float(env.now),
                        "waiting_orders": order_pool.get_order_count(),
                        "pending_orders": pending_orders,
                        "active_orders": active_orders,
                        "backlog_orders": (
                            order_pool.get_order_count() + pending_orders + active_orders
                        ),
                        "completed_orders_cumulative": io_pool.total_completed_orders,
                        "active_pickers": len(io_pool.assigned_batches),
                    }
                )
                yield env.timeout(trace_interval)

        env.process(monitor_process())
    trigger_params = {
        "time_window": params["trigger_parameters"]["FTWB_interval"],
        "order_threshold": params["trigger_parameters"]["VTWB_threshold"],
        "urgent_threshold": params["trigger_parameters"]["Urgent_threshold"],
        "num_pickers": scenario.num_pickers,
        "routing_policy": routing_name,
        "routing_config": params,
        "algorithm_variant": params["algorithm_variant"],
        "timing_policy_override": params.get("timing_policy_override"),
        "composition_rule_override": params.get("composition_rule_override"),
    }
    env.process(
        trigger_method(
            env, order_pool, cart_capacity, io_pool, trigger_name, batching_name, **trigger_params
        )
    )

    def picker_process(picker_id: str):
        while True:
            batch = io_pool.assign_batch_to_picker(picker_id)
            if batch is None:
                yield io_pool.wait_for_change()
                continue
            items = [item for order in batch["orders"] for item in order["Order List"]]
            trip_time = calculate_total_time(items, routing_strategy, params)
            yield env.timeout(trip_time)
            if not io_pool.complete_batch(picker_id, trip_time):
                raise RuntimeError(f"Could not complete picker assignment: {picker_id}")

    for index in range(scenario.num_pickers):
        env.process(picker_process(f"Picker{index + 1}"))
    env.run(until=horizon)

    generated_all = order_pool.get_generated_orders()
    eligible_orders = [
        order
        for order in generated_all
        if float(order["Created Time Seconds"]) >= observation_start
    ]
    generated = len(eligible_orders)
    locations = _all_order_locations(order_pool, io_pool)
    if len(locations) != len(set(locations)):
        raise AssertionError("Order appears in more than one terminal location")
    conservation_ok = set(locations) == order_pool.generated_order_ids
    if not conservation_ok:
        raise AssertionError("Order conservation invariant failed")

    stats = io_pool.get_stats(observation_start, horizon)
    outstanding = generated - stats["total_completed_orders"]
    completed_ids = set(stats["completed_order_ids"])
    outstanding_orders = [
        order for order in eligible_orders if str(order["Order ID"]) not in completed_ids
    ]
    late_outstanding = sum(_due_seconds(order) < horizon for order in outstanding_orders)
    completed = stats["total_completed_orders"]
    total_late = stats["total_late_orders"] + late_outstanding
    late_ratio = total_late / generated if generated else 0.0
    service_level = (1.0 - late_ratio) * 100
    completed_batches = [
        batch
        for batch in io_pool.get_completed_batches()
        if any(float(order["Created Time Seconds"]) >= observation_start for order in batch["orders"])
        and float(batch["completion_time"]) <= horizon
    ]
    cart_utils = [batch["total_items"] / cart_capacity * 100 for batch in completed_batches]
    source_hash, git_dirty = _source_provenance()
    run_uuid = _run_uuid(config_hash, scenario, repetition)

    state_by_order: dict[str, str] = {
        str(order["Order ID"]): "waiting" for order in order_pool.get_all_orders()
    }
    for batch in io_pool.batches:
        for order in batch["orders"]:
            state_by_order[str(order["Order ID"])] = str(batch["status"])
    if order_records is not None:
        for order in generated_all:
            order_id = str(order["Order ID"])
            state = state_by_order[order_id]
            arrival = float(order["Created Time Seconds"])
            due = float(order["Due Time Seconds"])
            start = order.get("Picking Start Time Seconds")
            completion = order.get("Completion Time Seconds")
            completed_late = completion is not None and float(completion) > due
            overdue_outstanding = completion is None and due < horizon
            observed_waiting = (
                float(start) - arrival if start is not None else horizon - arrival
            )
            observed_flow = (
                float(completion) - arrival if completion is not None else horizon - arrival
            )
            lower_bound = max(0.0, horizon - due) if completion is None else ""
            order_records.append(
                {
                    "run_uuid": run_uuid,
                    "repetition": repetition,
                    "seed": seed,
                    "incoming_rate": arrival_rate,
                    "cart_capacity": cart_capacity,
                    "trigger_method": trigger_name,
                    "batching_method": batching_name,
                    "routing_policy": routing_name,
                    "algorithm_variant": params["algorithm_variant"],
                    "num_pickers": scenario.num_pickers,
                    "timing_policy": params.get("timing_policy_override", trigger_name),
                    "composition_rule": params.get("composition_rule_override", batching_name),
                    "order_id": order_id,
                    "measurement_eligible": arrival >= observation_start,
                    "arrival_seconds": arrival,
                    "due_seconds": due,
                    "line_count": len(order["Order List"]),
                    "total_pieces": int(order["Total Item"]),
                    "batch_id": order.get("Batch ID", ""),
                    "batch_release_reason": order.get("Batch Release Reason", ""),
                    "batch_release_seconds": order.get("Batch Release Time Seconds", ""),
                    "batch_order_count": order.get("Batch Order Count", ""),
                    "batch_total_pieces": order.get("Batch Total Pieces", ""),
                    "picker_id": order.get("Picker ID", ""),
                    "start_seconds": "" if start is None else float(start),
                    "completion_seconds": "" if completion is None else float(completion),
                    "tour_time_seconds": order.get("Tour Time Seconds", ""),
                    "censor_seconds": "" if completion is not None else horizon,
                    "horizon_state": state,
                    "waiting_observed_seconds": observed_waiting,
                    "flow_observed_seconds": observed_flow,
                    "late_completed": bool(completed_late),
                    "overdue_outstanding": bool(overdue_outstanding),
                    "tardiness_seconds": (
                        max(0.0, float(completion) - due) if completion is not None else ""
                    ),
                    "tardiness_lower_bound_seconds": lower_bound,
                    "config_sha256": config_hash,
                    "source_tree_sha256": source_hash,
                    "model_version": MODEL_VERSION,
                    "ftwb_interval_seconds": params["trigger_parameters"]["FTWB_interval"],
                    "vtwb_threshold_orders": params["trigger_parameters"]["VTWB_threshold"],
                    "urgency_beta": params["trigger_parameters"]["Urgent_threshold"],
                    "observation_start_seconds": observation_start,
                    "observation_end_seconds": horizon,
                }
            )

    return {
        "run_uuid": run_uuid,
        "repetition": repetition,
        "seed": seed,
        "status": "success",
        "error_type": "",
        "error_message": "",
        "incoming_rate": arrival_rate,
        "cart_capacity": cart_capacity,
        "trigger_method": trigger_name,
        "batching_method": batching_name,
        "routing_policy": routing_name,
        "algorithm_variant": params["algorithm_variant"],
        "timing_policy": params.get("timing_policy_override", trigger_name),
        "composition_rule": params.get("composition_rule_override", batching_name),
        "num_pickers": scenario.num_pickers,
        "generated_orders": generated,
        "completed_orders": completed,
        "outstanding_orders": outstanding,
        "total_late_orders": total_late,
        "late_order_ratio": late_ratio,
        "on_time_rate_percent": service_level,
        "throughput_per_hour": completed / (observation_duration / 3600),
        "late_completed_orders": stats["total_late_orders"],
        "late_outstanding_orders": late_outstanding,
        "service_level_percent": service_level,
        "mean_tardiness_seconds": stats["mean_tardiness_seconds"],
        "mean_late_tardiness_seconds": stats["mean_late_tardiness_seconds"],
        "median_tardiness_seconds": stats["median_tardiness_seconds"],
        "max_tardiness_seconds": stats["max_tardiness_seconds"],
        "p95_tardiness_seconds": stats["p95_tardiness_seconds"],
        "mean_flow_time_seconds": stats["mean_flow_time_seconds"],
        "p95_flow_time_seconds": stats["p95_flow_time_seconds"],
        "mean_waiting_time_seconds": stats["mean_waiting_time_seconds"],
        "p95_waiting_time_seconds": stats["p95_waiting_time_seconds"],
        "picker_utility_percent": stats["picker_utility"],
        "picker_utilization_spread_pp": (
            max(stats["picker_utilization_by_picker"].values())
            - min(stats["picker_utilization_by_picker"].values())
        ),
        "mean_cart_utilization_percent": sum(cart_utils) / len(cart_utils) if cart_utils else 0.0,
        "trip_count": len(completed_batches),
        "warmup_seconds": observation_start,
        "observation_start_seconds": observation_start,
        "observation_end_seconds": horizon,
        "conservation_ok": conservation_ok,
        "config_sha256": config_hash,
        "git_commit": _git_commit(),
        "git_dirty": git_dirty,
        "source_tree_sha256": source_hash,
        "model_version": MODEL_VERSION,
        "input_sample_id": params.get("input_sample_id", ""),
        "sampled_due_time_min_seconds": params.get("due_time_min_seconds", ""),
        "sampled_due_time_max_seconds": params.get("due_time_max_seconds", ""),
        "sampled_picking_time_per_item": params.get("picking_time_per_item", ""),
        "sampled_setup_time": params.get("setup_time", ""),
        "sampled_walking_time_multiplier": params.get("walking_time_multiplier", 1.0),
        "sampled_ftwb_interval_seconds": params["trigger_parameters"]["FTWB_interval"],
        "sampled_vtwb_threshold_orders": params["trigger_parameters"]["VTWB_threshold"],
        "sampled_urgency_beta": params["trigger_parameters"]["Urgent_threshold"],
        "surrogate_calibration_id": params.get("travel_time_surrogate", {}).get(
            "calibration_id", "embedded-coefficients"
        ),
    }


def _due_seconds(order: Order) -> float:
    return float(order["Due Time Seconds"])


def scenarios(params: dict[str, Any], mode: str) -> Iterable[Scenario]:
    selected = params["SELECTED_CONFIGURATION"]
    if mode in {"selected", "smoke"}:
        trigger_keys = (
            list(params["trigger_method"]) if mode == "smoke" else [selected["trigger_method"]]
        )
        for trigger_key in trigger_keys:
            yield Scenario(
                selected["incoming_rate"],
                trigger_key,
                selected["num_pickers_options"],
                selected["batching_method"],
                selected["cart_capacity"],
                selected["routing_policy"],
            )
        return
    design = params["experiment_design"]
    yield from (
        Scenario(*values)
        for values in itertools.product(
            design["incoming_rate_keys"],
            design["trigger_method_keys"],
            design["num_pickers"],
            design["batching_method_keys"],
            design["cart_capacity_keys"],
            design["routing_policy_keys"],
        )
    )


def run_experiment(config: LoadedConfig, output_dir: Path, mode: str, repetitions: int) -> Path:
    persist_order_records = bool(config.values.get("persist_order_records", True))
    order_compression = str(config.values.get("order_output_compression", "gzip"))
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "results.csv"
    order_filename = "orders.csv.gz" if order_compression == "gzip" else "orders.csv"
    order_output = output_dir / order_filename
    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists():
        from src.audit_results import audit

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = len(list(scenarios(config.values, mode))) * repetitions
        if (
            manifest.get("config_sha256") != config.sha256
            or manifest.get("mode") != mode
            or int(manifest.get("expected_runs", -1)) != expected
        ):
            raise ValueError("Completed output belongs to a different experiment plan")
        current_source_hash, _ = _source_provenance()
        if manifest.get("source_tree_sha256") != current_source_hash:
            raise ValueError("Completed output was created from a different source tree")
        report = audit(output, manifest_path)
        if report["status"] != "pass":
            raise ValueError(f"Completed output failed artifact audit: {report['errors']}")
        LOGGER.info("Reusing %s fully audited completed runs", expected)
        (output_dir / "partial_results.csv").unlink(missing_ok=True)
        (output_dir / "partial_orders.csv").unlink(missing_ok=True)
        (output_dir / "partial_orders.csv.gz").unlink(missing_ok=True)
        (output_dir / "checkpoint.json").unlink(missing_ok=True)
        return output
    partial = output_dir / "partial_results.csv"
    order_partial = output_dir / (
        "partial_orders.csv.gz" if order_compression == "gzip" else "partial_orders.csv"
    )
    checkpoint = output_dir / "checkpoint.json"
    if checkpoint.exists() and not order_partial.exists() and order_output.exists():
        order_output.replace(order_partial)
    planned = [
        (scenario, repetition)
        for scenario in scenarios(config.values, mode)
        for repetition in range(repetitions)
    ]
    execution_order_seed = int.from_bytes(
        hashlib.sha256(
            f"execution|{config.values['master_seed']}|{config.sha256}".encode()
        ).digest()[:8],
        "big",
    )
    if config.values.get("randomize_execution_order", True):
        np.random.default_rng(execution_order_seed).shuffle(planned)
    planned_uuids = {
        _run_uuid(config.sha256, scenario, repetition) for scenario, repetition in planned
    }
    current_source_hash, _ = _source_provenance()
    existing: dict[str, dict[str, Any]] = {}
    batch_started_at_utc = datetime.now(UTC).isoformat()
    if checkpoint.exists():
        checkpoint_data = json.loads(checkpoint.read_text(encoding="utf-8"))
        batch_started_at_utc = str(
            checkpoint_data.get("batch_started_at_utc", batch_started_at_utc)
        )
        if checkpoint_data.get("config_sha256") != config.sha256:
            raise ValueError("Checkpoint belongs to a different configuration")
        if checkpoint_data.get("expected_runs") != len(planned):
            raise ValueError("Checkpoint expected-run count differs from current plan")
        if not partial.exists():
            raise ValueError("Checkpoint exists without partial results")
        # Roll back any append that was not certified by the last atomic checkpoint.
        # This makes a kill/power-loss between CSV/GZIP append and checkpoint commit safe.
        for artifact, size_key in (
            (partial, "partial_results_bytes"),
            (order_partial, "partial_orders_bytes"),
        ):
            if size_key in checkpoint_data and artifact.exists():
                certified_size = int(checkpoint_data[size_key])
                if artifact.stat().st_size < certified_size:
                    raise ValueError(f"{artifact.name} is shorter than its certified checkpoint")
                if artifact.stat().st_size > certified_size:
                    with artifact.open("r+b") as handle:
                        handle.truncate(certified_size)
    elif partial.exists() or order_partial.exists():
        raise ValueError("Partial artifacts exist without an atomic checkpoint")
    if partial.exists():
        with partial.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row.get("config_sha256") != config.sha256:
                    raise ValueError("Partial results belong to a different configuration")
                run_uuid = row.get("run_uuid", "")
                if not run_uuid or run_uuid in existing:
                    raise ValueError("Partial results contain missing/duplicate run UUIDs")
                if run_uuid not in planned_uuids:
                    raise ValueError("Partial results contain a run outside the current plan")
                if row.get("source_tree_sha256") != current_source_hash:
                    raise ValueError("Partial results were created from a different source tree")
                existing[run_uuid] = row
        order_counts: dict[str, int] = {}
        if order_partial.exists():
            opener = gzip.open if order_compression == "gzip" else open
            with opener(order_partial, "rt", newline="", encoding="utf-8") as handle:
                for order_row in csv.DictReader(handle):
                    order_run_uuid = order_row.get("run_uuid", "")
                    if order_run_uuid not in existing:
                        raise ValueError("Partial order data contains a run outside partial results")
                    order_counts[order_run_uuid] = order_counts.get(order_run_uuid, 0) + 1
        for run_uuid, result_row in existing.items():
            if result_row.get("status") == "success" and int(
                float(result_row.get("generated_orders", 0) or 0)
            ) > 0 and persist_order_records and order_counts.get(run_uuid, 0) == 0:
                raise ValueError("Successful partial result is missing per-order evidence")
        if checkpoint.exists() and checkpoint_data.get("completed_runs") != len(existing):
            raise ValueError("Checkpoint count differs from partial results")
        if checkpoint.exists() and checkpoint_data.get("last_run_uuid") != next(
            reversed(existing), None
        ):
            raise ValueError("Checkpoint last-run UUID differs from partial results")

    if not checkpoint.exists():
        with partial.open("w", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=RESULT_FIELDS).writeheader()
            handle.flush()
            os.fsync(handle.fileno())
        opener = gzip.open if order_compression == "gzip" else open
        with opener(order_partial, "wt", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=ORDER_RESULT_FIELDS).writeheader()
            handle.flush()
            os.fsync(handle.fileno())
        _atomic_write_json(
            checkpoint,
            {
                "config_sha256": config.sha256,
                "completed_runs": 0,
                "expected_runs": len(planned),
                "last_run_uuid": None,
                "batch_started_at_utc": batch_started_at_utc,
                "last_checkpoint_utc": datetime.now(UTC).isoformat(),
                "successful_simulation_wall_seconds": 0.0,
                "estimated_remaining_simulation_wall_seconds": None,
                "partial_results_bytes": partial.stat().st_size,
                "partial_orders_bytes": order_partial.stat().st_size,
            },
        )

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    successful_wall = sum(
        float(item.get("wall_seconds", 0) or 0)
        for item in existing.values()
        if item.get("status") == "success"
    )
    successful_count = sum(item.get("status") == "success" for item in existing.values())
    for run_id, (scenario, repetition) in enumerate(planned, 1):
        expected_uuid = _run_uuid(config.sha256, scenario, repetition)
        if expected_uuid in existing:
            row = existing[expected_uuid]
            rows.append(row)
            if row.get("status") == "failed":
                failures.append(row)
            continue
        try:
            generated_order_rows: list[dict[str, Any]] = []
            started = time.perf_counter()
            row = run_simulation(
                config.values,
                scenario,
                repetition,
                config.sha256,
                order_records=generated_order_rows if persist_order_records else None,
            )
            row["wall_seconds"] = time.perf_counter() - started
        except Exception as error:
            LOGGER.exception("Run failed: scenario=%s repetition=%s", scenario, repetition)
            source_hash, git_dirty = _source_provenance()
            row = {
                "run_uuid": _run_uuid(config.sha256, scenario, repetition),
                "repetition": repetition,
                "seed": deterministic_seed(
                    config.values["master_seed"], scenario.incoming_rate_key, repetition
                ),
                "status": "failed",
                "wall_seconds": "",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "config_sha256": config.sha256,
                "git_commit": _git_commit(),
                "git_dirty": git_dirty,
                "source_tree_sha256": source_hash,
                "model_version": MODEL_VERSION,
            }
            failures.append(row)
        row["run_id"] = run_id
        rows.append(row)
        if row.get("status") == "success":
            successful_wall += float(row.get("wall_seconds", 0) or 0)
            successful_count += 1
        new_file = not partial.exists()
        with partial.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS, extrasaction="ignore")
            if new_file:
                writer.writeheader()
            writer.writerow(row)
            handle.flush()
            os.fsync(handle.fileno())
        if row["status"] == "success" and persist_order_records:
            new_order_file = not order_partial.exists()
            opener = gzip.open if order_compression == "gzip" else open
            with opener(order_partial, "at", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=ORDER_RESULT_FIELDS)
                if new_order_file:
                    writer.writeheader()
                writer.writerows(generated_order_rows)
                handle.flush()
                os.fsync(handle.fileno())
        checkpoint_payload = {
            "config_sha256": config.sha256,
            "completed_runs": len(rows),
            "expected_runs": len(planned),
            "last_run_uuid": row["run_uuid"],
            "batch_started_at_utc": batch_started_at_utc,
            "last_checkpoint_utc": datetime.now(UTC).isoformat(),
        }
        checkpoint_payload["successful_simulation_wall_seconds"] = successful_wall
        checkpoint_payload["estimated_remaining_simulation_wall_seconds"] = (
            successful_wall / successful_count * (len(planned) - len(rows))
            if successful_count
            else None
        )
        checkpoint_payload["partial_results_bytes"] = partial.stat().st_size
        checkpoint_payload["partial_orders_bytes"] = (
            order_partial.stat().st_size if order_partial.exists() else 0
        )
        _atomic_write_json(checkpoint, checkpoint_payload)

    temporary = output.with_suffix(".csv.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    if order_partial.exists():
        order_partial.replace(order_output)
    else:
        opener = gzip.open if order_compression == "gzip" else open
        with opener(order_output, "wt", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=ORDER_RESULT_FIELDS).writeheader()
    order_digest = hashlib.sha256(order_output.read_bytes()).hexdigest()
    source_hash, git_dirty = _source_provenance()
    manifest = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "status": "failed" if failures else "success",
        "mode": mode,
        "expected_runs": len(planned),
        "successful_runs": len(planned) - len(failures),
        "failed_runs": len(failures),
        "execution_order_randomized": bool(config.values.get("randomize_execution_order", True)),
        "execution_order_seed": execution_order_seed,
        "results_sha256": digest,
        "orders_sha256": order_digest,
        "order_rows": _order_row_count(order_output, order_compression),
        "orders_file": order_filename,
        "order_output_compression": order_compression,
        "per_order_evidence_persisted": persist_order_records,
        "config_path": str(config.path),
        "config_sha256": config.sha256,
        "git_commit": _git_commit(),
        "git_dirty": git_dirty,
        "source_tree_sha256": source_hash,
        "model_version": MODEL_VERSION,
        "dependency_lock_sha256": _file_sha256(
            Path(__file__).resolve().parents[1] / "requirements.lock"
        ),
        "python": sys.version,
        "platform": platform.platform(),
        "dependencies": {
            name: importlib.metadata.version(name) for name in ("numpy", "PyYAML", "simpy")
        },
        "successful_simulation_wall_seconds": sum(
            float(row.get("wall_seconds", 0) or 0)
            for row in rows
            if row.get("status") == "success"
        ),
    }
    _atomic_write_json(manifest_path, manifest)
    if failures:
        raise RuntimeError(f"{len(failures)} of {len(planned)} runs failed; inspect results.csv")
    partial.unlink(missing_ok=True)
    order_partial.unlink(missing_ok=True)
    checkpoint.unlink(missing_ok=True)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/latest"))
    parser.add_argument("--mode", choices=("selected", "smoke", "full"), default="selected")
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--log-level", default="WARNING")
    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    config = load_config(args.config)
    repetitions = (
        args.repetitions if args.repetitions is not None else int(config.values["repetitions"])
    )
    if repetitions <= 0:
        parser.error("--repetitions must be positive")
    output = run_experiment(config, args.output_dir.resolve(), args.mode, repetitions)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
