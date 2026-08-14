"""Fail-fast release-readiness checks for long experiment batches."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.artifacts import atomic_write_text
from src.configuration import load_config
from src.experiment import MODEL_VERSION, scenarios


def _git(args: list[str]) -> str:
    return subprocess.check_output(
        ["git", *args], text=True, stderr=subprocess.STDOUT
    ).strip()


def _nearest_existing_parent(path: Path) -> Path:
    candidate = path.resolve()
    while not candidate.exists():
        candidate = candidate.parent
    return candidate


def _estimate_storage(
    reference_manifest_path: Path | None, expected_runs: int, expected_order_rows: float
) -> dict[str, Any] | None:
    if reference_manifest_path is None or not reference_manifest_path.exists():
        estimated_bytes = 64 * expected_order_rows + 2048 * expected_runs
        return {
            "reference_manifest": None,
            "estimation_basis": "conservative fallback: 64 compressed bytes/order + 2 KiB/run",
            "expected_order_rows_from_arrival_process": expected_order_rows,
            "estimated_gib": estimated_bytes / 1024**3,
            "recommended_gib_with_1_5x_margin": estimated_bytes * 1.5 / 1024**3,
        }
    manifest = json.loads(reference_manifest_path.read_text(encoding="utf-8"))
    reference_runs = int(manifest["expected_runs"])
    orders_path = reference_manifest_path.parent / str(manifest["orders_file"])
    results_path = reference_manifest_path.parent / "results.csv"
    if reference_runs <= 0 or not orders_path.exists() or not results_path.exists():
        return _estimate_storage(None, expected_runs, expected_order_rows)
    reference_rows = int(manifest.get("order_rows", 0))
    if reference_rows <= 0:
        return _estimate_storage(None, expected_runs, expected_order_rows)
    measured_order_bytes_per_row = orders_path.stat().st_size / reference_rows
    # Never let a narrow/older smoke understate production storage.
    order_bytes_per_row = max(64.0, measured_order_bytes_per_row)
    result_bytes_per_run = results_path.stat().st_size / reference_runs
    estimated_bytes = (
        order_bytes_per_row * expected_order_rows + result_bytes_per_run * expected_runs
    )
    return {
        "reference_manifest": str(reference_manifest_path.resolve()),
        "reference_runs": reference_runs,
        "reference_order_rows": reference_rows,
        "measured_compressed_order_bytes_per_row": measured_order_bytes_per_row,
        "planning_compressed_order_bytes_per_row": order_bytes_per_row,
        "expected_order_rows_from_arrival_process": expected_order_rows,
        "estimated_gib": estimated_bytes / 1024**3,
        "recommended_gib_with_1_5x_margin": estimated_bytes * 1.5 / 1024**3,
    }


def build_report(
    *,
    config_path: Path,
    output_dir: Path,
    mode: str,
    repetitions: int,
    require_clean: bool,
    minimum_free_gib: float,
    reference_manifest: Path | None,
) -> dict[str, Any]:
    loaded = load_config(config_path)
    planned_scenarios = list(scenarios(loaded.values, mode))
    scenario_count = len(planned_scenarios)
    expected_runs = scenario_count * repetitions
    generation_minutes = (
        float(loaded.values["warmup_seconds"]) + float(loaded.values["simulation_time"])
    ) / 60
    expected_order_rows = repetitions * generation_minutes * sum(
        float(loaded.values["incoming_rate"][scenario.incoming_rate_key])
        for scenario in planned_scenarios
    )
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": detail})

    record("positive_repetitions", repetitions > 0, repetitions)
    canonical_main = mode != "full" or expected_runs == 207_360 or config_path.name != "parameters.yaml"
    record("canonical_main_run_count", canonical_main, expected_runs)
    record(
        "canonical_parameters",
        loaded.values["trigger_parameters"]["FTWB_interval"] == 720
        and loaded.values["trigger_parameters"]["VTWB_threshold"] == 12
        and loaded.values["picking_time_per_item"] == 5
        and loaded.values["setup_time"] == 180
        and loaded.values["warmup_seconds"] == 5460,
        {
            "F": loaded.values["trigger_parameters"]["FTWB_interval"],
            "V": loaded.values["trigger_parameters"]["VTWB_threshold"],
            "beta": loaded.values["trigger_parameters"]["Urgent_threshold"],
            "pick_seconds_per_piece": loaded.values["picking_time_per_item"],
            "setup_seconds_per_tour": loaded.values["setup_time"],
            "warmup_seconds": loaded.values["warmup_seconds"],
        },
    )
    record(
        "main_per_order_evidence",
        config_path.name != "parameters.yaml" or bool(loaded.values.get("persist_order_records", True)),
        bool(loaded.values.get("persist_order_records", True)),
    )
    record(
        "compressed_order_output",
        loaded.values.get("order_output_compression", "gzip") == "gzip",
        loaded.values.get("order_output_compression", "gzip"),
    )

    dirty = bool(_git(["status", "--porcelain", "--", "src", "config", "pyproject.toml", "requirements.lock"]))
    record("clean_source_tree", not require_clean or not dirty, {"required": require_clean, "dirty": dirty})
    commit = _git(["rev-parse", "HEAD"])
    dependency_lock = Path(__file__).resolve().parents[1] / "requirements.lock"
    record("dependency_lock_present", dependency_lock.exists(), str(dependency_lock))

    existing_manifest = output_dir / "manifest.json"
    existing_checkpoint = output_dir / "checkpoint.json"
    if existing_manifest.exists():
        existing = json.loads(existing_manifest.read_text(encoding="utf-8"))
        if "mode" in existing and "expected_runs" in existing:
            compatible = (
                existing.get("config_sha256") == loaded.sha256
                and existing.get("mode") == mode
                and int(existing.get("expected_runs", -1)) == expected_runs
            )
            detail: Any = (
                "compatible completed simulation output" if compatible else "incompatible manifest"
            )
        else:
            compatible = (
                existing.get("status") == "success"
                and existing.get("config_sha256") == loaded.sha256
            )
            detail = (
                "compatible completed aggregate output" if compatible else "incompatible aggregate manifest"
            )
    elif existing_checkpoint.exists():
        existing = json.loads(existing_checkpoint.read_text(encoding="utf-8"))
        compatible = (
            existing.get("config_sha256") == loaded.sha256
            and int(existing.get("expected_runs", -1)) == expected_runs
        )
        detail = {
            "resume_completed_runs": int(existing.get("completed_runs", 0)),
            "expected_runs": expected_runs,
        }
    else:
        compatible, detail = True, "new output directory"
    record("output_plan_compatible", compatible, detail)

    disk_root = _nearest_existing_parent(output_dir)
    disk = shutil.disk_usage(disk_root)
    free_gib = disk.free / 1024**3
    estimate = _estimate_storage(reference_manifest, expected_runs, expected_order_rows)
    required_gib = max(
        minimum_free_gib,
        0.0 if estimate is None else float(estimate["recommended_gib_with_1_5x_margin"]),
    )
    record(
        "free_disk_space",
        free_gib >= required_gib,
        {"disk_root": str(disk_root), "free_gib": free_gib, "required_gib": required_gib},
    )

    report = {
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "config_path": str(config_path.resolve()),
        "config_sha256": loaded.sha256,
        "output_dir": str(output_dir.resolve()),
        "mode": mode,
        "scenario_count": scenario_count,
        "repetitions": repetitions,
        "expected_runs": expected_runs,
        "model_version": MODEL_VERSION,
        "git_commit": commit,
        "python": sys.version,
        "platform": platform.platform(),
        "dependencies": {
            name: importlib.metadata.version(name)
            for name in ("numpy", "pandas", "PyYAML", "scipy", "simpy", "statsmodels")
        },
        "dependency_lock_sha256": (
            hashlib.sha256(dependency_lock.read_bytes()).hexdigest()
            if dependency_lock.exists()
            else None
        ),
        "storage_estimate": estimate,
        "checks": checks,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=("selected", "smoke", "full"), default="full")
    parser.add_argument("--repetitions", type=int, default=30)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--minimum-free-gib", type=float, default=10.0)
    parser.add_argument(
        "--reference-manifest",
        type=Path,
        default=Path("outputs/compression-smoke-v1/manifest.json"),
    )
    args = parser.parse_args()
    report = build_report(
        config_path=args.config,
        output_dir=args.output_dir,
        mode=args.mode,
        repetitions=args.repetitions,
        require_clean=args.require_clean,
        minimum_free_gib=args.minimum_free_gib,
        reference_manifest=args.reference_manifest,
    )
    rendered = json.dumps(report, indent=2)
    atomic_write_text(args.report, rendered + "\n")
    print(rendered)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
