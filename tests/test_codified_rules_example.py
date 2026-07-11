"""Regression tests for the runnable Codified Rules example."""

import os
import re
import shutil
import stat
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent.parent
EXAMPLE = ROOT / "examples" / "codified-rules"
AGENTIC_CICD = ROOT / "docs" / "agentic-cicd.md"
WRAPPERS = (
    "check_specifications.sh",
    "check_traceability.sh",
    "run_orr_checklist.sh",
)


def run(*command, cwd=EXAMPLE):
    """Run one bounded local-only example command."""
    environment = {
        **os.environ,
        "PYTHON_BIN": os.environ.get("PYTHON", "python3"),
    }
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


def test_checked_in_enforcement_and_sample_project_are_runnable():
    """Every promised wrapper and the traced standard-library test must pass."""
    expected = (
        "Specification validation passed",
        "Traceability validation passed",
        "ORR structure validation passed",
    )
    for wrapper, message in zip(WRAPPERS, expected):
        path = EXAMPLE / wrapper
        assert path.stat().st_mode & stat.S_IXUSR
        syntax = run("bash", "-n", wrapper)
        assert syntax.returncode == 0, syntax.stderr
        result = run(f"./{wrapper}")
        assert result.returncode == 0, result.stderr
        assert message in result.stdout

    tests = run(
        "python3", "-m", "unittest", "discover",
        "-s", "sample-project/tests", "-t", "sample-project", "-v",
    )
    assert tests.returncode == 0, tests.stderr
    assert "Ran 2 tests" in tests.stderr


def test_specification_validation_fails_when_test_scenarios_are_missing(tmp_path):
    """A document with criteria but no TEST-* evidence must fail closed."""
    project = tmp_path / "project"
    shutil.copytree(EXAMPLE / "sample-project", project)
    specification = project / "specs" / "subscription-reminders.md"
    specification.write_text(
        "# SPEC-001 Subscription Reminders\n\n- AC-001: Reminder is due.\n",
        encoding="utf-8",
    )

    result = run("./check_specifications.sh", str(project))

    assert result.returncode == 1
    assert "contains no TEST-* scenario IDs" in result.stderr


def test_traceability_validation_fails_when_source_coverage_is_missing(tmp_path):
    """Every criterion must be referenced independently by tests and source."""
    project = tmp_path / "project"
    shutil.copytree(EXAMPLE / "sample-project", project)
    source = project / "src" / "subscription_reminders.py"
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "# Implements: specs/subscription-reminders.md#AC-002\n", ""),
        encoding="utf-8",
    )

    result = run("./check_traceability.sh", str(project))

    assert result.returncode == 1
    assert "missing implementation references" in result.stderr
    assert "AC-002" in result.stderr


def test_validation_rejects_a_symbolic_link_project_root(tmp_path):
    """A caller cannot bypass link rejection by supplying a linked scan root."""
    linked_project = tmp_path / "linked-project"
    linked_project.symlink_to(EXAMPLE / "sample-project", target_is_directory=True)

    result = run("./check_specifications.sh", str(linked_project))

    assert result.returncode == 1
    assert "project root must be a regular directory" in result.stderr


def test_orr_validation_fails_for_an_unchecked_control(tmp_path):
    """An unchecked readiness item cannot be reported as structurally complete."""
    checklist = tmp_path / "ORR_CHECKLIST.md"
    checklist.write_text(
        (EXAMPLE / "sample-project" / "ORR_CHECKLIST.md")
        .read_text(encoding="utf-8")
        .replace("[x] ORR-SECURITY", "[ ] ORR-SECURITY"),
        encoding="utf-8",
    )

    result = run("./run_orr_checklist.sh", str(checklist))

    assert result.returncode == 1
    assert "ORR checklist item is not complete: ORR-SECURITY" in result.stderr


def test_every_readme_shell_block_executes_in_a_clean_checkout():
    """Runnable-looking README commands may not depend on phantom scripts."""
    readme = (EXAMPLE / "README.md").read_text(encoding="utf-8")
    blocks = re.findall(
        r"^[ \t]*```bash[ \t]*\n(.*?)^[ \t]*```[ \t]*$",
        readme,
        flags=re.DOTALL | re.MULTILINE,
    )

    assert len(blocks) >= 8
    for index, block in enumerate(blocks, start=1):
        result = run("bash", "-c", "set -euo pipefail\n" + block)
        assert result.returncode == 0, (
            f"README bash block {index} failed:\n{block}\n{result.stderr}")


def test_agentic_cicd_integrity_requirements_fail_closed():
    """Documentation may not authorize identity bypass or ambiguous fast paths."""
    requirements = AGENTIC_CICD.read_text(encoding="utf-8")
    sci_002 = next(
        line for line in requirements.splitlines() if "[SCI-002]" in line)
    sci_011 = next(
        line for line in requirements.splitlines() if "[SCI-011]" in line)

    assert "SHALL NOT" in sci_002
    assert "bypass capability as a substitute" in sci_002
    assert "explicit, version-controlled allowlist" in sci_011
    assert "positively verifies every changed path and its content" in sci_011
    assert "fail closed and trigger the complete validation suite" in sci_011
