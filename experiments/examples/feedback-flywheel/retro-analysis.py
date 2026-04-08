"""Feedback Flywheel retrospective analysis.

Analyzes AI-assisted session logs to extract correction patterns,
calculate acceptance rates, and propose rule updates.
"""

import argparse
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import yaml


def load_sessions(log_dir: Path, period_days: int) -> list[dict]:
    """Load session logs from the given period."""
    cutoff = datetime.now() - timedelta(days=period_days)
    sessions = []

    for log_file in sorted(log_dir.glob("*.yaml")):
        data = yaml.safe_load(log_file.read_text())
        if not data or "session" not in data:
            continue
        session_date = datetime.strptime(data["session"]["date"], "%Y-%m-%d")
        if session_date >= cutoff:
            sessions.append(data)

    return sessions


def compute_acceptance_rate(sessions: list[dict]) -> float:
    """Compute aggregate first-pass acceptance rate."""
    total_accepted = sum(s["outcomes"]["first_pass_accepted"] for s in sessions)
    total_generations = sum(s["outcomes"]["total_generations"] for s in sessions)
    if total_generations == 0:
        return 0.0
    return total_accepted / total_generations


def extract_corrections(sessions: list[dict]) -> list[dict]:
    """Collect all corrections across sessions."""
    corrections = []
    for session in sessions:
        for correction in session.get("corrections", []):
            correction["session_date"] = session["session"]["date"]
            correction["developer"] = session["session"]["developer"]
            corrections.append(correction)
    return corrections


def find_root_causes(corrections: list[dict]) -> list[tuple[str, int]]:
    """Rank root causes by frequency."""
    causes = Counter(c["root_cause"] for c in corrections)
    return causes.most_common()


def find_repeated_corrections(corrections: list[dict]) -> list[dict]:
    """Identify corrections that recur across sessions."""
    by_rule = {}
    for correction in corrections:
        rule = correction.get("proposed_rule", "")
        if rule not in by_rule:
            by_rule[rule] = []
        by_rule[rule].append(correction)
    return [
        {"proposed_rule": rule, "occurrences": len(items), "sessions": items}
        for rule, items in by_rule.items()
        if len(items) > 1
    ]


def generate_report(
    sessions: list[dict],
    period_days: int,
    show_trend: bool,
) -> str:
    """Generate a markdown retrospective report."""
    acceptance_rate = compute_acceptance_rate(sessions)
    corrections = extract_corrections(sessions)
    root_causes = find_root_causes(corrections)
    repeated = find_repeated_corrections(corrections)

    lines = [
        f"# Feedback Flywheel Retrospective ({period_days}-Day)",
        "",
        f"**Period**: Last {period_days} days",
        f"**Sessions analyzed**: {len(sessions)}",
        f"**First-pass acceptance rate**: {acceptance_rate:.0%}",
        f"**Total corrections**: {len(corrections)}",
        "",
    ]

    if repeated:
        lines.append("## Repeated Corrections (Action Required)")
        lines.append("")
        for item in repeated:
            lines.append(
                f"- **{item['proposed_rule']}** "
                f"({item['occurrences']} occurrences)"
            )
        lines.append("")

    if root_causes:
        lines.append("## Top Root Causes")
        lines.append("")
        lines.append("| Root Cause | Count |")
        lines.append("|------------|-------|")
        for cause, count in root_causes[:5]:
            lines.append(f"| {cause} | {count} |")
        lines.append("")

    proposed_rules = [c["proposed_rule"] for c in corrections if c.get("proposed_rule")]
    if proposed_rules:
        lines.append("## Proposed Rule Updates")
        lines.append("")
        for rule in dict.fromkeys(proposed_rules):
            lines.append(f"- [ ] {rule}")
        lines.append("")

    if show_trend and len(sessions) >= 2:
        lines.append("## Acceptance Rate Trend")
        lines.append("")
        for session in sessions:
            date = session["session"]["date"]
            rate = session["outcomes"].get("acceptance_rate", 0)
            lines.append(f"- {date}: {rate:.0%}")
        lines.append("")

    lines.append("## Next Steps")
    lines.append("")
    lines.append("1. Review proposed rules above")
    lines.append("2. Add validated rules to `.ai/rules/`")
    lines.append("3. Address repeated corrections first (highest impact)")
    lines.append("4. Re-run retro next period to measure improvement")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Run retrospective analysis from CLI."""
    parser = argparse.ArgumentParser(
        description="Analyze AI session logs for feedback flywheel retrospective"
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path(".ai/session-logs"),
        help="Directory containing session log YAML files",
    )
    parser.add_argument(
        "--period",
        type=str,
        default="7d",
        help="Analysis period (e.g., 7d, 30d)",
    )
    parser.add_argument(
        "--trend",
        action="store_true",
        help="Show acceptance rate trend over time",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    period_days = int(args.period.rstrip("d"))

    if not args.log_dir.exists():
        print(f"Error: Log directory not found: {args.log_dir}", file=sys.stderr)
        print("Create it with: mkdir -p .ai/session-logs", file=sys.stderr)
        sys.exit(1)

    sessions = load_sessions(args.log_dir, period_days)
    if not sessions:
        print(f"No session logs found in {args.log_dir} for the last {period_days} days")
        sys.exit(0)

    report = generate_report(sessions, period_days, args.trend)

    if args.output:
        args.output.write_text(report)
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
