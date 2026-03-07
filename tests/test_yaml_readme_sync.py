"""
Tests that patterns.yaml entries match README.md pattern headings.

Prevents drift between the machine-readable manifest and the human-readable
documentation.
"""

import yaml
import re
import pytest
from pathlib import Path
from conftest import REPO_ROOT, EXPECTED_PATTERNS


PATTERNS_YAML_PATH = REPO_ROOT / "patterns.yaml"


@pytest.fixture
def yaml_patterns():
    """Load and return patterns from patterns.yaml."""
    with open(PATTERNS_YAML_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["patterns"]


@pytest.fixture
def readme_headings():
    """Extract all ## and ### headings from README.md as a set of strings."""
    readme_path = REPO_ROOT / "README.md"
    headings = set()
    with open(readme_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"^#{2,3} (.+?)(?:\s*\{.*\})?\s*$", line)
            if match:
                headings.add(match.group(1).strip())
    return headings


class TestYamlReadmeSync:
    """Validate patterns.yaml stays in sync with README.md."""

    def test_every_yaml_pattern_has_readme_heading(
        self, yaml_patterns, readme_headings
    ):
        """Every pattern in patterns.yaml must have a matching ## heading."""
        missing = [
            p["name"]
            for p in yaml_patterns
            if p["name"] not in readme_headings
        ]
        assert not missing, (
            f"patterns.yaml entries with no matching README heading: {missing}"
        )

    def test_every_expected_pattern_in_yaml(self, yaml_patterns):
        """Every pattern in EXPECTED_PATTERNS must appear in patterns.yaml."""
        yaml_names = {p["name"] for p in yaml_patterns}
        missing = [ep for ep in EXPECTED_PATTERNS if ep not in yaml_names]
        assert not missing, (
            f"EXPECTED_PATTERNS entries missing from patterns.yaml: {missing}"
        )

    def test_yaml_anchors_match_readme_headings(
        self, yaml_patterns, readme_headings
    ):
        """Each YAML anchor must be the kebab-case form of the heading."""
        mismatches = []
        for p in yaml_patterns:
            if p["name"] not in readme_headings:
                continue
            expected_anchor = (
                "#" + re.sub(r"[^a-z0-9-]", "",
                             p["name"].lower().replace(" ", "-"))
            )
            if p["anchor"] != expected_anchor:
                mismatches.append(
                    f"{p['name']}: got {p['anchor']}, "
                    f"expected {expected_anchor}"
                )
        assert not mismatches, (
            f"Anchor mismatches: {mismatches}"
        )

    def test_yaml_ids_are_kebab_case_of_names(self, yaml_patterns):
        """Each YAML id must be the kebab-case form of the name."""
        mismatches = []
        for p in yaml_patterns:
            expected_id = re.sub(
                r"[^a-z0-9-]", "", p["name"].lower().replace(" ", "-")
            )
            if p["id"] != expected_id:
                mismatches.append(
                    f"{p['name']}: id={p['id']}, expected={expected_id}"
                )
        assert not mismatches, f"ID mismatches: {mismatches}"

    def test_no_duplicate_yaml_ids(self, yaml_patterns):
        """Pattern IDs in patterns.yaml must be unique."""
        ids = [p["id"] for p in yaml_patterns]
        duplicates = [pid for pid in ids if ids.count(pid) > 1]
        assert not duplicates, f"Duplicate pattern IDs: {set(duplicates)}"

    def test_yaml_pattern_count_matches_expected(self, yaml_patterns):
        """patterns.yaml should have the same count as EXPECTED_PATTERNS."""
        assert len(yaml_patterns) == len(EXPECTED_PATTERNS), (
            f"patterns.yaml has {len(yaml_patterns)} patterns, "
            f"EXPECTED_PATTERNS has {len(EXPECTED_PATTERNS)}"
        )
