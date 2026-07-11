"""Focused tests for local-manifest paths in the research scope gate."""

import datetime
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).parent.parent
SPEC = importlib.util.spec_from_file_location(
    "validate_research_scope", ROOT / "scripts" / "validate-research-scope.py")
SCOPE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCOPE)

LOCAL_UUID = "123e4567-e89b-42d3-a456-426614174000"
LOCAL_REF = f"verification/local-runs/codex-local-{LOCAL_UUID}.yaml"


def init_git(root):
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)


def expected_local_run():
    return {
        "run_id": f"codex-local:{LOCAL_UUID}",
        "checked_date": datetime.date.today().isoformat(),
        "run_ref": LOCAL_REF,
        "run_manifest_sha256": "a" * 64,
        "provider": "openai",
        "model": "codex-managed",
        "prompt_version": f"evidence-v2-codex-local-v1+sha256.{'b' * 64}",
    }


def write_local_evidence(root, expected):
    path = root / "verification" / "evidence" / "sample-pattern.yaml"
    path.write_text(yaml.safe_dump({
        "provenance_status": "complete",
        "last_checked": expected["checked_date"],
        "slug": "sample-pattern",
        "search": {
            "run_id": expected["run_id"],
            "run_ref": expected["run_ref"],
            "run_manifest_sha256": expected["run_manifest_sha256"],
            "provider": expected["provider"],
            "model": expected["model"],
            "prompt_version": expected["prompt_version"],
        },
        "evidence": "none found",
    }), encoding="utf-8")


def local_repo(tmp_path):
    evidence = tmp_path / "verification" / "evidence"
    evidence.mkdir(parents=True)
    (evidence / "sample-pattern.yaml").write_text("old\n", encoding="utf-8")
    for name in ("DECISIONS.md", "STATUS.md", "pending-evidence.yaml"):
        (tmp_path / "verification" / name).write_text(
            f"old {name}\n", encoding="utf-8")
    notes = tmp_path / "experiments" / "NOTES.md"
    notes.parent.mkdir()
    notes.write_text("old notes\n", encoding="utf-8")
    init_git(tmp_path)
    return tmp_path


def test_scope_includes_untracked_expected_local_manifest(tmp_path):
    root = local_repo(tmp_path)
    expected = expected_local_run()
    write_local_evidence(root, expected)
    manifest = root / LOCAL_REF
    manifest.parent.mkdir(parents=True)
    manifest.write_text("approved: manifest\n", encoding="utf-8")

    changed = SCOPE.validate(
        root, "evidence", json.dumps(["sample-pattern"]), expected)

    assert changed == {
        "verification/evidence/sample-pattern.yaml",
        LOCAL_REF,
    }


def test_scope_rejects_an_extra_untracked_local_manifest(tmp_path):
    root = local_repo(tmp_path)
    expected = expected_local_run()
    write_local_evidence(root, expected)
    manifest = root / LOCAL_REF
    manifest.parent.mkdir(parents=True)
    manifest.write_text("approved: manifest\n", encoding="utf-8")
    (manifest.parent / "codex-local-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa.yaml").write_text(
        "unexpected: manifest\n", encoding="utf-8")

    with pytest.raises(ValueError, match="research changed forbidden paths"):
        SCOPE.validate(
            root, "evidence", json.dumps(["sample-pattern"]), expected)


def test_scope_rejects_forbidden_staged_changes(tmp_path):
    root = local_repo(tmp_path)
    expected = expected_local_run()
    write_local_evidence(root, expected)
    manifest = root / LOCAL_REF
    manifest.parent.mkdir(parents=True)
    manifest.write_text("approved: manifest\n", encoding="utf-8")
    forbidden = root / "README.md"
    forbidden.write_text("staged unrelated change\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=root, check=True)

    with pytest.raises(ValueError, match="research changed forbidden paths"):
        SCOPE.validate(
            root, "evidence", json.dumps(["sample-pattern"]), expected)


def test_scope_rejects_forbidden_untracked_files_anywhere(tmp_path):
    root = local_repo(tmp_path)
    expected = expected_local_run()
    write_local_evidence(root, expected)
    manifest = root / LOCAL_REF
    manifest.parent.mkdir(parents=True)
    manifest.write_text("approved: manifest\n", encoding="utf-8")
    (root / "scratch.txt").write_text("unrelated\n", encoding="utf-8")

    with pytest.raises(ValueError, match="scratch.txt"):
        SCOPE.validate(
            root, "evidence", json.dumps(["sample-pattern"]), expected)


def test_combined_discovery_allows_notes_but_rejects_shared_state_edits(tmp_path):
    root = local_repo(tmp_path)
    expected = expected_local_run()
    write_local_evidence(root, expected)
    manifest = root / LOCAL_REF
    manifest.parent.mkdir(parents=True)
    manifest.write_text("approved: manifest\n", encoding="utf-8")
    (root / "experiments" / "NOTES.md").write_text(
        "new discovery notes\n", encoding="utf-8")

    changed = SCOPE.validate(
        root, "evidence", json.dumps(["sample-pattern"]), expected,
        allow_discovery=True)
    assert "experiments/NOTES.md" in changed

    (root / "verification" / "DECISIONS.md").write_text(
        "unrelated human decision\n", encoding="utf-8")
    with pytest.raises(ValueError, match="DECISIONS.md"):
        SCOPE.validate(
            root, "evidence", json.dumps(["sample-pattern"]), expected,
            allow_discovery=True)


def test_discovery_scope_allows_only_notes_and_expected_local_manifest(tmp_path):
    root = local_repo(tmp_path)
    expected = expected_local_run()
    notes = root / "experiments" / "NOTES.md"
    notes.write_text("new discovery notes\n", encoding="utf-8")
    manifest = root / LOCAL_REF
    manifest.parent.mkdir(parents=True)
    manifest.write_text("approved: manifest\n", encoding="utf-8")

    changed = SCOPE.validate(root, "discovery", "[]", expected)

    assert changed == {"experiments/NOTES.md", LOCAL_REF}


def test_discovery_scope_rejects_an_extra_local_manifest(tmp_path):
    root = local_repo(tmp_path)
    expected = expected_local_run()
    manifest = root / LOCAL_REF
    manifest.parent.mkdir(parents=True)
    manifest.write_text("approved: manifest\n", encoding="utf-8")
    (manifest.parent / "codex-local-aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa.yaml").write_text(
        "unexpected: manifest\n", encoding="utf-8")

    with pytest.raises(ValueError, match="discovery changed forbidden paths"):
        SCOPE.validate(root, "discovery", "[]", expected)
