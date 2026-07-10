#!/usr/bin/env python3
"""Assemble independently validated verification units onto a trusted base."""

import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path

import yaml


SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
PLAN_ID_RE = re.compile(r"[0-9a-f]{64}")
MAX_FILE_SIZE = 5 * 1024 * 1024


def checked_file(path):
    info = path.lstat()
    if path.is_symlink() or not stat.S_ISREG(info.st_mode):
        raise ValueError(f"validated unit path is not a regular file: {path}")
    if info.st_size > MAX_FILE_SIZE:
        raise ValueError(f"validated unit file exceeds 5 MiB: {path}")
    return path.read_bytes()


def expected_units(matrix):
    data = json.loads(Path(matrix).read_text(encoding="utf-8"))
    include = data.get("include") if isinstance(data, dict) else None
    if not isinstance(include, list):
        raise ValueError("execution matrix must contain an include list")
    units = [unit for unit in include if unit.get("kind") != "noop"]
    if len({unit.get("unit_id") for unit in units}) != len(units):
        raise ValueError("execution matrix contains duplicate unit IDs")
    return units


def assemble(root, artifacts, matrix, plan_id):
    root = Path(root)
    artifacts = Path(artifacts)
    matrix = Path(matrix)
    if PLAN_ID_RE.fullmatch(plan_id or "") is None:
        raise ValueError("plan_id must be a lowercase SHA-256 digest")
    actual_plan_id = hashlib.sha256(matrix.read_bytes()).hexdigest()
    if actual_plan_id != plan_id:
        raise ValueError(
            f"execution plan digest mismatch: expected {plan_id}, got {actual_plan_id}")
    artifact_prefix = f"validated-verification-unit-{plan_id}-"
    units = expected_units(matrix)
    expected_names = {f"{artifact_prefix}{unit['unit_id']}" for unit in units}
    actual_names = {path.name for path in artifacts.iterdir() if path.is_dir()}
    if actual_names != expected_names:
        raise ValueError(
            f"validated unit set mismatch; missing={sorted(expected_names - actual_names)}, "
            f"extra={sorted(actual_names - expected_names)}")
    selected = []
    discovery_seen = False
    for unit in units:
        directory = artifacts / f"{artifact_prefix}{unit['unit_id']}"
        allowed = {"manifest.json"}
        manifest_path = directory / "manifest.json"
        manifest = json.loads(checked_file(manifest_path).decode("utf-8"))
        for field in ("unit_id", "kind", "slug"):
            if manifest.get(field) != unit.get(field):
                raise ValueError(f"{unit['unit_id']}: manifest {field} mismatch")
        if manifest.get("selected_slugs") != json.loads(unit["selected_slugs_json"]):
            raise ValueError(f"{unit['unit_id']}: manifest selected scope mismatch")
        relative = manifest.get("path")
        if unit["kind"] == "evidence":
            slug = unit["slug"]
            if SLUG_RE.fullmatch(slug or "") is None:
                raise ValueError(f"{unit['unit_id']}: unsafe evidence slug")
            expected_relative = f"verification/evidence/{slug}.yaml"
            selected.append(slug)
        elif unit["kind"] == "discovery":
            if discovery_seen:
                raise ValueError("execution matrix contains multiple discovery units")
            discovery_seen = True
            expected_relative = "experiments/NOTES.md"
        else:
            raise ValueError(f"{unit['unit_id']}: unsupported unit kind")
        if relative != expected_relative:
            raise ValueError(f"{unit['unit_id']}: manifest path mismatch")
        allowed.add(relative)
        files = {
            path.relative_to(directory).as_posix()
            for path in directory.rglob("*") if path.is_file() or path.is_symlink()
        }
        if files != allowed:
            raise ValueError(
                f"{unit['unit_id']}: unexpected validated paths: {sorted(files - allowed)}")
        source = directory / relative
        content = checked_file(source)
        if hashlib.sha256(content).hexdigest() != manifest.get("sha256"):
            raise ValueError(f"{unit['unit_id']}: evidence digest mismatch")
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    if len(selected) != len(set(selected)):
        raise ValueError("execution matrix assigns an evidence slug more than once")
    pending_path = root / "verification" / "pending-evidence.yaml"
    pending_text = pending_path.read_text(encoding="utf-8")
    pending_data = yaml.safe_load(pending_text) or {}
    pending = pending_data.get("pending")
    if not isinstance(pending, list) or not all(isinstance(slug, str) for slug in pending):
        raise ValueError("pending-evidence.yaml must contain a pending list")
    if len(pending) != len(set(pending)):
        raise ValueError("pending-evidence.yaml contains duplicate slugs")
    selected_set = set(selected)
    remaining = [slug for slug in pending if slug not in selected_set]
    marker = "pending:"
    marker_index = pending_text.find(marker)
    if marker_index < 0:
        raise ValueError("pending-evidence.yaml is missing its pending key")
    prefix = pending_text[:marker_index]
    rendered = ("pending:\n" + "".join(f"- {slug}\n" for slug in remaining)
                if remaining else "pending: []\n")
    pending_path.write_text(prefix + rendered, encoding="utf-8")
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--plan-id", required=True)
    args = parser.parse_args()
    try:
        selected = assemble(args.root, args.artifacts, args.matrix, args.plan_id)
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Assembled {len(selected)} independently validated evidence unit(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
