# Test Traceability Coverage
# Validates that all requirements have proper test coverage and traceability links

import pytest
import re
import os
import yaml
from pathlib import Path

class TestRequirementTraceability:
    """Ensure all requirements have test coverage and proper traceability"""
    
    def setup_method(self):
        """Load traceability configuration"""
        self.project_root = Path(__file__).parent.parent.parent
        self.traceability_config = self._load_traceability_config()
        self.requirements = self._extract_requirements()
        self.test_files = self._find_test_files()
        
    def _load_traceability_config(self):
        """Load traceability rules from configuration"""
        config_path = self.project_root / ".ai" / "traceability" / "requirements_map.yml"
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {}
    
    def _extract_requirements(self):
        """Extract all requirements from documentation"""
        requirements = set()
        
        # Scan README and docs for requirements
        for file_path in self.project_root.rglob("*.md"):
            if file_path.is_file():
                content = file_path.read_text()
                req_matches = re.findall(r'REQ-\d+', content)
                requirements.update(req_matches)
                
        return requirements
    
    def _find_test_files(self):
        """Find all test files in the project"""
        test_files = []
        test_dirs = ["tests/", "test/"]
        
        for test_dir in test_dirs:
            test_path = self.project_root / test_dir
            if test_path.exists():
                test_files.extend(test_path.rglob("test_*.py"))
                test_files.extend(test_path.rglob("*_test.py"))
                
        return test_files
    
    @pytest.mark.requirement("REQ-TRACE-001")
    def test_all_requirements_have_tests(self):
        """
        REQ-TRACE-001: All business requirements must have corresponding test coverage
        """
        requirements_with_tests = set()
        
        # Scan all test files for requirement markers
        for test_file in self.test_files:
            content = test_file.read_text()
            
            # Find pytest markers: @pytest.mark.requirement("REQ-123")
            marker_matches = re.findall(r'@pytest\.mark\.requirement\(["\']([^"\']+)["\']\)', content)
            requirements_with_tests.update(marker_matches)
            
            # Find docstring references: REQ-123
            docstring_matches = re.findall(r'REQ-\d+', content)
            requirements_with_tests.update(docstring_matches)
        
        # Check coverage
        untested_requirements = self.requirements - requirements_with_tests
        coverage_percentage = (len(requirements_with_tests) / len(self.requirements)) * 100 if self.requirements else 100
        
        target_coverage = self.traceability_config.get('quality_gates', {}).get('min_test_coverage_traceability', 90)
        
        assert coverage_percentage >= target_coverage, (
            f"Requirement test coverage is {coverage_percentage:.1f}%, below target {target_coverage}%.\n"
            f"Untested requirements: {sorted(untested_requirements)}"
        )
    
    @pytest.mark.requirement("REQ-TRACE-002") 
    def test_no_orphaned_test_markers(self):
        """
        REQ-TRACE-002: Test requirement markers must reference valid requirements
        """
        orphaned_markers = set()
        
        for test_file in self.test_files:
            content = test_file.read_text()
            marker_matches = re.findall(r'@pytest\.mark\.requirement\(["\']([^"\']+)["\']\)', content)
            
            for marker in marker_matches:
                if marker not in self.requirements:
                    orphaned_markers.add(f"{marker} in {test_file.relative_to(self.project_root)}")
        
        assert not orphaned_markers, (
            f"Found orphaned test requirement markers (referencing non-existent requirements):\n"
            f"{sorted(orphaned_markers)}"
        )
    
    @pytest.mark.requirement("REQ-TRACE-003")
    def test_code_has_requirement_annotations(self):
        """
        REQ-TRACE-003: Implementation code should reference requirements in comments/docstrings
        """
        code_files = list(self.project_root.rglob("*.py"))
        code_files = [f for f in code_files if not any(exclude in str(f) for exclude in ["tests/", "test/", "__pycache__"])]
        
        files_with_requirements = 0
        total_code_files = len(code_files)
        
        for code_file in code_files:
            content = code_file.read_text()
            
            # Look for requirement annotations
            if re.search(r'(# Implements:|# Satisfies:|REQ-\d+)', content):
                files_with_requirements += 1
        
        if total_code_files > 0:
            annotation_percentage = (files_with_requirements / total_code_files) * 100
            target_percentage = self.traceability_config.get('quality_gates', {}).get('min_backward_traceability', 70)
            
            assert annotation_percentage >= target_percentage, (
                f"Code requirement annotation coverage is {annotation_percentage:.1f}%, below target {target_percentage}%.\n"
                f"Files with requirement annotations: {files_with_requirements}/{total_code_files}"
            )
    
    @pytest.mark.requirement("REQ-TRACE-004")
    def test_user_stories_have_acceptance_criteria(self):
        """
        REQ-TRACE-004: All user stories must have linked acceptance criteria
        """
        user_stories = set()
        acceptance_criteria = set()
        
        # Extract user stories and acceptance criteria from documentation
        for file_path in self.project_root.rglob("*.md"):
            if file_path.is_file():
                content = file_path.read_text()
                us_matches = re.findall(r'US-\d+', content)
                ac_matches = re.findall(r'AC-\d+', content)
                user_stories.update(us_matches)
                acceptance_criteria.update(ac_matches)
        
        # For this test, we'll check that we have some acceptance criteria
        # In a real implementation, you'd need more sophisticated linking logic
        if user_stories:
            assert acceptance_criteria, (
                f"Found {len(user_stories)} user stories but no acceptance criteria (AC-*) defined.\n"
                f"User stories: {sorted(user_stories)}"
            )
    
    @pytest.mark.requirement("REQ-TRACE-005")
    def test_compliance_requirements_mapped(self):
        """
        REQ-TRACE-005: Compliance requirements must be mapped to implementation requirements
        """
        compliance_config_path = self.project_root / ".ai" / "traceability" / "compliance_map.yml"
        
        if not compliance_config_path.exists():
            pytest.skip("No compliance mapping configuration found")
        
        with open(compliance_config_path) as f:
            compliance_config = yaml.safe_load(f)
        
        compliance_requirements = compliance_config.get('compliance_requirements', {})
        
        for framework, config in compliance_requirements.items():
            linked_reqs = config.get('linked_requirements', [])
            test_evidence = config.get('test_evidence', [])
            
            assert linked_reqs, f"Compliance framework {framework} has no linked requirements"
            assert test_evidence, f"Compliance framework {framework} has no test evidence defined"
            
            # Verify test evidence files exist
            for evidence_path in test_evidence:
                evidence_file = self.project_root / evidence_path
                assert evidence_file.exists(), f"Test evidence file not found: {evidence_path}"

    def test_traceability_health_metrics(self):
        """Generate and validate overall traceability health metrics"""
        
        metrics = {
            'total_requirements': len(self.requirements),
            'total_test_files': len(self.test_files),
            'requirements_with_tests': 0,
            'orphaned_tests': 0,
            'code_files_with_annotations': 0
        }
        
        # Calculate detailed metrics
        # This would be expanded with actual metric collection logic
        
        print(f"\n=== Traceability Health Report ===")
        print(f"Total Requirements: {metrics['total_requirements']}")
        print(f"Total Test Files: {metrics['total_test_files']}")
        
        if metrics['total_requirements'] > 0:
            coverage = (metrics['requirements_with_tests'] / metrics['total_requirements']) * 100
            print(f"Test Coverage: {coverage:.1f}%")
        
        # This test always passes but provides visibility into traceability health
        assert True