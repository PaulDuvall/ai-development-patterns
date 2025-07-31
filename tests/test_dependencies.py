"""
Tests for pattern dependency validation and dependency graph analysis
"""

import pytest
from typing import Dict, List, Set, Tuple
from tests.utils.pattern_parser import PatternParser, ReferenceTableParser
from tests.conftest import PATTERN_CATEGORIES, EXPECTED_PATTERNS


class DependencyGraphAnalyzer:
    """Analyzer for pattern dependency relationships"""
    
    def __init__(self, patterns_data: Dict[str, Dict[str, str]]):
        self.patterns_data = patterns_data
        self.dependency_graph = self._build_dependency_graph()
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph from pattern data"""
        graph = {}
        
        for pattern_name, data in self.patterns_data.items():
            dependencies_text = data.get('dependencies', '').strip()
            dependencies = []
            
            if dependencies_text and dependencies_text.lower() != 'none':
                # Parse dependencies from text
                if '[' in dependencies_text:
                    # Extract from markdown links
                    import re
                    dep_matches = re.findall(r'\\[([^\\]]+)\\]', dependencies_text)
                    dependencies.extend(dep_matches)
                else:
                    # Split by comma for plain text
                    deps = [d.strip() for d in dependencies_text.split(',')]
                    dependencies.extend([d for d in deps if d])
            
            graph[pattern_name] = dependencies
        
        return graph
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the graph"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for dependency in self.dependency_graph.get(node, []):
                if dependency in self.patterns_data:  # Only follow valid dependencies
                    dfs(dependency, path + [node])
            
            rec_stack.remove(node)
        
        for pattern in self.dependency_graph:
            if pattern not in visited:
                dfs(pattern, [])
        
        return cycles
    
    def validate_dependency_existence(self) -> List[Dict[str, str]]:
        """Validate all dependencies refer to existing patterns"""
        invalid_deps = []
        
        for pattern_name, dependencies in self.dependency_graph.items():
            for dep in dependencies:
                if dep not in self.patterns_data:
                    invalid_deps.append({
                        'pattern': pattern_name,
                        'invalid_dependency': dep,
                        'suggestion': self._find_similar_pattern(dep)
                    })
        
        return invalid_deps
    
    def _find_similar_pattern(self, target: str) -> str:
        """Find similar pattern names for suggestions"""
        from difflib import get_close_matches
        pattern_names = list(self.patterns_data.keys())
        matches = get_close_matches(target, pattern_names, n=1, cutoff=0.6)
        return matches[0] if matches else "No similar pattern found"
    
    def analyze_dependency_depth(self) -> Dict[str, int]:
        """Calculate dependency depth for each pattern"""
        depths = {}
        
        def calculate_depth(pattern, visited=None):
            if visited is None:
                visited = set()
            
            if pattern in visited:
                return float('inf')  # Circular dependency
            
            if pattern in depths:
                return depths[pattern]
            
            dependencies = self.dependency_graph.get(pattern, [])
            if not dependencies:
                depths[pattern] = 0
                return 0
            
            visited.add(pattern)
            max_dep_depth = 0
            
            for dep in dependencies:
                if dep in self.patterns_data:
                    dep_depth = calculate_depth(dep, visited.copy())
                    max_dep_depth = max(max_dep_depth, dep_depth)
            
            depths[pattern] = max_dep_depth + 1
            return depths[pattern]
        
        for pattern in self.patterns_data:
            calculate_depth(pattern)
        
        return depths
    
    def validate_maturity_level_progression(self) -> List[Dict[str, str]]:
        """Validate that dependencies follow logical maturity progression"""
        maturity_order = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}
        violations = []
        
        for pattern_name, dependencies in self.dependency_graph.items():
            pattern_maturity = self.patterns_data[pattern_name].get('maturity', '')
            pattern_level = maturity_order.get(pattern_maturity, -1)
            
            for dep in dependencies:
                if dep in self.patterns_data:
                    dep_maturity = self.patterns_data[dep].get('maturity', '')
                    dep_level = maturity_order.get(dep_maturity, -1)
                    
                    # Advanced patterns can depend on anything
                    # Intermediate can depend on Beginner or Intermediate
                    # Beginner should only depend on Beginner
                    if pattern_level != -1 and dep_level != -1:
                        if pattern_level < dep_level:
                            violations.append({
                                'pattern': pattern_name,
                                'pattern_maturity': pattern_maturity,
                                'dependency': dep,
                                'dependency_maturity': dep_maturity,
                                'issue': f'{pattern_maturity} pattern depends on {dep_maturity} pattern'
                            })
        
        return violations


class TestPatternDependencies:
    """Test suite for pattern dependency validation"""
    
    def test_all_dependencies_exist(self, readme_content):
        """Verify all pattern dependencies refer to existing patterns"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        analyzer = DependencyGraphAnalyzer(table_data)
        invalid_deps = analyzer.validate_dependency_existence()
        
        assert not invalid_deps, f"Invalid pattern dependencies found: {invalid_deps}"
    
    def test_no_circular_dependencies(self, readme_content):
        """Verify no circular dependencies exist in pattern graph"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        analyzer = DependencyGraphAnalyzer(table_data)
        cycles = analyzer.find_circular_dependencies()
        
        assert not cycles, f"Circular dependencies found: {cycles}"
    
    def test_maturity_level_dependency_logic(self, readme_content):
        """Verify dependency maturity levels follow logical progression"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        analyzer = DependencyGraphAnalyzer(table_data)
        violations = analyzer.validate_maturity_level_progression()
        
        assert not violations, f"Maturity level progression violations: {violations}"
    
    def test_foundation_patterns_minimal_dependencies(self, readme_content):
        """Verify Foundation patterns have minimal external dependencies"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        analyzer = DependencyGraphAnalyzer(table_data)
        
        foundation_violations = []
        
        for pattern_name, data in table_data.items():
            pattern_type = data.get('type', '')
            if pattern_type == 'Foundation':
                dependencies = analyzer.dependency_graph.get(pattern_name, [])
                # Foundation patterns should have minimal dependencies
                if len(dependencies) > 2:  # Allow up to 2 dependencies
                    foundation_violations.append({
                        'pattern': pattern_name,
                        'dependency_count': len(dependencies),
                        'dependencies': dependencies
                    })
        
        assert not foundation_violations, f"Foundation patterns with too many dependencies: {foundation_violations}"
    
    def test_dependency_depth_reasonable(self, readme_content):
        """Verify dependency chains aren't too deep"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        analyzer = DependencyGraphAnalyzer(table_data)
        depths = analyzer.analyze_dependency_depth()
        
        deep_dependencies = []
        max_reasonable_depth = 4  # Reasonable maximum dependency depth
        
        for pattern, depth in depths.items():
            if depth > max_reasonable_depth:
                deep_dependencies.append({
                    'pattern': pattern,
                    'depth': depth,
                    'dependencies': analyzer.dependency_graph.get(pattern, [])
                })
        
        assert not deep_dependencies, f"Patterns with excessive dependency depth: {deep_dependencies}"
    
    def test_beginner_patterns_have_no_dependencies(self, readme_content):
        """Verify at least some Beginner patterns have no dependencies"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        analyzer = DependencyGraphAnalyzer(table_data)
        
        beginner_patterns = []
        beginner_no_deps = []
        
        for pattern_name, data in table_data.items():
            if data.get('maturity') == 'Beginner':
                beginner_patterns.append(pattern_name)
                dependencies = analyzer.dependency_graph.get(pattern_name, [])
                if not dependencies:
                    beginner_no_deps.append(pattern_name)
        
        # At least 30% of Beginner patterns should have no dependencies
        if beginner_patterns:
            no_deps_ratio = len(beginner_no_deps) / len(beginner_patterns)
            assert no_deps_ratio >= 0.3, \
                f"Too few Beginner patterns without dependencies: {no_deps_ratio:.1%} (expected ≥30%)"
    
    def test_dependency_categories_logical(self, readme_content):
        """Verify dependencies follow logical category relationships"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        analyzer = DependencyGraphAnalyzer(table_data)
        
        category_violations = []
        
        # Expected category hierarchy: Foundation → Development → Operations
        category_levels = {'Foundation': 0, 'Development': 1, 'Operations': 2}
        
        for pattern_name, dependencies in analyzer.dependency_graph.items():
            pattern_type = table_data[pattern_name].get('type', '')
            pattern_level = category_levels.get(pattern_type, -1)
            
            for dep in dependencies:
                if dep in table_data:
                    dep_type = table_data[dep].get('type', '')
                    dep_level = category_levels.get(dep_type, -1)
                    
                    # Operations can depend on Development and Foundation
                    # Development can depend on Foundation
                    # Foundation should primarily depend on Foundation
                    if pattern_level != -1 and dep_level != -1:
                        if pattern_level < dep_level:
                            category_violations.append({
                                'pattern': pattern_name,
                                'pattern_type': pattern_type, 
                                'dependency': dep,
                                'dependency_type': dep_type,
                                'issue': f'{pattern_type} pattern depends on {dep_type} pattern'
                            })
        
        assert not category_violations, f"Category dependency violations: {category_violations}"
    
    def test_reference_table_dependency_format(self, readme_content):
        """Verify dependency column format in reference table"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        format_issues = []
        
        for pattern_name, data in table_data.items():
            dependencies_text = data.get('dependencies', '').strip()
            
            if dependencies_text and dependencies_text.lower() != 'none':
                # Check format: should be either "None" or comma-separated pattern names
                # Optionally with markdown links
                
                if '[' in dependencies_text and ']' in dependencies_text:
                    # Has markdown links - this is good
                    import re
                    links = re.findall(r'\\[([^\\]]+)\\]\\([^)]+\\)', dependencies_text)
                    if not links:
                        format_issues.append({
                            'pattern': pattern_name,
                            'dependencies': dependencies_text,
                            'issue': 'Invalid markdown link format'
                        })
                else:
                    # Plain text - should be comma-separated
                    deps = [d.strip() for d in dependencies_text.split(',')]
                    for dep in deps:
                        if not dep or len(dep) < 3:
                            format_issues.append({
                                'pattern': pattern_name,
                                'dependencies': dependencies_text,
                                'issue': f'Invalid dependency format: "{dep}"'
                            })
        
        assert not format_issues, f"Dependency format issues: {format_issues}"


class TestDependencyGraph:
    """Tests for overall dependency graph structure and properties"""
    
    def test_dependency_graph_connected(self, readme_content):
        """Verify dependency graph forms a reasonable connected structure"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        analyzer = DependencyGraphAnalyzer(table_data)
        
        # Find patterns with no dependencies (roots)
        roots = []
        leaves = []
        
        for pattern_name in table_data.keys():
            dependencies = analyzer.dependency_graph.get(pattern_name, [])
            if not dependencies:
                roots.append(pattern_name)
            
            # Check if pattern is depended upon by others
            is_dependency = any(pattern_name in deps 
                               for deps in analyzer.dependency_graph.values())
            if not is_dependency:
                leaves.append(pattern_name)
        
        # Should have some root patterns (no dependencies)
        assert len(roots) >= 1, f"No root patterns found (patterns without dependencies)"
        
        # Should have some leaf patterns (not depended upon)
        assert len(leaves) >= 1, f"No leaf patterns found (patterns not used as dependencies)"
        
        print(f"Dependency graph structure: {len(roots)} roots, {len(leaves)} leaves")
    
    def test_dependency_graph_metrics(self, readme_content):
        """Analyze and validate overall dependency graph metrics"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        analyzer = DependencyGraphAnalyzer(table_data)
        depths = analyzer.analyze_dependency_depth()
        
        # Calculate metrics
        total_patterns = len(table_data)
        total_dependencies = sum(len(deps) for deps in analyzer.dependency_graph.values())
        avg_dependencies = total_dependencies / total_patterns if total_patterns > 0 else 0
        max_depth = max(depths.values()) if depths else 0
        avg_depth = sum(depths.values()) / len(depths) if depths else 0
        
        print(f"Dependency graph metrics:")
        print(f"  Total patterns: {total_patterns}")
        print(f"  Total dependencies: {total_dependencies}")
        print(f"  Average dependencies per pattern: {avg_dependencies:.1f}")
        print(f"  Maximum dependency depth: {max_depth}")
        print(f"  Average dependency depth: {avg_depth:.1f}")
        
        # Validate reasonable metrics
        assert avg_dependencies >= 0.5, f"Average dependencies too low: {avg_dependencies:.1f}"
        assert avg_dependencies <= 3.0, f"Average dependencies too high: {avg_dependencies:.1f}"
        assert max_depth <= 5, f"Maximum dependency depth too high: {max_depth}"