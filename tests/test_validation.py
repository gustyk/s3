from __future__ import annotations

import csv

import pytest

from src.validation import evaluate


def _write_rows(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["split", "metric", "observed", "simulated"])
        writer.writeheader()
        writer.writerows(rows)


def test_validation_reports_error_and_predeclared_tolerance(tmp_path):
    source = tmp_path / "validation.csv"
    _write_rows(
        source,
        [
            {"split": "calibration", "metric": "throughput", "observed": 10, "simulated": 11},
            {"split": "calibration", "metric": "throughput", "observed": 12, "simulated": 11},
            {"split": "validation", "metric": "throughput", "observed": 20, "simulated": 22},
            {"split": "validation", "metric": "throughput", "observed": 24, "simulated": 22},
        ],
    )
    report = evaluate(source, {"throughput": {"max_mae": 2, "max_rmse": 2}}, bootstrap_samples=100)
    assert report["status"] == "pass"
    validation = next(row for row in report["estimates"] if row["split"] == "validation")
    assert validation["mae"] == pytest.approx(2)
    assert validation["rmse"] == pytest.approx(2)


def test_validation_rejects_missing_holdout_and_unset_tolerance(tmp_path):
    source = tmp_path / "validation.csv"
    _write_rows(
        source,
        [{"split": "calibration", "metric": "throughput", "observed": 10, "simulated": 11}],
    )
    with pytest.raises(ValueError, match="both calibration and validation"):
        evaluate(source, {}, bootstrap_samples=100)
    _write_rows(
        source,
        [
            {"split": "calibration", "metric": "throughput", "observed": 10, "simulated": 11},
            {"split": "validation", "metric": "throughput", "observed": 10, "simulated": 11},
        ],
    )
    report = evaluate(source, {}, bootstrap_samples=100)
    assert report["status"] == "fail"
    assert "no predeclared validation tolerance" in report["violations"][0]
