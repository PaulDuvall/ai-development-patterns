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
    "Foundation": ["AI Readiness Assessment", "Rules as Code", "AI Security Sandbox", 
                   "AI Developer Lifecycle", "AI Tool Integration", "AI Issue Generation"],
    "Development": ["Specification Driven Development", "AI Plan-First Development", "Progressive AI Enhancement",
                    "AI Choice Generation", "Parallelized AI Coding Agents", "AI Context Persistence",
                    "Constraint-Based AI Development", "Atomic Task Decomposition",
                    "Observable AI Development", "AI-Driven Refactoring",
                    "AI-Driven Architecture Design", "AI-Driven Traceability"],
    "Operations": ["Policy-as-Code Generation", "Security Scanning Orchestration", 
                   "Performance Baseline Management"]
}

# Expected patterns from the reference table
EXPECTED_PATTERNS = [
    "AI Readiness Assessment",
    "Rules as Code", 
    "AI Security Sandbox",
    "AI Developer Lifecycle",
    "AI Tool Integration",
    "AI Issue Generation",
    "Specification Driven Development",
    "AI Plan-First Development",
    "Progressive AI Enhancement",
    "AI Choice Generation",
    "Atomic Task Decomposition",
    "Parallelized AI Coding Agents",
    "AI Context Persistence",
    "Constraint-Based AI Development",
    "Observable AI Development",
    "AI-Driven Refactoring",
    "AI-Driven Architecture Design",
    "AI-Driven Traceability",
    "Policy-as-Code Generation",
    "Security Scanning Orchestration",
    "Performance Baseline Management"
]