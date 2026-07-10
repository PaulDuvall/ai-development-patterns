"""Tests for isolated verification-unit activation, export, and aggregation."""

import datetime
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def load_script(name):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ACTIVATE = load_script("activate-verification-unit.py")
EXPORT = load_script("export-verification-unit.py")
ASSEMBLE = load_script("assemble-verification-units.py")
SCOPE = load_script("validate-research-scope.py")
DECISIONS = load_script("sync-verification-decisions.py")
HYDRATE = load_script("hydrate-evidence-content.py")


def unit(slug, index=1):
    unit_id = f"evidence-{index:03d}-{slug}"
    return {
        "unit_id": unit_id,
        "kind": "evidence",
        "slug": slug,
        "selected_slugs_json": json.dumps([slug], separators=(",", ":")),
        "worklist": f"verification/run-plan/units/{unit_id}.txt",
    }


def test_activate_requires_matrix_and_worklist_to_match(tmp_path, monkeypatch):
    item = unit("sample-pattern")
    matrix = tmp_path / "verification" / "run-plan" / "execution-matrix.json"
    worklist = tmp_path / item["worklist"]
    worklist.parent.mkdir(parents=True)
    worklist.write_text("sample-pattern\n", encoding="utf-8")
    matrix.parent.mkdir(parents=True, exist_ok=True)
    matrix.write_text(json.dumps({"include": [item]}), encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    activated = ACTIVATE.activate(matrix, item["unit_id"], "active.txt")

    assert activated == item
    assert (tmp_path / "active.txt").read_text(encoding="utf-8") == "sample-pattern\n"

    worklist.write_text("other-pattern\n", encoding="utf-8")
    with pytest.raises(ValueError, match="does not match"):
        ACTIVATE.activate(matrix, item["unit_id"], "active.txt")


def test_export_copies_only_the_fixed_unit_path_and_manifest(tmp_path):
    source = tmp_path / "source"
    evidence = source / "verification" / "evidence" / "sample-pattern.yaml"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("slug: sample-pattern\n", encoding="utf-8")
    destination = tmp_path / "candidate"
    metadata = {
        "unit_id": "evidence-001-sample-pattern",
        "kind": "evidence",
        "slug": "sample-pattern",
        "selected_slugs": ["sample-pattern"],
        "base_sha": "a" * 40,
    }

    manifest = EXPORT.export_unit(source, destination, metadata)

    assert manifest["path"] == "verification/evidence/sample-pattern.yaml"
    assert (destination / manifest["path"]).read_text(encoding="utf-8") == (
        "slug: sample-pattern\n")
    assert json.loads((destination / "manifest.json").read_text(
        encoding="utf-8"))["sha256"] == manifest["sha256"]
    assert {path.relative_to(destination).as_posix() for path in destination.rglob("*")
            if path.is_file()} == {"manifest.json", manifest["path"]}


def make_complete_evidence(slug, expected):
    return {
        "provenance_status": "complete",
        "last_checked": datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
        "search": expected,
        "evidence": "none found",
        "slug": slug,
    }


def init_git(root):
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)


def test_scope_validator_rejects_extra_evidence(tmp_path):
    evidence_dir = tmp_path / "verification" / "evidence"
    evidence_dir.mkdir(parents=True)
    (tmp_path / "experiments").mkdir()
    (tmp_path / "experiments" / "NOTES.md").write_text("notes\n", encoding="utf-8")
    expected = {
        "run_id": "github-actions:123",
        "checked_date": datetime.datetime.now(
            datetime.timezone.utc).date().isoformat(),
        "run_url": "https://example.test/runs/123",
        "provider": "openai",
        "model": "gpt-test",
        "prompt_version": "prompt-test",
    }
    (evidence_dir / "sample-pattern.yaml").write_text("old\n", encoding="utf-8")
    init_git(tmp_path)
    (evidence_dir / "sample-pattern.yaml").write_text(
        yaml.safe_dump(make_complete_evidence("sample-pattern", expected)), encoding="utf-8")

    SCOPE.validate(tmp_path, "evidence", '["sample-pattern"]', expected)

    (evidence_dir / "other-pattern.yaml").write_text("extra\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"extra=\['other-pattern'\]"):
        SCOPE.validate(tmp_path, "evidence", '["sample-pattern"]', expected)


def test_hydrate_derives_retrieval_fields_from_trusted_fetch(tmp_path, monkeypatch):
    path = tmp_path / "sample.yaml"
    path.write_text(yaml.safe_dump({
        "evidence": [{
            "url": "https://example.test/source",
            "mechanism_quote": "A sufficiently specific mechanism quote from the source.",
            "resolved_url": "invented",
            "content_sha256": "0" * 64,
        }],
    }), encoding="utf-8")
    monkeypatch.setattr(HYDRATE, "fetch", lambda url, quote: {
        "resolved_url": "https://example.test/canonical",
        "content_sha256": "a" * 64,
        "mechanism_quote_present": True,
    })

    assert HYDRATE.hydrate(path) == 1
    entry = yaml.safe_load(path.read_text(encoding="utf-8"))["evidence"][0]
    assert entry["resolved_url"] == "https://example.test/canonical"
    assert entry["content_sha256"] == "a" * 64


def test_hydrate_rejects_quote_missing_from_fetched_content(tmp_path, monkeypatch):
    path = tmp_path / "sample.yaml"
    path.write_text(yaml.safe_dump({
        "evidence": [{
            "url": "https://example.test/source",
            "mechanism_quote": "A sufficiently specific mechanism quote from the source.",
        }],
    }), encoding="utf-8")
    monkeypatch.setattr(HYDRATE, "fetch", lambda url, quote: {
        "resolved_url": url,
        "content_sha256": "a" * 64,
        "mechanism_quote_present": False,
    })

    with pytest.raises(ValueError, match="mechanism_quote is absent"):
        HYDRATE.hydrate(path)


def test_assemble_requires_every_unit_and_preserves_pending_comments(tmp_path):
    root = tmp_path / "root"
    artifacts = tmp_path / "artifacts"
    (root / "verification" / "evidence").mkdir(parents=True)
    pending = root / "verification" / "pending-evidence.yaml"
    pending.write_text(
        "# visible evidence gaps\npending:\n- first-pattern\n- second-pattern\n",
        encoding="utf-8")
    units = [unit("first-pattern", 1), unit("second-pattern", 2)]
    matrix = tmp_path / "matrix.json"
    matrix.write_text(json.dumps({"include": units}), encoding="utf-8")
    plan_id = hashlib.sha256(matrix.read_bytes()).hexdigest()
    for item in units:
        source = tmp_path / f"source-{item['slug']}"
        path = source / "verification" / "evidence" / f"{item['slug']}.yaml"
        path.parent.mkdir(parents=True)
        path.write_text(f"slug: {item['slug']}\n", encoding="utf-8")
        EXPORT.export_unit(
            source,
            artifacts / f"validated-verification-unit-{plan_id}-{item['unit_id']}",
            {
                "unit_id": item["unit_id"],
                "kind": "evidence",
                "slug": item["slug"],
                "selected_slugs": [item["slug"]],
            },
        )

    with pytest.raises(ValueError, match="execution plan digest mismatch"):
        ASSEMBLE.assemble(root, artifacts, matrix, "0" * 64)

    selected = ASSEMBLE.assemble(root, artifacts, matrix, plan_id)

    assert selected == ["first-pattern", "second-pattern"]
    assert pending.read_text(encoding="utf-8") == (
        "# visible evidence gaps\npending: []\n")
    assert sorted(path.stem for path in (root / "verification" / "evidence").glob("*.yaml")) == [
        "first-pattern", "second-pattern"]


def test_decision_sync_preserves_human_values_and_adds_review_placeholder(tmp_path):
    verification = tmp_path / "verification"
    evidence_dir = verification / "evidence"
    evidence_dir.mkdir(parents=True)
    (verification / "DECISIONS.md").write_text(
        "# Decisions\n\n## Naming-decision ledger\n\n"
        "| Pattern | Alignment | Industry terms | Recommendation | Decision |\n"
        "|---------|-----------|----------------|----------------|----------|\n"
        "| Existing Pattern | weak | old | Keep | Accepted by human |\n\n"
        "## Rubric decision record\n",
        encoding="utf-8",
    )
    (evidence_dir / "existing-pattern.yaml").write_text(yaml.safe_dump({
        "pattern": "Existing Pattern", "naming_alignment": "strong", "verdict": "verified",
    }), encoding="utf-8")
    (evidence_dir / "new-pattern.yaml").write_text(yaml.safe_dump({
        "pattern": "New Pattern",
        "naming_alignment": "aliased",
        "verdict": "verified",
        "terminology_variants": [{"term": "Industry Name"}],
    }), encoding="utf-8")

    DECISIONS.synchronize(tmp_path)
    content = (verification / "DECISIONS.md").read_text(encoding="utf-8")

    assert "| Existing Pattern | strong | old | Keep | Accepted by human |" in content
    assert "| New Pattern | aliased | Industry Name | Review naming signal | — |" in content
