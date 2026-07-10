"""Tests for deterministic verification inventory and work selection."""

import datetime
import importlib.util
from pathlib import Path

import yaml


SCRIPT = Path(__file__).parent.parent / "scripts" / "build-verification-inventory.py"
SPEC = importlib.util.spec_from_file_location("verification_inventory", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def record(name, slug, location="main"):
    return {
        "name": name,
        "slug": slug,
        "type": "development",
        "maturity": "beginner",
        "location": location,
    }


def write_evidence(directory, slug, checked, provenance="complete"):
    data = {
        "last_checked": checked,
        "provenance_status": provenance,
        "evidence": [{"tier": "T1"}],
        "terminology_variants": [{"term": "Alias"}],
    }
    (directory / f"{slug}.yaml").write_text(
        yaml.safe_dump(data), encoding="utf-8")


def test_inventory_distinguishes_missing_legacy_stale_and_current(tmp_path):
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    write_evidence(evidence, "legacy", "2026-07-01", "legacy-import")
    write_evidence(evidence, "stale", "2026-01-01")
    write_evidence(evidence, "current", "2026-07-01")
    catalog = [record(name.title(), name) for name in ("missing", "legacy", "stale", "current")]

    inventory = MODULE.build_inventory(
        catalog, evidence, set(), datetime.date(2026, 7, 10), 90)

    assert [item["refresh_state"] for item in inventory] == [
        "missing", "needs-refresh", "stale", "current"]
    assert inventory[1]["aliases"] == ["Alias"]


def test_default_selection_prioritizes_main_gaps_and_excludes_inflight(tmp_path):
    catalog = [
        record("Legacy", "legacy"),
        record("Missing", "missing"),
        record("In Flight", "in-flight"),
        record("Experiment", "experiment", "experimental"),
    ]
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    write_evidence(evidence, "legacy", "2026-07-01", "legacy-import")
    inventory = MODULE.build_inventory(
        catalog, evidence, {"in-flight"}, datetime.date(2026, 7, 10), 90)

    selected = MODULE.select_work(inventory, "stale-default", limit=10)

    assert [item["slug"] for item in selected] == ["missing", "legacy", "experiment"]


def test_single_pattern_and_full_modes_are_deterministic(tmp_path):
    catalog = [record("First Pattern", "first"), record("Second Pattern", "second")]
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    inventory = MODULE.build_inventory(
        catalog, evidence, set(), datetime.date(2026, 7, 10), 90)

    assert [item["slug"] for item in MODULE.select_work(
        inventory, "single-pattern", "Second Pattern", 10)] == ["second"]
    assert [item["slug"] for item in MODULE.select_work(
        inventory, "full", limit=0)] == ["first", "second"]
    assert MODULE.select_work(inventory, "discover-only", limit=10) == []
