"""
Tests for hyperlink integrity validation - internal and external links
"""

import pytest
import os
from utils.link_checker import LinkChecker
from utils.pattern_parser import PatternParser, ReferenceTableParser
from conftest import EXPECTED_PATTERNS


class TestHyperlinkIntegrity:
    """Test suite for validating all hyperlinks in README.md"""
    
    def test_internal_anchor_links_valid(self, readme_content):
        """Verify all internal anchor links point to existing headers"""
        checker = LinkChecker(readme_content)
        invalid_links = checker.validate_internal_links()
        
        assert not invalid_links, f"Invalid internal anchor links found: {invalid_links}"
    
    def test_pattern_reference_links_work(self, readme_content):
        """Verify all pattern reference links in the table work correctly"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        checker = LinkChecker(readme_content)
        anchors = checker.extract_anchors()
        
        broken_links = []
        
        for pattern_name, data in table_data.items():
            anchor_link = data.get('anchor_link', '')
            if anchor_link and anchor_link not in anchors:
                broken_links.append({
                    'pattern': pattern_name,
                    'anchor': anchor_link,
                    'available_anchors': list(anchors)[:5]  # Show first 5 for debugging
                })
        
        assert not broken_links, f"Broken pattern reference links: {broken_links}"
    
    def test_related_patterns_links_valid(self, readme_content):
        """Verify all 'Related Patterns' section links are valid"""
        parser = PatternParser(readme_content)
        patterns = parser.extract_patterns()
        
        checker = LinkChecker(readme_content)
        anchors = checker.extract_anchors()
        
        invalid_related_links = []
        
        for pattern_name, pattern in patterns.items():
            for related_pattern in pattern.related_patterns:
                # Convert pattern name to expected anchor format using same logic as LinkChecker
                expected_anchor = '#' + checker._text_to_anchor(related_pattern)
                
                if expected_anchor not in anchors:
                    invalid_related_links.append({
                        'pattern': pattern_name,
                        'related_pattern': related_pattern,
                        'expected_anchor': expected_anchor
                    })
        
        assert not invalid_related_links, f"Invalid related pattern links: {invalid_related_links}"
    
    def test_anchor_format_consistency(self, readme_content):
        """Verify anchor links follow consistent naming convention"""
        table_parser = ReferenceTableParser(readme_content)
        table_data = table_parser.extract_reference_table()
        
        format_issues = []
        
        for pattern_name, data in table_data.items():
            anchor_link = data.get('anchor_link', '')
            if anchor_link:
                # Verify anchor follows expected format
                expected_anchor = self._pattern_name_to_anchor(pattern_name)
                
                if anchor_link != expected_anchor:
                    format_issues.append({
                        'pattern': pattern_name,
                        'actual_anchor': anchor_link,
                        'expected_anchor': expected_anchor
                    })
        
        assert not format_issues, f"Anchor format inconsistencies: {format_issues}"
    
    @pytest.mark.slow
    def test_external_links_accessible(self, readme_content):
        """Verify external HTTP/HTTPS links are accessible (slow test)"""
        checker = LinkChecker(readme_content, timeout=5)
        invalid_external_links = checker.validate_external_links(check_live=True)
        
        # Filter out common acceptable errors (like 403 for some sites)
        critical_errors = []
        for link_error in invalid_external_links:
            error = link_error['error']
            if 'timeout' in error.lower() or 'connection error' in error.lower():
                critical_errors.append(link_error)
        
        assert not critical_errors, f"Critical external link errors: {critical_errors}"
        
        # Warn about other errors but don't fail
        non_critical = len(invalid_external_links) - len(critical_errors)
        if non_critical > 0:
            print(f"Warning: {non_critical} external links returned non-critical errors")
    
    def test_relative_file_links_exist(self, readme_content, repo_root):
        """Verify relative file path links point to existing files"""
        checker = LinkChecker(readme_content)
        invalid_relative_links = checker.validate_relative_links(str(repo_root))
        
        assert not invalid_relative_links, f"Invalid relative file links: {invalid_relative_links}"
    
    def test_pattern_mentions_are_hyperlinked(self, readme_content):
        """Verify pattern names mentioned in text are properly hyperlinked"""
        checker = LinkChecker(readme_content)
        
        # Get list of patterns that should be linked
        parser = PatternParser(readme_content)
        patterns = list(parser.extract_patterns().keys())
        
        unlinked_mentions = checker.validate_pattern_references(patterns)
        
        # Filter out acceptable cases (like in code blocks or headers)
        critical_unlinked = []
        for mention in unlinked_mentions:
            line_content = readme_content.split('\n')[mention['line'] - 1]
            
            # Skip if in code block, header, or already part of a link
            if ('```' in line_content or 
                line_content.strip().startswith('#') or
                '](#' in line_content):
                continue
                
            critical_unlinked.append(mention)
        
        assert not critical_unlinked, f"Pattern mentions not hyperlinked: {critical_unlinked}"
    
    def test_no_broken_markdown_links(self, readme_content):
        """Verify all markdown links have proper syntax"""
        lines = readme_content.split('\n')
        broken_markdown = []
        in_code_block = False
        
        for line_num, line in enumerate(lines, 1):
            # Track code block boundaries
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            # Skip lines inside code blocks
            if in_code_block:
                continue
            # Find potential broken markdown links
            
            # Pattern 1: [text] without (url) 
            bracket_matches = []
            start = 0
            while True:
                start_bracket = line.find('[', start)
                if start_bracket == -1:
                    break
                end_bracket = line.find(']', start_bracket)
                if end_bracket == -1:
                    break
                    
                # Check if followed by (url)
                next_char_pos = end_bracket + 1
                if next_char_pos < len(line) and line[next_char_pos] != '(':
                    # Might be broken link, but could be valid reference link
                    text = line[start_bracket:end_bracket + 1]
                    if not text.startswith('!['):  # Skip image references
                        bracket_matches.append({
                            'line': line_num,
                            'text': text,
                            'issue': 'Potential incomplete link'
                        })
                
                start = end_bracket + 1
            
            # Pattern 2: Unmatched brackets
            if line.count('[') != line.count(']'):
                broken_markdown.append({
                    'line': line_num,
                    'content': line.strip(),
                    'issue': 'Unmatched brackets'
                })
            
            if line.count('(') != line.count(')') and ('[' in line or ']' in line):
                broken_markdown.append({
                    'line': line_num,
                    'content': line.strip(),
                    'issue': 'Unmatched parentheses in potential link'
                })
        
        assert not broken_markdown, f"Broken markdown link syntax: {broken_markdown}"
    
    def test_duplicate_anchor_targets(self, readme_content):
        """Verify no duplicate anchor targets exist"""
        checker = LinkChecker(readme_content)
        anchors = list(checker.extract_anchors())
        
        # Check for duplicates
        anchor_counts = {}
        for anchor in anchors:
            anchor_counts[anchor] = anchor_counts.get(anchor, 0) + 1
        
        duplicates = {anchor: count for anchor, count in anchor_counts.items() if count > 1}
        
        assert not duplicates, f"Duplicate anchor targets found: {duplicates}"
    
    def test_link_density_reasonable(self, readme_content):
        """Verify link density is reasonable (not too many or too few links)"""
        checker = LinkChecker(readme_content)
        all_links = checker.find_all_links()
        
        total_links = sum(len(links) for links in all_links.values())
        total_words = len(readme_content.split())
        
        # Reasonable link density: 1-5% of words should be links
        link_density = (total_links * 2) / total_words  # Assuming avg 2 words per link
        
        assert 0.01 <= link_density <= 0.10, \
            f"Link density {link_density:.2%} outside reasonable range (1-10%)"
    
    def _pattern_name_to_anchor(self, pattern_name: str) -> str:
        """Convert pattern name to expected anchor format"""
        anchor = pattern_name.lower()
        anchor = anchor.replace(' ', '-')
        anchor = anchor.replace('&', '')
        anchor = anchor.replace(',', '')
        anchor = ''.join(c for c in anchor if c.isalnum() or c == '-')
        anchor = anchor.strip('-')
        return f'#{anchor}'


class TestLinkQuality:
    """Additional tests for link quality and best practices"""
    
    def test_external_links_use_https(self, readme_content):
        """Verify external links prefer HTTPS over HTTP"""
        checker = LinkChecker(readme_content)
        all_links = checker.find_all_links()
        
        http_links = []
        for url, line_num in all_links['external']:
            if url.startswith('http://'):
                http_links.append({
                    'url': url,
                    'line': line_num,
                    'suggestion': url.replace('http://', 'https://')
                })
        
        # This is a warning rather than failure
        if http_links:
            print(f"Warning: HTTP links found (consider HTTPS): {http_links}")
    
    def test_link_text_descriptive(self, readme_content):
        """Verify link text is descriptive (not just 'here' or 'click')"""
        import re
        
        non_descriptive_patterns = [
            r'\[here\]\(',
            r'\[click here\]\(',
            r'\[this\]\(',
            r'\[link\]\('
        ]
        
        poor_link_text = []
        lines = readme_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in non_descriptive_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    poor_link_text.append({
                        'line': line_num,
                        'content': line.strip(),
                        'issue': 'Non-descriptive link text'
                    })
        
        # This is a quality check - warn but don't fail
        if poor_link_text:
            print(f"Quality issue: Non-descriptive link text found: {poor_link_text}")