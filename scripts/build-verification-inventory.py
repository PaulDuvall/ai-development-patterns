#!/usr/bin/env python3
"""Build and select the deterministic pattern-verification worklist.

This moves catalog parsing, freshness ordering, and in-flight de-duplication out
of the research agent. The generated inventory is ephemeral and gitignored.
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

import yaml


MAX_EXECUTION_UNITS = 256
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
EXPERIMENT_ROW_RE = re.compile(
    r"^\|\s*\*\*\[([^]]+)\]\(#([a-z0-9-]+)\)\*\*\s*\|\s*"
    r"(Beginner|Intermediate|Advanced)\s*\|\s*([^|]+)\|"
)


def load_catalog(registry_path, experiments_path):
    """Return catalog records in stable main-then-experimental order."""
    registry = yaml.safe_load(Path(registry_path).read_text(encoding="utf-8"))
    records = [
        {
            "name": item["name"],
            "slug": item["id"],
            "type": item.get("category", "unknown"),
            "maturity": item.get("maturity", "unknown"),
            "location": "main",
        }
        for item in registry.get("patterns", [])
    ]
    for line in Path(experiments_path).read_text(encoding="utf-8").splitlines():
        match = EXPERIMENT_ROW_RE.match(line)
        if match:
            name, slug, maturity, pattern_type = match.groups()
            records.append({
                "name": name,
                "slug": slug,
                "type": pattern_type.strip().casefold(),
                "maturity": maturity.casefold(),
                "location": "experimental",
            })
    slugs = [record["slug"] for record in records]
    if len(slugs) != len(set(slugs)):
        raise ValueError("catalog contains duplicate pattern slugs")
    return records


def load_inflight(path):
    """Return slugs already changed by an open verification PR."""
    if not path:
        return set()
    source = Path(path)
    if not source.exists():
        return set()
    return {
        line.strip() for line in source.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def evidence_summary(evidence_dir, slug, today, stale_days):
    """Return evidence metadata and refresh state for one catalog record."""
    path = Path(evidence_dir) / f"{slug}.yaml"
    if not path.is_file():
        return {
            "last_checked": None,
            "evidence_count": 0,
            "provenance_status": None,
            "aliases": [],
            "refresh_state": "missing",
        }
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    checked_text = data.get("last_checked")
    checked = None
    try:
        checked = datetime.date.fromisoformat(str(checked_text))
    except (TypeError, ValueError):
        pass
    if data.get("provenance_status") != "complete":
        state = "needs-refresh"
    elif checked is None or (today - checked).days > stale_days:
        state = "stale"
    else:
        state = "current"
    evidence = data.get("evidence")
    variants = data.get("terminology_variants") or []
    return {
        "last_checked": str(checked_text) if checked_text else None,
        "evidence_count": len(evidence) if isinstance(evidence, list) else 0,
        "provenance_status": data.get("provenance_status"),
        "aliases": [item["term"] for item in variants
                    if isinstance(item, dict) and item.get("term")],
        "refresh_state": state,
    }


def build_inventory(catalog, evidence_dir, inflight, today, stale_days):
    """Join catalog, evidence, and open-PR state into one inventory."""
    inventory = []
    for record in catalog:
        item = dict(record)
        item.update(evidence_summary(evidence_dir, record["slug"], today, stale_days))
        item["in_flight"] = record["slug"] in inflight
        inventory.append(item)
    return inventory


def select_work(inventory, mode, pattern=None, limit=10):
    """Select a stable bounded worklist without model judgment."""
    if mode == "discover-only":
        return []
    available = [item for item in inventory if not item["in_flight"]]
    if mode == "single-pattern":
        matches = [item for item in available if item["name"] == pattern]
        if not matches:
            raise ValueError(f"pattern is unknown or already in flight: {pattern!r}")
        return matches
    if mode == "full":
        selected = available
    else:
        priority = {"missing": 0, "needs-refresh": 1, "stale": 2, "current": 3}
        selected = [item for item in available if item["refresh_state"] != "current"]
        selected.sort(key=lambda item: (
            0 if item["location"] == "main" else 1,
            priority[item["refresh_state"]],
            item["last_checked"] or "",
            item["slug"],
        ))
    return selected[:limit] if limit else selected


def build_execution_matrix(
        selected, mode, unit_dir="verification/run-plan/units"):
    """Return one immutable research unit per pattern plus optional discovery."""
    unit_dir = Path(unit_dir)
    units = []
    for index, item in enumerate(selected, 1):
        slug = item["slug"]
        if not isinstance(slug, str) or SLUG_RE.fullmatch(slug) is None:
            raise ValueError(f"selected pattern has an unsafe slug: {slug!r}")
        unit_id = f"evidence-{index:03d}-{slug}"
        units.append({
            "unit_id": unit_id,
            "kind": "evidence",
            "slug": slug,
            "selected_slugs_json": json.dumps([slug], separators=(",", ":")),
            "worklist": (unit_dir / f"{unit_id}.txt").as_posix(),
        })
    if mode in {"full", "discover-only"}:
        units.append({
            "unit_id": "discovery",
            "kind": "discovery",
            "slug": "",
            "selected_slugs_json": "[]",
            "worklist": (unit_dir / "discovery.txt").as_posix(),
        })
    if len(units) > MAX_EXECUTION_UNITS:
        raise ValueError(
            f"execution plan exceeds GitHub's {MAX_EXECUTION_UNITS}-job matrix limit")
    # GitHub rejects an empty matrix before a job-level condition can reliably
    # short-circuit it. The sentinel is never executed because has_units=false.
    include = units or [{
        "unit_id": "noop",
        "kind": "noop",
        "slug": "",
        "selected_slugs_json": "[]",
        "worklist": (unit_dir / "noop.txt").as_posix(),
    }]
    return {"include": include}, units


def write_execution_plan(matrix, units, unit_dir, matrix_output):
    """Persist auditable unit worklists and a compact Actions matrix."""
    directory = Path(unit_dir)
    directory.mkdir(parents=True, exist_ok=True)
    for unit in units:
        slugs = json.loads(unit["selected_slugs_json"])
        (directory / f"{unit['unit_id']}.txt").write_text(
            "".join(f"{slug}\n" for slug in slugs), encoding="utf-8")
    Path(matrix_output).write_text(
        json.dumps(matrix, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default="patterns.yaml")
    parser.add_argument("--experiments", default="experiments/README.md")
    parser.add_argument("--evidence-dir", default="verification/evidence")
    parser.add_argument("--inflight-slugs")
    parser.add_argument("--mode", choices=(
        "stale-default", "full", "discover-only", "single-pattern"),
        default="stale-default")
    parser.add_argument("--pattern")
    parser.add_argument("--stale-days", type=int, default=90)
    parser.add_argument("--limit", type=int, default=10,
                        help="maximum selected patterns; 0 means unlimited")
    parser.add_argument("--today", help="ISO date override for reproducible tests")
    parser.add_argument("--inventory", default="verification/pattern-inventory.yaml")
    parser.add_argument("--worklist", default=".verify-worklist")
    parser.add_argument("--unit-dir", default="verification/run-plan/units")
    parser.add_argument(
        "--matrix-output", default="verification/run-plan/execution-matrix.json")
    parser.add_argument("--json", action="store_true", help="print selected slugs as JSON")
    args = parser.parse_args()

    try:
        today = (datetime.date.fromisoformat(args.today)
                 if args.today else datetime.date.today())
        if args.stale_days < 1 or args.limit < 0:
            raise ValueError("stale-days must be positive and limit must be non-negative")
        catalog = load_catalog(args.registry, args.experiments)
        inventory = build_inventory(
            catalog, args.evidence_dir, load_inflight(args.inflight_slugs),
            today, args.stale_days)
        selected = select_work(inventory, args.mode, args.pattern, args.limit)
        matrix, units = build_execution_matrix(selected, args.mode, args.unit_dir)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    inventory_path = Path(args.inventory)
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(
        yaml.safe_dump({"generated": today.isoformat(), "patterns": inventory},
                       sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    Path(args.worklist).write_text(
        "".join(f"{item['slug']}\n" for item in selected), encoding="utf-8")
    write_execution_plan(matrix, units, args.unit_dir, args.matrix_output)
    if args.json:
        print(json.dumps([item["slug"] for item in selected]))
    else:
        print(f"Selected {len(selected)} of {len(inventory)} catalog patterns")
    return 0


if __name__ == "__main__":
    sys.exit(main())
