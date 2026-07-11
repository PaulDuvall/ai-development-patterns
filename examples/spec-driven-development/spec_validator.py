#!/usr/bin/env python3
"""
Specification Validator for SpecDriven AI Development
====================================================

Automated tool for validating specification coverage, authority conflicts,
and traceability in machine-readable specifications.

Usage:
    python spec_validator.py --check-coverage
    python spec_validator.py --authority-conflicts  
    python spec_validator.py --validate-syntax spec_file.md
"""

import argparse
import re
import sys
from pathlib import Path
import ast


class SpecificationValidator:
    """Validates machine-readable specifications for coverage and compliance"""
    
    def __init__(self, spec_file: str = "iam_policy_spec.md", test_dir: str = "tests"):
        self.spec_file = Path(spec_file)
        self.test_dir = Path(test_dir)
        self.authority_levels = {"system": 3, "platform": 2, "feature": 1}
        
    def extract_specifications(self) -> dict[str, dict]:
        """Extract specifications with authority levels and test references"""
        if not self.spec_file.exists():
            print(f"❌ Specification file not found: {self.spec_file}")
            return {}
            
        content = self.spec_file.read_text(encoding="utf-8")
        specifications = {}

        section_pattern = re.compile(
            r'^##\s+(.+?)\s+\{#([A-Za-z0-9_-]+)'
            r'(?:\s+authority=(system|platform|feature))?\}\s*$',
            re.MULTILINE,
        )
        test_definitions = dict(re.findall(
            r'^\[\^([^\]]+)\]:\s*(\S.*?)\s*$', content, re.MULTILINE))
        section_matches = list(section_pattern.finditer(content))

        for index, match in enumerate(section_matches):
            title = match.group(1).strip()
            anchor = match.group(2)
            authority = match.group(3) or "feature"  # Default authority

            section_end = (
                section_matches[index + 1].start()
                if index + 1 < len(section_matches)
                else len(content)
            )
            section_body = content[match.end():section_end]
            requirements = []
            unlinked_requirements = []
            cited_reference_ids = []

            for line in section_body.splitlines():
                if not re.search(r'\b(?:MUST|SHOULD|MAY)\b', line):
                    continue
                requirement = re.sub(r'\s*\[\^[^\]]+\]', '', line)
                requirement = requirement.strip().lstrip('-').strip()
                requirements.append(requirement)
                line_references = re.findall(r'\[\^([^\]]+)\]', line)
                if not line_references:
                    unlinked_requirements.append(requirement)
                for reference_id in line_references:
                    if reference_id not in cited_reference_ids:
                        cited_reference_ids.append(reference_id)

            # Anchored explanatory sections are useful documentation but are
            # not coverage units. Only normative sections enter the report.
            if not requirements:
                continue

            specifications[anchor] = {
                "title": title,
                "authority": authority,
                "authority_level": self.authority_levels.get(authority, 1),
                "test_references": [
                    {"id": reference_id,
                     "path": test_definitions.get(reference_id)}
                    for reference_id in cited_reference_ids
                ],
                "requirements": requirements,
                "unlinked_requirements": unlinked_requirements,
            }

        return specifications
    
    def find_test_files(self) -> set[str]:
        """Find all test files in the test directory"""
        test_files = set()
        if self.test_dir.exists():
            for test_file in self.test_dir.rglob("*.py"):
                if test_file.name.startswith("test_"):
                    test_files.add(str(test_file))
        return test_files

    @staticmethod
    def _node_exists(nodes: list[ast.AST], node_path: list[str]) -> bool:
        """Return whether an AST contains a pytest ``Class::method`` path."""
        current_nodes = nodes
        for node_name in node_path:
            matching_node = next(
                (
                    node for node in current_nodes
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef,
                                         ast.AsyncFunctionDef))
                    and node.name == node_name
                ),
                None,
            )
            if matching_node is None:
                return False
            current_nodes = matching_node.body
        return True
    
    def validate_test_references(self, specifications: dict[str, dict]) -> dict[str, list[str]]:
        """Validate that referenced test files and functions exist"""
        validation_results = {}

        for spec_id, spec_data in specifications.items():
            missing_tests = [
                f"Requirement has no test reference: {requirement}"
                for requirement in spec_data["unlinked_requirements"]
            ]

            for test_ref in spec_data["test_references"]:
                test_path = test_ref["path"]

                if not test_path:
                    missing_tests.append(
                        f"Undefined test reference: [^{test_ref['id']}]")
                    continue

                path_parts = test_path.split("::")
                file_path = path_parts[0]
                node_path = path_parts[1:]
                full_path = Path(file_path)
                if not full_path.is_absolute():
                    full_path = self.spec_file.resolve().parent / full_path

                # Check if file exists
                if not full_path.is_file():
                    missing_tests.append(f"Missing test file: {file_path}")
                    continue

                if node_path:
                    try:
                        tree = ast.parse(full_path.read_text(encoding="utf-8"))
                        if not self._node_exists(tree.body, node_path):
                            missing_tests.append(
                                f"Missing test node: {'::'.join(node_path)} "
                                f"in {file_path}")
                    except (OSError, SyntaxError) as error:
                        missing_tests.append(
                            f"Error reading {file_path}: {error}")

            validation_results[spec_id] = missing_tests

        return validation_results
    
    def check_authority_conflicts(self, specifications: dict[str, dict]) -> list[str]:
        """Check for potential authority conflicts"""
        conflicts = []
        
        # Group specifications by topic/area for conflict detection
        topic_groups = {}
        for spec_id, spec_data in specifications.items():
            # Simple topic grouping based on title keywords
            title_lower = spec_data["title"].lower()
            topic = "general"
            
            if "cli" in title_lower or "command" in title_lower:
                topic = "cli"
            elif "validation" in title_lower or "input" in title_lower:
                topic = "validation"
            elif "security" in title_lower or "auth" in title_lower:
                topic = "security"
            elif "output" in title_lower or "format" in title_lower:
                topic = "output"
            
            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append((spec_id, spec_data))
        
        # Check for authority conflicts within topic groups
        for topic, specs in topic_groups.items():
            if len(specs) > 1:
                authorities = [(spec_id, spec_data["authority"], spec_data["authority_level"]) 
                             for spec_id, spec_data in specs]
                
                # Check for conflicting requirements with different authorities
                for i, (spec_id1, auth1, level1) in enumerate(authorities):
                    for spec_id2, auth2, level2 in authorities[i+1:]:
                        if auth1 != auth2 and abs(level1 - level2) > 1:
                            conflicts.append(
                                f"Potential authority conflict in {topic}: "
                                f"{spec_id1} ({auth1}) vs {spec_id2} ({auth2})"
                            )
        
        return conflicts
    
    def generate_coverage_report(self, specifications: dict[str, dict],
                               validation_results: dict[str, list[str]]) -> str:
        """Generate specification coverage report"""
        total_specs = len(specifications)
        total_tests = sum(len(spec["test_references"]) for spec in specifications.values())
        missing_tests = sum(len(missing) for missing in validation_results.values())
        coverage_percentage = ((total_tests - missing_tests) / max(total_tests, 1)) * 100
        
        report = [
            "Specification Coverage Report",
            "=" * 35,
            f"Total specifications: {total_specs}",
            f"Total test references: {total_tests}",
            f"Missing tests: {missing_tests}",
            f"Coverage: {coverage_percentage:.1f}%",
            "",
        ]
        
        for spec_id, spec_data in specifications.items():
            test_count = len(spec_data["test_references"])
            missing_count = len(validation_results.get(spec_id, []))
            spec_coverage = ((test_count - missing_count) / max(test_count, 1)) * 100 if test_count > 0 else 0
            
            status = "✅" if missing_count == 0 and test_count > 0 else "⚠️" if test_count > 0 else "❌"
            report.append(f"{status} {spec_id}: {spec_coverage:.0f}% ({test_count - missing_count}/{test_count} tests linked)")
            
            # Show missing tests
            for missing in validation_results.get(spec_id, []):
                report.append(f"    ❌ {missing}")
        
        return "\n".join(report)
    
    def validate_syntax(self) -> list[str]:
        """Validate specification syntax and structure"""
        errors = []
        
        if not self.spec_file.exists():
            errors.append(f"Specification file not found: {self.spec_file}")
            return errors
        
        content = self.spec_file.read_text()
        
        # Check for required elements
        if not re.search(r'## .+\{#[^}]+\}', content):
            errors.append("No anchored headings found (format: ## Title {#anchor})")
        
        if not re.search(r'authority=(system|platform|feature)', content):
            errors.append("No authority levels found")
        
        if not re.search(r'\[\^[^\]]+\]:', content):
            errors.append("No test references found (format: [^test_id]: test/path)")
        
        # Check for MUST/SHOULD/MAY usage
        if not re.search(r'(MUST|SHOULD|MAY)', content):
            errors.append("No requirement strength indicators found (MUST/SHOULD/MAY)")
        
        # Validate authority attributes on anchored headings only. Examples in
        # prose may legitimately show placeholders such as ``authority=level``.
        heading_authorities = re.findall(
            r'^#{2,6}\s+.+?\s+\{#[^}\s]+'
            r'(?:\s+authority=([^}\s]+))?\}\s*$',
            content,
            re.MULTILINE,
        )
        for auth in filter(None, heading_authorities):
            if auth not in self.authority_levels:
                errors.append(f"Invalid authority level: {auth}")
        
        return errors
    
    def run_validation(self, check_coverage: bool = False, check_conflicts: bool = False,
                      validate_syntax: bool = False) -> int:
        """Run validation checks and return exit code"""
        exit_code = 0
        
        if validate_syntax:
            print("Validating specification syntax...")
            syntax_errors = self.validate_syntax()
            if syntax_errors:
                print("❌ Syntax validation failed:")
                for error in syntax_errors:
                    print(f"  {error}")
                exit_code = 1
            else:
                print("✅ Specification syntax is valid")
        
        if check_coverage or check_conflicts:
            specifications = self.extract_specifications()
            
            if not specifications:
                print("❌ No specifications found")
                return 1
        
        if check_coverage:
            print("\nChecking specification coverage...")
            validation_results = self.validate_test_references(specifications)
            report = self.generate_coverage_report(specifications, validation_results)
            print(report)
            
            # Set exit code based on coverage
            missing_tests = sum(len(missing) for missing in validation_results.values())
            if missing_tests > 0:
                exit_code = 1
        
        if check_conflicts:
            print("\nChecking authority conflicts...")
            conflicts = self.check_authority_conflicts(specifications)
            if conflicts:
                print("⚠️ Potential authority conflicts found:")
                for conflict in conflicts:
                    print(f"  {conflict}")
                exit_code = 1
            else:
                print("✅ No authority conflicts detected")
        
        return exit_code


def main():
    parser = argparse.ArgumentParser(description="Validate machine-readable specifications")
    parser.add_argument("--check-coverage", action="store_true", 
                       help="Check specification test coverage")
    parser.add_argument("--authority-conflicts", action="store_true",
                       help="Check for authority level conflicts")
    parser.add_argument("--validate-syntax", metavar="FILE",
                       help="Validate specification syntax")
    parser.add_argument("--spec-file", default="iam_policy_spec.md",
                       help="Specification file to validate")
    parser.add_argument("--test-dir", default="tests",
                       help="Test directory to scan")
    
    args = parser.parse_args()
    
    if not any([args.check_coverage, args.authority_conflicts, args.validate_syntax]):
        parser.print_help()
        return 1
    
    selected_spec_file = args.validate_syntax or args.spec_file
    validator = SpecificationValidator(selected_spec_file, args.test_dir)
    
    exit_code = validator.run_validation(
        check_coverage=args.check_coverage,
        check_conflicts=args.authority_conflicts,
        validate_syntax=bool(args.validate_syntax or args.check_coverage)
    )
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
