from __future__ import annotations

import pytest

from src.benchmark import _summarize, benchmark


def test_benchmark_summary_reports_nonnegative_student_t_interval():
    rows = [
        {"benchmark": "route_kernel", "item_lines": 1, "wall_seconds": 1.0},
        {"benchmark": "route_kernel", "item_lines": 1, "wall_seconds": 3.0},
        {"benchmark": "route_kernel", "item_lines": 1, "wall_seconds": 2.0},
    ]
    summary = _summarize(rows)[0]
    assert summary["repeats"] == 3
    assert summary["wall_seconds_mean"] == pytest.approx(2)
    assert summary["wall_seconds_ci95_low"] >= 0
    assert summary["wall_seconds_ci95_high"] > summary["wall_seconds_mean"]


def test_benchmark_rejects_unreplicated_measurement(tmp_path):
    with pytest.raises(ValueError, match="repeats must be at least 2"):
        benchmark(tmp_path / "missing.yaml", tmp_path / "output", repeats=1)
