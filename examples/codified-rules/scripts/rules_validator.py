#!/usr/bin/env python3
"""Deterministically validate the runnable Codified Rules example."""

import argparse
import re
import sys
from pathlib import Path


MAX_FILE_BYTES = 1024 * 1024
MAX_SCAN_FILES = 1000
RULE_FILES = (
    "DEVELOPMENT_RULES.md",
    "QUALITY_RULES.md",
    "PIPELINE_RULES.md",
)
FEATURE_ID = re.compile(r"\b(?:SPEC|FEAT)-[A-Z0-9][A-Z0-9-]*\b")
ACCEPTANCE_ID = re.compile(r"\bAC-[A-Z0-9][A-Z0-9-]*\b")
TEST_ID = re.compile(r"\bTEST-[A-Z0-9][A-Z0-9-]*\b")
TRACE_REFERENCE = re.compile(
    r"(?P<path>specs/[A-Za-z0-9_.\-/]+\.md)#(?P<acceptance>AC-[A-Z0-9-]+)"
)
ORR_ITEM = re.compile(
    r"^- \[(?P<state>[ xX])\] (?P<item>ORR-[A-Z-]+):\s*(?P<evidence>.+)$"
)
REQUIRED_ORR_ITEMS = {
    "ORR-ALERTS",
    "ORR-APPROVAL",
    "ORR-FEATURE-FLAG",
    "ORR-OBSERVABILITY",
    "ORR-ROLLBACK",
    "ORR-SECURITY",
}
SOURCE_SUFFIXES = frozenset(
    {".go", ".java", ".js", ".jsx", ".py", ".rs", ".ts", ".tsx"}
)
PLACEHOLDER_EVIDENCE = frozenset({"n/a", "none", "tbd", "todo"})


class RulesValidationError(ValueError):
    """Raised when deterministic rule evidence is incomplete or ambiguous."""


def require_regular_directory(path, label):
    """Reject missing directories and directly supplied symbolic-link roots."""
    if path.is_symlink() or not path.is_dir():
        raise RulesValidationError(f"{label} must be a regular directory: {path}")


def read_bounded_text(path):
    """Read one regular, bounded UTF-8 file without following a symlink."""
    if path.is_symlink() or not path.is_file():
        raise RulesValidationError(f"required regular file is missing: {path}")
    if path.stat().st_size > MAX_FILE_BYTES:
        raise RulesValidationError(f"file exceeds {MAX_FILE_BYTES} bytes: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise RulesValidationError(f"file is not valid UTF-8: {path}") from exc


def regular_files(root, suffixes):
    """Return a bounded, sorted set of non-symlink files beneath ``root``."""
    if root.is_symlink() or not root.is_dir():
        raise RulesValidationError(f"required directory is missing: {root}")
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RulesValidationError(f"symbolic links are not allowed: {path}")
        if path.is_file() and path.suffix.casefold() in suffixes:
            files.append(path)
            if len(files) > MAX_SCAN_FILES:
                raise RulesValidationError(
                    f"scan exceeds {MAX_SCAN_FILES} files beneath {root}")
    return files


def validate_rule_documents(rules_root):
    """Require all rule documents and exact references from ``CLAUDE.md``."""
    require_regular_directory(rules_root, "rules root")
    claude = read_bounded_text(rules_root / "CLAUDE.md")
    for name in RULE_FILES:
        rule = read_bounded_text(rules_root / name)
        if len(rule.splitlines()) < 20:
            raise RulesValidationError(f"rule document is unexpectedly short: {name}")
        if name not in claude:
            raise RulesValidationError(f"CLAUDE.md does not reference {name}")


def specification_inventory(project_root):
    """Return acceptance criteria after validating unique specification IDs."""
    require_regular_directory(project_root, "project root")
    specs_root = project_root / "specs"
    spec_files = regular_files(specs_root, frozenset({".md"}))
    if not spec_files:
        raise RulesValidationError(f"no Markdown specifications found in {specs_root}")

    seen_features = {}
    seen_acceptance = {}
    acceptance = set()
    for path in spec_files:
        text = read_bounded_text(path)
        features = set(FEATURE_ID.findall(text))
        criteria = set(ACCEPTANCE_ID.findall(text))
        tests = set(TEST_ID.findall(text))
        if len(features) != 1:
            raise RulesValidationError(
                f"{path} must contain exactly one unique SPEC-* or FEAT-* ID")
        if not criteria:
            raise RulesValidationError(f"{path} contains no AC-* acceptance criteria")
        if not tests:
            raise RulesValidationError(f"{path} contains no TEST-* scenario IDs")
        feature = next(iter(features))
        if feature in seen_features:
            raise RulesValidationError(
                f"duplicate feature ID {feature}: {seen_features[feature]} and {path}")
        seen_features[feature] = path
        relative = path.relative_to(project_root).as_posix()
        for criterion in criteria:
            if criterion in seen_acceptance:
                raise RulesValidationError(
                    f"duplicate acceptance ID {criterion}: "
                    f"{seen_acceptance[criterion]} and {path}")
            seen_acceptance[criterion] = path
            acceptance.add((relative, criterion))
    return acceptance, len(spec_files), len(seen_features), len(seen_acceptance)


def validate_specifications(rules_root, project_root):
    """Validate rule-document presence and the project's specification set."""
    validate_rule_documents(rules_root)
    _, spec_count, feature_count, acceptance_count = specification_inventory(
        project_root)
    print(
        "Specification validation passed: "
        f"{spec_count} file(s), {feature_count} feature ID(s), "
        f"{acceptance_count} acceptance criterion/criteria."
    )


def trace_references(project_root, directory):
    """Collect and validate specification references from one source tree."""
    references = set()
    files = regular_files(project_root / directory, SOURCE_SUFFIXES)
    if not files:
        raise RulesValidationError(
            f"no supported files found in {project_root / directory}")
    for path in files:
        for match in TRACE_REFERENCE.finditer(read_bounded_text(path)):
            references.add((match.group("path"), match.group("acceptance")))
    return references


def validate_traceability(project_root):
    """Require every acceptance criterion in both tests and implementation."""
    acceptance, _, _, _ = specification_inventory(project_root)
    test_references = trace_references(project_root, "tests")
    source_references = trace_references(project_root, "src")
    unknown = (test_references | source_references) - acceptance
    if unknown:
        rendered = ", ".join(f"{path}#{item}" for path, item in sorted(unknown))
        raise RulesValidationError(f"trace references unknown criteria: {rendered}")
    missing_tests = acceptance - test_references
    missing_source = acceptance - source_references
    if missing_tests or missing_source:
        details = []
        if missing_tests:
            details.append(
                "missing test references: "
                + ", ".join(
                    f"{path}#{item}" for path, item in sorted(missing_tests)))
        if missing_source:
            details.append(
                "missing implementation references: "
                + ", ".join(
                    f"{path}#{item}" for path, item in sorted(missing_source)))
        raise RulesValidationError("; ".join(details))
    print(
        "Traceability validation passed: "
        f"{len(acceptance)} acceptance criterion/criteria covered by tests and source."
    )


def validate_orr(checklist):
    """Validate a complete, evidence-bearing Markdown ORR checklist."""
    found = {}
    for line in read_bounded_text(checklist).splitlines():
        match = ORR_ITEM.fullmatch(line.strip())
        if not match:
            continue
        item = match.group("item")
        if item in found:
            raise RulesValidationError(f"duplicate ORR checklist item: {item}")
        if item not in REQUIRED_ORR_ITEMS:
            raise RulesValidationError(f"unrecognized ORR checklist item: {item}")
        found[item] = (match.group("state"), match.group("evidence").strip())
    missing = REQUIRED_ORR_ITEMS - set(found)
    if missing:
        raise RulesValidationError(
            "missing ORR checklist items: " + ", ".join(sorted(missing)))
    for item, (state, evidence) in found.items():
        if state.casefold() != "x":
            raise RulesValidationError(f"ORR checklist item is not complete: {item}")
        if evidence.casefold() in PLACEHOLDER_EVIDENCE or len(evidence) < 8:
            raise RulesValidationError(f"ORR evidence is missing or a placeholder: {item}")
    print(
        "ORR structure validation passed: all required evidence fields are complete. "
        "Human release authorization remains external to this script."
    )


def main():
    """Parse the requested deterministic validation and report a safe failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    specifications = subparsers.add_parser("specifications")
    specifications.add_argument("rules_root", type=Path)
    specifications.add_argument("project_root", type=Path)
    traceability = subparsers.add_parser("traceability")
    traceability.add_argument("project_root", type=Path)
    orr = subparsers.add_parser("orr")
    orr.add_argument("checklist", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "specifications":
            validate_specifications(args.rules_root, args.project_root)
        elif args.command == "traceability":
            validate_traceability(args.project_root)
        else:
            validate_orr(args.checklist)
    except (OSError, RulesValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
