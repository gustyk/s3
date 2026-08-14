from __future__ import annotations

import csv

import pytest

from src.input_analysis import analyze_inputs


def _write(path, values):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["parameter", "value", "split"])
        writer.writeheader()
        for index, value in enumerate(values):
            writer.writerow(
                {
                    "parameter": "pick_time",
                    "value": value,
                    "split": "calibration" if index < 12 else "validation",
                }
            )


def test_input_analysis_fits_candidates_without_using_validation_for_selection(tmp_path):
    source = tmp_path / "inputs.csv"
    _write(source, [1, 2, 2, 3, 3, 3, 4, 4, 5, 6, 7, 8, 2, 4, 6, 8])
    report = analyze_inputs(source)
    analysis = report["parameters"][0]
    assert report["status"] == "complete"
    assert analysis["calibration_n_used"] == 12
    assert analysis["validation_n"] == 4
    assert len(analysis["candidate_fits"]) == 5
    assert analysis["selected_by_calibration_aic"] in {
        fit["distribution"] for fit in analysis["candidate_fits"]
    }


def test_input_analysis_rejects_nonpositive_and_insufficient_holdout(tmp_path):
    source = tmp_path / "inputs.csv"
    _write(source, [1] * 12 + [1, 1])
    with pytest.raises(ValueError, match="at least 8 calibration and 3 validation"):
        analyze_inputs(source)
    _write(source, [1] * 12 + [1, 1, 0])
    with pytest.raises(ValueError, match="finite and positive"):
        analyze_inputs(source)
