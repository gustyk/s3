from __future__ import annotations

import copy
import csv
import gzip
import json

import pytest

from src.configuration import LoadedConfig
from src.experiment import Scenario, deterministic_seed, run_experiment, run_simulation, scenarios


def test_common_random_number_seed_excludes_policy():
    assert deterministic_seed(123, 4, 0) == deterministic_seed(123, 4, 0)
    assert deterministic_seed(123, 4, 0) != deterministic_seed(123, 4, 1)


def test_same_seed_reproduces_same_result(small_params):
    scenario = Scenario(4, 3, 2, 1, 1, 1)  # MaxPicker
    first = run_simulation(small_params, scenario, 0, "config-hash")
    second = run_simulation(small_params, scenario, 0, "config-hash")
    ignored = {"git_commit"}
    assert {k: v for k, v in first.items() if k not in ignored} == {
        k: v for k, v in second.items() if k not in ignored
    }
    assert first["conservation_ok"] is True
    assert first["generated_orders"] == first["completed_orders"] + first["outstanding_orders"]


@pytest.mark.parametrize("trigger_key", range(1, 9))
def test_every_trigger_smoke(small_params, trigger_key):
    scenario = Scenario(4, trigger_key, 2, 1, 1, 1)
    result = run_simulation(small_params, scenario, 0, "config-hash")
    assert result["status"] == "success"
    assert result["conservation_ok"] is True
    assert 0 <= result["service_level_percent"] <= 100
    assert 0 <= result["picker_utility_percent"] <= 100


@pytest.mark.parametrize("trigger_key", [7, 8])
def test_canonical_advanced_algorithms_run_as_base(small_params, trigger_key):
    result = run_simulation(small_params, Scenario(4, trigger_key, 2, 1, 1, 1), 0, "base")
    assert result["status"] == "success"
    assert result["algorithm_variant"] == "base"


def test_near_zero_demand_degenerate_case_is_well_defined(small_params):
    small_params["incoming_rate"][4] = 0.001
    result = run_simulation(small_params, Scenario(4, 1, 1, 1, 1, 1), 0, "near-zero")
    assert result["generated_orders"] == 0
    assert result["completed_orders"] == 0
    assert result["service_level_percent"] == 100
    assert result["conservation_ok"] is True


def test_overload_accumulates_visible_backlog_without_losing_orders(small_params):
    small_params["simulation_time"] = 120
    small_params["incoming_rate"][4] = 100
    small_params["trigger_parameters"]["FTWB_interval"] = 10
    result = run_simulation(small_params, Scenario(4, 1, 1, 1, 1, 1), 0, "overload")
    assert result["generated_orders"] > result["completed_orders"]
    assert result["outstanding_orders"] > 0
    assert result["generated_orders"] == (
        result["completed_orders"] + result["outstanding_orders"]
    )


def test_more_pickers_do_not_reduce_completion_under_identical_demand(small_params):
    small_params["trigger_parameters"]["FTWB_interval"] = 10
    one = run_simulation(small_params, Scenario(4, 1, 1, 1, 1, 1), 0, "staffing")
    twelve = run_simulation(small_params, Scenario(4, 1, 12, 1, 1, 1), 0, "staffing")
    assert one["generated_orders"] == twelve["generated_orders"]
    assert twelve["completed_orders"] >= one["completed_orders"]


def test_relaxed_due_allowance_cannot_create_more_late_orders(small_params):
    tight = copy.deepcopy(small_params)
    relaxed = copy.deepcopy(small_params)
    tight["due_time_min_seconds"], tight["due_time_max_seconds"] = 1, 2
    relaxed["due_time_min_seconds"], relaxed["due_time_max_seconds"] = 3600, 3601
    tight["due_time_resolution_seconds"] = 1
    relaxed["due_time_resolution_seconds"] = 1
    scenario = Scenario(4, 1, 2, 1, 1, 1)
    tight_result = run_simulation(tight, scenario, 0, "due-regime")
    relaxed_result = run_simulation(relaxed, scenario, 0, "due-regime")
    tight_late = tight_result["late_completed_orders"] + tight_result["late_outstanding_orders"]
    relaxed_late = (
        relaxed_result["late_completed_orders"] + relaxed_result["late_outstanding_orders"]
    )
    assert tight_result["generated_orders"] == relaxed_result["generated_orders"]
    assert relaxed_late <= tight_late


def test_pilot_factorial_design_has_expected_size():
    from src.configuration import load_config

    params = load_config("config/pilot_factorial.yaml").values
    planned = list(scenarios(params, "full"))
    assert len(planned) == 256
    assert len(set(planned)) == 256


def test_run_experiment_writes_manifest_and_unique_rows(tmp_path, small_params):
    small_params["SELECTED_CONFIGURATION"]["trigger_method"] = 3
    config = LoadedConfig(tmp_path / "config.yaml", small_params, "abc")
    output = run_experiment(config, tmp_path / "output", "selected", 2)
    rows = list(csv.DictReader(output.open(newline="", encoding="utf-8")))
    assert len(rows) == 2
    assert len({row["run_uuid"] for row in rows}) == 2
    assert all(row["status"] == "success" for row in rows)
    assert (tmp_path / "output" / "manifest.json").exists()
    manifest = json.loads((tmp_path / "output" / "manifest.json").read_text(encoding="utf-8"))
    assert (tmp_path / "output" / manifest["orders_file"]).exists()
    assert manifest["order_rows"] >= sum(int(row["generated_orders"]) for row in rows)
    with gzip.open(
        tmp_path / "output" / manifest["orders_file"], "rt", newline="", encoding="utf-8"
    ) as handle:
        order_rows = list(csv.DictReader(handle))
    assert order_rows
    assert {
        "batch_release_reason",
        "batch_release_seconds",
        "batch_order_count",
        "batch_total_pieces",
        "tour_time_seconds",
        "urgency_beta",
        "model_version",
    } <= set(order_rows[0])


def test_auxiliary_experiment_can_omit_duplicate_order_evidence(tmp_path, small_params):
    small_params["persist_order_records"] = False
    config = LoadedConfig(tmp_path / "config.yaml", small_params, "aggregate-only")
    run_experiment(config, tmp_path / "aggregate", "selected", 1)
    manifest = json.loads(
        (tmp_path / "aggregate" / "manifest.json").read_text(encoding="utf-8")
    )
    with gzip.open(
        tmp_path / "aggregate" / manifest["orders_file"], "rt", encoding="utf-8"
    ) as handle:
        orders = list(csv.DictReader(handle))
    assert orders == []
    assert manifest["order_rows"] == 0
    assert manifest["per_order_evidence_persisted"] is False


def test_run_experiment_resumes_validated_partial_results(tmp_path, small_params, monkeypatch):
    from src import experiment

    config = LoadedConfig(tmp_path / "config.yaml", small_params, "abc")
    source = run_experiment(config, tmp_path / "source", "selected", 2)
    source_rows = list(csv.DictReader(source.open(newline="", encoding="utf-8")))
    target = tmp_path / "resumed"
    target.mkdir()
    partial = target / "partial_results.csv"
    with partial.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=experiment.RESULT_FIELDS)
        writer.writeheader()
        writer.writerow(source_rows[0])
    source_manifest = json.loads(
        (tmp_path / "source" / "manifest.json").read_text(encoding="utf-8")
    )
    with gzip.open(
        tmp_path / "source" / source_manifest["orders_file"], "rt", newline="", encoding="utf-8"
    ) as handle:
        source_order_rows = list(csv.DictReader(handle))
    with gzip.open(
        target / "partial_orders.csv.gz", "wt", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=experiment.ORDER_RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(
            row for row in source_order_rows if row["run_uuid"] == source_rows[0]["run_uuid"]
        )
    (target / "checkpoint.json").write_text(
        json.dumps(
            {
                "config_sha256": "abc",
                "completed_runs": 1,
                "expected_runs": 2,
                "last_run_uuid": source_rows[0]["run_uuid"],
            }
        ),
        encoding="utf-8",
    )
    original = experiment.run_simulation
    calls = 0

    def counted_run(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(experiment, "run_simulation", counted_run)
    output = run_experiment(config, target, "selected", 2)
    rows = list(csv.DictReader(output.open(newline="", encoding="utf-8")))
    assert calls == 1
    assert len(rows) == 2
    assert not partial.exists()
    assert not (target / "checkpoint.json").exists()


def test_interrupted_run_rolls_back_uncertified_bytes_and_reuses_completed_output(
    tmp_path, small_params, monkeypatch
):
    from src import experiment

    config = LoadedConfig(tmp_path / "config.yaml", small_params, "a" * 64)
    output_dir = tmp_path / "interrupted"
    original = experiment.run_simulation
    calls = 0

    def interrupt_second(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise KeyboardInterrupt("simulated power loss")
        return original(*args, **kwargs)

    monkeypatch.setattr(experiment, "run_simulation", interrupt_second)
    with pytest.raises(KeyboardInterrupt, match="simulated power loss"):
        run_experiment(config, output_dir, "selected", 3)

    checkpoint = json.loads((output_dir / "checkpoint.json").read_text(encoding="utf-8"))
    assert checkpoint["completed_runs"] == 1
    with (output_dir / "partial_results.csv").open("ab") as handle:
        handle.write(b"uncertified-tail")
    with (output_dir / "partial_orders.csv.gz").open("ab") as handle:
        handle.write(b"uncertified-tail")

    resumed_calls = 0

    def counted_run(*args, **kwargs):
        nonlocal resumed_calls
        resumed_calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(experiment, "run_simulation", counted_run)
    output = run_experiment(config, output_dir, "selected", 3)
    assert resumed_calls == 2
    assert len(list(csv.DictReader(output.open(encoding="utf-8")))) == 3

    monkeypatch.setattr(
        experiment,
        "run_simulation",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("must be reused")),
    )
    assert run_experiment(config, output_dir, "selected", 3) == output


def test_run_experiment_records_fault_and_exits_nonzero(tmp_path, small_params, monkeypatch):
    from src import experiment

    config = LoadedConfig(tmp_path / "config.yaml", small_params, "abc")
    monkeypatch.setattr(
        experiment,
        "run_simulation",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("injected")),
    )
    with pytest.raises(RuntimeError, match="runs failed"):
        run_experiment(config, tmp_path / "failed", "selected", 1)
    rows = list(csv.DictReader((tmp_path / "failed" / "results.csv").open(encoding="utf-8")))
    manifest = json.loads((tmp_path / "failed" / "manifest.json").read_text(encoding="utf-8"))
    assert rows[0]["status"] == "failed"
    assert rows[0]["error_type"] == "RuntimeError"
    assert manifest["status"] == "failed"
