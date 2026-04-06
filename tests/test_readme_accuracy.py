"""
Tests for README.md accuracy and consistency validation
"""

import os
import pytest
import re
from utils.pattern_parser import PatternParser, ReferenceTableParser
from utils.experimental_pattern_parser import ExperimentalPatternParser
from conftest import PATTERN_CATEGORIES, EXPECTED_PATTERNS, EXPERIMENTS_DIR


class TestReadmeAccuracy:
    """Test suite for validating README.md accuracy and internal consistency"""
    
    def test_pattern_reference_table_matches_implementations(self, readme_content):
        """Verify reference table exactly matches implemented patterns"""
        table_parser = ReferenceTableParser(readme_content)
        pattern_parser = PatternParser(readme_content)
        
        table_patterns = set(table_parser.extract_reference_table().keys())
        implemented_patterns = set(pattern_parser.extract_patterns().keys())
        
        # Check for mismatches
        only_in_table = table_patterns - implemented_patterns
        only_implemented = implemented_patterns - table_patterns
        
        errors = []
        if only_in_table:
            errors.append(f"Patterns in reference table but not implemented: {list(only_in_table)}")
        if only_implemented:
            errors.append(f"Patterns implemented but missing from reference table: {list(only_implemented)}")
        
        assert not errors, f"Reference table mismatch: {errors}"
    
    def test_pattern_count_consistency(self, readme_content):
        """Verify pattern counts are consistent throughout document"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        # Count patterns by category
        category_counts = {}
        for pattern in patterns.values():
            category = pattern.category if pattern.category else "Unknown"
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Verify we have the expected total number of patterns
        total_patterns = len(patterns)
        expected_total = len(EXPECTED_PATTERNS)
        
        assert total_patterns == expected_total, \
            f"Expected {expected_total} patterns, found {total_patterns}"
        
        # Verify Foundation patterns are present
        foundation_patterns = [p for p in patterns.values() if p.category == "Foundation"]
        assert len(foundation_patterns) >= 5, \
            f"Expected at least 5 Foundation patterns, found {len(foundation_patterns)}"
    
    def test_maturity_level_distribution(self, readme_content):
        """Verify maturity levels are properly distributed"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        maturity_counts = {"Beginner": 0, "Intermediate": 0, "Advanced": 0}
        
        for pattern in patterns.values():
            if pattern.maturity in maturity_counts:
                maturity_counts[pattern.maturity] += 1
        
        # Should have patterns at all maturity levels
        for level, count in maturity_counts.items():
            assert count > 0, f"No patterns found at {level} maturity level"
        
        # Intermediate should be the most common (as designed)
        assert maturity_counts["Intermediate"] >= maturity_counts["Beginner"], \
            "Should have at least as many Intermediate as Beginner patterns"
    
    def test_pattern_organization_structure(self, readme_content):
        """Verify patterns are organized in correct structure"""
        lines = readme_content.split('\n')
        
        # Track section order
        section_order = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('# ') and 'Pattern' in stripped:
                section_name = stripped.replace('# ', '').strip()
                section_order.append(section_name)
        
        # Verify expected section order
        expected_order = ["Foundation Patterns", "Development Patterns", "Operations Patterns"]
        found_sections = [s for s in section_order if s in expected_order]
        
        assert found_sections == expected_order, \
            f"Pattern sections not in correct order. Expected: {expected_order}, Found: {found_sections}"
    
    def test_dependency_references_exist(self, readme_content):
        """Verify all dependency references point to existing patterns"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        all_pattern_names = set(table_data.keys())
        dependency_errors = []
        
        for pattern_name, data in table_data.items():
            dependencies = data.get('dependencies', '')
            if dependencies and dependencies != 'None':
                # Parse dependencies (comma-separated, may have markdown links)
                dep_names = []
                
                # Extract pattern names from dependencies text
                # Handle both plain text and markdown links
                if '[' in dependencies:
                    # Extract from markdown links
                    dep_matches = re.findall(r'\\[([^\\]]+)\\]', dependencies)
                    dep_names.extend(dep_matches)
                else:
                    # Split by comma for plain text
                    dep_names = [d.strip() for d in dependencies.split(',')]
                
                # Check each dependency exists
                for dep_name in dep_names:
                    dep_name = dep_name.strip()
                    if dep_name and dep_name not in all_pattern_names:
                        dependency_errors.append({
                            'pattern': pattern_name,
                            'missing_dependency': dep_name
                        })
        
        assert not dependency_errors, f"Patterns with invalid dependencies: {dependency_errors}"
    
    def test_mermaid_diagrams_syntax(self, readme_content):
        """Verify Mermaid diagrams have correct syntax"""
        lines = readme_content.split('\n')
        
        diagram_errors = []
        in_mermaid = False
        current_diagram_start = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if stripped == '```mermaid':
                in_mermaid = True
                current_diagram_start = i + 1
            elif stripped == '```' and in_mermaid:
                in_mermaid = False
                # Basic syntax validation for the diagram
                diagram_lines = lines[current_diagram_start:i]
                if diagram_lines:
                    first_line = diagram_lines[0].strip()
                    
                    # Check for valid diagram types
                    valid_types = ['graph', 'sequenceDiagram', 'classDiagram', 'gitGraph']
                    if not any(first_line.startswith(t) for t in valid_types):
                        diagram_errors.append({
                            'line': current_diagram_start,
                            'error': f'Unknown diagram type: {first_line}'
                        })
        
        assert not diagram_errors, f"Mermaid diagram syntax errors: {diagram_errors}"
    
    def test_code_block_language_tags(self, readme_content):
        """Verify code blocks have appropriate language tags"""
        lines = readme_content.split('\n')
        
        code_block_issues = []
        
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                language = line.strip()[3:].strip()
                
                # Skip mermaid and empty language tags (sometimes OK)
                if language and language != 'mermaid':
                    # Common valid languages
                    valid_languages = {
                        'bash', 'shell', 'sh', 'python', 'py', 'yaml', 'yml', 
                        'json', 'javascript', 'js', 'docker', 'dockerfile',
                        'markdown', 'md', 'xml', 'html', 'css', 'sql'
                    }
                    
                    if language.lower() not in valid_languages:
                        code_block_issues.append({
                            'line': i + 1,
                            'language': language,
                            'suggestion': 'Consider using standard language identifier'
                        })
        
        # This is a warning rather than failure - some custom languages may be valid
        if code_block_issues:
            print(f"Warning: Potentially non-standard language tags: {code_block_issues}")
    
    def test_pattern_naming_consistency(self, readme_content):
        """Verify pattern names are consistent across all references"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        # Check for naming inconsistencies
        naming_issues = []
        
        for pattern_name in patterns.keys():
            if pattern_name not in table_data:
                # Check for similar names (potential typos)
                similar_names = [name for name in table_data.keys() 
                               if self._similar_strings(pattern_name, name)]
                if similar_names:
                    naming_issues.append({
                        'pattern': pattern_name,
                        'similar_in_table': similar_names,
                        'issue': 'Potential naming inconsistency'
                    })
        
        assert not naming_issues, f"Pattern naming inconsistencies: {naming_issues}"
    
    def test_anti_pattern_completeness(self, readme_content):
        """Verify all patterns have anti-patterns with sufficient content"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        insufficient_anti_patterns = []
        
        for pattern_name, pattern in patterns.items():
            anti_pattern_content = pattern.anti_pattern_content.strip()
            
            # Anti-pattern should have reasonable content length
            if len(anti_pattern_content) < 50:  # Minimum threshold
                insufficient_anti_patterns.append({
                    'pattern': pattern_name,
                    'content_length': len(anti_pattern_content)
                })
        
        assert not insufficient_anti_patterns, \
            f"Patterns with insufficient anti-pattern content: {insufficient_anti_patterns}"
    
    def test_examples_directory_references(self, readme_content, examples_dir):
        """Verify references to examples directory point to existing directories"""
        import os
        
        # Find all references to examples/ directory
        example_refs = re.findall(r'examples/([a-zA-Z0-9-_/]+)', readme_content)
        
        missing_examples = []
        
        for ref in example_refs:
            # Remove any trailing file references, just check directory
            dir_path = ref.split('/')[0] if '/' in ref else ref
            full_path = os.path.join(examples_dir, dir_path)
            
            if not os.path.exists(full_path):
                missing_examples.append(ref)
        
        assert not missing_examples, f"References to non-existent examples: {missing_examples}"
    
    def _similar_strings(self, s1: str, s2: str) -> bool:
        """Check if two strings are similar (for detecting typos)"""
        from difflib import SequenceMatcher
        ratio = SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
        return 0.7 <= ratio < 1.0  # Similar but not identical


class TestExperimentalReadmeAccuracy:
    """Validate experiments/README.md accuracy and internal consistency"""

    @pytest.fixture
    def exp_content(self):
        readme_path = EXPERIMENTS_DIR / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def exp_parser(self, exp_content):
        return ExperimentalPatternParser(exp_content)

    def test_examples_index_matches_disk(self):
        """experiments/examples/README.md index must match actual subdirectories"""
        examples_dir = EXPERIMENTS_DIR / "examples"
        index_path = examples_dir / "README.md"
        if not index_path.exists():
            pytest.skip("experiments/examples/README.md not found")

        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()

        # Extract directory names from the table links
        linked_dirs = set(re.findall(r'\[`([^`]+)/`\]', index_content))

        # Get git-tracked subdirectories (excludes empty/untracked placeholders)
        from utils.git_utils import git_tracked_child_dirs
        repo_root = EXPERIMENTS_DIR.parent
        actual_dirs = {
            d.name for d in git_tracked_child_dirs(repo_root, "experiments/examples")
        }

        in_index_not_on_disk = linked_dirs - actual_dirs
        on_disk_not_in_index = actual_dirs - linked_dirs

        issues = []
        if in_index_not_on_disk:
            issues.append(f"Listed in index but missing on disk: {sorted(in_index_not_on_disk)}")
        if on_disk_not_in_index:
            issues.append(f"On disk but missing from index: {sorted(on_disk_not_in_index)}")

        assert not issues, f"experiments/examples index mismatch: {issues}"

    def test_experimental_file_references_exist(self, exp_content):
        """File paths referenced outside code blocks must exist on disk"""
        lines = exp_content.split('\n')
        in_code_block = False
        refs = set()

        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            # Match markdown links and prose references to examples/ paths
            found = re.findall(
                r'(?:examples|scripts)/[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_.-]+)*/?',
                line
            )
            refs.update(found)

        missing = []
        for ref in sorted(refs):
            full = EXPERIMENTS_DIR / ref
            if not full.exists():
                missing.append(ref)

        assert not missing, \
            f"File references in experiments/README.md point to missing paths: {missing}"

    def test_experimental_mermaid_diagrams_syntax(self, exp_content):
        """Mermaid diagrams in experiments/README.md must have valid type keywords"""
        lines = exp_content.split('\n')
        errors = []
        in_mermaid = False
        start = 0

        valid_types = [
            'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
            'stateDiagram', 'gitGraph', 'gantt', 'pie', 'erDiagram',
            'journey', 'timeline'
        ]

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == '```mermaid':
                in_mermaid = True
                start = i + 1
            elif stripped == '```' and in_mermaid:
                in_mermaid = False
                diagram_lines = lines[start:i]
                if diagram_lines:
                    first = diagram_lines[0].strip()
                    if not any(first.startswith(t) for t in valid_types):
                        errors.append({
                            'line': start + 1,
                            'first_line': first,
                            'error': 'Unknown Mermaid diagram type'
                        })

        assert not errors, f"Mermaid syntax errors in experiments/README.md: {errors}"

    def test_experimental_code_block_languages(self, exp_content):
        """Code blocks should use recognized language tags"""
        lines = exp_content.split('\n')
        valid_langs = {
            'bash', 'shell', 'sh', 'python', 'py', 'yaml', 'yml',
            'json', 'javascript', 'js', 'markdown', 'md', 'mermaid',
            'dockerfile', 'docker', 'xml', 'html', 'css', 'sql', ''
        }
        issues = []
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                lang = line.strip()[3:].strip()
                if lang.lower() not in valid_langs:
                    issues.append({'line': i + 1, 'language': lang})

        if issues:
            print(f"Warning: Non-standard language tags in experiments/README.md: {issues}")