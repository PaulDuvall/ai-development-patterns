"""
Pattern parser utility for extracting and analyzing patterns from README.md
"""

import re
from typing import Dict, List, NamedTuple, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Pattern:
    """Represents a parsed pattern from README.md"""
    name: str
    line_number: int
    maturity: Optional[str] = None
    description: Optional[str] = None
    related_patterns: List[str] = None
    implementation_content: str = ""
    anti_pattern_content: str = ""
    category: str = ""
    
    def __post_init__(self):
        if self.related_patterns is None:
            self.related_patterns = []


class PatternParser:
    """Parser for extracting pattern information from README.md"""
    
    def __init__(self, readme_content: str):
        self.content = readme_content
        self.lines = readme_content.split('\n')
        
    def extract_patterns(self) -> Dict[str, Pattern]:
        """Extract all patterns from README.md content"""
        patterns = {}
        current_category = ""
        
        i = 0
        while i < len(self.lines):
            line = self.lines[i].strip()
            
            # Track current category
            if self._is_category_header(line):
                current_category = self._extract_category_name(line)
                i += 1
                continue
                
            # Check for pattern header
            if self._is_pattern_header(line):
                pattern_name = self._extract_pattern_name(line)
                if pattern_name:
                    pattern = self._parse_pattern(i, pattern_name, current_category)
                    if pattern:
                        patterns[pattern_name] = pattern
                        # Skip to end of this pattern
                        i = self._find_next_pattern_start(i + 1) - 1
            
            i += 1
            
        return patterns
    
    def extract_reference_table_patterns(self) -> List[Tuple[str, str, str, str]]:
        """Extract patterns from the reference table"""
        patterns = []
        in_table = False
        
        for line in self.lines:
            stripped = line.strip()
            
            # Detect table start
            if "| Pattern | Maturity | Type | Description |" in stripped:
                in_table = True
                continue
                
            # Detect table end (empty line after table)
            if in_table and (not stripped or not stripped.startswith('|')):
                break
                
            # Parse table rows
            if in_table and stripped.startswith('|') and 'Pattern' not in stripped:
                parts = [p.strip() for p in stripped.split('|')[1:-1]]  # Remove empty first/last
                if len(parts) >= 4 and not parts[0].startswith('**'):  # Skip category headers
                    # Extract pattern name from markdown link
                    pattern_match = re.search(r'\*\*\[(.*?)\]', parts[0])
                    if pattern_match:
                        pattern_name = pattern_match.group(1)
                        maturity = parts[1]
                        pattern_type = parts[2]
                        description = parts[3]
                        patterns.append((pattern_name, maturity, pattern_type, description))
        
        return patterns
    
    def _is_category_header(self, line: str) -> bool:
        """Check if line is a category header (Foundation/Development/Operations Patterns)"""
        category_patterns = [
            r'^## Foundation Patterns',
            r'^## Development Patterns', 
            r'^## Operations Patterns',
            r'^### Security & Compliance',
            r'^### Deployment Automation',
            r'^### Monitoring & Maintenance'
        ]
        return any(re.match(pattern, line) for pattern in category_patterns)
    
    def _extract_category_name(self, line: str) -> str:
        """Extract category name from header"""
        if "Foundation" in line:
            return "Foundation"
        elif "Development" in line:
            return "Development"
        elif "Operations" in line:
            return "Operations"
        elif "Security & Compliance" in line:
            return "Security & Compliance"
        elif "Deployment Automation" in line:
            return "Deployment Automation"
        elif "Monitoring & Maintenance" in line:
            return "Monitoring & Maintenance"
        return ""
    
    def _is_pattern_header(self, line: str) -> bool:
        """Check if line is a pattern header (## or ### Pattern Name)"""
        if not (re.match(r'^### [A-Za-z]', line) or re.match(r'^## [A-Za-z]', line)):
            return False
        
        if self._is_category_header(line):
            return False
            
        # Exclude organizational sections that aren't actual patterns
        excluded_sections = [
            'Pattern Organization', 'Pattern Dependencies & Implementation Order',
            'Complete Pattern Reference', 'Pattern Maturity Levels', 'Task Sizing Framework',
            'Pattern Selection Decision Framework', 'Decision Tree', 'Context-Based Pattern Selection',
            'Project Type Recommendations', 'Team Size Considerations', 'Technology Stack Considerations',
            'Code Quality Prerequisites', 'Documentation Standards', 'Feature Request',
            'Contributing', 'Getting Started', 'License', 'Success Metrics',
            'CLI Requirements', 'Input Validation', 'Long Method Smell', 'Large Class Smell',
            'Foundation Anti-Patterns', 'Development Anti-Patterns', 'Operations Anti-Patterns',
            'Common AI Development Anti-Patterns', 'Foundation Metrics', 'Development Metrics', 
            'Operations Metrics', 'Phase 1:', 'Phase 2:', 'Phase 3:', 'Pattern Contribution Guidelines',
            'Security & Compliance Patterns', 'Deployment Automation Patterns', 'Monitoring & Maintenance Patterns'
        ]
        
        header_text = line.strip().replace('#', '').strip()
        for excluded in excluded_sections:
            if excluded in header_text:
                return False
                
        return True
    
    def _extract_pattern_name(self, line: str) -> Optional[str]:
        """Extract pattern name from header line"""
        match = re.match(r'^### (.+)', line) or re.match(r'^## (.+)', line)
        return match.group(1).strip() if match else None
    
    def _parse_pattern(self, start_line: int, pattern_name: str, category: str) -> Optional[Pattern]:
        """Parse a complete pattern starting from the header line"""
        pattern = Pattern(name=pattern_name, line_number=start_line + 1, category=category)
        
        i = start_line + 1
        current_section = None
        section_content = []
        
        while i < len(self.lines):
            line = self.lines[i]
            stripped = line.strip()
            
            # Stop at next pattern or major section
            if (stripped.startswith('### ') and self._is_pattern_header(stripped)) or \
               stripped.startswith('## '):
                break
            
            # Track current section
            if stripped.startswith('**Maturity**:'):
                pattern.maturity = self._extract_field_value(stripped, 'Maturity')
                current_section = 'maturity'
            elif stripped.startswith('**Description**:'):
                pattern.description = self._extract_field_value(stripped, 'Description')
                current_section = 'description'
            elif stripped.startswith('**Related Patterns**:'):
                related_patterns_text = self._extract_field_value(stripped, 'Related Patterns')
                pattern.related_patterns = self._extract_related_patterns(related_patterns_text)
                current_section = 'related_patterns'
            elif (stripped.startswith('#### ') and 'Anti-pattern' in stripped) or stripped.startswith('**Anti-pattern'):
                current_section = 'anti_pattern'
                section_content = [line]  # Include the anti-pattern header
            elif current_section == 'anti_pattern':
                section_content.append(line)
            elif stripped and current_section not in ['anti_pattern']:  # Implementation content
                if not any(stripped.startswith(prefix) for prefix in ['**Maturity**:', '**Description**:', '**Related Patterns**:', '####', '**Anti-pattern']):
                    pattern.implementation_content += line + '\n'
            
            i += 1
        
        # Finalize anti-pattern content
        if current_section == 'anti_pattern':
            pattern.anti_pattern_content = '\n'.join(section_content)
        
        return pattern
    
    def _extract_field_value(self, line: str, field_name: str) -> str:
        """Extract value from a field line (e.g., **Maturity**: Beginner)"""
        pattern = f'\\*\\*{field_name}\\*\\*:\\s*(.+)'
        match = re.search(pattern, line)
        return match.group(1).strip() if match else ""
    
    def _extract_related_patterns(self, text: str) -> List[str]:
        """Extract pattern names from related patterns text"""
        # Find all markdown links [Pattern Name](#anchor)
        pattern_links = re.findall(r'\[([^\]]+)\]\([^)]+\)', text)
        return pattern_links
    
    def _find_next_pattern_start(self, start_line: int) -> int:
        """Find the line number of the next pattern header"""
        for i in range(start_line, len(self.lines)):
            if self._is_pattern_header(self.lines[i].strip()):
                return i
        return len(self.lines)


class ReferenceTableParser:
    """Parser specifically for the reference table validation"""
    
    def __init__(self, readme_content: str):
        self.content = readme_content
        self.lines = readme_content.split('\n')
    
    def extract_reference_table(self) -> Dict[str, Dict[str, str]]:
        """Extract complete reference table information"""
        table_data = {}
        in_table = False
        
        for line in self.lines:
            stripped = line.strip()
            
            # Detect table start
            if "| Pattern | Maturity | Type | Description | Dependencies |" in stripped:
                in_table = True
                continue
            
            # Skip separator line
            if in_table and stripped.startswith('|---'):
                continue
                
            # Detect table end
            if in_table and (not stripped or not stripped.startswith('|')):
                break
            
            # Parse table rows
            if in_table and stripped.startswith('|'):
                parts = [p.strip() for p in stripped.split('|')[1:-1]]
                if len(parts) >= 5:
                    # Extract pattern name from markdown link
                    pattern_match = re.search(r'\*\*\[(.+?)\]\((.+?)\)\*\*', parts[0])
                    if pattern_match:
                        pattern_name = pattern_match.group(1)
                        anchor_link = pattern_match.group(2)
                        
                        table_data[pattern_name] = {
                            'maturity': parts[1],
                            'type': parts[2], 
                            'description': parts[3],
                            'dependencies': parts[4],
                            'anchor_link': anchor_link
                        }
        
        return table_data


def validate_anchor_format(pattern_name: str, anchor: str) -> bool:
    """Validate that anchor follows the correct format"""
    expected_anchor = '#' + pattern_name.lower().replace(' ', '-').replace('&', '').replace(',', '')
    expected_anchor = re.sub(r'[^a-z0-9-]', '', expected_anchor)
    return anchor == expected_anchor