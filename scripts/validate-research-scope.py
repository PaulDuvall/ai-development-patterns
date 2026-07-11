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
DISCOVERY_PATH = "experiments/NOTES.md"


def changed_paths(root):
    tracked = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--"], cwd=root, check=True,
        capture_output=True, text=True).stdout.splitlines()
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"], cwd=root, check=True,
        capture_output=True, text=True).stdout.splitlines()
    return set(tracked) | set(untracked)


def validate_provenance(root, slugs, expected):
    expected_date = expected["checked_date"]
    for slug in slugs:
        path = Path(root) / "verification" / "evidence" / f"{slug}.yaml"
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"{slug}: evidence output must be a regular non-symlink file")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"{slug}: evidence output must be a YAML mapping")
        if data.get("provenance_status") != "complete":
            raise ValueError(f"{slug}: selected output must have complete provenance")
        if str(data.get("last_checked")) != expected_date:
            raise ValueError(f"{slug}: last_checked must be {expected_date}")
        search = data.get("search")
        if not isinstance(search, dict):
            raise ValueError(f"{slug}: search must be a mapping")
        for field in ("run_id", "provider", "model", "prompt_version"):
            if search.get(field) != expected[field]:
                raise ValueError(f"{slug}: search.{field} does not match this run")
        if expected.get("run_ref"):
            for field in ("run_ref", "run_manifest_sha256"):
                if search.get(field) != expected[field]:
                    raise ValueError(f"{slug}: search.{field} does not match this run")
            if "run_url" in search:
                raise ValueError(f"{slug}: local search provenance must not use run_url")
        elif search.get("run_url") != expected.get("run_url"):
            raise ValueError(f"{slug}: search.run_url does not match this run")
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
            if expected.get("run_ref"):
                for field in ("run_ref", "run_manifest_sha256"):
                    if verifier.get(field) != expected[field]:
                        raise ValueError(
                            f"{slug}: evidence[{index}] verifier.{field} "
                            "does not match this run")
                if "run_url" in verifier:
                    raise ValueError(
                        f"{slug}: local verifier provenance must not use run_url")
            elif verifier.get("run_url") != expected.get("run_url"):
                raise ValueError(
                    f"{slug}: evidence[{index}] verifier.run_url does not match this run")


def validate(root, kind, selected_json, expected, allow_discovery=False):
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
    local_artifacts = set()
    if expected.get("run_ref"):
        ledger_ref = expected.get("search_ledger_ref")
        if not isinstance(ledger_ref, str) or not ledger_ref:
            raise ValueError("local research scope requires search_ledger_ref")
        local_artifacts = {expected["run_ref"], ledger_ref}
        missing_artifacts = local_artifacts - changed
        if missing_artifacts:
            raise ValueError(
                f"local research scope is missing run artifacts: {sorted(missing_artifacts)}")
    if kind == "discovery":
        if selected or evidence_changed:
            raise ValueError("discovery unit must not select or change evidence")
        allowed_discovery = {DISCOVERY_PATH}
        allowed_discovery.update(local_artifacts)
        unexpected = non_evidence - allowed_discovery
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
    allowed_non_evidence = {DISCOVERY_PATH} if allow_discovery else set()
    allowed_non_evidence.update(local_artifacts)
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
    provenance = parser.add_mutually_exclusive_group(required=True)
    provenance.add_argument("--expected-run-url")
    provenance.add_argument("--expected-run-ref")
    parser.add_argument("--expected-run-manifest-sha256")
    parser.add_argument("--expected-search-ledger-ref")
    parser.add_argument("--expected-provider", required=True)
    parser.add_argument("--expected-model", required=True)
    parser.add_argument("--expected-prompt-version", required=True)
    parser.add_argument("--allow-discovery", action="store_true")
    args = parser.parse_args()
    expected = {
        "run_id": args.expected_run_id,
        "checked_date": args.expected_checked_date,
        "provider": args.expected_provider,
        "model": args.expected_model,
        "prompt_version": args.expected_prompt_version,
    }
    if args.expected_run_ref:
        if not args.expected_run_manifest_sha256:
            parser.error(
                "--expected-run-manifest-sha256 is required with --expected-run-ref")
        expected.update({
            "run_ref": args.expected_run_ref,
            "run_manifest_sha256": args.expected_run_manifest_sha256,
            "search_ledger_ref": args.expected_search_ledger_ref,
        })
    else:
        if args.expected_run_manifest_sha256:
            parser.error(
                "--expected-run-manifest-sha256 requires --expected-run-ref")
        expected["run_url"] = args.expected_run_url
    try:
        changed = validate(
            args.root, args.kind, args.selected_json, expected, args.allow_discovery)
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError,
            subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Validated exact {args.kind} scope across {len(changed)} changed path(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
