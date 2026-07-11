"""Keep the Issue Generation example aligned with the catalog's sizing rule."""

import importlib.util
from pathlib import Path


ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "examples" / "issue-generation" / "issue-generator.py"
SPEC = importlib.util.spec_from_file_location("issue_generator", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def raw_estimates(generator):
    """Return every concrete example estimate before platform formatting."""
    groups = (
        generator._password_reset_breakdown("raw"),
        generator._dashboard_breakdown("raw"),
        generator._generic_breakdown("Example feature", "raw"),
        generator._generate_technical_tasks("Example feature", "raw"),
    )
    return [item["estimate"] for group in groups for item in group]


def test_example_estimates_fit_the_under_one_hour_contract():
    generator = MODULE.KanbanIssueGenerator()

    minutes = [generator._estimate_minutes(item) for item in raw_estimates(generator)]

    assert minutes
    assert min(minutes) >= generator.min_task_minutes
    assert max(minutes) <= generator.max_task_minutes == 60


def test_platform_estimates_preserve_minute_semantics():
    generator = MODULE.KanbanIssueGenerator()
    issue = {"title": "Task", "body": "Body", "estimate": "45 minutes"}

    jira = generator._format_for_jira(issue)
    azure = generator._format_for_azure(issue)

    assert jira["fields"]["timetracking"]["originalEstimate"] == "45m"
    assert azure["fields"]["Microsoft.VSTS.Scheduling.OriginalEstimate"] == 0.75
