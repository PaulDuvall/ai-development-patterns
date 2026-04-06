"""
Parser for extracting and analyzing patterns from experiments/README.md
"""

import re
from dataclasses import dataclass, field


@dataclass
class ExperimentalPattern:
    """Represents a parsed pattern from experiments/README.md"""
    name: str
    line_number: int
    maturity: str | None = None
    description: str | None = None
    related_patterns: list[str] = field(default_factory=list)
    related_patterns_raw: str = ""
    implementation_content: str = ""
    anti_pattern_content: str = ""
    category: str = ""


class ExperimentalPatternParser:
    """Parser for extracting pattern information from experiments/README.md"""

    def __init__(self, content: str):
        self.content = content
        self.lines = content.split('\n')

    def extract_patterns(self) -> dict[str, ExperimentalPattern]:
        """Extract all patterns from experiments/README.md content"""
        patterns = {}
        current_category = ""

        i = 0
        while i < len(self.lines):
            line = self.lines[i].strip()

            if self._is_category_header(line):
                current_category = self._extract_category_name(line)
                i += 1
                continue

            if self._is_pattern_header(line):
                pattern_name = self._extract_pattern_name(line)
                if pattern_name:
                    pattern = self._parse_pattern(i, pattern_name, current_category)
                    if pattern:
                        patterns[pattern_name] = pattern
                        i = self._find_next_pattern_start(i + 1) - 1

            i += 1

        return patterns

    def extract_reference_table(self) -> dict[str, dict[str, str]]:
        """Extract the experimental pattern reference table"""
        table_data = {}
        in_table = False

        for line in self.lines:
            stripped = line.strip()

            if "| Pattern | Maturity | Type | Description | Dependencies |" in stripped:
                in_table = True
                continue

            if in_table and stripped.startswith('|---'):
                continue

            if in_table and (not stripped or not stripped.startswith('|')):
                break

            if in_table and stripped.startswith('|'):
                parts = [p.strip() for p in stripped.split('|')[1:-1]]
                if len(parts) >= 5:
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

    def extract_mermaid_diagrams(self) -> list[dict]:
        """Extract all Mermaid diagram blocks"""
        diagrams = []
        i = 0
        while i < len(self.lines):
            if self.lines[i].strip() == '```mermaid':
                start = i + 1
                i += 1
                while i < len(self.lines) and self.lines[i].strip() != '```':
                    i += 1
                content = '\n'.join(self.lines[start:i])
                diagrams.append({
                    'start_line': start,
                    'end_line': i,
                    'content': content
                })
            i += 1
        return diagrams

    def _is_category_header(self, line: str) -> bool:
        category_patterns = [
            r'^## Advanced Workflows',
            r'^## Operations Automation',
            r'^## Monitoring & Intelligence'
        ]
        return any(re.match(p, line) for p in category_patterns)

    def _extract_category_name(self, line: str) -> str:
        if "Advanced Workflows" in line:
            return "Advanced Workflows"
        elif "Operations Automation" in line:
            return "Operations Automation"
        elif "Monitoring" in line:
            return "Monitoring & Intelligence"
        return ""

    def _is_pattern_header(self, line: str) -> bool:
        if not re.match(r'^### [A-Za-z]', line):
            return False
        if self._is_category_header(line):
            return False
        excluded = [
            'Pattern Organization', 'Experimental Pattern Reference',
            'Getting Started', 'Pattern Exploration'
        ]
        header_text = line.strip().replace('### ', '').strip()
        return header_text not in excluded

    def _extract_pattern_name(self, line: str) -> str | None:
        match = re.match(r'^### (.+)', line)
        return match.group(1).strip() if match else None

    def _parse_pattern(self, start_line: int, pattern_name: str,
                       category: str) -> ExperimentalPattern | None:
        pattern = ExperimentalPattern(
            name=pattern_name, line_number=start_line + 1, category=category
        )
        i = start_line + 1
        in_code_block = False
        anti_pattern_lines: list[str] = []
        in_anti_pattern = False

        while i < len(self.lines):
            line = self.lines[i]
            stripped = line.strip()

            if stripped.startswith('```'):
                in_code_block = not in_code_block

            if not in_code_block and stripped.startswith('### ') and self._is_pattern_header(stripped):
                break
            if not in_code_block and stripped.startswith('## '):
                break

            if stripped.startswith('**Maturity**:'):
                pattern.maturity = self._field_value(stripped, 'Maturity')
            elif stripped.startswith('**Description**:'):
                pattern.description = self._field_value(stripped, 'Description')
            elif stripped.startswith('**Related Patterns**:'):
                raw = self._field_value(stripped, 'Related Patterns')
                pattern.related_patterns_raw = raw
                pattern.related_patterns = self._parse_related(raw)

            if ('Anti-pattern' in stripped and
                    (stripped.startswith('####') or stripped.startswith('**Anti-pattern'))):
                in_anti_pattern = True
                anti_pattern_lines.append(line)
            elif in_anti_pattern:
                if stripped.startswith('---'):
                    in_anti_pattern = False
                else:
                    anti_pattern_lines.append(line)
            elif not any(stripped.startswith(p) for p in
                         ['**Maturity**:', '**Description**:', '**Related Patterns**:']):
                pattern.implementation_content += line + '\n'

            i += 1

        pattern.anti_pattern_content = '\n'.join(anti_pattern_lines)
        return pattern

    def _field_value(self, line: str, field: str) -> str:
        match = re.search(rf'\*\*{field}\*\*:\s*(.+)', line)
        return match.group(1).strip() if match else ""

    def _parse_related(self, text: str) -> list[str]:
        all_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
        return [name for name, _ in all_links]

    def _find_next_pattern_start(self, start_line: int) -> int:
        for i in range(start_line, len(self.lines)):
            stripped = self.lines[i].strip()
            if self._is_pattern_header(stripped) or stripped.startswith('## '):
                return i
        return len(self.lines)
