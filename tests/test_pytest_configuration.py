"""Regression tests for repository-root pytest collection."""

from configparser import ConfigParser
from pathlib import Path


ROOT = Path(__file__).parent.parent


def test_root_pytest_collects_only_the_supported_repository_suite():
    config = ConfigParser()
    config.read(ROOT / "pytest.ini", encoding="utf-8")

    testpaths = config.get("pytest", "testpaths").split()
    excluded = config.get("pytest", "norecursedirs").split()

    assert testpaths == ["tests"]
    assert {"examples", "experiments"} <= set(excluded)
