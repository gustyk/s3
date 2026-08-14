from __future__ import annotations

import copy
import csv
import hashlib
import json

import pytest

from src.audit_results import REQUIRED_ORDER_COLUMNS, audit
from src.configuration import load_config, load_item_probabilities, validate_config
from src.design_tools import repetitions_for_ci_half_width


def test_item_profile_is_complete_and_normalized():
    params = load_config().values
    probabilities = load_item_probabilities(params)
    assert len(probabilities) == params["warehouse_items"]
    assert sum(probabilities) == pytest.approx(1)
    assert sum(probabilities[:77]) == pytest.approx(0.80)
    assert sum(probabilities[77:192]) == pytest.approx(0.15)
    assert sum(probabilities[192:]) == pytest.approx(0.05)


@pytest.mark.parametrize("mutation", ["missing", "trigger", "positive", "horizon", "design"])
def test_config_fail_fast(mutation):
    params = copy.deepcopy(load_config().values)
    if mutation == "missing":
        del params["master_seed"]
    elif mutation == "trigger":
        params["trigger_method"][99] = "unknown"
    elif mutation == "positive":
        params["incoming_rate"][1] = 0
    elif mutation == "horizon":
        params["horizon_policy"] = "unknown"
    else:
        params["experiment_design"]["trigger_method_keys"] = [999]
    with pytest.raises(ValueError):
        validate_config(params)


def test_audit_accepts_valid_and_rejects_tampering(tmp_path):
    results = tmp_path / "results.csv"
    row = {
        "run_uuid": "00000000-0000-4000-8000-000000000001", "run_id": 1,
        "repetition": 0, "seed": 1, "status": "success", "wall_seconds": 0.1,
        "generated_orders": 2, "completed_orders": 1, "outstanding_orders": 1,
        "late_completed_orders": 0, "late_outstanding_orders": 0,
        "total_late_orders": 0, "late_order_ratio": 0,
        "on_time_rate_percent": 100,
        "service_level_percent": 50, "picker_utility_percent": 20,
        "mean_cart_utilization_percent": 50, "throughput_per_hour": 1,
        "mean_tardiness_seconds": 0, "mean_flow_time_seconds": 1,
        "mean_waiting_time_seconds": 0, "trip_count": 1, "conservation_ok": True,
        "config_sha256": "a" * 64, "git_commit": "g" * 40, "git_dirty": False,
        "source_tree_sha256": "b" * 64, "model_version": "v", "incoming_rate": 1,
        "cart_capacity": 100, "trigger_method": "FTWB", "batching_method": "FCFS",
        "routing_policy": "Traversal", "num_pickers": 1,
        "sampled_ftwb_interval_seconds": 720, "sampled_vtwb_threshold_orders": 12,
        "sampled_urgency_beta": 2, "surrogate_calibration_id": "test",
    }
    fields = list(row)
    with results.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)
    digest = hashlib.sha256(results.read_bytes()).hexdigest()
    orders = tmp_path / "orders.csv"
    with orders.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted(REQUIRED_ORDER_COLUMNS))
        writer.writeheader()
        writer.writerows(
            [{**dict.fromkeys(REQUIRED_ORDER_COLUMNS, ""), "order_id": value} for value in (1, 2)]
        )
    orders_digest = hashlib.sha256(orders.read_bytes()).hexdigest()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({
            "results_sha256": digest, "expected_runs": 1, "successful_runs": 1,
            "failed_runs": 0, "status": "success", "config_sha256": "a" * 64,
            "git_commit": "g" * 40, "git_dirty": False, "source_tree_sha256": "b" * 64,
            "model_version": "v", "dependency_lock_sha256": "d" * 64,
            "orders_sha256": orders_digest, "order_rows": 2,
        }),
        encoding="utf-8",
    )
    assert audit(results, manifest)["status"] == "pass"
    with results.open("a", newline="", encoding="utf-8") as handle:
        csv.DictWriter(handle, fieldnames=fields).writerow(row)
    report = audit(results, manifest)
    assert report["status"] == "fail"
    assert "duplicate run_uuid" in report["errors"]


def test_pilot_precision_requires_valid_inputs():
    import pandas as pd

    assert repetitions_for_ci_half_width(pd.Series([1.0, 2.0, 3.0]), 1.0) >= 2
    with pytest.raises(ValueError):
        repetitions_for_ci_half_width(pd.Series([1.0]), 1.0)
    with pytest.raises(ValueError):
        repetitions_for_ci_half_width(pd.Series([1.0, 2.0]), 0)
