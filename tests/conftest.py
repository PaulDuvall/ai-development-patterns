"""
Test configuration and shared fixtures for AI Development Patterns validation
"""

import pytest
import os
import yaml
from pathlib import Path

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent
README_PATH = REPO_ROOT / "README.md"
PATTERNS_YAML_PATH = REPO_ROOT / "patterns.yaml"
PATTERN_SPEC_PATH = REPO_ROOT / "pattern-spec.md"
EXAMPLES_DIR = REPO_ROOT / "examples"
EXPERIMENTS_DIR = REPO_ROOT / "experiments"

@pytest.fixture
def repo_root():
    """Fixture providing repository root path"""
    return REPO_ROOT

@pytest.fixture
def readme_content():
    """Fixture providing README.md content"""
    with open(README_PATH, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def pattern_spec_content():
    """Fixture providing pattern-spec.md content"""
    with open(PATTERN_SPEC_PATH, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def examples_dir():
    """Fixture providing examples directory path"""
    return EXAMPLES_DIR

@pytest.fixture
def experiments_dir():
    """Fixture providing experiments directory path"""
    return EXPERIMENTS_DIR

# Configuration constants
REQUIRED_MATURITY_LEVELS = {"Beginner", "Intermediate", "Advanced"}
REQUIRED_PATTERN_SECTIONS = {
    "maturity",
    "description", 
    "related_patterns",
    "implementation",
    "anti_pattern"
}

# Derive EXPECTED_PATTERNS and PATTERN_CATEGORIES from patterns.yaml (single source of truth)
def _load_patterns_yaml():
    with open(PATTERNS_YAML_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    patterns = data["patterns"]
    expected = [p["name"] for p in patterns]
    categories = {}
    for p in patterns:
        cat = p["category"].capitalize()
        categories.setdefault(cat, []).append(p["name"])
    return expected, categories

EXPECTED_PATTERNS, PATTERN_CATEGORIES = _load_patterns_yaml()
