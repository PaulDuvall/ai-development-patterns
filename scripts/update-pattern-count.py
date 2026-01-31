#!/usr/bin/env python3
"""
Script to automatically update the pattern count badges in README.md and index.html.
This script counts patterns from conftest.py and updates any matching shields.io badges.
"""

import os
import re
import sys
from pathlib import Path

def count_patterns_from_conftest():
    """Count patterns from the EXPECTED_PATTERNS list in conftest.py"""
    conftest_path = Path(__file__).parent.parent / "tests" / "conftest.py"

    if not conftest_path.exists():
        print(f"Error: conftest.py not found at {conftest_path}")
        return None

    with open(conftest_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find EXPECTED_PATTERNS list
    pattern_match = re.search(r'EXPECTED_PATTERNS = \[(.*?)\]', content, re.DOTALL)
    if not pattern_match:
        print("Error: EXPECTED_PATTERNS not found in conftest.py")
        return None

    # Count non-empty lines within the list
    patterns_content = pattern_match.group(1)
    pattern_lines = [line.strip() for line in patterns_content.split('\n') if line.strip() and not line.strip().startswith('#')]
    pattern_count = len([line for line in pattern_lines if '"' in line or "'" in line])

    return pattern_count

def update_pattern_badge(file_path: Path, pattern_count: int) -> bool:
    """Update the pattern count badge in a given file."""
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    badge_pattern = re.compile(r'(https://img\.shields\.io/badge/patterns-)(\d+)(-blue\.svg)')
    updated_content, substitutions = badge_pattern.subn(rf'\g<1>{pattern_count}\g<3>', content)

    if substitutions == 0:
        print(f"Warning: No pattern badges found to update in {file_path.name}")
        return False

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"✓ Updated {substitutions} badge reference(s) in {file_path.name}")
    return True

def main():
    """Main function to count patterns and update badges"""
    print("🔍 Counting patterns from conftest.py...")

    pattern_count = count_patterns_from_conftest()
    if pattern_count is None:
        print("❌ Failed to count patterns")
        sys.exit(1)

    print(f"✓ Found {pattern_count} patterns")

    repo_root = Path(__file__).parent.parent
    readme_path = repo_root / "README.md"
    index_path = repo_root / "index.html"

    print("📝 Updating pattern count badges...")
    updated_readme = update_pattern_badge(readme_path, pattern_count)
    updated_index = update_pattern_badge(index_path, pattern_count)

    if updated_readme and updated_index:
        print(f"✅ Successfully updated pattern count badges to {pattern_count}")

        # Output for GitHub Actions
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"pattern_count={pattern_count}\n")

        return pattern_count
    else:
        print("❌ Failed to update one or more pattern count badges")
        sys.exit(1)

if __name__ == "__main__":
    main()
