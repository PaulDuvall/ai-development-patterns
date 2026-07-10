"""Tests for the unprivileged research workspace write boundary."""

import importlib.util
import os
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parent.parent / "scripts" / "check-research-workspace.py"
SPEC = importlib.util.spec_from_file_location("research_workspace_check", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
EXPORT_SCRIPT = Path(__file__).parent.parent / "scripts" / "export-research-candidate.py"
EXPORT_SPEC = importlib.util.spec_from_file_location("research_candidate_export", EXPORT_SCRIPT)
EXPORT_MODULE = importlib.util.module_from_spec(EXPORT_SPEC)
EXPORT_SPEC.loader.exec_module(EXPORT_MODULE)


def make_workspace(root):
    for relative in MODULE.WRITABLE_FILES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"candidate {relative}\n", encoding="utf-8")
    evidence = root / MODULE.EVIDENCE_DIR
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "existing.yaml").write_text("schema_version: 2\n", encoding="utf-8")
    (root / "patterns.yaml").write_text("patterns: []\n", encoding="utf-8")
    (root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (root / ".github" / "workflows" / "verify.yml").write_text(
        "name: forbidden\n", encoding="utf-8")


def lock_workspace(root):
    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        relative = path.relative_to(root)
        if relative.as_posix() in MODULE.WRITABLE_FILES:
            path.chmod(0o600)
        elif relative == MODULE.EVIDENCE_DIR or MODULE.EVIDENCE_DIR in relative.parents:
            path.chmod(0o700 if path.is_dir() else 0o600)
        else:
            path.chmod(0o500 if path.is_dir() else 0o400)
    root.chmod(0o500)


def unlock_workspace(root):
    root.chmod(0o700)
    for path in root.rglob("*"):
        if not path.is_symlink():
            path.chmod(0o700 if path.is_dir() else 0o600)


def simulated_owner(root, *, research_owned_extra=(), foreign_owned_candidate=()):
    """Model the production root/research UID split without requiring sudo."""
    research_uid = os.geteuid()
    foreign_uid = research_uid + 1
    research_owned_extra = {Path(path) for path in research_owned_extra}
    foreign_owned_candidate = {Path(path) for path in foreign_owned_candidate}

    def owner_of(path):
        path = Path(path)
        if path == root.parent:
            return foreign_uid
        relative = Path(".") if path == root else path.relative_to(root)
        if relative in foreign_owned_candidate:
            return foreign_uid
        if MODULE.allowed_write(relative) or relative in research_owned_extra:
            return research_uid
        return foreign_uid

    return owner_of


def test_exact_candidate_paths_are_writable(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    make_workspace(workspace)
    lock_workspace(workspace)
    try:
        assert MODULE.check_workspace(
            workspace, owner_of=simulated_owner(workspace)
        ) == len(MODULE.WRITABLE_FILES) + 1
    finally:
        unlock_workspace(workspace)


def test_write_boundary_and_export_allowlists_match():
    assert set(MODULE.WRITABLE_FILES) == set(EXPORT_MODULE.FIXED_FILES)
    assert MODULE.EVIDENCE_DIR.as_posix() == EXPORT_MODULE.EVIDENCE_DIR


def test_rejects_writable_path_outside_candidate_set(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    make_workspace(workspace)
    lock_workspace(workspace)
    (workspace / "patterns.yaml").chmod(0o600)
    try:
        with pytest.raises(ValueError, match="unexpected paths are writable"):
            MODULE.check_workspace(workspace, owner_of=simulated_owner(workspace))
    finally:
        unlock_workspace(workspace)


def test_rejects_read_only_candidate_file(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    make_workspace(workspace)
    lock_workspace(workspace)
    (workspace / "README.md").chmod(0o400)
    try:
        with pytest.raises(ValueError, match="candidate file is not writable"):
            MODULE.check_workspace(workspace, owner_of=simulated_owner(workspace))
    finally:
        unlock_workspace(workspace)


def test_rejects_symbolic_candidate_file(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    make_workspace(workspace)
    readme = workspace / "README.md"
    readme.unlink()
    readme.symlink_to(workspace / "index.html")
    lock_workspace(workspace)
    try:
        with pytest.raises(ValueError, match="not a regular file"):
            MODULE.check_workspace(workspace, owner_of=simulated_owner(workspace))
    finally:
        unlock_workspace(workspace)


def test_rejects_nonwritable_evidence_directory(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    make_workspace(workspace)
    lock_workspace(workspace)
    (workspace / MODULE.EVIDENCE_DIR).chmod(0o500)
    try:
        with pytest.raises(ValueError, match="writable directory is not writable"):
            MODULE.check_workspace(workspace, owner_of=simulated_owner(workspace))
    finally:
        unlock_workspace(workspace)


def test_rejects_symbolic_workspace_root(tmp_path):
    target = tmp_path / "target"
    workspace = tmp_path / "workspace"
    target.mkdir()
    make_workspace(target)
    workspace.symlink_to(target, target_is_directory=True)

    with pytest.raises(ValueError, match="workspace must not be a symbolic link"):
        MODULE.check_workspace(workspace)


def test_rejects_symbolic_evidence_directory(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    make_workspace(workspace)
    evidence = workspace / MODULE.EVIDENCE_DIR
    for path in evidence.iterdir():
        path.unlink()
    evidence.rmdir()
    evidence.symlink_to(workspace / "verification", target_is_directory=True)

    with pytest.raises(ValueError, match="writable path is not a directory"):
        MODULE.check_workspace(workspace, owner_of=simulated_owner(workspace))


def test_scoped_unit_boundary_allows_only_one_evidence_file(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    make_workspace(workspace)
    lock_workspace(workspace)
    target = Path("verification/evidence/existing.yaml")
    for relative in MODULE.WRITABLE_FILES:
        (workspace / relative).chmod(0o400)
    (workspace / MODULE.EVIDENCE_DIR).chmod(0o500)
    (workspace / target).chmod(0o600)

    research_uid = os.geteuid()
    foreign_uid = research_uid + 1

    def owner_of(path):
        path = Path(path)
        if path == workspace.parent:
            return foreign_uid
        relative = Path(".") if path == workspace else path.relative_to(workspace)
        return research_uid if relative == target else foreign_uid

    try:
        assert MODULE.check_workspace(
            workspace,
            writable_files=[target.as_posix()],
            writable_dirs=[],
            owner_of=owner_of,
        ) == 1
    finally:
        unlock_workspace(workspace)


def test_rejects_research_owned_workspace_parent(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    make_workspace(workspace)
    lock_workspace(workspace)
    try:
        owner_of = simulated_owner(workspace)
        with pytest.raises(ValueError, match="must not own the workspace parent"):
            MODULE.check_workspace(
                workspace, owner_of=lambda path: (
                    os.geteuid() if Path(path) == workspace.parent else owner_of(path)
                )
            )
    finally:
        unlock_workspace(workspace)


def test_rejects_read_only_non_candidate_owned_by_research_account(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    make_workspace(workspace)
    lock_workspace(workspace)
    try:
        with pytest.raises(ValueError, match="can be chmodded"):
            MODULE.check_workspace(
                workspace,
                owner_of=simulated_owner(
                    workspace, research_owned_extra={Path("patterns.yaml")}
                ),
            )
    finally:
        unlock_workspace(workspace)


def test_rejects_candidate_owned_by_wrong_account(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    make_workspace(workspace)
    lock_workspace(workspace)
    try:
        with pytest.raises(ValueError, match="does not own candidate file"):
            MODULE.check_workspace(
                workspace,
                owner_of=simulated_owner(
                    workspace, foreign_owned_candidate={Path("README.md")}
                ),
            )
    finally:
        unlock_workspace(workspace)
