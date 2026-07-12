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
import ast
from collections import Counter
import os
import re
import subprocess
import sys
from pathlib import Path


class SpecificationValidator:
    """Validates machine-readable specifications for coverage and compliance"""
    
    def __init__(self, spec_file: str = "iam_policy_spec.md", test_dir: str = "tests"):
        self.spec_file = Path(spec_file)
        self.test_dir = Path(test_dir)
        self.authority_levels = {"system": 3, "platform": 2, "feature": 1}

    @staticmethod
    def _identifier_uniqueness_errors(content: str) -> list[str]:
        """Return duplicate declaration errors across the entire spec."""
        normative_requirement_ids = []
        for line in content.splitlines():
            if re.search(r'\b(?:MUST|SHOULD|MAY)\b', line):
                normative_requirement_ids.extend(
                    re.findall(r'\bREQ-\d{3}\b', line))
        heading_anchors = re.findall(
            r'^#{1,6}\s+.+?\s+\{#([^}\s]+)(?:\s+[^}]*)?\}\s*$',
            content,
            re.MULTILINE,
        )
        footnote_definitions = re.findall(
            r'^\[\^([^\]]+)\]:', content, re.MULTILINE)

        errors = []
        for requirement_id, count in sorted(
            Counter(normative_requirement_ids).items()):
            if count > 1:
                errors.append(
                    f"Duplicate requirement ID: {requirement_id} "
                    f"({count} declarations)")
        for anchor, count in sorted(Counter(heading_anchors).items()):
            if count > 1:
                errors.append(
                    f"Duplicate section anchor: {anchor} ({count} definitions)")
        for footnote, count in sorted(Counter(footnote_definitions).items()):
            if count > 1:
                errors.append(
                    f"Duplicate footnote definition: [^{footnote}] "
                    f"({count} definitions)")
        return errors
        
    def extract_specifications(self) -> dict[str, dict]:
        """Extract specifications with authority levels and test references"""
        if not self.spec_file.exists():
            print(f"❌ Specification file not found: {self.spec_file}")
            return {}
            
        content = self.spec_file.read_text(encoding="utf-8")
        uniqueness_errors = self._identifier_uniqueness_errors(content)
        if uniqueness_errors:
            print("❌ Ambiguous specification identifiers:")
            for error in uniqueness_errors:
                print(f"  {error}")
            return {}
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
            test_references = []

            for line in section_body.splitlines():
                if not re.search(r'\b(?:MUST|SHOULD|MAY)\b', line):
                    continue
                requirement = re.sub(r'\s*\[\^[^\]]+\]', '', line)
                requirement = requirement.strip().lstrip('-').strip()
                line_references = re.findall(r'\[\^([^\]]+)\]', line)
                requirement_match = re.search(r'\bREQ-\d{3}\b', requirement)
                requirement_id = (
                    requirement_match.group(0) if requirement_match else None
                )
                requirement_data = {
                    "id": requirement_id,
                    "text": requirement,
                    "reference_ids": line_references,
                }
                requirements.append(requirement_data)
                if requirement_id is None or not line_references:
                    unlinked_requirements.append(requirement)
                for reference_id in line_references:
                    test_references.append({
                        "requirement_id": requirement_id,
                        "id": reference_id,
                        "path": test_definitions.get(reference_id),
                    })

            # Anchored explanatory sections are useful documentation but are
            # not coverage units. Only normative sections enter the report.
            if not requirements:
                continue

            specifications[anchor] = {
                "title": title,
                "authority": authority,
                "authority_level": self.authority_levels.get(authority, 1),
                "test_references": test_references,
                "requirements": requirements,
                "unlinked_requirements": unlinked_requirements,
            }

        return specifications
    
    @staticmethod
    def _find_node(
        nodes: list[ast.AST], node_path: list[str]
    ) -> ast.AST | None:
        """Return the AST node identified by a pytest ``Class::method`` path."""
        current_nodes = nodes
        matching_node = None
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
                return None
            current_nodes = matching_node.body
        return matching_node

    @staticmethod
    def _normalize_node_path(node_path: list[str]) -> tuple[str, ...]:
        """Normalize parametrized pytest node suffixes for stable citations."""
        if not node_path:
            return ()
        normalized = list(node_path)
        normalized[-1] = normalized[-1].split("[", 1)[0]
        return tuple(normalized)

    def _collect_pytest_nodes(
        self,
    ) -> tuple[set[tuple[Path, tuple[str, ...]]], str | None]:
        """Collect executable pytest nodes under the configured test directory."""
        test_root = self.test_dir.resolve()
        if not test_root.is_dir():
            return set(), f"Test directory not found: {self.test_dir}"

        spec_root = self.spec_file.resolve().parent
        environment = os.environ.copy()
        environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--collect-only",
                "-q",
                "-o",
                "addopts=",
                "--rootdir",
                str(spec_root),
                str(test_root),
            ],
            cwd=spec_root,
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )
        if result.returncode != 0:
            details = (result.stderr or result.stdout).strip().splitlines()
            summary = details[-1] if details else "unknown collection error"
            return set(), f"Pytest collection failed: {summary}"

        collected = set()
        for raw_line in result.stdout.splitlines():
            line = raw_line.strip()
            if "::" not in line:
                continue
            file_name, *node_path = line.split("::")
            if not file_name.endswith(".py"):
                continue
            file_path = Path(file_name)
            if not file_path.is_absolute():
                file_path = spec_root / file_path
            collected.add((
                file_path.resolve(),
                self._normalize_node_path(node_path),
            ))
        return collected, None

    @staticmethod
    def _is_within(path: Path, directory: Path) -> bool:
        """Return whether ``path`` is contained by ``directory``."""
        try:
            path.relative_to(directory)
        except ValueError:
            return False
        return True

    def validate_test_references(
        self, specifications: dict[str, dict]
    ) -> dict[str, dict]:
        """Validate collected pytest nodes and per-requirement bindings."""
        validation_results = {}
        collected_nodes, collection_error = self._collect_pytest_nodes()
        test_root = self.test_dir.resolve()

        for spec_id, spec_data in specifications.items():
            result = {
                "validated_references": 0,
                "reference_errors": [],
                "unlinked_requirements": list(
                    spec_data["unlinked_requirements"]),
                "collection_error": collection_error,
            }

            if collection_error:
                validation_results[spec_id] = result
                continue

            for test_ref in spec_data["test_references"]:
                test_path = test_ref["path"]
                requirement_id = test_ref["requirement_id"]

                if not test_path:
                    result["reference_errors"].append(
                        f"Undefined test reference: [^{test_ref['id']}]")
                    continue

                if requirement_id is None:
                    result["reference_errors"].append(
                        f"Test reference [^{test_ref['id']}] cannot bind to "
                        "a requirement without a REQ-NNN identifier")
                    continue

                path_parts = test_path.split("::")
                file_path = path_parts[0]
                node_path = path_parts[1:]
                if not node_path:
                    result["reference_errors"].append(
                        f"Test reference must name a pytest node: {test_path}")
                    continue
                full_path = Path(file_path)
                if not full_path.is_absolute():
                    full_path = self.spec_file.resolve().parent / full_path
                full_path = full_path.resolve()

                if not self._is_within(full_path, test_root):
                    result["reference_errors"].append(
                        f"Test reference is outside test directory: {test_path}")
                    continue

                if not full_path.is_file():
                    result["reference_errors"].append(
                        f"Missing test file: {file_path}")
                    continue

                normalized_node = self._normalize_node_path(node_path)
                if (full_path, normalized_node) not in collected_nodes:
                    result["reference_errors"].append(
                        f"Uncollected pytest node: {test_path}")
                    continue

                try:
                    tree = ast.parse(full_path.read_text(encoding="utf-8"))
                    node = self._find_node(tree.body, list(normalized_node))
                except (OSError, SyntaxError) as error:
                    result["reference_errors"].append(
                        f"Error reading {file_path}: {error}")
                    continue

                docstring = ast.get_docstring(node, clean=False) if node else None
                documented_requirements = set(re.findall(
                    r"\bREQ-\d{3}\b", docstring or ""))
                if requirement_id not in documented_requirements:
                    result["reference_errors"].append(
                        f"Pytest node {test_path} does not declare "
                        f"{requirement_id} in its docstring")
                    continue

                result["validated_references"] += 1

            validation_results[spec_id] = result

        return validation_results

    @staticmethod
    def validation_errors(result: dict) -> list[str]:
        """Return human-readable errors without conflating accounting units."""
        errors = [
            f"Requirement has no test reference: {requirement}"
            for requirement in result["unlinked_requirements"]
        ]
        if result["collection_error"]:
            errors.append(result["collection_error"])
        errors.extend(result["reference_errors"])
        return errors
    
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
                               validation_results: dict[str, dict]) -> str:
        """Generate a report with distinct link and requirement accounting."""
        total_specs = len(specifications)
        total_tests = sum(len(spec["test_references"]) for spec in specifications.values())
        validated_tests = sum(
            result["validated_references"]
            for result in validation_results.values())
        invalid_tests = max(total_tests - validated_tests, 0)
        unlinked_requirements = sum(
            len(result["unlinked_requirements"])
            for result in validation_results.values())
        collection_failures = len({
            result["collection_error"]
            for result in validation_results.values()
            if result["collection_error"]
        })
        coverage_percentage = (
            (validated_tests / total_tests) * 100 if total_tests else 0)
        
        report = [
            "Specification Coverage Report",
            "=" * 35,
            f"Total specifications: {total_specs}",
            f"Total test references: {total_tests}",
            f"Validated test references: {validated_tests}",
            f"Invalid test references: {invalid_tests}",
            f"Unlinked requirements: {unlinked_requirements}",
            f"Collection failures: {collection_failures}",
            f"Coverage: {coverage_percentage:.1f}%",
            "",
        ]
        
        for spec_id, spec_data in specifications.items():
            test_count = len(spec_data["test_references"])
            result = validation_results[spec_id]
            linked_count = result["validated_references"]
            spec_coverage = (
                (linked_count / test_count) * 100 if test_count > 0 else 0
            )
            errors = self.validation_errors(result)
            status = (
                "✅" if not errors and linked_count == test_count and test_count
                else "⚠️" if test_count else "❌")
            report.append(
                f"{status} {spec_id}: {spec_coverage:.0f}% "
                f"({linked_count}/{test_count} references validated; "
                f"{len(result['unlinked_requirements'])} unlinked requirements)")
            
            for error in errors:
                report.append(f"    ❌ {error}")
        
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

        errors.extend(self._identifier_uniqueness_errors(content))
        
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
            has_errors = any(
                self.validation_errors(result)
                or result["validated_references"]
                != len(specifications[spec_id]["test_references"])
                for spec_id, result in validation_results.items()
            )
            if has_errors:
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
