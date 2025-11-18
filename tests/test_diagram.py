"""
Tests for Mermaid diagram validation in README.md

Validates that the pattern dependency diagram:
1. Includes all expected patterns
2. Has valid clickable links to pattern sections
3. Uses correct anchor formats
"""

import pytest
import re
from conftest import EXPECTED_PATTERNS, README_PATH


class TestMermaidDiagram:
    """Tests for Mermaid diagram accuracy and link integrity"""

    @pytest.fixture
    def readme_content(self):
        """Load README content"""
        with open(README_PATH, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def mermaid_diagram(self, readme_content):
        """Extract Mermaid diagram from README"""
        pattern = r'```mermaid\n(.*?)```'
        match = re.search(pattern, readme_content, re.DOTALL)
        return match.group(1) if match else ""

    @pytest.fixture
    def diagram_patterns(self, mermaid_diagram):
        """Extract pattern names from diagram node definitions"""
        # Match patterns like: RA([Readiness<br/>Assessment])
        # or: CR([Codified<br/>Rules])
        pattern = r'\[\(([^)]+)\)\]|\[([^\]]+)\]'
        matches = re.findall(pattern, mermaid_diagram)

        patterns = []
        for match in matches:
            # Get the non-empty group
            text = match[0] if match[0] else match[1]
            # Remove <br/> and normalize whitespace
            name = text.replace('<br/>', ' ').strip()
            if name and not name.startswith('%'):
                patterns.append(name)

        return patterns

    @pytest.fixture
    def diagram_click_links(self, mermaid_diagram):
        """Extract click links from diagram"""
        # Match: click RA "https://github.com/..."
        pattern = r'click\s+(\w+)\s+"([^"]+)"'
        return dict(re.findall(pattern, mermaid_diagram))

    def test_diagram_includes_all_patterns(self, diagram_patterns):
        """Verify all expected patterns appear in the diagram"""
        # Map of expected pattern names to their diagram representations
        pattern_mapping = {
            "Readiness Assessment": "Readiness Assessment",
            "Codified Rules": "Codified Rules",
            "Security Sandbox": "Security Sandbox",
            "Developer Lifecycle": "Developer Lifecycle",
            "Tool Integration": "Tool Integration",
            "Issue Generation": "Issue Generation",
            "Context Persistence": "Context Persistence",
            "Progressive Enhancement": "Progressive Enhancement",
            "Spec-Driven Development": "Spec-Driven Development",
            "Atomic Decomposition": "Atomic Decomposition",
            "Parallel Agents": "Parallel Agents",
            "Observable Development": "Observable Development",
            "Guided Refactoring": "Guided Refactoring",
            "Automated Traceability": "Automated Traceability",
            "Policy Generation": "Policy Generation",
            "Security Orchestration": "Security Orchestration",
            "Baseline Management": "Baseline Management",
        }

        missing_patterns = []
        for expected in pattern_mapping.keys():
            diagram_name = pattern_mapping[expected]
            if diagram_name not in diagram_patterns:
                missing_patterns.append(expected)

        assert not missing_patterns, \
            f"Patterns missing from diagram: {missing_patterns}"

    def test_diagram_click_links_exist(self, diagram_click_links):
        """Verify diagram has clickable links for patterns"""
        # Should have links for the main patterns shown
        assert len(diagram_click_links) > 0, \
            "Diagram should have clickable links"

        # Minimum expected patterns with links
        min_expected = 15
        assert len(diagram_click_links) >= min_expected, \
            f"Expected at least {min_expected} click links, found {len(diagram_click_links)}"

    def test_diagram_links_use_correct_format(self, diagram_click_links):
        """Verify click links use absolute GitHub URLs"""
        invalid_links = []

        for node_id, url in diagram_click_links.items():
            # Should be absolute GitHub URL with anchor
            if not url.startswith("https://github.com/PaulDuvall/ai-development-patterns#"):
                invalid_links.append({
                    "node": node_id,
                    "url": url,
                    "issue": "Should use absolute GitHub URL with anchor"
                })

        assert not invalid_links, \
            f"Invalid link formats: {invalid_links}"

    def test_diagram_anchors_match_patterns(self, diagram_click_links, readme_content):
        """Verify diagram link anchors point to existing sections"""
        # Extract all ## and ### headings from README (patterns can be at either level)
        heading_pattern = r'^#{2,3}\s+(.+)$'
        headings = re.findall(heading_pattern, readme_content, re.MULTILINE)

        # Convert headings to anchor format
        valid_anchors = set()
        for heading in headings:
            # GitHub anchor format: lowercase, spaces to hyphens, remove special chars
            anchor = heading.lower()
            anchor = re.sub(r'[^\w\s-]', '', anchor)
            anchor = anchor.replace(' ', '-')
            anchor = re.sub(r'-+', '-', anchor)
            valid_anchors.add(anchor)

        broken_links = []
        for node_id, url in diagram_click_links.items():
            # Extract anchor from URL
            if '#' in url:
                anchor = url.split('#')[-1]
                if anchor not in valid_anchors:
                    broken_links.append({
                        "node": node_id,
                        "anchor": anchor,
                        "url": url
                    })

        assert not broken_links, \
            f"Diagram links point to non-existent anchors: {broken_links}"

    def test_diagram_has_styling(self, mermaid_diagram):
        """Verify diagram has color styling for visual clarity"""
        assert "classDef" in mermaid_diagram, \
            "Diagram should have class definitions for styling"

        # Check for the three category styles
        assert "foundation" in mermaid_diagram.lower(), \
            "Diagram should have foundation styling"
        assert "development" in mermaid_diagram.lower(), \
            "Diagram should have development styling"
        assert "operations" in mermaid_diagram.lower(), \
            "Diagram should have operations styling"

    def test_diagram_syntax_valid(self, mermaid_diagram):
        """Basic validation of Mermaid diagram syntax"""
        # Should start with graph direction
        assert re.search(r'graph\s+(TB|TD|LR|RL|BT)', mermaid_diagram), \
            "Diagram should specify graph direction (TB, TD, LR, RL, or BT)"

        # Should have node definitions (square brackets or stadium shapes)
        assert re.search(r'\w+\s*[\[\(]', mermaid_diagram), \
            "Diagram should have node definitions"

        # Should have connections
        assert '-->' in mermaid_diagram, \
            "Diagram should have connections between nodes"

    def test_no_duplicate_node_ids(self, mermaid_diagram):
        """Verify no duplicate node IDs in diagram"""
        # Extract node IDs (first word before [ or ()
        node_pattern = r'^\s*(\w+)\s*[\[\(]'
        node_ids = re.findall(node_pattern, mermaid_diagram, re.MULTILINE)

        duplicates = [id for id in set(node_ids) if node_ids.count(id) > 1]

        assert not duplicates, \
            f"Duplicate node IDs found: {duplicates}"
