#!/usr/bin/env python3
"""
Generate a local coding-agent fix prompt from pytest JSON results.

Usage:
    # In CI (after pytest --json-report):
    python3 scripts/generate-audit-prompt.py tests/.report.json

    # Locally:
    cd tests && python3 -m pytest --json-report --json-report-file=.report.json -q
    python3 ../scripts/generate-audit-prompt.py .report.json

    # For an embedded suite:
    python3 scripts/generate-audit-prompt.py \
        --rerun-command 'cd examples/spec-driven-development && pytest -x -q' \
        tests/test-results/spec-driven-report.json
"""

import argparse
import json
import sys
from pathlib import Path


FAILURE_OUTCOMES = {"failed", "error"}


def load_report(report_path: str) -> dict:
    """Load pytest JSON report."""
    with open(report_path) as f:
        return json.load(f)


def extract_failures(report: dict) -> list[dict]:
    """Extract test, collection, and session failures from a pytest report."""
    failures = []
    for test in report.get("tests", []):
        if test.get("outcome") not in FAILURE_OUTCOMES:
            continue
        entry = {
            "test": test.get("nodeid", "pytest test"),
            "outcome": test.get("outcome", "failed"),
        }
        for phase in ("call", "setup", "teardown"):
            phase_data = test.get(phase, {})
            if phase_data.get("longrepr"):
                entry["error"] = phase_data["longrepr"]
                break
        failures.append(entry)

    for collector in report.get("collectors", []):
        if collector.get("outcome") not in FAILURE_OUTCOMES:
            continue
        entry = {
            "test": f"collection: {collector.get('nodeid') or 'pytest session'}",
            "outcome": collector.get("outcome", "failed"),
        }
        if collector.get("longrepr"):
            entry["error"] = collector["longrepr"]
        failures.append(entry)

    exit_code = report.get("exitcode", 0)
    summary = report.get("summary", {})
    session_failed = bool(
        exit_code
        or summary.get("failed", 0)
        or summary.get("error", 0)
    )
    if session_failed and not failures:
        failures.append({
            "test": "pytest session",
            "outcome": f"exit code {exit_code or 'unknown'}",
            "error": (
                "Pytest exited unsuccessfully before reporting an actionable "
                "test or collector failure. Re-run the prescribed command "
                "locally to capture the complete import/configuration error."
            ),
        })
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


DEFAULT_RERUN_COMMAND = 'python3 -m pytest -m "not slow" -x -q'


def build_prompt(
    failures: list[dict], rerun_command: str = DEFAULT_RERUN_COMMAND
) -> str:
    """Build a local coding-agent prompt from failures."""
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
        f"Run `{rerun_command}` after each fix to verify.",
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


def main(argv=None):
    """Generate and print a remediation prompt from a pytest JSON report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_path")
    parser.add_argument(
        "--rerun-command",
        default=DEFAULT_RERUN_COMMAND,
        help="exact local command the generated prompt should prescribe",
    )
    args = parser.parse_args(argv)

    report_path = args.report_path
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

    print(
        f"{failed} failed, {errored} errors, "
        f"exit code {report.get('exitcode', 'unknown')}",
        file=sys.stderr,
    )

    prompt = build_prompt(failures, rerun_command=args.rerun_command)
    print(prompt)
    sys.exit(1)


if __name__ == "__main__":
    main()
