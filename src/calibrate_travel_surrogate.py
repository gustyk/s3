"""Calibrate and validate the urgency travel-time surrogate.

Addresses the paper's O(1)-per-order urgency approximation and R2-Mayor #3.
The command writes candidate coefficients; it never mutates production config.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from src.configuration import load_config, load_item_probabilities
from src.routing import calculate_total_time
from src.travel_surrogate import travel_features


def _synthetic_batch(
    rng: np.random.Generator, probabilities: np.ndarray, capacity: int
) -> list[dict[str, Any]]:
    orders: list[dict[str, Any]] = []
    used = 0
    target_orders = int(rng.integers(1, 21))
    for order_index in range(target_orders):
        lines = int(rng.integers(1, 11))
        items = rng.choice(np.arange(1, len(probabilities) + 1), lines, replace=False, p=probabilities)
        quantities = rng.integers(1, 11, size=lines)
        total = int(quantities.sum())
        if used + total > capacity:
            continue
        orders.append(
            {
                "Order ID": f"S{order_index}",
                "Order List": [
                    (int(item), int(quantity))
                    for item, quantity in zip(items, quantities, strict=True)
                ],
                "Total Item": total,
            }
        )
        used += total
    return orders or [{"Order ID": "fallback", "Order List": [(1, 1)], "Total Item": 1}]


def _metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    residual = actual - predicted
    denominator = float(((actual - actual.mean()) ** 2).sum())
    return {
        "mae_seconds": float(np.abs(residual).mean()),
        "rmse_seconds": float(np.sqrt((residual**2).mean())),
        "r_squared": 1.0 - float((residual**2).sum()) / denominator if denominator else 0.0,
        "max_abs_error_seconds": float(np.abs(residual).max()),
    }


def calibrate(config_path: Path, output_dir: Path, *, samples: int, seed: int) -> None:
    if samples < 100:
        raise ValueError("At least 100 samples are required")
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite surrogate output: {output_dir}")
    loaded = load_config(config_path)
    params = loaded.values
    rng = np.random.default_rng(seed)
    probabilities = np.asarray(load_item_probabilities(params))
    rows: list[dict[str, Any]] = []
    for sample_id in range(samples):
        capacity = int(rng.choice(list(params["cart_capacity"].values())))
        orders = _synthetic_batch(rng, probabilities, capacity)
        items = [item for order in orders for item in order["Order List"]]
        features = travel_features(orders, params)
        pieces = sum(int(order["Total Item"]) for order in orders)
        for routing_name, routing_code in (("Traversal", 1), ("Largest Gap", 2)):
            total = calculate_total_time(items, routing_code, params)
            travel = total - float(params["setup_time"]) - pieces * float(
                params["picking_time_per_item"]
            )
            rows.append(
                {
                    "sample_id": sample_id,
                    "routing_policy": routing_name,
                    "capacity": capacity,
                    "actual_travel_seconds": travel,
                    **{f"x{index}": value for index, value in enumerate(features)},
                }
            )
    output_dir.mkdir(parents=True)
    split = int(samples * 0.8)
    report: dict[str, Any] = {
        "reviewer_ids": ["R1-Mayor #1", "R2-Mayor #3"],
        "config_sha256": loaded.sha256,
        "seed": seed,
        "samples_per_policy": samples,
        "train_samples_per_policy": split,
        "holdout_samples_per_policy": samples - split,
        "feature_order": params["travel_time_surrogate"]["feature_order"],
        "policies": {},
    }
    candidate = {
        "feature_order": params["travel_time_surrogate"]["feature_order"],
        "calibration_id": f"seed-{seed}-n-{samples}-config-{loaded.sha256[:12]}",
    }
    for routing_name in ("Traversal", "Largest Gap"):
        policy_rows = [row for row in rows if row["routing_policy"] == routing_name]
        x = np.asarray([[row[f"x{i}"] for i in range(5)] for row in policy_rows], dtype=float)
        y = np.asarray([row["actual_travel_seconds"] for row in policy_rows], dtype=float)
        coefficients, *_ = np.linalg.lstsq(x[:split], y[:split], rcond=None)
        predicted = np.maximum(0.0, x[split:] @ coefficients)
        candidate[routing_name] = [float(value) for value in coefficients]
        report["policies"][routing_name] = {
            "coefficients": candidate[routing_name],
            "holdout": _metrics(y[split:], predicted),
        }
    with (output_dir / "calibration_samples.csv").open("w", encoding="utf-8") as handle:
        columns = list(rows[0])
        handle.write(",".join(columns) + "\n")
        for row in rows:
            handle.write(",".join(str(row[column]) for column in columns) + "\n")
    (output_dir / "candidate_surrogate.yaml").write_text(
        yaml.safe_dump(candidate, sort_keys=False), encoding="utf-8"
    )
    (output_dir / "calibration_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260814)
    args = parser.parse_args()
    calibrate(args.config, args.output_dir, samples=args.samples, seed=args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
