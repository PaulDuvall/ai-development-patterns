"""Tests for the deterministic traceability maintenance wrapper."""

from pathlib import Path
import subprocess


EXAMPLE_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = EXAMPLE_ROOT / "maintain_traceability.sh"


def test_maintenance_wrapper_has_valid_shell_syntax():
    result = subprocess.run(
        ["bash", "-n", str(SCRIPT)], capture_output=True, text=True)

    assert result.returncode == 0, result.stderr


def test_maintenance_wrapper_contains_no_legacy_mutation_or_model_calls():
    content = SCRIPT.read_text(encoding="utf-8")
    forbidden = ("a" + "i ", ".git" + "/hooks", "[^" + "req-")

    assert all(value not in content for value in forbidden)
    assert "spec_validator.py" in content
    assert "pre-commit run" in content


def test_maintenance_wrapper_help_is_read_only_and_current():
    result = subprocess.run(
        [str(SCRIPT), "--help"], capture_output=True, text=True)

    assert result.returncode == 0
    assert "never performs model inference" in result.stdout
    assert "--install-hooks" in result.stdout


def test_maintenance_wrapper_rejects_unknown_commands():
    result = subprocess.run(
        [str(SCRIPT), "--obsolete"], capture_output=True, text=True)

    assert result.returncode == 2
    assert "Unknown command: --obsolete" in result.stderr
