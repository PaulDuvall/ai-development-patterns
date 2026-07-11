"""Tests for deterministic verification inventory and work selection."""

import datetime
import importlib.util
import json
from pathlib import Path

import pytest
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


def test_real_catalog_contains_all_main_and_experimental_patterns():
    root = Path(__file__).parent.parent
    catalog = MODULE.load_catalog(
        root / "patterns.yaml", root / "experiments" / "README.md")

    assert len(catalog) == 49
    assert sum(item["location"] == "main" for item in catalog) == 24
    assert sum(item["location"] == "experimental" for item in catalog) == 25


def test_full_execution_matrix_assigns_every_pattern_exactly_once():
    root = Path(__file__).parent.parent
    catalog = MODULE.load_catalog(
        root / "patterns.yaml", root / "experiments" / "README.md")

    matrix, units = MODULE.build_execution_matrix(catalog, "full")

    evidence_units = [unit for unit in units if unit["kind"] == "evidence"]
    assert len(evidence_units) == 49
    assert units[-1]["kind"] == "discovery"
    assert matrix["include"] == units
    selected = [json.loads(unit["selected_slugs_json"])[0]
                for unit in evidence_units]
    assert selected == [item["slug"] for item in catalog]
    assert len(selected) == len(set(selected))
    assert all(unit["unit_id"].startswith("evidence-") for unit in evidence_units)


def test_execution_matrix_respects_inflight_filtered_selection(tmp_path):
    catalog = [
        record("First Pattern", "first"),
        record("Second Pattern", "second"),
        record("Experiment Pattern", "experiment", "experimental"),
    ]
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    inventory = MODULE.build_inventory(
        catalog, evidence, {"second"}, datetime.date(2026, 7, 10), 90)
    selected = MODULE.select_work(inventory, "full", limit=0)

    _, units = MODULE.build_execution_matrix(selected, "full")

    assert [unit["slug"] for unit in units if unit["kind"] == "evidence"] == [
        "first", "experiment"]
    assert units[-1]["kind"] == "discovery"


def test_real_full_catalog_preserves_order_after_inflight_exclusions(tmp_path):
    root = Path(__file__).parent.parent
    catalog = MODULE.load_catalog(
        root / "patterns.yaml", root / "experiments" / "README.md")
    excluded = {
        "agent-readiness", "event-automation", "handoff-protocols", "bounded-autonomy",
    }
    inventory = MODULE.build_inventory(
        catalog, root / "verification" / "evidence", excluded,
        datetime.date(2026, 7, 10), 90)

    selected = MODULE.select_work(inventory, "full", limit=0)
    _, units = MODULE.build_execution_matrix(selected, "full")
    actual = [unit["slug"] for unit in units if unit["kind"] == "evidence"]
    expected = [item["slug"] for item in catalog if item["slug"] not in excluded]

    assert len(actual) == 45
    assert actual == expected
    assert not excluded.intersection(actual)
    assert units[-1]["kind"] == "discovery"


def test_no_work_uses_non_executing_matrix_sentinel():
    matrix, units = MODULE.build_execution_matrix([], "stale-default")

    assert units == []
    assert matrix == {"include": [{
        "unit_id": "noop",
        "kind": "noop",
        "slug": "",
        "selected_slugs_json": "[]",
        "worklist": "verification/run-plan/units/noop.txt",
    }]}


def test_discovery_mode_has_one_shared_file_unit():
    matrix, units = MODULE.build_execution_matrix([], "discover-only")

    assert matrix["include"] == units
    assert units == [{
        "unit_id": "discovery",
        "kind": "discovery",
        "slug": "",
        "selected_slugs_json": "[]",
        "worklist": "verification/run-plan/units/discovery.txt",
    }]


def test_execution_matrix_enforces_local_safety_limit():
    selected = [record(f"Pattern {index}", f"pattern-{index}")
                for index in range(MODULE.MAX_EXECUTION_UNITS + 1)]

    with pytest.raises(ValueError, match="unit safety limit"):
        MODULE.build_execution_matrix(selected, "stale-default")


def test_execution_plan_round_trips_unit_worklists(tmp_path):
    selected = [record("First Pattern", "first"), record("Second Pattern", "second")]
    unit_dir = tmp_path / "units"
    matrix_path = tmp_path / "matrix.json"
    matrix, units = MODULE.build_execution_matrix(
        selected, "stale-default", unit_dir)

    MODULE.write_execution_plan(matrix, units, unit_dir, matrix_path)

    assert json.loads(matrix_path.read_text(encoding="utf-8")) == matrix
    for unit in units:
        assert Path(unit["worklist"]).read_text(
            encoding="utf-8").splitlines() == json.loads(
                unit["selected_slugs_json"])
