"""
Link validation utilities for checking internal and external hyperlinks
"""

import re
import requests
from typing import List, Dict, Tuple, Set
from urllib.parse import urlparse
import time


class LinkChecker:
    """Utility for validating internal and external hyperlinks"""
    
    def __init__(self, readme_content: str, timeout: int = 10):
        self.content = readme_content
        self.lines = readme_content.split('\n')
        self.timeout = timeout
        self._external_cache = {}  # Cache for external link checks
        
    def find_all_links(self) -> Dict[str, List[Tuple[str, int]]]:
        """Find all links in the README categorized by type"""
        links = {
            'internal': [],      # Links to #anchors
            'external': [],      # HTTP/HTTPS links
            'relative': [],      # Relative file paths
            'mailto': []         # Email links
        }
        
        for line_num, line in enumerate(self.lines, 1):
            # Find all markdown links [text](url)
            markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
            
            for link_text, url in markdown_links:
                url = url.strip()
                
                if url.startswith('#'):
                    links['internal'].append((url, line_num))
                elif url.startswith(('http://', 'https://')):
                    links['external'].append((url, line_num))
                elif url.startswith('mailto:'):
                    links['mailto'].append((url, line_num))
                else:
                    links['relative'].append((url, line_num))
        
        return links
    
    def extract_anchors(self) -> Set[str]:
        """Extract all valid anchor targets from headers in README"""
        anchors = set()
        
        for line in self.lines:
            # Find headers (# ## ### etc.)
            header_match = re.match(r'^(#{1,6})\s+(.+)', line.strip())
            if header_match:
                header_text = header_match.group(2)
                # Convert to anchor format: lowercase, spaces to hyphens, remove special chars
                anchor = self._text_to_anchor(header_text)
                anchors.add(f'#{anchor}')
        
        return anchors
    
    def validate_internal_links(self) -> List[Dict[str, any]]:
        """Validate all internal anchor links"""
        links = self.find_all_links()
        anchors = self.extract_anchors()
        invalid_links = []
        
        for link, line_num in links['internal']:
            if link not in anchors:
                invalid_links.append({
                    'link': link,
                    'line': line_num,
                    'error': f'Anchor not found: {link}',
                    'type': 'internal'
                })
        
        return invalid_links
    
    def validate_external_links(self, check_live: bool = True) -> List[Dict[str, any]]:
        """Validate external HTTP/HTTPS links"""
        if not check_live:
            return []
            
        links = self.find_all_links()
        invalid_links = []
        
        for url, line_num in links['external']:
            # Use cache to avoid repeated requests
            if url in self._external_cache:
                is_valid, error = self._external_cache[url]
            else:
                is_valid, error = self._check_external_url(url)
                self._external_cache[url] = (is_valid, error)
                # Rate limiting
                time.sleep(0.1)
            
            if not is_valid:
                invalid_links.append({
                    'link': url,
                    'line': line_num,
                    'error': error,
                    'type': 'external'
                })
        
        return invalid_links
    
    def validate_relative_links(self, repo_root_path: str) -> List[Dict[str, any]]:
        """Validate relative file path links"""
        import os
        
        links = self.find_all_links()
        invalid_links = []
        
        for path, line_num in links['relative']:
            # Handle different types of relative paths
            full_path = os.path.join(repo_root_path, path)
            
            if not os.path.exists(full_path):
                # Try removing leading ./
                if path.startswith('./'):
                    full_path = os.path.join(repo_root_path, path[2:])
                
                if not os.path.exists(full_path):
                    invalid_links.append({
                        'link': path,
                        'line': line_num,
                        'error': f'File not found: {path}',
                        'type': 'relative'
                    })
        
        return invalid_links
    
    def _text_to_anchor(self, text: str) -> str:
        """Convert header text to anchor format"""
        # Remove markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Remove bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)        # Remove italic
        text = re.sub(r'`(.+?)`', r'\1', text)            # Remove code
        
        # Convert to lowercase and replace spaces with hyphens
        anchor = text.lower()
        anchor = re.sub(r'[^a-z0-9\s-]', '', anchor)      # Remove special chars
        anchor = re.sub(r'\s+', '-', anchor)              # Spaces to hyphens
        anchor = re.sub(r'-+', '-', anchor)                # Multiple hyphens to single
        anchor = anchor.strip('-')                         # Remove leading/trailing hyphens
        
        return anchor
    
    def _check_external_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible"""
        try:
            # Use HEAD request for efficiency
            response = requests.head(url, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code == 405:  # Method not allowed, try GET
                response = requests.get(url, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code < 400:
                return True, ""
            else:
                return False, f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection error"
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def validate_pattern_references(self, patterns: List[str]) -> List[Dict[str, any]]:
        """Validate that all pattern references are properly linked"""
        invalid_references = []
        in_code_block = False
        in_mermaid = False
        
        for line_num, line in enumerate(self.lines, 1):
            # Track code block and mermaid diagram boundaries
            if line.strip().startswith('```'):
                if 'mermaid' in line:
                    in_mermaid = True
                elif in_mermaid:
                    in_mermaid = False
                else:
                    in_code_block = not in_code_block
                continue
            
            # Skip lines inside code blocks or mermaid diagrams
            if in_code_block or in_mermaid:
                continue
            # Find pattern names mentioned in text
            for pattern in patterns:
                # Look for pattern name not already in a link
                pattern_mentions = []
                
                # Find all occurrences of pattern name
                start = 0
                while True:
                    pos = line.find(pattern, start)
                    if pos == -1:
                        break
                    pattern_mentions.append(pos)
                    start = pos + 1
                
                # Check if each mention is properly linked
                for pos in pattern_mentions:
                    # Check if this mention is inside a markdown link
                    before_pos = line.rfind('[', 0, pos)
                    after_pos = line.find(']', pos)
                    
                    if before_pos == -1 or after_pos == -1:
                        # Not in a link at all
                        invalid_references.append({
                            'pattern': pattern,
                            'line': line_num,
                            'error': f'Pattern "{pattern}" not hyperlinked',
                            'type': 'unlinked_pattern'
                        })
                    else:
                        # Check if there's a URL after the closing bracket
                        url_start = line.find('(', after_pos)
                        url_end = line.find(')', url_start) if url_start != -1 else -1
                        
                        if url_start == -1 or url_end == -1:
                            invalid_references.append({
                                'pattern': pattern,
                                'line': line_num,
                                'error': f'Pattern "{pattern}" has incomplete link',
                                'type': 'incomplete_link'
                            })
        
        return invalid_references
    
    def generate_link_report(self, check_external: bool = True) -> Dict[str, any]:
        """Generate comprehensive link validation report"""
        report = {
            'total_links': 0,
            'valid_links': 0,
            'invalid_links': 0,
            'errors': [],
            'summary': {}
        }
        
        # Get all links
        all_links = self.find_all_links()
        report['total_links'] = sum(len(links) for links in all_links.values())
        
        # Validate each type
        errors = []
        errors.extend(self.validate_internal_links())
        
        if check_external:
            errors.extend(self.validate_external_links(check_live=True))
        
        # Note: relative link validation requires repo_root_path parameter
        
        report['errors'] = errors
        report['invalid_links'] = len(errors)
        report['valid_links'] = report['total_links'] - report['invalid_links']
        
        # Summary by link type
        for link_type, links in all_links.items():
            type_errors = [e for e in errors if e.get('type') == link_type]
            report['summary'][link_type] = {
                'total': len(links),
                'valid': len(links) - len(type_errors),
                'invalid': len(type_errors)
            }
        
        return report