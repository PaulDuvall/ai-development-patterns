#!/usr/bin/env python3
"""
Update pattern count badges in README.md and index.html.
Reads the count from patterns.yaml (single source of truth).
"""

import os
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
BADGE_RE = re.compile(r'(https://img\.shields\.io/badge/patterns-)(\d+)(-blue\.svg)')


def count_patterns():
    """Count patterns from patterns.yaml."""
    yaml_path = REPO_ROOT / "patterns.yaml"
    if not yaml_path.exists():
        print(f"Error: patterns.yaml not found at {yaml_path}")
        return None
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return len(data.get("patterns", []))


def read_file(path):
    """Read and return file content, or None if missing."""
    if not path.exists():
        print(f"Error: File not found at {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def update_badge_in_file(file_path, pattern_count):
    """Replace badge count in a single file. Returns True on success."""
    content = read_file(file_path)
    if content is None:
        return False
    updated, subs = BADGE_RE.subn(rf'\g<1>{pattern_count}\g<3>', content)
    if subs == 0:
        print(f"Warning: No pattern badges found in {file_path.name}")
        return False
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated)
    print(f"Updated {subs} badge(s) in {file_path.name}")
    return True


def write_github_output(pattern_count):
    """Write pattern count to GITHUB_OUTPUT if running in Actions."""
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"pattern_count={pattern_count}\n")


def main():
    """Count patterns and update badges."""
    pattern_count = count_patterns()
    if pattern_count is None:
        sys.exit(1)
    print(f"Found {pattern_count} patterns")

    readme_ok = update_badge_in_file(REPO_ROOT / "README.md", pattern_count)
    index_ok = update_badge_in_file(REPO_ROOT / "index.html", pattern_count)

    if not (readme_ok and index_ok):
        sys.exit(1)

    write_github_output(pattern_count)
    print(f"All badges updated to {pattern_count}")


if __name__ == "__main__":
    main()
