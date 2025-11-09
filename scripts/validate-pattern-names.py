#!/usr/bin/env python3
"""
Pattern Name Validation Script

Validates that all patterns and antipatterns in the AI Development Patterns
repository comply with the strict two-word naming convention.

Usage:
    python3 scripts/validate-pattern-names.py

Exit codes:
    0 - All validations passed
    1 - Validation failures found
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set


# Negative prefixes and modifiers for antipatterns
NEGATIVE_PREFIXES = {
    'broken', 'blind', 'over', 'under', 'false', 'un', 'premature',
    'reckless', 'static', 'manual', 'scattered', 'chaotic', 'unsafe',
    'reactive', 'confused', 'ignored', 'wasteful', 'overwhelming',
    'unchecked', 'redundant', 'shallow', 'hardcoded', 'contextless',
    'unprotected', 'overlapping', 'unplanned', 'isolated', 'monolithic',
    'bloated', 'unconstrained', 'constraint', 'delayed', 'undocumented',
    'random', 'unrestricted'
}

# Words to avoid in pattern names (too generic or redundant in AI context)
AVOID_WORDS = {'ai', 'pattern', 'helper', 'utility', 'common', 'general', 'manager', 'handler', 'service'}


class ValidationError:
    def __init__(self, pattern_name: str, error_type: str, message: str, line_num: int = None):
        self.pattern_name = pattern_name
        self.error_type = error_type
        self.message = message
        self.line_num = line_num

    def __str__(self):
        location = f" (line {self.line_num})" if self.line_num else ""
        return f"❌ {self.error_type}: '{self.pattern_name}'{location}\n   {self.message}"


class PatternValidator:
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []
        self.patterns_found: Set[str] = set()
        self.antipatterns_found: Set[str] = set()

    def count_words(self, name: str) -> int:
        """Count words in a pattern name. Hyphenated words count as one word."""
        # Remove hyphens within words (e.g., "Spec-First" is 1 word, "AI-Driven" is 1 word)
        # Split by spaces
        words = name.strip().split()
        return len(words)

    def has_negative_indicator(self, name: str) -> bool:
        """Check if antipattern name has a negative prefix or modifier."""
        words = name.lower().split()
        if not words:
            return False

        # Check first word for negative prefix
        first_word = words[0].replace('-', '')

        # Check if first word starts with negative prefix
        for prefix in NEGATIVE_PREFIXES:
            if first_word.startswith(prefix):
                return True

        # Check if first word IS a negative modifier
        if first_word in NEGATIVE_PREFIXES:
            return True

        return False

    def has_avoid_words(self, name: str) -> List[str]:
        """Check if pattern name contains words to avoid."""
        words = [w.lower().replace('-', '') for w in name.split()]
        found_avoid = []
        for word in words:
            if word in AVOID_WORDS:
                found_avoid.append(word)
        return found_avoid

    def is_title_case(self, name: str) -> bool:
        """Check if name follows Title Case convention."""
        words = name.split()
        for word in words:
            # Handle hyphenated words (e.g., "Spec-First")
            parts = word.split('-')
            for part in parts:
                if part and not part[0].isupper():
                    return False
        return True

    def validate_pattern_name(self, name: str, line_num: int = None) -> bool:
        """Validate a pattern name against all rules."""
        valid = True

        # Rule 1: Exactly two words
        word_count = self.count_words(name)
        if word_count != 2:
            self.errors.append(ValidationError(
                name, "Word Count",
                f"Must be exactly 2 words (found {word_count}). Hyphenated compounds count as one word.",
                line_num
            ))
            valid = False

        # Rule 2: Title Case
        if not self.is_title_case(name):
            self.errors.append(ValidationError(
                name, "Title Case",
                "Pattern name must use Title Case (each word capitalized)",
                line_num
            ))
            valid = False

        # Rule 3: Avoid generic words
        avoid_found = self.has_avoid_words(name)
        if avoid_found:
            self.warnings.append(
                f"⚠️  Pattern '{name}' contains generic/redundant words: {', '.join(avoid_found)}"
            )

        # Track pattern
        if valid:
            self.patterns_found.add(name)

        return valid

    def validate_antipattern_name(self, name: str, line_num: int = None) -> bool:
        """Validate an antipattern name against all rules."""
        valid = True

        # Rule 1: Exactly two words
        word_count = self.count_words(name)
        if word_count != 2:
            self.errors.append(ValidationError(
                name, "Word Count",
                f"Must be exactly 2 words (found {word_count})",
                line_num
            ))
            valid = False

        # Rule 2: Must have negative indicator
        if not self.has_negative_indicator(name):
            self.errors.append(ValidationError(
                name, "Negative Indicator",
                "Antipattern must have negative prefix or modifier (Broken, Blind, Over-, Under-, Un-, etc.)",
                line_num
            ))
            valid = False

        # Rule 3: Title Case
        if not self.is_title_case(name):
            self.errors.append(ValidationError(
                name, "Title Case",
                "Antipattern name must use Title Case",
                line_num
            ))
            valid = False

        # Track antipattern
        if valid:
            self.antipatterns_found.add(name)

        return valid

    def extract_patterns_from_reference_table(self, content: str, start_marker: str, end_marker: str) -> List[Tuple[str, int]]:
        """Extract pattern names from reference table in markdown."""
        patterns = []
        lines = content.split('\n')
        in_table = False

        for i, line in enumerate(lines, 1):
            if start_marker in line:
                in_table = True
                continue
            if end_marker in line:
                in_table = False
                break

            if in_table and '|' in line:
                # Parse markdown table row
                # Expected format: | [Pattern Name](#anchor) | Maturity | Dependencies |
                match = re.search(r'\|\s*\[([^\]]+)\]', line)
                if match:
                    pattern_name = match.group(1).strip()
                    # Skip header rows
                    if pattern_name not in ['Pattern', 'Pattern Name', '---', '']:
                        patterns.append((pattern_name, i))

        return patterns

    def extract_patterns_from_headers(self, content: str, header_level: str = '##') -> List[Tuple[str, int]]:
        """Extract pattern names from section headers."""
        patterns = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if line.startswith(f'{header_level} ') and not line.startswith(f'{header_level}#'):
                # Extract pattern name from header
                pattern_name = line.replace(f'{header_level} ', '').strip()
                # Skip common section headers
                skip_headers = [
                    'Foundation Patterns', 'Development Patterns', 'Operations Patterns',
                    'Anti-Patterns', 'Pattern Categories', 'Overview', 'Introduction',
                    'Experimental Patterns', 'Pattern Reference', 'Related Patterns',
                    'Core Implementation', 'Benefits', 'Dependencies', 'Implementation',
                    'Example', 'When to Use', 'How It Works', 'Anti-Pattern'
                ]
                if pattern_name not in skip_headers and len(pattern_name) < 50:
                    patterns.append((pattern_name, i))

        return patterns

    def validate_readme(self, file_path: Path) -> bool:
        """Validate patterns in README.md."""
        print(f"\n📄 Validating {file_path}...")

        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False

        content = file_path.read_text(encoding='utf-8')

        # Extract patterns from reference table (lines ~50-89)
        table_patterns = self.extract_patterns_from_reference_table(
            content,
            '| Pattern | Maturity | Dependencies |',
            '---'  # End after table section
        )

        print(f"  Found {len(table_patterns)} patterns in reference table")

        for pattern_name, line_num in table_patterns:
            self.validate_pattern_name(pattern_name, line_num)

        # Extract patterns from section headers (## Pattern Name)
        header_patterns = self.extract_patterns_from_headers(content, '##')

        # Filter to only pattern headers (skip common sections)
        pattern_headers = [p for p in header_patterns if self.count_words(p[0]) <= 4]

        print(f"  Found {len(pattern_headers)} potential pattern sections")

        # Extract antipatterns from ### Anti-Pattern: subsections
        antipattern_matches = re.finditer(r'###\s*Anti-Pattern:\s*([^\n]+)', content)
        antipatterns = [(m.group(1).strip(), content[:m.start()].count('\n') + 1) for m in antipattern_matches]

        print(f"  Found {len(antipatterns)} antipatterns")

        for antipattern_name, line_num in antipatterns:
            self.validate_antipattern_name(antipattern_name, line_num)

        return len(self.errors) == 0

    def validate_experiments_readme(self, file_path: Path) -> bool:
        """Validate patterns in experiments/README.md."""
        print(f"\n📄 Validating {file_path}...")

        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False

        content = file_path.read_text(encoding='utf-8')

        # Extract patterns from reference table
        table_patterns = self.extract_patterns_from_reference_table(
            content,
            '| Pattern | Dependencies |',
            '---'
        )

        print(f"  Found {len(table_patterns)} experimental patterns in reference table")

        for pattern_name, line_num in table_patterns:
            self.validate_pattern_name(pattern_name, line_num)

        # Extract antipatterns
        antipattern_matches = re.finditer(r'###\s*Anti-Pattern:\s*([^\n]+)', content)
        antipatterns = [(m.group(1).strip(), content[:m.start()].count('\n') + 1) for m in antipattern_matches]

        print(f"  Found {len(antipatterns)} experimental antipatterns")

        for antipattern_name, line_num in antipatterns:
            self.validate_antipattern_name(antipattern_name, line_num)

        return len(self.errors) == 0

    def check_for_old_names(self, repo_root: Path) -> List[Tuple[str, str, int]]:
        """Search for old pattern names that should have been renamed."""
        old_names = [
            "AI Readiness Assessment", "Rules as Code", "AI Security Sandbox",
            "AI Developer Lifecycle", "AI Tool Integration", "AI Issue Generation",
            "Specification Driven Development", "AI Plan-First Development",
            "Progressive AI Enhancement", "AI Choice Generation",
            "Atomic Task Decomposition", "Parallelized AI Coding Agents",
            "AI Context Persistence", "Constraint-Based AI Development",
            "Observable AI Development", "AI-Driven Refactoring",
            "AI-Driven Architecture Design", "AI-Driven Traceability",
            "Policy-as-Code Generation", "Security Scanning Orchestration",
            "Performance Baseline Management", "Human-AI Handoff Protocol",
            "Comprehensive AI Testing Strategy", "AI Workflow Orchestration",
            "AI Review Automation", "Technical Debt Forecasting",
            "AI-Guided Blue-Green Deployment", "Drift Detection & Remediation",
            "Release Note Synthesis", "Incident Response Automation",
            "Test Suite Health Management", "Dependency Upgrade Advisor",
            "On-Call Handoff Automation", "Chaos Engineering Scenarios",
            "ChatOps Security Integration", "Compliance Evidence Automation",
            "Context Window Optimization", "Visual Context Scaffolding",
            "AI Event Automation", "Custom AI Commands"
        ]

        found_old = []
        files_to_check = [
            repo_root / 'README.md',
            repo_root / 'experiments' / 'README.md',
            repo_root / 'CLAUDE.md'
            # pattern-spec.md excluded - contains intentional examples of old names
        ]

        for file_path in files_to_check:
            if not file_path.exists():
                continue

            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            for old_name in old_names:
                for i, line in enumerate(lines, 1):
                    if old_name in line and 'PATTERN_MIGRATION_GUIDE' not in line:
                        found_old.append((str(file_path.relative_to(repo_root)), old_name, i))

        return found_old

    def print_report(self):
        """Print validation report."""
        print("\n" + "="*80)
        print("VALIDATION REPORT")
        print("="*80)

        print(f"\n📊 Statistics:")
        print(f"  Patterns found: {len(self.patterns_found)}")
        print(f"  Antipatterns found: {len(self.antipatterns_found)}")
        print(f"  Total: {len(self.patterns_found) + len(self.antipatterns_found)}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        else:
            print(f"\n✅ All pattern names are compliant!")

        print("\n" + "="*80)


def main():
    """Main validation routine."""
    repo_root = Path(__file__).parent.parent
    validator = PatternValidator()

    print("🔍 AI Development Patterns - Name Validation")
    print("="*80)

    # Validate main README.md
    readme_valid = validator.validate_readme(repo_root / 'README.md')

    # Validate experiments/README.md
    experiments_valid = validator.validate_experiments_readme(repo_root / 'experiments' / 'README.md')

    # Check for old pattern names
    print("\n🔎 Checking for old pattern names...")
    old_names_found = validator.check_for_old_names(repo_root)

    if old_names_found:
        print(f"\n⚠️  Found {len(old_names_found)} references to old pattern names:")
        for file_path, old_name, line_num in old_names_found[:10]:  # Show first 10
            print(f"  {file_path}:{line_num} - '{old_name}'")
        if len(old_names_found) > 10:
            print(f"  ... and {len(old_names_found) - 10} more")
    else:
        print("  ✅ No old pattern names found")

    # Print final report
    validator.print_report()

    # Exit with appropriate code
    if validator.errors or old_names_found:
        print("\n❌ Validation FAILED")
        return 1
    else:
        print("\n✅ Validation PASSED")
        return 0


if __name__ == '__main__':
    sys.exit(main())
