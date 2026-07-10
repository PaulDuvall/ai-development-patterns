#!/usr/bin/env python3
"""Verify the unprivileged research workspace has an exact write boundary."""

import argparse
import os
import stat
import sys
from pathlib import Path


WRITABLE_FILES = (
    "README.md",
    "index.html",
    "assets/js/patterns-data.js",
    "experiments/NOTES.md",
    "verification/DECISIONS.md",
    "verification/STATUS.md",
    "verification/pending-evidence.yaml",
)
EVIDENCE_DIR = Path("verification/evidence")


def is_writable(path):
    """Check write access using the effective identity when supported."""
    try:
        return os.access(path, os.W_OK, effective_ids=True)
    except (NotImplementedError, TypeError):
        return os.access(path, os.W_OK)


def open_writable_file(path):
    """Prove an existing file can be opened for writing without modifying it."""
    flags = os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    os.close(descriptor)


def allowed_write(relative, writable_files=WRITABLE_FILES, writable_dirs=(EVIDENCE_DIR,)):
    """Return whether a relative path belongs to the intended candidate set."""
    return relative.as_posix() in writable_files or any(
        relative == directory or directory in relative.parents
        for directory in writable_dirs)


def check_workspace(workspace, *, writable_files=None, writable_dirs=None,
                    owner_of=None, effective_uid=None):
    """Fail unless only fixed candidate paths are writable by this process."""
    if writable_files is None:
        writable_files = tuple(WRITABLE_FILES)
    else:
        writable_files = tuple(writable_files)
    if writable_dirs is None:
        writable_dirs = (EVIDENCE_DIR,)
    else:
        writable_dirs = tuple(Path(path) for path in writable_dirs)
    if effective_uid is None:
        effective_uid = os.geteuid()
    if owner_of is None:
        def owner_of(path):
            return path.lstat().st_uid

    raw_workspace = Path(workspace)
    if raw_workspace.is_symlink():
        raise ValueError("research workspace must not be a symbolic link")
    workspace = raw_workspace.resolve(strict=True)
    if not workspace.is_dir():
        raise ValueError("research workspace must be a directory")
    if owner_of(workspace.parent) == effective_uid:
        raise ValueError("research account must not own the workspace parent")

    for relative in writable_files:
        path = workspace / relative
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError as exc:
            raise ValueError(f"writable candidate file is missing: {relative}") from exc
        if not stat.S_ISREG(mode):
            raise ValueError(f"writable candidate path is not a regular file: {relative}")
        if owner_of(path) != effective_uid:
            raise ValueError(f"research account does not own candidate file: {relative}")
        if not is_writable(path):
            raise ValueError(f"candidate file is not writable: {relative}")
        open_writable_file(path)

    for relative in writable_dirs:
        directory = workspace / relative
        try:
            directory_mode = directory.lstat().st_mode
        except FileNotFoundError as exc:
            raise ValueError(f"writable directory is missing: {relative}") from exc
        if not stat.S_ISDIR(directory_mode):
            raise ValueError(f"writable path is not a directory: {relative}")
        if owner_of(directory) != effective_uid:
            raise ValueError(f"research account does not own writable directory: {relative}")
        if not is_writable(directory):
            raise ValueError(f"writable directory is not writable: {relative}")

        probe = directory / f".research-write-probe-{os.getpid()}"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = None
        try:
            descriptor = os.open(probe, flags, 0o600)
        finally:
            if descriptor is not None:
                os.close(descriptor)
            probe.unlink(missing_ok=True)

    unexpected = []
    unsafe_owners = []
    wrong_candidate_owners = []
    for path in (workspace, *workspace.rglob("*")):
        relative = Path(".") if path == workspace else path.relative_to(workspace)
        allowed = allowed_write(relative, writable_files, writable_dirs)
        owner = owner_of(path)
        if allowed and owner != effective_uid:
            wrong_candidate_owners.append(relative.as_posix())
        elif not allowed and owner == effective_uid:
            unsafe_owners.append(relative.as_posix())
        if is_writable(path) and not allowed:
            unexpected.append(relative.as_posix())
    if wrong_candidate_owners:
        raise ValueError(
            "candidate paths are not owned by the research account: "
            + ", ".join(sorted(wrong_candidate_owners)[:20])
        )
    if unsafe_owners:
        raise ValueError(
            "non-candidate paths are owned by the research account and can be chmodded: "
            + ", ".join(sorted(unsafe_owners)[:20])
        )
    if unexpected:
        raise ValueError(
            "unexpected paths are writable by the research account: "
            + ", ".join(sorted(unexpected)[:20])
        )

    return len(writable_files) + len(writable_dirs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", help="Isolated workspace to inspect")
    parser.add_argument("--writable-file", action="append", dest="writable_files")
    parser.add_argument("--writable-dir", action="append", dest="writable_dirs")
    args = parser.parse_args()
    scoped = args.writable_files is not None or args.writable_dirs is not None
    try:
        count = check_workspace(
            args.workspace,
            writable_files=(args.writable_files or ()) if scoped else None,
            writable_dirs=(args.writable_dirs or ()) if scoped else None,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Verified {count} writable candidate path(s) and no others")
    return 0


if __name__ == "__main__":
    sys.exit(main())
