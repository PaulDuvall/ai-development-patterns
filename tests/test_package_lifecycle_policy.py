"""Tests for the package-manager lifecycle-hook policy."""

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "validate-package-lifecycle.py"
SPEC = importlib.util.spec_from_file_location("lifecycle_policy", SCRIPT)
POLICY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(POLICY)


def write_manifest(root, scripts=None, relative="package.json"):
    """Write one minimal package manifest."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"name": "example", "scripts": scripts or {}}),
        encoding="utf-8",
    )


def test_rejects_lifecycle_hook_in_new_manifest(tmp_path):
    """A new package must not introduce automatic install execution."""
    trusted = tmp_path / "trusted"
    candidate = tmp_path / "candidate"
    trusted.mkdir()
    candidate.mkdir()
    write_manifest(candidate, {"preinstall": "echo RCE_OK"})

    assert POLICY.changed_lifecycle_scripts(trusted, candidate) == [
        "package.json: introduced scripts.preinstall"
    ]


def test_rejects_modified_existing_lifecycle_hook(tmp_path):
    """A candidate must not replace an established lifecycle command."""
    trusted = tmp_path / "trusted"
    candidate = tmp_path / "candidate"
    trusted.mkdir()
    candidate.mkdir()
    write_manifest(trusted, {"prepare": "trusted-command"}, "app/package.json")
    write_manifest(candidate, {"prepare": "candidate-command"}, "app/package.json")

    assert POLICY.changed_lifecycle_scripts(trusted, candidate) == [
        "app/package.json: modified scripts.prepare"
    ]


def test_allows_ordinary_script_and_dependency_changes(tmp_path):
    """Non-lifecycle package changes remain eligible for normal review."""
    trusted = tmp_path / "trusted"
    candidate = tmp_path / "candidate"
    trusted.mkdir()
    candidate.mkdir()
    write_manifest(trusted, {"test": "pytest"})
    write_manifest(candidate, {"test": "pytest -q", "lint": "ruff check ."})

    assert POLICY.changed_lifecycle_scripts(trusted, candidate) == []


def test_allows_removing_a_lifecycle_hook(tmp_path):
    """Removing automatic execution is safe and must not be blocked."""
    trusted = tmp_path / "trusted"
    candidate = tmp_path / "candidate"
    trusted.mkdir()
    candidate.mkdir()
    write_manifest(trusted, {"postinstall": "legacy-command"})
    write_manifest(candidate, {})

    assert POLICY.changed_lifecycle_scripts(trusted, candidate) == []
