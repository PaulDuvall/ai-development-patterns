"""Regression tests for repository-root pytest collection."""

from configparser import ConfigParser
from pathlib import Path


ROOT = Path(__file__).parent.parent
SPEC_EXAMPLE = ROOT / "examples" / "spec-driven-development"


def test_root_pytest_collects_only_the_supported_repository_suite():
    config = ConfigParser()
    config.read(ROOT / "pytest.ini", encoding="utf-8")

    testpaths = config.get("pytest", "testpaths").split()
    excluded = config.get("pytest", "norecursedirs").split()

    assert testpaths == ["tests"]
    assert {"examples", "experiments"} <= set(excluded)


def test_spec_driven_example_enforces_its_embedded_coverage_gate():
    """The nested suite must use active pytest syntax and pinned tooling."""
    config = ConfigParser()
    config.read(SPEC_EXAMPLE / "pytest.ini", encoding="utf-8")

    assert config.has_section("pytest")
    assert not config.has_section("tool:pytest")
    assert config.get("pytest", "testpaths").split() == [
        "tests", "test_requirement_coverage.py"]
    addopts = config.get("pytest", "addopts").split()
    assert "--cov=iam_policy_generator" in addopts
    assert "--cov=spec_validator" in addopts
    assert "--cov-fail-under=85" in addopts

    requirements = {
        line.strip()
        for line in (SPEC_EXAMPLE / "requirements.txt").read_text(
            encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    assert requirements == {
        "PyYAML==6.0.3",
        "pre-commit==4.6.0",
        "pytest==9.1.1",
        "pytest-cov==7.1.0",
    }
