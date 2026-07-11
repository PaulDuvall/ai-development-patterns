#!/usr/bin/env python3
"""
Pattern Name Validation Script

Validates that every active canonical pattern and anti-pattern in the stable
and experimental catalogs complies with the naming specification.

Usage:
    python3 scripts/validate-pattern-names.py

Exit codes:
    0 - All validations passed
    1 - Validation failures found
"""

import re
import sys
from pathlib import Path

import yaml

# Words to avoid in pattern names (too generic or redundant in AI context)
AVOID_WORDS = {'ai', 'pattern', 'helper', 'utility', 'common', 'general', 'manager', 'handler', 'service'}
TECHNICAL_TITLE_WORDS = {'ChatOps'}
# Anti-pattern semantics cannot be inferred reliably from capitalization alone.
# Keep the accepted cautionary modifiers explicit so adding a neutral label is
# an intentional specification change rather than an accidental bypass.
CAUTIONARY_MODIFIERS = {
    'blind', 'bloated', 'brittle', 'broken', 'chaotic', 'conflicting',
    'confused', 'delayed', 'disconnected', 'false', 'hardcoded', 'ignored',
    'manual', 'maximal', 'missing', 'monolithic', 'mutable', 'narrative',
    'opaque', 'over-alerting', 'over-analysis', 'over-architecting',
    'over-constrained', 'over-decomposition', 'over-documentation',
    'over-prompting', 'overwhelming', 'passive', 'permission-only',
    'premature', 'random', 'reactive', 'reckless', 'redundant', 'scattered',
    'self-grading', 'shallow', 'single-model', 'spec-ignored', 'static',
    'synthetic', 'unbounded', 'unchecked', 'unconstrained', 'uncoordinated',
    'under-specified', 'undocumented', 'unmonitored', 'unplanned',
    'unrestricted', 'unsafe', 'untested',
}
TABLE_LINK_RE = re.compile(
    r'^\|\s*\*\*\[([^\]]+)\]\(#([a-z0-9]+(?:-[a-z0-9]+)*)\)\*\*\s*\|')


class ValidationError:
    def __init__(self, pattern_name: str, error_type: str, message: str,
                 line_num: int | None = None, source: str | None = None):
        self.pattern_name = pattern_name
        self.error_type = error_type
        self.message = message
        self.line_num = line_num
        self.source = source

    def __str__(self):
        if self.source and self.line_num:
            location = f" ({self.source}:{self.line_num})"
        elif self.source:
            location = f" ({self.source})"
        else:
            location = f" (line {self.line_num})" if self.line_num else ""
        return f"❌ {self.error_type}: '{self.pattern_name}'{location}\n   {self.message}"


class PatternValidator:
    def __init__(self):
        self.errors: list[ValidationError] = []
        self.warnings: list[str] = []
        self.patterns_found: set[str] = set()
        self.antipatterns_found: set[str] = set()
        self.stable_count = 0
        self.experimental_count = 0
        self.stable_antipattern_count = 0
        self.experimental_antipattern_count = 0

    def count_words(self, name: str) -> int:
        """Count words in a pattern name. Hyphenated words count as one word."""
        # Remove hyphens within words (e.g., "Spec-Driven" is 1 word, "AI-Driven" is 1 word)
        # Split by spaces
        words = name.strip().split()
        return len(words)

    def has_avoid_words(self, name: str) -> list[str]:
        """Check if pattern name contains words to avoid."""
        words = [w.lower().replace('-', '') for w in name.split()]
        found_avoid = []
        for word in words:
            if word in AVOID_WORDS:
                found_avoid.append(word)
        return found_avoid

    def is_title_case(self, name: str) -> bool:
        """Check exact Title Case, while allowing catalog technical terms/acronyms."""
        words = name.split()
        for word in words:
            parts = word.split('-')
            for part in parts:
                if not part or not (
                        part.istitle() or part.isupper()
                        or part in TECHNICAL_TITLE_WORDS):
                    return False
        return True

    def has_ai_prefix(self, name: str) -> bool:
        """Return True for the redundant AI/AI-* prefix forbidden by the spec."""
        words = name.split()
        if not words:
            return False
        first = words[0]
        normalized = first.casefold()
        return (
            normalized == 'ai'
            or normalized.startswith('ai-')
            or bool(re.match(r'^AI[A-Z]', first))
        )

    def validate_pattern_name(self, name: str, line_num: int = None) -> bool:
        """Validate a pattern name against all rules."""
        valid = True

        # Rule 1: Exactly two words
        word_count = self.count_words(name)
        if word_count != 2:
            self.errors.append(ValidationError(
                name, "Word Count",
                f"Must be exactly 2 words (found {word_count}). Hyphenated compounds count as one word.",
                line_num
            ))
            valid = False

        # Rule 2: Title Case
        if not self.is_title_case(name):
            self.errors.append(ValidationError(
                name, "Title Case",
                "Pattern name must use Title Case (each word capitalized)",
                line_num
            ))
            valid = False

        # Rule 3: No redundant AI prefix
        if self.has_ai_prefix(name):
            self.errors.append(ValidationError(
                name, "AI Prefix",
                "Pattern name must not start with the redundant 'AI' prefix",
                line_num
            ))
            valid = False

        # Advisory: avoid other generic words from the naming specification.
        avoid_found = self.has_avoid_words(name)
        if avoid_found:
            self.warnings.append(
                f"⚠️  Pattern '{name}' contains generic/redundant words: {', '.join(avoid_found)}"
            )

        # Track pattern
        if valid:
            self.patterns_found.add(name)

        return valid

    def validate_antipattern_name(
            self, name: str, line_num: int = None, source: str = None) -> bool:
        """Validate one canonical anti-pattern label."""
        valid = True
        word_count = self.count_words(name)
        is_single_compound = word_count == 1 and '-' in name.strip('-')
        if word_count != 2 and not is_single_compound:
            self.errors.append(ValidationError(
                name, "Anti-pattern Word Count",
                "Must be exactly 2 words or one hyphenated compound",
                line_num, source))
            valid = False

        if not name or not self.is_title_case(name):
            self.errors.append(ValidationError(
                name, "Anti-pattern Title Case",
                "Anti-pattern name must use Title Case",
                line_num, source))
            valid = False

        first_word = name.split()[0].casefold() if name.split() else ''
        if first_word not in CAUTIONARY_MODIFIERS:
            self.errors.append(ValidationError(
                name, "Cautionary Modifier",
                "Anti-pattern name must begin with an approved negative or cautionary modifier",
                line_num, source))
            valid = False

        if valid:
            self.antipatterns_found.add(name)
        return valid

    @staticmethod
    def canonical_slug(name: str) -> str:
        """Convert a canonical display name to its required catalog slug."""
        return re.sub(r'[^a-z0-9]+', '-', name.casefold()).strip('-')

    @staticmethod
    def line_for_value(content: str, field: str, value: str) -> int | None:
        """Locate a simple YAML scalar for actionable diagnostics."""
        pattern = re.compile(
            rf'^\s*{re.escape(field)}:\s*["\']?{re.escape(value)}["\']?\s*$')
        for line_num, line in enumerate(content.splitlines(), 1):
            if pattern.fullmatch(line):
                return line_num
        return None

    @staticmethod
    def markdown_headings(lines: list[str]) -> list[dict]:
        """Return ATX headings outside CommonMark fenced code blocks."""
        headings = []
        in_fence = False
        fence_marker = ""
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            fence_open = re.match(r"^(`{3,}|~{3,})", stripped)
            if not in_fence and fence_open:
                in_fence = True
                fence_marker = fence_open.group(1)
                continue
            if in_fence:
                fence_close = re.match(r"^(`{3,}|~{3,})\s*$", stripped)
                if fence_close \
                        and fence_close.group(1)[0] == fence_marker[0] \
                        and len(fence_close.group(1)) >= len(fence_marker):
                    in_fence = False
                    fence_marker = ""
                continue
            match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if match:
                headings.append({
                    "line": line_num,
                    "level": len(match.group(1)),
                    "text": match.group(2).strip(),
                })
        return headings

    @staticmethod
    def antipattern_labels(lines: list[str]) -> list[dict]:
        """Return anti-pattern labels outside CommonMark fenced code blocks."""
        labels = []
        in_fence = False
        fence_marker = ""
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            fence_open = re.match(r"^(`{3,}|~{3,})", stripped)
            if not in_fence and fence_open:
                in_fence = True
                fence_marker = fence_open.group(1)
                continue
            if in_fence:
                fence_close = re.match(r"^(`{3,}|~{3,})\s*$", stripped)
                if fence_close \
                        and fence_close.group(1)[0] == fence_marker[0] \
                        and len(fence_close.group(1)) >= len(fence_marker):
                    in_fence = False
                    fence_marker = ""
                continue

            heading = re.match(
                r"^(#{1,6})\s+Anti-pattern:\s*(.*?)\s*$", stripped)
            if heading:
                labels.append({
                    'name': heading.group(2),
                    'level': len(heading.group(1)),
                    'line': line_num,
                })
                continue
            bold = re.match(r"^\*\*Anti-pattern:\s*(.*?)\*\*$", stripped)
            if bold:
                labels.append({
                    'name': bold.group(1),
                    'level': 0,
                    'line': line_num,
                })
        return labels

    def validate_antipattern_catalog(self, path: Path, label: str) -> int:
        """Validate every canonical anti-pattern label in one catalog."""
        if not path.is_file():
            return 0
        labels = self.antipattern_labels(
            path.read_text(encoding='utf-8').splitlines())
        if not labels:
            self.errors.append(ValidationError(
                label, "Missing Anti-patterns",
                "Catalog must contain canonical anti-pattern labels",
                source=label))
            return 0
        for item in labels:
            if item['level'] != 4:
                self.errors.append(ValidationError(
                    item['name'], "Anti-pattern Markup",
                    "Canonical anti-pattern labels must use an H4 heading",
                    item['line'], label))
            self.validate_antipattern_name(
                item['name'], item['line'], label)
        return len(labels)

    def load_stable_catalog(self, path: Path) -> list[dict]:
        """Load canonical stable names from patterns.yaml and validate their IDs."""
        if not path.is_file():
            self.errors.append(ValidationError(
                str(path), "Missing Catalog", "patterns.yaml does not exist"))
            return []
        content = path.read_text(encoding='utf-8')
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            self.errors.append(ValidationError(
                str(path), "Invalid YAML", str(exc)))
            return []
        values = data.get('patterns') if isinstance(data, dict) else None
        if not isinstance(values, list):
            self.errors.append(ValidationError(
                str(path), "Catalog Schema",
                "patterns.yaml must contain a 'patterns' list"))
            return []

        records = []
        for index, value in enumerate(values):
            if not isinstance(value, dict):
                self.errors.append(ValidationError(
                    f"patterns[{index}]", "Catalog Schema",
                    "Each stable pattern must be a mapping"))
                continue
            name = value.get('name')
            slug = value.get('id')
            anchor = value.get('anchor')
            line_num = (
                self.line_for_value(content, 'name', name)
                if isinstance(name, str) else None)
            if not isinstance(name, str) or not name.strip():
                self.errors.append(ValidationError(
                    repr(name), "Catalog Schema",
                    f"patterns[{index}].name must be a non-empty string"))
                continue
            if name != name.strip() or name != ' '.join(name.split()):
                self.errors.append(ValidationError(
                    name, "Whitespace",
                    "Pattern names must use single spaces with no surrounding whitespace",
                    line_num))
            expected_slug = self.canonical_slug(name)
            if slug != expected_slug:
                self.errors.append(ValidationError(
                    name, "ID Mismatch",
                    f"patterns.yaml id must be '{expected_slug}', found {slug!r}",
                    line_num))
            if anchor != f"#{expected_slug}":
                self.errors.append(ValidationError(
                    name, "Anchor Mismatch",
                    f"patterns.yaml anchor must be '#{expected_slug}', found {anchor!r}",
                    line_num))
            records.append({
                'name': name,
                'slug': slug if isinstance(slug, str) else '',
                'line': line_num,
            })
        return records

    def extract_catalog_table(
            self, path: Path, heading: str, label: str) -> list[dict]:
        """Extract linked active names from one explicitly bounded reference table."""
        if not path.is_file():
            self.errors.append(ValidationError(
                str(path), "Missing Catalog", f"{label} markdown file does not exist"))
            return []
        lines = path.read_text(encoding='utf-8').splitlines()
        expected = re.fullmatch(r'(#{1,6})\s+(.+)', heading)
        if not expected:
            raise ValueError(f"Invalid catalog heading selector: {heading!r}")
        match = next((
            item for item in self.markdown_headings(lines)
            if item['level'] == len(expected.group(1))
            and item['text'] == expected.group(2)
        ), None)
        if match is None:
            self.errors.append(ValidationError(
                label, "Missing Reference Table",
                f"Required heading {heading!r} was not found"))
            return []
        start = match['line'] - 1

        records = []
        table_started = False
        for line_num, line in enumerate(lines[start + 1:], start + 2):
            if line.startswith('|'):
                table_started = True
                match = TABLE_LINK_RE.match(line)
                if match:
                    records.append({
                        'name': match.group(1).strip(),
                        'slug': match.group(2),
                        'line': line_num,
                    })
                continue
            if table_started and line.strip() == '':
                break
            if table_started:
                break
        return records

    def validate_unique_records(self, records: list[dict]) -> None:
        """Reject duplicate active names and slugs, including cross-catalog copies."""
        seen_names: dict[str, dict] = {}
        seen_slugs: dict[str, dict] = {}
        for record in records:
            name_key = record['name'].casefold()
            slug_key = record['slug'].casefold()
            if name_key in seen_names:
                first = seen_names[name_key]
                self.errors.append(ValidationError(
                    record['name'], "Duplicate Name",
                    f"Active name duplicates {first['name']!r}", record.get('line')))
            else:
                seen_names[name_key] = record
            if slug_key in seen_slugs:
                first = seen_slugs[slug_key]
                self.errors.append(ValidationError(
                    record['name'], "Duplicate Slug",
                    f"Active slug {record['slug']!r} is already used by "
                    f"{first['name']!r}", record.get('line')))
            else:
                seen_slugs[slug_key] = record

    def validate_table_matches(
            self, canonical: list[dict], displayed: list[dict], label: str) -> None:
        """Require a display table to exactly match its canonical catalog sequence."""
        self.validate_unique_records(displayed)
        canonical_pairs = [(item['name'], item['slug']) for item in canonical]
        displayed_pairs = [(item['name'], item['slug']) for item in displayed]
        if canonical_pairs == displayed_pairs:
            return

        canonical_names = {item['name'] for item in canonical}
        displayed_names = {item['name'] for item in displayed}
        for name in sorted(canonical_names - displayed_names):
            self.errors.append(ValidationError(
                name, "Missing Display Name",
                f"{label} reference table is missing this canonical pattern"))
        for name in sorted(displayed_names - canonical_names):
            item = next(item for item in displayed if item['name'] == name)
            self.errors.append(ValidationError(
                name, "Unexpected Display Name",
                f"{label} reference table does not match the canonical catalog",
                item.get('line')))
        for expected, actual in zip(canonical, displayed):
            if expected['name'] == actual['name'] \
                    and expected['slug'] != actual['slug']:
                self.errors.append(ValidationError(
                    actual['name'], "Display Anchor Mismatch",
                    f"{label} link must target '#{expected['slug']}', "
                    f"found '#{actual['slug']}'", actual.get('line')))
        if canonical_names == displayed_names and canonical_pairs != displayed_pairs:
            self.errors.append(ValidationError(
                label, "Display Order Mismatch",
                "Reference table order must match its canonical catalog"))

    def validate_section_headings(
            self, path: Path, records: list[dict], levels: tuple[int, ...],
            label: str, reject_unexpected: bool = False) -> None:
        """Require exactly one canonical content section for every active name."""
        # extract_catalog_table already emits the actionable missing-file error.
        if not path.is_file():
            return
        lines = path.read_text(encoding='utf-8').splitlines()
        heading_counts: dict[str, list[int]] = {}
        for heading in self.markdown_headings(lines):
            if heading['level'] in levels:
                heading_counts.setdefault(
                    heading['text'], []).append(heading['line'])
        for record in records:
            occurrences = heading_counts.get(record['name'], [])
            if not occurrences:
                self.errors.append(ValidationError(
                    record['name'], "Missing Pattern Section",
                    f"{label} must contain a level "
                    f"{'/'.join(map(str, levels))} heading with the exact canonical name"))
            elif len(occurrences) > 1:
                self.errors.append(ValidationError(
                    record['name'], "Duplicate Pattern Section",
                    f"{label} contains {len(occurrences)} canonical headings",
                    occurrences[1]))
        if reject_unexpected:
            expected = {record['name'] for record in records}
            for name in sorted(heading_counts.keys() - expected):
                self.errors.append(ValidationError(
                    name, "Unexpected Pattern Section",
                    f"{label} heading is not present in its active reference table",
                    heading_counts[name][0]))

    def validate_active_catalogs(self, repo_root: Path) -> bool:
        """Validate every active stable and experimental canonical pattern."""
        stable = self.load_stable_catalog(repo_root / 'patterns.yaml')
        experimental = self.extract_catalog_table(
            repo_root / 'experiments' / 'README.md',
            '## Experimental Pattern Reference', 'experimental catalog')
        stable_display = self.extract_catalog_table(
            repo_root / 'README.md',
            '## Complete Pattern Reference', 'stable catalog')

        self.stable_count = len(stable)
        self.experimental_count = len(experimental)
        if not stable:
            self.errors.append(ValidationError(
                'patterns.yaml', "Empty Catalog",
                "No active stable patterns were found; refusing zero-pattern success"))
        if not experimental:
            self.errors.append(ValidationError(
                'experiments/README.md', "Empty Catalog",
                "No active experimental patterns were found; refusing zero-pattern success"))

        active = stable + experimental
        self.validate_unique_records(active)
        for record in active:
            expected_slug = self.canonical_slug(record['name'])
            if record['slug'] != expected_slug:
                self.errors.append(ValidationError(
                    record['name'], "Anchor Mismatch",
                    f"Active anchor/slug must be '{expected_slug}', "
                    f"found {record['slug']!r}", record.get('line')))
            self.validate_pattern_name(record['name'], record.get('line'))

        self.validate_table_matches(stable, stable_display, 'README.md')
        if stable:
            self.validate_section_headings(
                repo_root / 'README.md', stable, (2, 3), 'README.md')
        if experimental:
            self.validate_section_headings(
                repo_root / 'experiments' / 'README.md', experimental, (3,),
                'experiments/README.md', reject_unexpected=True)
        self.stable_antipattern_count = self.validate_antipattern_catalog(
            repo_root / 'README.md', 'README.md')
        self.experimental_antipattern_count = self.validate_antipattern_catalog(
            repo_root / 'experiments' / 'README.md', 'experiments/README.md')
        return not self.errors

    def print_report(self):
        """Print validation report."""
        print("\n" + "="*80)
        print("VALIDATION REPORT")
        print("="*80)

        print(f"\n📊 Statistics:")
        print(f"  Stable patterns: {self.stable_count}")
        print(f"  Experimental patterns: {self.experimental_count}")
        print(f"  Active patterns found: {len(self.patterns_found)}")
        print(f"  Stable anti-patterns: {self.stable_antipattern_count}")
        print(f"  Experimental anti-patterns: {self.experimental_antipattern_count}")
        print(f"  Active anti-pattern names found: {len(self.antipatterns_found)}")
        print(f"  Total names: {len(self.patterns_found) + len(self.antipatterns_found)}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        else:
            print(f"\n✅ All pattern names are compliant!")

        print("\n" + "="*80)


def main():
    """Main validation routine."""
    repo_root = Path(__file__).parent.parent
    validator = PatternValidator()

    print("🔍 AI Development Patterns - Name Validation")
    print("="*80)

    # Only active catalog sources define canonical names. Historical prose and
    # compatibility anchors are intentionally outside this validation surface.
    validator.validate_active_catalogs(repo_root)

    # Print final report
    validator.print_report()

    # Exit with appropriate code
    if validator.errors:
        print("\n❌ Validation FAILED")
        return 1
    else:
        print("\n✅ Validation PASSED")
        return 0


if __name__ == '__main__':
    sys.exit(main())
