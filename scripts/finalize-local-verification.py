#!/usr/bin/env python3
"""Finalize an approved local Codex evaluation without publishing it."""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from local_verification import (
    load_manifest,
    load_search_ledger,
    reconcile_search_projection,
    search_ledger_ref_for_id,
)


ROOT = Path(__file__).parent.parent.resolve()


def load_script(name):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCOPE = load_script("validate-research-scope.py")


def atomic_write_bytes(path, content):
    """Replace one shared file without exposing a partially written target."""
    path = Path(path)
    mode = path.stat().st_mode & 0o777
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            os.fchmod(handle.fileno(), mode)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def remove_pending(root, selected):
    path = Path(root) / "verification" / "pending-evidence.yaml"
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    pending = data.get("pending")
    if not isinstance(pending, list) or not all(isinstance(item, str) for item in pending):
        raise ValueError("pending-evidence.yaml must contain a pending list")
    if len(pending) != len(set(pending)):
        raise ValueError("pending-evidence.yaml contains duplicate slugs")
    remaining = [slug for slug in pending if slug not in set(selected)]
    marker = text.find("pending:")
    if marker < 0:
        raise ValueError("pending-evidence.yaml is missing its pending key")
    rendered = ("pending:\n" + "".join(f"- {slug}\n" for slug in remaining)
                if remaining else "pending: []\n")
    atomic_write_bytes(path, (text[:marker] + rendered).encode("utf-8"))


def run(command, root):
    subprocess.run(command, cwd=root, check=True)


def snapshot_files(root, relative_paths):
    """Capture finalizer-owned shared files so failures can restore them."""
    return {
        relative: (Path(root) / relative).read_bytes()
        for relative in relative_paths
    }


def restore_files(root, snapshots):
    for relative, content in snapshots.items():
        atomic_write_bytes(Path(root) / relative, content)


def reconcile_selected_searches(root, ledger, selected):
    """Reconcile every asserted evidence search against trusted events."""
    for slug in selected:
        path = Path(root) / "verification" / "evidence" / f"{slug}.yaml"
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"{slug}: evidence output must be a regular non-symlink file")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        search = data.get("search") if isinstance(data, dict) else None
        modes = search.get("modes") if isinstance(search, dict) else None
        reconcile_search_projection(ledger, slug, modes)


def finalize(root, run_ref, manifest_sha):
    manifest, _, actual_sha = load_manifest(root, run_ref, manifest_sha)
    if actual_sha != manifest_sha:
        raise ValueError("approved manifest digest changed before finalization")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True,
        capture_output=True, text=True).stdout.strip()
    if head != manifest["base_sha"]:
        raise ValueError(
            "repository HEAD changed after planning; start a new local evaluation plan")
    execution = manifest["execution"]
    ledger_ref = search_ledger_ref_for_id(manifest["run_id"])
    ledger, _ = load_search_ledger(
        root, ledger_ref, manifest, run_ref, manifest_sha,
        require_complete=True)
    selected = manifest["selected_slugs"]
    reconcile_selected_searches(root, ledger, selected)
    expected = {
        "run_id": manifest["run_id"],
        "checked_date": manifest["checked_date"],
        "run_ref": run_ref,
        "run_manifest_sha256": manifest_sha,
        "provider": execution["provider"],
        "model": execution["model"],
        "prompt_version": execution["prompt_version"],
        "search_ledger_ref": ledger_ref,
    }
    kind = "discovery" if manifest["scope"] == "discovery" else "evidence"
    SCOPE.validate(
        root, kind, json.dumps(selected, separators=(",", ":")),
        expected, allow_discovery=manifest["include_discovery"])
    snapshots = snapshot_files(root, (
        "verification/pending-evidence.yaml",
        "verification/DECISIONS.md",
        "verification/STATUS.md",
    ))
    try:
        remove_pending(root, selected)
        run([sys.executable, "scripts/sync-verification-decisions.py"], root)
        run([sys.executable, "scripts/generate-verification-status.py"], root)
        run([
            sys.executable, "scripts/validate-evidence.py",
            "--registry", "patterns.yaml",
            "--allowlist", "verification/pending-evidence.yaml",
        ], root)
        run([
            sys.executable, "scripts/scan-candidate-secrets.py",
            "verification", "experiments/NOTES.md",
        ], root)
        run([
            sys.executable, "-m", "pytest",
            "tests/test_evidence_files.py",
            "tests/test_evidence_content.py",
            "tests/test_verification_status.py",
            "tests/test_candidate_secret_scan.py",
            "tests/test_local_research_scope.py",
            "tests/test_local_verification.py",
            "-m", "not slow", "--tb=short",
        ], root)
    except Exception:
        restore_files(root, snapshots)
        raise
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    try:
        selected = finalize(ROOT, args.manifest, args.manifest_sha256)
    except (OSError, ValueError, yaml.YAMLError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Finalized {len(selected)} local evidence unit(s).")
    print("No commit, push, pull request, or merge was performed.")
    print("Obtain separate human publication approval before opening one draft PR.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
