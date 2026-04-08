#!/usr/bin/env python3
"""
Generate a Claude Code fix prompt from pytest JSON results.

Usage:
    # In CI (after pytest --json-report):
    python3 scripts/generate-audit-prompt.py tests/.report.json

    # Locally:
    cd tests && python3 -m pytest --json-report --json-report-file=.report.json -q
    python3 ../scripts/generate-audit-prompt.py .report.json
"""

import json
import sys
from pathlib import Path


def load_report(report_path: str) -> dict:
    """Load pytest JSON report."""
    with open(report_path) as f:
        return json.load(f)


def extract_failures(report: dict) -> list[dict]:
    """Extract actionable failure details from report."""
    failures = []
    for test in report.get("tests", []):
        if test.get("outcome") != "passed":
            entry = {
                "test": test["nodeid"],
                "outcome": test["outcome"],
            }
            for phase in ("call", "setup", "teardown"):
                phase_data = test.get(phase, {})
                if phase_data.get("longrepr"):
                    entry["error"] = phase_data["longrepr"]
                    break
            failures.append(entry)
    return failures


def categorize(test_id: str) -> str:
    """Map test file to audit category."""
    categories = {
        "test_pattern_compliance": "Pattern Compliance",
        "test_readme_accuracy": "README Accuracy",
        "test_links": "Link Integrity",
        "test_examples": "Example Validation",
        "test_dependencies": "Dependency Graph",
        "test_diagram": "Diagram Accuracy",
        "test_yaml_readme_sync": "YAML-README Sync",
    }
    for key, label in categories.items():
        if key in test_id:
            return label
    return "Other"


def build_prompt(failures: list[dict]) -> str:
    """Build a Claude Code prompt from failures."""
    if not failures:
        return ""

    by_category: dict[str, list[dict]] = {}
    for f in failures:
        cat = categorize(f["test"])
        by_category.setdefault(cat, []).append(f)

    lines = [
        "The CI audit found issues that need fixing. "
        "For each failure below, read the referenced files, "
        "diagnose the root cause, and fix it directly. "
        "Run `cd tests && python3 -m pytest -x -q` after each fix to verify.",
        "",
    ]

    for category, items in by_category.items():
        suffix = "s" if len(items) != 1 else ""
        lines.append(f"## {category} ({len(items)} failure{suffix})")
        lines.append("")
        for item in items:
            lines.append(f"**`{item['test']}`** - {item['outcome']}")
            if "error" in item:
                error_lines = item["error"].strip().splitlines()
                if len(error_lines) > 20:
                    error_text = "\n".join(
                        error_lines[:10] + ["...", ""] + error_lines[-8:]
                    )
                else:
                    error_text = "\n".join(error_lines)
                lines.append(f"```\n{error_text}\n```")
            lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <pytest-json-report>", file=sys.stderr)
        sys.exit(1)

    report_path = sys.argv[1]
    if not Path(report_path).exists():
        print(f"Report not found: {report_path}", file=sys.stderr)
        sys.exit(1)

    report = load_report(report_path)
    failures = extract_failures(report)

    summary = report.get("summary", {})
    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    errored = summary.get("error", 0)

    print(f"Audit results: {passed}/{total} passed", file=sys.stderr)

    if not failures:
        print("All audit checks passed.", file=sys.stderr)
        sys.exit(0)

    print(f"{failed} failed, {errored} errors", file=sys.stderr)

    prompt = build_prompt(failures)
    print(prompt)
    sys.exit(1)


if __name__ == "__main__":
    main()
