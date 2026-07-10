#!/usr/bin/env python3
"""Export fixed verification candidate paths from an isolated workspace."""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


FIXED_FILES = (
    "README.md",
    "index.html",
    "assets/js/patterns-data.js",
    "experiments/NOTES.md",
    "verification/DECISIONS.md",
    "verification/STATUS.md",
    "verification/pending-evidence.yaml",
)
EVIDENCE_DIR = "verification/evidence"
SLUG_FILE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.yaml$")
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_TOTAL_BYTES = 25 * 1024 * 1024
MAX_EVIDENCE_FILES = 1000


def regular_file(path):
    """Return true only for a non-symlink regular file."""
    return path.is_file() and not path.is_symlink()


def candidate_files(source):
    """Return validated (relative path, source path) candidate entries."""
    if source.is_symlink() or not source.is_dir():
        raise ValueError("isolated workspace must be a real directory")

    files = []
    for relative in FIXED_FILES:
        path = source / relative
        if not regular_file(path):
            raise ValueError(f"candidate path is missing or not a regular file: {relative}")
        files.append((relative, path))

    evidence = source / EVIDENCE_DIR
    if evidence.is_symlink() or not evidence.is_dir():
        raise ValueError(f"candidate path is missing or not a directory: {EVIDENCE_DIR}")
    evidence_paths = []
    for path in evidence.iterdir():
        if len(evidence_paths) >= MAX_EVIDENCE_FILES:
            raise ValueError(f"candidate has more than {MAX_EVIDENCE_FILES} evidence files")
        evidence_paths.append(path)
    for path in sorted(evidence_paths):
        relative = f"{EVIDENCE_DIR}/{path.name}"
        if not regular_file(path):
            raise ValueError(f"nested, symbolic, or non-file evidence is forbidden: {relative}")
        if SLUG_FILE_RE.fullmatch(path.name) is None:
            raise ValueError(f"invalid evidence filename: {relative}")
        files.append((relative, path))

    total = 0
    for relative, path in files:
        size = path.stat(follow_symlinks=False).st_size
        if size > MAX_FILE_BYTES:
            raise ValueError(f"candidate file exceeds 5 MiB: {relative}")
        total += size
    if total > MAX_TOTAL_BYTES:
        raise ValueError("candidate bundle exceeds 25 MiB")
    return files


def export_candidate(source, destination):
    """Copy only validated candidate files into the trusted checkout."""
    raw_source = Path(source)
    raw_destination = Path(destination)
    if raw_source.is_symlink():
        raise ValueError("isolated workspace must not be a symbolic link")
    if raw_destination.is_symlink():
        raise ValueError("trusted destination must not be a symbolic link")
    source = raw_source.resolve(strict=True)
    destination = raw_destination.resolve(strict=True)
    if source == destination:
        raise ValueError("source and destination must differ")

    files = candidate_files(source)
    for relative, source_path in files:
        destination_path = destination / relative
        if destination_path.is_symlink():
            raise ValueError(f"destination must not be a symbolic link: {relative}")
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, destination_path, follow_symlinks=False)
        os.chmod(destination_path, 0o644, follow_symlinks=False)
    return len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Isolated model workspace")
    parser.add_argument("destination", help="Trusted checkout to receive fixed paths")
    args = parser.parse_args()
    try:
        count = export_candidate(args.source, args.destination)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Exported {count} fixed candidate file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
