"""Certify final derived evidence against the immutable simulation manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def certify(root: Path) -> Path:
    main_manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    main_audit = json.loads((root / "audit.json").read_text(encoding="utf-8"))
    additional_manifest = json.loads(
        (root / "additional-metrics" / "manifest.json").read_text(encoding="utf-8")
    )
    diagnostics = json.loads(
        (root / "analysis" / "model_diagnostics.json").read_text(encoding="utf-8")
    )
    table4 = pd.read_csv(root / "composite" / "table4_corrected.csv")
    rankings = pd.read_csv(root / "composite" / "weight_sensitivity_rankings.csv")
    trigger_summary = pd.read_csv(root / "analysis" / "trigger_summary_and_pareto.csv")
    primary = pd.read_csv(root / "analysis" / "planned_adaptive_vs_static_contrasts.csv")
    extended = pd.read_csv(root / "additional-metrics" / "table4_extended.csv")

    checks = {
        "main_artifact_audit_pass": main_audit.get("status") == "pass",
        "main_expected_runs": int(main_manifest.get("expected_runs", -1)) == 207_360,
        "main_all_runs_successful": int(main_manifest.get("successful_runs", -1)) == 207_360
        and int(main_manifest.get("failed_runs", -1)) == 0,
        "results_checksum_crosscheck": _sha256(root / "results.csv")
        == main_manifest.get("results_sha256")
        == main_audit.get("sha256"),
        "additional_metrics_success": additional_manifest.get("status") == "success",
        "all_raw_order_rows_reconciled": int(additional_manifest.get("raw_total_order_rows", -1))
        == int(main_manifest.get("order_rows", -2)),
        "measurement_cohort_reconciled": int(
            additional_manifest.get("raw_measurement_orders", -1)
        )
        == int(
            pd.read_csv(root / "results.csv", usecols=["generated_orders"])[
                "generated_orders"
            ].sum()
        ),
        "eight_methods_in_all_summary_tables": len(table4) == len(trigger_summary) == len(extended) == 8,
        "four_complete_weight_schemes": rankings["weight_scheme"].nunique() == 4
        and len(rankings) == 32,
        "mpbh_rank_one_all_weight_schemes": (
            rankings.loc[rankings["trigger_method"] == "MPBH", "rank"] == 1
        ).all(),
        "six_planned_adaptive_static_contrasts": len(primary) == 6,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"Final analysis certification failed: {failed}")

    artifacts = []
    for directory in (
        root / "analysis",
        root / "composite",
        root / "additional-metrics",
        root / "manuscript-tables",
    ):
        for path in sorted(directory.rglob("*")):
            if not path.is_file() or "partials" in path.parts:
                continue
            artifacts.append(
                {
                    "path": str(path.relative_to(root)),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )
    warnings = []
    if str(main_manifest.get("git_dirty")).lower() == "true":
        warnings.append("Simulation manifest records git_dirty=True; signed clean-tag gate remains open.")
    if diagnostics["models"]["poisson"]["status"] != "fit":
        warnings.append("Poisson model is overdispersed and descriptive only.")
    if diagnostics["models"]["negative_binomial"]["status"] != "fit":
        warnings.append("Negative-binomial model did not converge and must not support inference.")

    report = {
        "status": "pass_with_documented_warnings" if warnings else "pass",
        "certified_at_utc": datetime.now(UTC).isoformat(),
        "source_results_sha256": main_manifest["results_sha256"],
        "source_orders_sha256": main_manifest["orders_sha256"],
        "source_config_sha256": main_manifest["config_sha256"],
        "checks": checks,
        "warnings": warnings,
        "derived_artifacts": artifacts,
    }
    output = root / "analysis-certification.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(certify(args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
