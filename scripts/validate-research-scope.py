#!/usr/bin/env python3
"""Fail closed unless a research candidate exactly matches its trusted scope."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml


SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
EVIDENCE_PATH_RE = re.compile(
    r"verification/evidence/([a-z0-9]+(?:-[a-z0-9]+)*)\.yaml")
SHARED_PATHS = {
    "verification/pending-evidence.yaml",
    "verification/STATUS.md",
    "verification/DECISIONS.md",
    "experiments/NOTES.md",
}


def changed_paths(root):
    tracked = subprocess.run(
        ["git", "diff", "--name-only"], cwd=root, check=True,
        capture_output=True, text=True).stdout.splitlines()
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--",
         "verification/evidence"], cwd=root, check=True,
        capture_output=True, text=True).stdout.splitlines()
    return set(tracked) | set(untracked)


def validate_provenance(root, slugs, expected):
    expected_date = expected["checked_date"]
    for slug in slugs:
        data = yaml.safe_load((Path(root) / "verification" / "evidence" /
                               f"{slug}.yaml").read_text(encoding="utf-8"))
        if data.get("provenance_status") != "complete":
            raise ValueError(f"{slug}: selected output must have complete provenance")
        if str(data.get("last_checked")) != expected_date:
            raise ValueError(f"{slug}: last_checked must be {expected_date}")
        search = data.get("search") or {}
        for field in ("run_id", "run_url", "provider", "model", "prompt_version"):
            if search.get(field) != expected[field]:
                raise ValueError(f"{slug}: search.{field} does not match this run")
        entries = data.get("evidence")
        if entries == "none found":
            continue
        if not isinstance(entries, list):
            raise ValueError(f"{slug}: evidence must be a list or 'none found'")
        for index, entry in enumerate(entries):
            verifier = entry.get("verifier") if isinstance(entry, dict) else None
            if not isinstance(verifier, dict):
                raise ValueError(f"{slug}: evidence[{index}] lacks verifier metadata")
            if verifier.get("method") != "automated":
                raise ValueError(
                    f"{slug}: evidence[{index}] verifier.method must be automated")
            for field in ("model", "prompt_version"):
                if verifier.get(field) != expected[field]:
                    raise ValueError(
                        f"{slug}: evidence[{index}] verifier.{field} does not match this run")
            if verifier.get("run_url") != expected["run_url"]:
                raise ValueError(
                    f"{slug}: evidence[{index}] verifier.run_url does not match this run")


def validate(root, kind, selected_json, expected, allow_shared=False):
    selected = json.loads(selected_json)
    if not isinstance(selected, list) or not all(
            isinstance(slug, str) and SLUG_RE.fullmatch(slug) for slug in selected):
        raise ValueError("selected scope must be a JSON list of canonical slugs")
    if len(selected) != len(set(selected)):
        raise ValueError("selected scope contains duplicate slugs")
    changed = changed_paths(root)
    evidence_changed = {
        match.group(1) for path in changed
        if (match := EVIDENCE_PATH_RE.fullmatch(path))
    }
    non_evidence = changed - {
        f"verification/evidence/{slug}.yaml" for slug in evidence_changed}
    if kind == "discovery":
        if selected or evidence_changed:
            raise ValueError("discovery unit must not select or change evidence")
        unexpected = non_evidence - {"experiments/NOTES.md"}
        if unexpected:
            raise ValueError(f"discovery changed forbidden paths: {sorted(unexpected)}")
        return changed
    if kind != "evidence":
        raise ValueError(f"unsupported research kind: {kind!r}")
    missing = set(selected) - evidence_changed
    extra = evidence_changed - set(selected)
    if missing or extra:
        raise ValueError(
            f"evidence scope mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
    allowed_non_evidence = SHARED_PATHS if allow_shared else set()
    unexpected = non_evidence - allowed_non_evidence
    if unexpected:
        raise ValueError(f"research changed forbidden paths: {sorted(unexpected)}")
    validate_provenance(root, selected, expected)
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--kind", choices=("evidence", "discovery"), required=True)
    parser.add_argument("--selected-json", required=True)
    parser.add_argument("--expected-run-id", required=True)
    parser.add_argument("--expected-checked-date", required=True)
    parser.add_argument("--expected-run-url", required=True)
    parser.add_argument("--expected-provider", required=True)
    parser.add_argument("--expected-model", required=True)
    parser.add_argument("--expected-prompt-version", required=True)
    parser.add_argument("--allow-shared", action="store_true")
    args = parser.parse_args()
    expected = {
        "run_id": args.expected_run_id,
        "checked_date": args.expected_checked_date,
        "run_url": args.expected_run_url,
        "provider": args.expected_provider,
        "model": args.expected_model,
        "prompt_version": args.expected_prompt_version,
    }
    try:
        changed = validate(
            args.root, args.kind, args.selected_json, expected, args.allow_shared)
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError,
            subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Validated exact {args.kind} scope across {len(changed)} changed path(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
