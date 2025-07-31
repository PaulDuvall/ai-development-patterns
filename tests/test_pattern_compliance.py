"""
Tests for pattern specification compliance against pattern-spec.md requirements
"""

import pytest
import re
from tests.utils.pattern_parser import PatternParser, ReferenceTableParser
from tests.conftest import (
    REQUIRED_MATURITY_LEVELS, 
    REQUIRED_PATTERN_SECTIONS,
    EXPECTED_PATTERNS
)


class TestPatternSpecCompliance:
    """Test suite for validating patterns against pattern-spec.md requirements"""
    
    def test_all_expected_patterns_exist(self, readme_content):
        """Verify all expected patterns from reference table exist as sections"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        missing_patterns = []
        for expected_pattern in EXPECTED_PATTERNS:
            if expected_pattern not in patterns:
                missing_patterns.append(expected_pattern)
        
        assert not missing_patterns, f"Missing pattern sections: {missing_patterns}"
    
    def test_pattern_header_structure(self, readme_content):
        """Verify each pattern follows exact header structure from spec"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        invalid_patterns = []
        
        for pattern_name, pattern in patterns.items():
            errors = []
            
            # Check maturity level exists and is valid
            if not pattern.maturity:
                errors.append("Missing maturity level")
            elif pattern.maturity not in REQUIRED_MATURITY_LEVELS:
                errors.append(f"Invalid maturity level: {pattern.maturity}")
            
            # Check description exists
            if not pattern.description:
                errors.append("Missing description")
            elif len(pattern.description.split('.')) > 2:  # Should be single sentence
                errors.append("Description should be a single sentence")
            
            # Check related patterns exist
            if not pattern.related_patterns:
                errors.append("Missing related patterns section")
            
            if errors:
                invalid_patterns.append({
                    'pattern': pattern_name,
                    'errors': errors
                })
        
        assert not invalid_patterns, f"Patterns with header structure issues: {invalid_patterns}"
    
    def test_maturity_levels_valid(self, readme_content):
        """Verify all patterns have valid maturity levels"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        invalid_maturity = []
        
        for pattern_name, pattern in patterns.items():
            if pattern.maturity and pattern.maturity not in REQUIRED_MATURITY_LEVELS:
                invalid_maturity.append({
                    'pattern': pattern_name,
                    'maturity': pattern.maturity
                })
        
        assert not invalid_maturity, f"Patterns with invalid maturity levels: {invalid_maturity}"
    
    def test_patterns_have_anti_patterns(self, readme_content):
        """Verify each pattern includes an anti-pattern section"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        missing_anti_patterns = []
        
        for pattern_name, pattern in patterns.items():
            # Look for anti-pattern content in the pattern
            has_anti_pattern = False
            
            # Check if anti-pattern section exists in content
            pattern_content = pattern.implementation_content + pattern.anti_pattern_content
            anti_pattern_indicators = [
                '#### Anti-pattern',
                '**Anti-pattern**',
                'Anti-pattern:',
                'What NOT to do'
            ]
            
            for indicator in anti_pattern_indicators:
                if indicator in pattern_content:
                    has_anti_pattern = True
                    break
            
            if not has_anti_pattern:
                missing_anti_patterns.append(pattern_name)
        
        assert not missing_anti_patterns, f"Patterns missing anti-pattern sections: {missing_anti_patterns}"
    
    def test_pattern_implementation_content_exists(self, readme_content):
        """Verify each pattern has implementation content"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        missing_implementation = []
        
        for pattern_name, pattern in patterns.items():
            implementation_content = pattern.implementation_content.strip()
            
            if len(implementation_content) < 100:  # Minimum content threshold
                missing_implementation.append({
                    'pattern': pattern_name,
                    'content_length': len(implementation_content)
                })
        
        assert not missing_implementation, f"Patterns with insufficient implementation content: {missing_implementation}"
    
    def test_pattern_descriptions_are_single_sentence(self, readme_content):
        """Verify pattern descriptions are single sentences as required by spec"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        multi_sentence_descriptions = []
        
        for pattern_name, pattern in patterns.items():
            if pattern.description:
                # Count sentences by counting periods (simple heuristic)
                sentence_count = pattern.description.count('.')
                if sentence_count > 1:
                    multi_sentence_descriptions.append({
                        'pattern': pattern_name,
                        'description': pattern.description,
                        'sentence_count': sentence_count
                    })
        
        assert not multi_sentence_descriptions, f"Patterns with multi-sentence descriptions: {multi_sentence_descriptions}"
    
    def test_anti_patterns_have_descriptive_names(self, readme_content):
        """Verify anti-patterns have descriptive names as required by spec"""
        # Look for anti-pattern sections and verify they have proper names
        lines = readme_content.split('\n')
        anti_pattern_issues = []
        
        current_pattern = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Track current pattern
            if re.match(r'^### [A-Za-z]', stripped):
                current_pattern = re.match(r'^### (.+)', stripped).group(1)
            
            # Check anti-pattern headers
            if '#### Anti-pattern' in stripped or '**Anti-pattern**' in stripped:
                # Check if it has a descriptive name after the colon
                if ':' in stripped:
                    anti_pattern_name = stripped.split(':', 1)[1].strip()
                    if not anti_pattern_name or len(anti_pattern_name) < 5:
                        anti_pattern_issues.append({
                            'pattern': current_pattern,
                            'line': i + 1,
                            'issue': 'Anti-pattern needs descriptive name'
                        })
                else:
                    anti_pattern_issues.append({
                        'pattern': current_pattern,
                        'line': i + 1,
                        'issue': 'Anti-pattern missing descriptive name'
                    })
        
        assert not anti_pattern_issues, f"Anti-patterns with naming issues: {anti_pattern_issues}"
    
    def test_pattern_organization_follows_spec(self, readme_content):
        """Verify patterns are organized correctly by category"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        category_issues = []
        
        # Expected categories from spec
        expected_categories = {
            "Foundation", "Development", "Operations", 
            "Security & Compliance", "Deployment Automation", "Monitoring & Maintenance"
        }
        
        for pattern_name, pattern in patterns.items():
            if pattern.category not in expected_categories and pattern.category != "":
                category_issues.append({
                    'pattern': pattern_name,
                    'category': pattern.category
                })
        
        assert not category_issues, f"Patterns in unexpected categories: {category_issues}"
    
    def test_related_patterns_are_hyperlinked(self, readme_content):
        """Verify related patterns sections contain hyperlinks"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        missing_hyperlinks = []
        
        for pattern_name, pattern in patterns.items():
            if pattern.related_patterns:
                # Check if related patterns are actually hyperlinked in content
                # This is a basic check - the link_checker will do more thorough validation
                related_text = str(pattern.related_patterns)
                if '[' not in related_text or ']' not in related_text:
                    missing_hyperlinks.append({
                        'pattern': pattern_name,
                        'related_patterns': pattern.related_patterns
                    })
        
        assert not missing_hyperlinks, f"Related patterns without hyperlinks: {missing_hyperlinks}"
    
    def test_reference_table_completeness(self, readme_content):
        """Verify reference table includes all implemented patterns"""
        parser = ReferenceTableParser(readme_content)
        table_patterns = parser.extract_reference_table()
        
        pattern_parser = PatternParser(readme_content)
        implemented_patterns = pattern_parser.extract_patterns()
        
        # Check patterns in table but not implemented
        table_only = set(table_patterns.keys()) - set(implemented_patterns.keys())
        # Check patterns implemented but not in table
        implementation_only = set(implemented_patterns.keys()) - set(table_patterns.keys())
        
        issues = []
        if table_only:
            issues.append(f"Patterns in table but not implemented: {list(table_only)}")
        if implementation_only:
            issues.append(f"Patterns implemented but not in table: {list(implementation_only)}")
        
        assert not issues, f"Reference table completeness issues: {issues}"