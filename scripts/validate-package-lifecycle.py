#!/usr/bin/env python3
"""Reject introduced or modified package-manager lifecycle hooks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


LIFECYCLE_SCRIPTS = {
    "preinstall",
    "install",
    "postinstall",
    "prepare",
    "prepublish",
    "prepublishOnly",
}
IGNORED_DIRECTORIES = {".git", ".venv", "node_modules"}


def manifests(root: Path) -> dict[Path, Path]:
    """Return package manifests keyed by repository-relative path."""
    return {
        path.relative_to(root): path
        for path in root.rglob("package.json")
        if not IGNORED_DIRECTORIES.intersection(path.relative_to(root).parts)
    }


def lifecycle_scripts(path: Path | None) -> dict[str, object]:
    """Read lifecycle script values from one package manifest."""
    if path is None:
        return {}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot parse {path}: {error}") from error
    scripts = document.get("scripts", {})
    if not isinstance(scripts, dict):
        raise ValueError(f"scripts must be an object in {path}")
    return {
        name: scripts[name]
        for name in LIFECYCLE_SCRIPTS
        if name in scripts
    }


def changed_lifecycle_scripts(
    trusted_root: Path, candidate_root: Path
) -> list[str]:
    """Describe lifecycle hooks introduced or modified by the candidate."""
    trusted = manifests(trusted_root)
    candidate = manifests(candidate_root)
    findings: list[str] = []
    for relative, candidate_path in sorted(candidate.items()):
        before = lifecycle_scripts(trusted.get(relative))
        after = lifecycle_scripts(candidate_path)
        for name, value in sorted(after.items()):
            if before.get(name) != value:
                action = "introduced" if name not in before else "modified"
                findings.append(f"{relative}: {action} scripts.{name}")
    return findings


def main() -> int:
    """Validate candidate manifests against the trusted base."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--trusted-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        findings = changed_lifecycle_scripts(
            args.trusted_root.resolve(), args.candidate_root.resolve()
        )
    except ValueError as error:
        print(f"package lifecycle validation failed: {error}", file=sys.stderr)
        return 1
    if findings:
        print(
            "Candidate changes package-manager lifecycle hooks. "
            "These hooks execute automatically during dependency operations "
            "and require explicit security review:",
            file=sys.stderr,
        )
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print("Package lifecycle hooks are unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
