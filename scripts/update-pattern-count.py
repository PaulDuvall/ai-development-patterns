#!/usr/bin/env python3
"""
Script to automatically update the pattern count badge in README.md
This script counts patterns from conftest.py and updates the badge dynamically.
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

def update_readme_badge(pattern_count):
    """Update the pattern count badge in README.md"""
    readme_path = Path(__file__).parent.parent / "README.md"

    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}")
        return False

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"✓ README.md found, length: {len(content)} characters")

    # Multiple patterns to try, from most specific to most general
    badge_patterns = [
        # Exact pattern with complete-pattern-reference link
        r'(\[!\[Patterns\]\(https://img\.shields\.io/badge/patterns-)(\d+)(-blue\.svg\)\]\(#complete-pattern-reference\))',
        # Pattern with any anchor link
        r'(\[!\[Patterns\]\(https://img\.shields\.io/badge/patterns-)(\d+)(-blue\.svg\)\]\([^)]+\))',
        # Pattern without link
        r'(\[!\[Patterns\]\(https://img\.shields\.io/badge/patterns-)(\d+)(-blue\.svg\))',
    ]

    updated_content = content
    pattern_found = False

    for i, pattern in enumerate(badge_patterns):
        def replace_count(match):
            nonlocal pattern_found
            pattern_found = True
            return f"{match.group(1)}{pattern_count}{match.group(3)}"

        test_content = re.sub(pattern, replace_count, content)
        if test_content != content:
            updated_content = test_content
            print(f"✓ Used pattern {i+1} to update badge")
            break

    if not pattern_found:
        print("Warning: No badge pattern found to update")
        print("Searching for any Patterns badge in content...")

        # Debug: show what patterns we can find
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            if 'Patterns' in line and 'shields.io' in line:
                print(f"Found badge-like line {line_num}: {repr(line)}")
        return False

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    return True

def main():
    """Main function to count patterns and update README"""
    print("🔍 Counting patterns from conftest.py...")

    pattern_count = count_patterns_from_conftest()
    if pattern_count is None:
        print("❌ Failed to count patterns")
        sys.exit(1)

    print(f"✓ Found {pattern_count} patterns")

    print("📝 Updating README.md badge...")
    if update_readme_badge(pattern_count):
        print(f"✅ Successfully updated pattern count badge to {pattern_count}")

        # Output for GitHub Actions
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"pattern_count={pattern_count}\n")

        return pattern_count
    else:
        print("❌ Failed to update README.md badge")
        sys.exit(1)

if __name__ == "__main__":
    main()