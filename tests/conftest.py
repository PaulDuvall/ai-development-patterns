"""
Test configuration and shared fixtures for AI Development Patterns validation
"""

import pytest
import os
from pathlib import Path

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent
README_PATH = REPO_ROOT / "README.md"
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

PATTERN_CATEGORIES = {
    "Foundation": ["Readiness Assessment", "Codified Rules", "Security Sandbox",
                   "Developer Lifecycle", "Tool Integration", "Issue Generation"],
    "Development": ["Spec-Driven Development", "Planned Implementation", "Progressive Enhancement",
                    "Image Spec", "Choice Generation", "Parallel Agents", "Context Persistence",
                    "Constrained Generation", "Event Automation", "Custom Commands", "Progressive Disclosure", "Atomic Decomposition",
                    "Observable Development", "Guided Refactoring",
                    "Guided Architecture", "Automated Traceability", "Error Resolution"],
    "Operations": ["Policy Generation", "Security Orchestration",
                   "Centralized Rules", "Baseline Management"]
}

# Expected patterns from the reference table
EXPECTED_PATTERNS = [
    "Readiness Assessment",
    "Codified Rules",
    "Security Sandbox",
    "Developer Lifecycle",
    "Tool Integration",
    "Issue Generation",
    "Spec-Driven Development",
    "Image Spec",
    "Planned Implementation",
    "Progressive Enhancement",
    "Choice Generation",
    "Atomic Decomposition",
    "Parallel Agents",
    "Context Persistence",
    "Constrained Generation",
    "Event Automation",
    "Custom Commands",
    "Progressive Disclosure",
    "Observable Development",
    "Guided Refactoring",
    "Guided Architecture",
    "Automated Traceability",
    "Error Resolution",
    "Policy Generation",
    "Security Orchestration",
    "Centralized Rules",
    "Baseline Management"
]
