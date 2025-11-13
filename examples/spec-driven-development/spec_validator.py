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
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
import ast


class SpecificationValidator:
    """Validates machine-readable specifications for coverage and compliance"""
    
    def __init__(self, spec_file: str = "iam_policy_spec.md", test_dir: str = "tests"):
        self.spec_file = Path(spec_file)
        self.test_dir = Path(test_dir)
        self.authority_levels = {"system": 3, "platform": 2, "feature": 1}
        
    def extract_specifications(self) -> Dict[str, Dict]:
        """Extract specifications with authority levels and test references"""
        if not self.spec_file.exists():
            print(f"❌ Specification file not found: {self.spec_file}")
            return {}
            
        content = self.spec_file.read_text()
        specifications = {}
        
        # Extract anchored sections with authority levels
        section_pattern = r'## ([^{]+)\{#([^}]+)(?:\s+authority=([^}]+))?\}'
        test_ref_pattern = r'\[\^([^\]]+)\]:\s*([^\n]+)'
        
        # Find all sections
        for match in re.finditer(section_pattern, content):
            title = match.group(1).strip()
            anchor = match.group(2)
            authority = match.group(3) or "feature"  # Default authority
            
            specifications[anchor] = {
                "title": title,
                "authority": authority,
                "authority_level": self.authority_levels.get(authority, 1),
                "test_references": [],
                "requirements": []
            }
        
        # Find test references
        for match in re.finditer(test_ref_pattern, content):
            ref_id = match.group(1)
            test_path = match.group(2).strip()
            
            # Find which specification this reference belongs to
            for spec_id, spec_data in specifications.items():
                if f"[^{ref_id}]" in content:
                    spec_data["test_references"].append({
                        "id": ref_id,
                        "path": test_path
                    })
        
        # Extract requirements (lines starting with - or MUST/SHOULD)
        requirement_pattern = r'- (.+?)(?:\[|\n|$)'
        must_should_pattern = r'The system (MUST|SHOULD|MAY) (.+?)(?:\[|\n|$)'
        
        for match in re.finditer(requirement_pattern, content):
            req = match.group(1).strip()
            # Associate with nearest specification anchor
            # This is simplified - in practice you'd track section context
            for spec_data in specifications.values():
                if len(spec_data["requirements"]) < 5:  # Limit per section
                    spec_data["requirements"].append(req)
                    break
        
        return specifications
    
    def find_test_files(self) -> Set[str]:
        """Find all test files in the test directory"""
        test_files = set()
        if self.test_dir.exists():
            for test_file in self.test_dir.rglob("*.py"):
                if test_file.name.startswith("test_"):
                    test_files.add(str(test_file))
        return test_files
    
    def validate_test_references(self, specifications: Dict[str, Dict]) -> Dict[str, List[str]]:
        """Validate that referenced test files and functions exist"""
        validation_results = {}
        test_files = self.find_test_files()
        
        for spec_id, spec_data in specifications.items():
            missing_tests = []
            
            for test_ref in spec_data["test_references"]:
                test_path = test_ref["path"]
                
                # Parse test path (e.g., "tests/test_validation.py::test_arn_validation")
                if "::" in test_path:
                    file_path, function_name = test_path.split("::", 1)
                else:
                    file_path, function_name = test_path, None
                
                # Check if file exists
                full_path = Path(file_path)
                if not full_path.exists() and str(full_path) not in test_files:
                    missing_tests.append(f"Missing test file: {file_path}")
                    continue
                
                # Check if function exists (simplified - would need AST parsing for full validation)
                if function_name and full_path.exists():
                    try:
                        content = full_path.read_text()
                        if f"def {function_name}" not in content:
                            missing_tests.append(f"Missing test function: {function_name} in {file_path}")
                    except Exception as e:
                        missing_tests.append(f"Error reading {file_path}: {e}")
            
            validation_results[spec_id] = missing_tests
        
        return validation_results
    
    def check_authority_conflicts(self, specifications: Dict[str, Dict]) -> List[str]:
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
    
    def generate_coverage_report(self, specifications: Dict[str, Dict], 
                               validation_results: Dict[str, List[str]]) -> str:
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
    
    def validate_syntax(self) -> List[str]:
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
        
        # Validate authority levels
        invalid_authorities = re.findall(r'authority=([^}\s]+)', content)
        for auth in invalid_authorities:
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
    
    validator = SpecificationValidator(args.spec_file, args.test_dir)
    
    exit_code = validator.run_validation(
        check_coverage=args.check_coverage,
        check_conflicts=args.authority_conflicts,
        validate_syntax=bool(args.validate_syntax or args.check_coverage)
    )
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())