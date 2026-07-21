"""Small configuration loader with sensible defaults."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency guard
    yaml = None


DEFAULT_CONFIG: dict[str, Any] = {
    "data": {
        "seed": 42,
        "timezone": "Asia/Kolkata",
        "raw_dir": "data/raw",
        "processed_dir": "data/processed",
        "report_dir": "reports",
        "model_dir": "models",
    },
    "synthetic": {
        "start_date": "2025-07-01",
        "end_date": "2026-07-31",
        "patients": 5000,
        "doctors": 220,
        "pharmacies": 120,
        "medicines": 1200,
        "orders": 40000,
        "appointments": 18000,
    },
    "models": {"test_days": 45, "validation_days": 45, "random_state": 42},
}


def deep_merge(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    merged = {**left}
    for key, value in right.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path = "config/settings.yaml") -> dict[str, Any]:
    config_path = Path(path)
    if yaml is None or not config_path.exists():
        return DEFAULT_CONFIG
    with config_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    return deep_merge(DEFAULT_CONFIG, loaded)
