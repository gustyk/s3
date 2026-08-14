"""Configuration loading and fail-fast validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml

from src.batching_method import SUPPORTED_BATCHING_METHODS
from src.trigger_method import SUPPORTED_ROUTING_POLICIES, SUPPORTED_TRIGGER_METHODS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "parameters.yaml"


@dataclass(frozen=True)
class LoadedConfig:
    path: Path
    values: dict[str, Any]
    sha256: str


def load_config(path: str | Path = DEFAULT_CONFIG) -> LoadedConfig:
    resolved = Path(path).expanduser().resolve()
    raw = resolved.read_bytes()
    values = yaml.safe_load(raw)
    if not isinstance(values, dict):
        raise ValueError("Configuration root must be a mapping")
    if parent_name := values.pop("extends", None):
        parent = load_config(resolved.parent / parent_name)
        values = _deep_merge(parent.values, values)
    validate_config(values)
    canonical = json.dumps(values, sort_keys=True, separators=(",", ":")).encode()
    return LoadedConfig(resolved, values, sha256(canonical).hexdigest())


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def validate_config(params: dict[str, Any]) -> None:
    required = {
        "incoming_rate",
        "cart_capacity",
        "trigger_method",
        "batching_method",
        "routing_policy",
        "simulation_time",
        "num_pickers_options",
        "master_seed",
        "repetitions",
        "horizon_policy",
        "experiment_design",
        "algorithm_variant",
        "warmup_seconds",
        "due_time_resolution_seconds",
        "travel_time_surrogate",
    }
    missing = sorted(required - params.keys())
    if missing:
        raise ValueError(f"Missing configuration keys: {missing}")

    configured_triggers = set(params["trigger_method"].values())
    configured_batching = set(params["batching_method"].values())
    configured_routing = set(params["routing_policy"].values())
    mismatches = {
        "trigger_method": configured_triggers - SUPPORTED_TRIGGER_METHODS,
        "batching_method": configured_batching - SUPPORTED_BATCHING_METHODS,
        "routing_policy": configured_routing - SUPPORTED_ROUTING_POLICIES.keys(),
    }
    invalid = {key: sorted(value) for key, value in mismatches.items() if value}
    if invalid:
        raise ValueError(f"Configured methods have no implementation: {invalid}")

    positive_groups = ("incoming_rate", "cart_capacity")
    for group in positive_groups:
        if not params[group] or any(float(value) <= 0 for value in params[group].values()):
            raise ValueError(f"All {group} values must be positive")
    if not params["num_pickers_options"] or any(
        int(value) <= 0 for value in params["num_pickers_options"]
    ):
        raise ValueError("num_pickers_options must contain positive integers")
    if int(params["simulation_time"]) <= 0 or int(params["repetitions"]) <= 0:
        raise ValueError("simulation_time and repetitions must be positive")
    if float(params["warmup_seconds"]) < 0:
        raise ValueError("warmup_seconds must be non-negative")
    if int(params["due_time_resolution_seconds"]) <= 0:
        raise ValueError("due_time_resolution_seconds must be positive")
    if params["horizon_policy"] != "fixed_with_censoring":
        raise ValueError("Only fixed_with_censoring is currently verified")
    if params.get("order_output_compression", "gzip") not in {"gzip", "none"}:
        raise ValueError("order_output_compression must be gzip or none")
    variants = {"base"}
    if params["algorithm_variant"] not in variants:
        raise ValueError(f"Unsupported algorithm_variant: {params['algorithm_variant']}")
    surrogate = params["travel_time_surrogate"]
    feature_count = len(surrogate.get("feature_order", []))
    if feature_count == 0 or any(
        len(surrogate.get(policy, [])) != feature_count for policy in ("Traversal", "Largest Gap")
    ):
        raise ValueError("travel_time_surrogate coefficients must match feature_order")
    design = params["experiment_design"]
    references = {
        "incoming_rate_keys": params["incoming_rate"],
        "trigger_method_keys": params["trigger_method"],
        "num_pickers": params["num_pickers_options"],
        "batching_method_keys": params["batching_method"],
        "cart_capacity_keys": params["cart_capacity"],
        "routing_policy_keys": params["routing_policy"],
    }
    for field, available in references.items():
        selected = design.get(field)
        if not selected or any(value not in available for value in selected):
            raise ValueError(f"experiment_design.{field} contains unsupported values")


def load_item_probabilities(params: dict[str, Any]) -> list[float]:
    path = (PROJECT_ROOT / params["item_popularity_file"]).resolve()
    profile = yaml.safe_load(path.read_text(encoding="utf-8"))
    groups = profile.get("groups", [])
    item_count = int(params["warehouse_items"])
    values: list[float | None] = [None] * item_count
    for group in groups:
        start, end, probability = (
            int(group["start"]),
            int(group["end"]),
            float(group["probability"]),
        )
        if not 1 <= start <= end <= item_count or probability < 0:
            raise ValueError(f"Invalid item-popularity group: {group}")
        for item in range(start, end + 1):
            if values[item - 1] is not None:
                raise ValueError(f"Overlapping item-popularity group at item {item}")
            values[item - 1] = probability
    if any(value is None for value in values):
        raise ValueError("Item-popularity profile does not cover every item")
    probabilities = [float(value) for value in values if value is not None]
    if abs(sum(probabilities) - 1.0) > 1e-9:
        raise ValueError(f"Item-popularity probabilities sum to {sum(probabilities)}, not 1")
    return probabilities
