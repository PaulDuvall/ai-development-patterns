"""Aggregate detectors and dispatch a file path to each."""
from __future__ import annotations

from pathlib import Path

import yaml

from . import python_smells, secrets

THRESHOLDS_PATH = Path(__file__).resolve().parent.parent / "thresholds.yml"


def load_thresholds() -> dict:
    if not THRESHOLDS_PATH.exists():
        return {}
    try:
        return yaml.safe_load(THRESHOLDS_PATH.read_text()) or {}
    except (OSError, yaml.YAMLError) as exc:
        print(f"detectors: could not read thresholds ({exc})", flush=True)
        return {}


def in_skip_list(file_path: str, skip_dirs: list[str]) -> bool:
    return any(seg in file_path for seg in skip_dirs)


def run_all_detectors(file_path: str) -> list[dict]:
    cfg = load_thresholds()
    if in_skip_list(file_path, cfg.get("skip_directories", [])):
        return []

    violations: list[dict] = []
    violations.extend(secrets.detect(file_path))
    if file_path.endswith(".py"):
        violations.extend(python_smells.detect(file_path, cfg))
    return violations
