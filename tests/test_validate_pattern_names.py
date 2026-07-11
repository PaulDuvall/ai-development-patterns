"""Focused tests for the active pattern-name validator."""

import importlib.util
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate-pattern-names.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "validate_pattern_names", SCRIPT_PATH)
VALIDATOR_MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(VALIDATOR_MODULE)
PatternValidator = VALIDATOR_MODULE.PatternValidator


def _write_catalog(
        root: Path, *, stable_name: str = "Stable Pattern",
        stable_id: str = "stable-pattern",
        stable_anchor: str = "#stable-pattern",
        stable_display_name: str | None = None,
        stable_display_slug: str | None = None,
        experimental_name: str = "Experimental Pattern",
        experimental_slug: str = "experimental-pattern",
        stable_history: str = "",
        experimental_section: str | None = None) -> None:
    """Create the smallest repository layout accepted by the validator."""
    (root / "experiments").mkdir()
    stable_display_name = stable_display_name or stable_name
    stable_display_slug = stable_display_slug or stable_id
    experimental_section = experimental_section or experimental_name

    (root / "patterns.yaml").write_text(
        "patterns:\n"
        f"  - id: {stable_id}\n"
        f"    name: {stable_name}\n"
        f"    anchor: \"{stable_anchor}\"\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text(
        "# Catalog\n\n"
        "## Complete Pattern Reference\n\n"
        "| Pattern | Description |\n"
        "|---|---|\n"
        f"| **[{stable_display_name}](#{stable_display_slug})** | Example |\n\n"
        f"{stable_history}"
        f"## {stable_name}\n\n"
        "#### Anti-pattern: Broken Context\n",
        encoding="utf-8",
    )
    (root / "experiments" / "README.md").write_text(
        "# Experiments\n\n"
        "## Experimental Pattern Reference\n\n"
        "| Pattern | Description |\n"
        "|---|---|\n"
        f"| **[{experimental_name}](#{experimental_slug})** | Example |\n\n"
        f"### {experimental_section}\n\n"
        "#### Anti-pattern: False Testing\n",
        encoding="utf-8",
    )


def _error_types(validator: PatternValidator) -> set[str]:
    """Return the distinct error categories reported by the validator."""
    return {error.error_type for error in validator.errors}


def test_repository_catalog_validates_all_47_active_names():
    """The repository catalogs expose every canonical pattern and anti-pattern."""
    validator = PatternValidator()

    assert validator.validate_active_catalogs(REPO_ROOT)
    assert validator.stable_count == 29
    assert validator.experimental_count == 18
    assert len(validator.patterns_found) == 47
    assert validator.stable_antipattern_count == 45
    assert validator.experimental_antipattern_count == 24
    assert len(validator.antipatterns_found) == 69
    assert not validator.errors


def test_public_antipattern_reference_reuses_valid_canonical_names():
    """The downstream summary may only display canonical validated labels."""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    experiments = (REPO_ROOT / "experiments" / "README.md").read_text(
        encoding="utf-8")
    section = re.search(
        r"(?ms)^# Anti-Patterns Reference\s*$\n(.*?)(?=^---\s*$)", readme)
    assert section, "README anti-pattern reference section is missing"
    displayed = re.findall(
        r"(?m)^- \*\*\[([^\]]+)\]\(([^)]+)\)\*\*:", section.group(1))
    assert len(displayed) == 16
    assert len({name for name, _ in displayed}) == len(displayed)

    canonical = {
        item["name"]
        for content in (readme, experiments)
        for item in PatternValidator.antipattern_labels(content.splitlines())
    }
    validator = PatternValidator()
    for name, target in displayed:
        assert validator.validate_antipattern_name(name), (name, target)
        assert name in canonical, f"{name!r} is not a canonical H4 anti-pattern"
    assert not validator.errors


def test_name_validator_runs_weekly_and_on_demand_in_actions():
    """The validation workflow supports scheduled and manual name checks."""
    workflow = (REPO_ROOT / ".github" / "workflows" /
                "pattern-validation.yml").read_text(encoding="utf-8")

    assert re.search(r"(?m)^  workflow_dispatch:\s*$", workflow)
    assert re.search(r"(?m)^  schedule:\s*$", workflow)
    assert "python3 scripts/validate-pattern-names.py" in workflow


@pytest.mark.parametrize(
    "name",
    [
        "Agent Hooks",
        "Spec-Driven Development",
        "On-Call Handoff",
        "Autonomous SOC",
        "ChatOps Security",
    ],
)
def test_exact_two_word_title_case_names_are_valid(name):
    """Canonical two-word Title Case pattern names are accepted."""
    validator = PatternValidator()

    assert validator.validate_pattern_name(name)
    assert not validator.errors


@pytest.mark.parametrize(
    ("name", "expected_error"),
    [
        ("Hooks", "Word Count"),
        ("Agent Lifecycle Hooks", "Word Count"),
        ("agent Hooks", "Title Case"),
        ("MoDEL Routing", "Title Case"),
        ("AI Routing", "AI Prefix"),
        ("Ai Routing", "AI Prefix"),
        ("AI-Driven Development", "AI Prefix"),
    ],
)
def test_invalid_active_names_are_rejected(name, expected_error):
    """Malformed active pattern names report the expected error category."""
    validator = PatternValidator()

    assert not validator.validate_pattern_name(name)
    assert expected_error in _error_types(validator)


@pytest.mark.parametrize(
    "name",
    [
        "Opaque Runs",
        "False Consensus",
        "Over-Alerting",
        "Spec-Ignored",
    ],
)
def test_valid_antipattern_names_are_accepted(name):
    """Canonical cautionary anti-pattern names are accepted."""
    validator = PatternValidator()

    assert validator.validate_antipattern_name(name)
    assert not validator.errors


@pytest.mark.parametrize(
    ("name", "expected_error"),
    [
        ("Opaque Agent Runs", "Anti-pattern Word Count"),
        ("Voting Theater", "Cautionary Modifier"),
        ("Opaque runs", "Anti-pattern Title Case"),
        ("Opaque", "Anti-pattern Word Count"),
        ("", "Anti-pattern Word Count"),
    ],
)
def test_invalid_antipattern_names_are_rejected(name, expected_error):
    """Malformed anti-pattern names report the expected error category."""
    validator = PatternValidator()

    assert not validator.validate_antipattern_name(name)
    assert expected_error in _error_types(validator)


def test_empty_catalogs_never_report_success(tmp_path):
    """Empty stable and experimental catalogs fail validation explicitly."""
    (tmp_path / "experiments").mkdir()
    (tmp_path / "patterns.yaml").write_text("patterns: []\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "## Complete Pattern Reference\n\n| Pattern |\n|---|\n",
        encoding="utf-8",
    )
    (tmp_path / "experiments" / "README.md").write_text(
        "## Experimental Pattern Reference\n\n| Pattern |\n|---|\n",
        encoding="utf-8",
    )
    validator = PatternValidator()

    assert not validator.validate_active_catalogs(tmp_path)
    assert validator.stable_count == 0
    assert validator.experimental_count == 0
    assert [error.error_type for error in validator.errors].count("Empty Catalog") == 2


def test_missing_markdown_catalog_fails_without_crashing(tmp_path):
    """A missing stable catalog is reported as an error without an exception."""
    (tmp_path / "experiments").mkdir()
    (tmp_path / "patterns.yaml").write_text(
        "patterns:\n"
        "  - id: stable-pattern\n"
        "    name: Stable Pattern\n"
        '    anchor: "#stable-pattern"\n',
        encoding="utf-8",
    )
    (tmp_path / "experiments" / "README.md").write_text(
        "## Experimental Pattern Reference\n\n"
        "| Pattern |\n"
        "|---|\n"
        "| **[Experimental Pattern](#experimental-pattern)** |\n\n"
        "### Experimental Pattern\n",
        encoding="utf-8",
    )
    validator = PatternValidator()

    assert not validator.validate_active_catalogs(tmp_path)
    assert "Missing Catalog" in _error_types(validator)


def test_cross_catalog_duplicate_name_and_slug_are_rejected(tmp_path):
    """Names and slugs must remain unique across stable and experimental catalogs."""
    _write_catalog(
        tmp_path,
        experimental_name="Stable Pattern",
        experimental_slug="stable-pattern",
    )
    validator = PatternValidator()

    assert not validator.validate_active_catalogs(tmp_path)
    assert {"Duplicate Name", "Duplicate Slug"} <= _error_types(validator)


def test_catalog_ids_display_links_and_sections_must_match(tmp_path):
    """Catalog metadata, links, display names, and sections must agree."""
    _write_catalog(
        tmp_path,
        stable_id="wrong-id",
        stable_anchor="#wrong-anchor",
        stable_display_name="Different Pattern",
        stable_display_slug="different-pattern",
        experimental_slug="wrong-experimental-anchor",
        experimental_section="Different Experiment",
    )
    validator = PatternValidator()

    assert not validator.validate_active_catalogs(tmp_path)
    assert {
        "ID Mismatch",
        "Anchor Mismatch",
        "Missing Display Name",
        "Unexpected Display Name",
        "Missing Pattern Section",
        "Unexpected Pattern Section",
    } <= _error_types(validator)


def test_legacy_history_and_compatibility_anchors_are_not_active_names(tmp_path):
    """Historical prose and compatibility anchors do not create active patterns."""
    _write_catalog(
        tmp_path,
        stable_history=(
            '<a id="ai-readiness-assessment"></a>\n'
            "Historical name: AI Readiness Assessment.\n\n"
        ),
    )
    validator = PatternValidator()

    assert validator.validate_active_catalogs(tmp_path)
    assert validator.patterns_found == {"Stable Pattern", "Experimental Pattern"}
    assert not validator.errors


def test_fenced_heading_cannot_substitute_for_missing_pattern_section(tmp_path):
    """A heading inside a code fence cannot satisfy a catalog section."""
    _write_catalog(tmp_path)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    (tmp_path / "README.md").write_text(
        readme.replace(
            "## Stable Pattern\n",
            "```markdown\n## Stable Pattern\n```\n",
        ),
        encoding="utf-8",
    )
    validator = PatternValidator()

    assert not validator.validate_active_catalogs(tmp_path)
    assert "Missing Pattern Section" in _error_types(validator)


def test_fenced_reference_heading_cannot_shadow_real_catalog(tmp_path):
    """A fenced reference-table example cannot shadow the real catalog."""
    _write_catalog(tmp_path)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    (tmp_path / "README.md").write_text(
        readme.replace(
            "# Catalog\n\n",
            "# Catalog\n\n"
            "```markdown\n"
            "## Complete Pattern Reference\n\n"
            "| Pattern | Description |\n"
            "|---|---|\n"
            "| **[Shadow Pattern](#shadow-pattern)** | Not active |\n"
            "```\n\n",
        ),
        encoding="utf-8",
    )
    validator = PatternValidator()

    assert validator.validate_active_catalogs(tmp_path)
    assert not validator.errors


def test_antipattern_labels_must_use_h4_markup(tmp_path):
    """Canonical anti-pattern labels require the prescribed H4 markup."""
    _write_catalog(tmp_path)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    (tmp_path / "README.md").write_text(
        readme.replace(
            "#### Anti-pattern: Broken Context\n",
            "**Anti-pattern: Broken Context**\n",
        ),
        encoding="utf-8",
    )
    validator = PatternValidator()

    assert not validator.validate_active_catalogs(tmp_path)
    assert "Anti-pattern Markup" in _error_types(validator)


def test_fenced_antipattern_labels_are_not_canonical(tmp_path):
    """Anti-pattern examples inside code fences are ignored as canonical labels."""
    _write_catalog(tmp_path)
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    (tmp_path / "README.md").write_text(
        readme.replace(
            "# Catalog\n\n",
            "# Catalog\n\n"
            "```markdown\n"
            "#### Anti-pattern: Voting Theater\n"
            "````\n\n",
        ),
        encoding="utf-8",
    )
    validator = PatternValidator()

    assert validator.validate_active_catalogs(tmp_path)
    assert not validator.errors
