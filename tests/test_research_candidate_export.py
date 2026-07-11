"""Tests for exporting model output from an isolated research workspace."""

import importlib.util
import stat
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parent.parent / "scripts" / "export-research-candidate.py"
SPEC = importlib.util.spec_from_file_location("research_candidate_export", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def make_workspace(root):
    for relative in MODULE.FIXED_FILES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"candidate {relative}\n", encoding="utf-8")
    evidence = root / MODULE.EVIDENCE_DIR
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "example-pattern.yaml").write_text(
        "schema_version: 2\n", encoding="utf-8")


def test_export_copies_only_fixed_paths(tmp_path):
    source = tmp_path / "isolated"
    destination = tmp_path / "trusted"
    source.mkdir()
    destination.mkdir()
    make_workspace(source)
    forbidden = source / ".github" / "workflows" / "owned.yml"
    forbidden.parent.mkdir(parents=True)
    forbidden.write_text("malicious\n", encoding="utf-8")

    count = MODULE.export_candidate(source, destination)

    assert count == len(MODULE.FIXED_FILES) + 1
    assert (destination / "README.md").read_text() == "candidate README.md\n"
    assert (destination / MODULE.EVIDENCE_DIR / "example-pattern.yaml").is_file()
    assert not (destination / ".github").exists()


def test_exported_files_are_owner_only(tmp_path):
    source = tmp_path / "isolated"
    destination = tmp_path / "trusted"
    source.mkdir()
    destination.mkdir()
    make_workspace(source)

    MODULE.export_candidate(source, destination)

    evidence_file = Path(MODULE.EVIDENCE_DIR) / "example-pattern.yaml"
    for relative in (*MODULE.FIXED_FILES, evidence_file):
        mode = stat.S_IMODE((destination / relative).stat().st_mode)
        assert mode == 0o600


@pytest.mark.parametrize("relative", ["README.md", "verification/evidence/bad.yaml"])
def test_export_rejects_symbolic_links(tmp_path, relative):
    source = tmp_path / "isolated"
    destination = tmp_path / "trusted"
    source.mkdir()
    destination.mkdir()
    make_workspace(source)
    target = source / relative
    target.unlink(missing_ok=True)
    target.symlink_to(source / "index.html")

    with pytest.raises(ValueError, match="regular file|symbolic"):
        MODULE.export_candidate(source, destination)


def test_export_rejects_nested_evidence(tmp_path):
    source = tmp_path / "isolated"
    destination = tmp_path / "trusted"
    source.mkdir()
    destination.mkdir()
    make_workspace(source)
    (source / MODULE.EVIDENCE_DIR / "nested").mkdir()

    with pytest.raises(ValueError, match="nested"):
        MODULE.export_candidate(source, destination)


def test_export_rejects_noncanonical_evidence_filename(tmp_path):
    source = tmp_path / "isolated"
    destination = tmp_path / "trusted"
    source.mkdir()
    destination.mkdir()
    make_workspace(source)
    (source / MODULE.EVIDENCE_DIR / "Bad_Name.yaml").write_text(
        "schema_version: 2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid evidence filename"):
        MODULE.export_candidate(source, destination)


def test_export_rejects_symbolic_workspace_root(tmp_path):
    source = tmp_path / "isolated"
    target = tmp_path / "target"
    destination = tmp_path / "trusted"
    target.mkdir()
    destination.mkdir()
    make_workspace(target)
    source.symlink_to(target, target_is_directory=True)

    with pytest.raises(ValueError, match="workspace must not be a symbolic link"):
        MODULE.export_candidate(source, destination)
