#!/usr/bin/env python3
"""Activate one trusted verification-matrix unit as the model worklist."""

import argparse
import json
import re
import sys
from pathlib import Path


UNIT_RE = re.compile(r"(?:evidence-[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*|discovery)")
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def activate(matrix_path, unit_id, destination):
    matrix_path = Path(matrix_path)
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    include = matrix.get("include") if isinstance(matrix, dict) else None
    if not isinstance(include, list):
        raise ValueError("execution matrix must contain an include list")
    matches = [unit for unit in include
               if isinstance(unit, dict) and unit.get("unit_id") == unit_id]
    if len(matches) != 1 or UNIT_RE.fullmatch(unit_id) is None:
        raise ValueError(f"unknown or unsafe execution unit: {unit_id!r}")
    unit = matches[0]
    kind = unit.get("kind")
    slug = unit.get("slug")
    selected = json.loads(unit.get("selected_slugs_json", "null"))
    if kind == "evidence":
        if not isinstance(slug, str) or SLUG_RE.fullmatch(slug) is None:
            raise ValueError("evidence unit has an unsafe slug")
        if selected != [slug]:
            raise ValueError("evidence unit selected scope does not match its slug")
    elif kind == "discovery":
        if slug != "" or selected != []:
            raise ValueError("discovery unit must have an empty evidence scope")
    else:
        raise ValueError(f"execution unit has unsupported kind: {kind!r}")
    source = Path(unit.get("worklist", ""))
    source = (Path.cwd() / source).resolve() if not source.is_absolute() else source.resolve()
    expected_parent = (matrix_path.parent / "units").resolve()
    if source.parent != expected_parent or source.name != f"{unit_id}.txt":
        raise ValueError("execution unit worklist path is not canonical")
    lines = source.read_text(encoding="utf-8").splitlines()
    if lines != selected:
        raise ValueError("execution unit worklist does not match its selected scope")
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(f"{item}\n" for item in selected), encoding="utf-8")
    return unit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--unit-id", required=True)
    parser.add_argument("--destination", default="verification/run-plan/worklist.txt")
    args = parser.parse_args()
    try:
        unit = activate(args.matrix, args.unit_id, args.destination)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(unit, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
