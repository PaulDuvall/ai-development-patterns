# Test Traceability Coverage
# Validates that all requirements have proper test coverage and traceability links

import re
import yaml
from pathlib import Path

from spec_validator import SpecificationValidator

class TestRequirementTraceability:
    """Ensure all requirements have test coverage and proper traceability"""

    def setup_method(self):
        """Load traceability configuration"""
        # This is a self-contained example. Repository-wide scanning silently
        # mixes unrelated requirements and implementation files into its
        # denominator, so every traceability surface is rooted here.
        self.project_root = Path(__file__).resolve().parent
        self.traceability_config = self._load_traceability_config()
        self.requirements = self._extract_requirements()
        self.test_files = self._find_test_files()
        self.validator = SpecificationValidator(
            self.project_root / self.traceability_config["specification_files"][0],
            self.project_root / "tests",
        )
        
    def _load_traceability_config(self):
        """Load traceability rules from configuration"""
        config_path = self.project_root / "traceability.yaml"
        assert config_path.is_file(), "traceability.yaml is required"
        with open(config_path, encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        assert isinstance(config, dict), "traceability.yaml must be a mapping"
        return config
    
    def _extract_requirements(self):
        """Extract requirement IDs only from declared specification files."""
        requirements = set()
        specification_files = self.traceability_config.get(
            "specification_files", [])
        assert specification_files, "Declare at least one specification file"
        for relative in specification_files:
            file_path = self.project_root / relative
            assert file_path.is_file(), f"Specification file not found: {relative}"
            content = file_path.read_text(encoding="utf-8")
            requirements.update(re.findall(r'\bREQ-\d{3}\b', content))
        assert requirements, "Declared specifications contain no REQ-NNN IDs"
        return requirements
    
    def _find_test_files(self):
        """Find all test files in the project"""
        test_path = self.project_root / "tests"
        assert test_path.is_dir(), "tests/ directory is required"
        return sorted(test_path.rglob("test_*.py"))

    def _test_requirement_references(self):
        """Return requirement IDs explicitly declared by test docstrings."""
        references = set()
        for test_file in self.test_files:
            content = test_file.read_text(encoding="utf-8")
            references.update(re.findall(r'\bREQ-\d{3}\b', content))
        return references

    def _validated_requirement_references(self):
        """Return requirements whose cited nodes collect and bind correctly."""
        specifications = self.validator.extract_specifications()
        validation_results = self.validator.validate_test_references(
            specifications)
        errors = [
            error
            for result in validation_results.values()
            for error in self.validator.validation_errors(result)
        ]
        assert not errors, "Invalid requirement-to-test links:\n" + "\n".join(errors)
        assert all(
            validation_results[section_id]["validated_references"]
            == len(section["test_references"])
            for section_id, section in specifications.items()
        ), "Not every requirement-to-test reference was validated"
        return {
            reference["requirement_id"]
            for section in specifications.values()
            for reference in section["test_references"]
        }

    def test_all_requirements_have_tests(self):
        """All declared requirements must have real executable test coverage."""
        requirements_with_tests = self._validated_requirement_references()
        untested_requirements = self.requirements - requirements_with_tests
        covered = self.requirements & requirements_with_tests
        coverage_percentage = (len(covered) / len(self.requirements)) * 100
        
        target_coverage = self.traceability_config.get('quality_gates', {}).get('min_test_coverage_traceability', 90)
        
        assert coverage_percentage >= target_coverage, (
            f"Requirement test coverage is {coverage_percentage:.1f}%, below target {target_coverage}%.\n"
            f"Untested requirements: {sorted(untested_requirements)}"
        )

    def test_specification_identifiers_are_unique(self):
        """The checked-in specification must pass structural uniqueness checks."""
        assert self.validator.validate_syntax() == []
    
    def test_no_orphaned_test_requirement_references(self):
        """Tests may reference only requirement IDs declared by the spec."""
        orphaned = self._test_requirement_references() - self.requirements
        assert not orphaned, (
            "Found test references to undeclared requirements:\n"
            f"{sorted(orphaned)}"
        )
    
    def test_code_has_requirement_annotations(self):
        """Declared implementation files must link back to valid requirements."""
        relative_files = self.traceability_config.get(
            "implementation_files", [])
        assert relative_files, "Declare at least one implementation file"
        code_files = [self.project_root / relative for relative in relative_files]
        assert all(path.is_file() for path in code_files), (
            f"Missing implementation files: "
            f"{[str(path) for path in code_files if not path.is_file()]}"
        )
        files_with_requirements = 0
        annotated_requirements = set()
        for code_file in code_files:
            content = code_file.read_text(encoding="utf-8")
            annotations = set(re.findall(r'\bREQ-\d{3}\b', content))
            orphaned = annotations - self.requirements
            assert not orphaned, (
                f"{code_file.name} references undeclared requirements: "
                f"{sorted(orphaned)}")
            if annotations:
                files_with_requirements += 1
                annotated_requirements.update(annotations)

        annotation_percentage = (files_with_requirements / len(code_files)) * 100
        target_percentage = self.traceability_config.get('quality_gates', {}).get('min_backward_traceability', 70)
        assert annotation_percentage >= target_percentage, (
            f"Code requirement annotation coverage is {annotation_percentage:.1f}%, below target {target_percentage}%.\n"
            f"Files with requirement annotations: {files_with_requirements}/{len(code_files)}"
        )
        missing = self.requirements - annotated_requirements
        assert not missing, (
            "Implementation annotations do not cover requirements: "
            f"{sorted(missing)}")

    def test_traceability_health_metrics(self):
        """Generate and validate overall traceability health metrics"""
        requirements_with_tests = (
            self.requirements & self._validated_requirement_references())
        implementation_text = "\n".join(
            (self.project_root / relative).read_text(encoding="utf-8")
            for relative in self.traceability_config["implementation_files"])
        annotated = self.requirements & set(
            re.findall(r'\bREQ-\d{3}\b', implementation_text))
        metrics = {
            'total_requirements': len(self.requirements),
            'total_test_files': len(self.test_files),
            'requirements_with_tests': len(requirements_with_tests),
            'orphaned_tests': len(
                self._test_requirement_references() - self.requirements),
            'requirements_with_code': len(annotated),
        }

        print(f"\n=== Traceability Health Report ===")
        print(f"Total Requirements: {metrics['total_requirements']}")
        print(f"Total Test Files: {metrics['total_test_files']}")
        coverage = (metrics['requirements_with_tests'] / metrics['total_requirements']) * 100
        print(f"Test Traceability: {coverage:.1f}%")
        print(f"Requirements Linked to Code: {metrics['requirements_with_code']}")

        assert metrics['orphaned_tests'] == 0
        assert metrics['requirements_with_tests'] == metrics['total_requirements']
        assert metrics['requirements_with_code'] == metrics['total_requirements']
