"""Tests for the codified GitHub repository-rules configuration."""

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parent.parent / "scripts" / "configure-repository-rules.py"
SPEC = importlib.util.spec_from_file_location("configure_repository_rules", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_ruleset_targets_default_branch_and_required_evidence_check():
    payload = MODULE.ruleset_payload()

    assert payload["enforcement"] == "active"
    assert payload["conditions"]["ref_name"]["include"] == ["~DEFAULT_BRANCH"]
    status_rule = next(rule for rule in payload["rules"]
                       if rule["type"] == "required_status_checks")
    assert status_rule["parameters"]["required_status_checks"] == [
        {
            "context": MODULE.REQUIRED_CHECK,
            "integration_id": MODULE.GITHUB_ACTIONS_INTEGRATION_ID,
        }
    ]
    assert status_rule["parameters"]["strict_required_status_checks_policy"] is True


def test_ruleset_requires_pull_requests_and_blocks_force_pushes():
    rules = MODULE.ruleset_payload()["rules"]
    types = {rule["type"] for rule in rules}

    assert "pull_request" in types
    assert "non_fast_forward" in types
    pull_request = next(rule for rule in rules if rule["type"] == "pull_request")
    assert pull_request["parameters"]["required_review_thread_resolution"] is True
    assert pull_request["parameters"]["required_approving_review_count"] == 0


def test_workflow_token_defaults_to_read_and_can_open_publisher_prs():
    assert MODULE.workflow_permissions_payload() == {
        "default_workflow_permissions": "read",
        "can_approve_pull_request_reviews": True,
    }


def test_paid_research_environment_requires_human_review_on_protected_branches():
    payload = MODULE.paid_research_environment_payload(1619259)

    assert MODULE.PAID_RESEARCH_ENVIRONMENT == "evidence-paid-research"
    assert payload == {
        "wait_timer": 0,
        "prevent_self_review": False,
        "can_admins_bypass": False,
        "reviewers": [{"type": "User", "id": 1619259}],
        "deployment_branch_policy": {
            "protected_branches": True,
            "custom_branch_policies": False,
        },
    }


def test_apply_configures_approval_before_other_repository_controls(monkeypatch):
    calls = []
    monkeypatch.setattr(
        MODULE, "repository_name", lambda: "PaulDuvall/ai-development-patterns")
    monkeypatch.setattr(
        MODULE, "authenticated_user",
        lambda: {"login": "PaulDuvall", "id": 1619259, "type": "User"})
    monkeypatch.setattr(
        MODULE, "apply_paid_research_environment",
        lambda repo, payload: calls.append(("environment", repo, payload)))
    monkeypatch.setattr(
        MODULE, "apply_workflow_permissions",
        lambda repo, payload: calls.append(("permissions", repo, payload)))
    monkeypatch.setattr(
        MODULE, "apply_ruleset",
        lambda repo, payload: (
            calls.append(("ruleset", repo, payload)) or
            {"name": MODULE.RULESET_NAME, "id": 18778612}
        ))
    monkeypatch.setattr(MODULE.sys, "argv", [str(SCRIPT), "--apply"])

    assert MODULE.main() == 0
    assert [call[0] for call in calls] == [
        "environment", "permissions", "ruleset"]


def test_apply_fails_before_other_controls_when_environment_setup_fails(
        monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(
        MODULE, "repository_name", lambda: "PaulDuvall/ai-development-patterns")
    monkeypatch.setattr(
        MODULE, "authenticated_user",
        lambda: {"login": "PaulDuvall", "id": 1619259, "type": "User"})

    def fail_environment(repo, payload):
        calls.append("environment")
        raise RuntimeError("environment rejected")

    monkeypatch.setattr(MODULE, "apply_paid_research_environment", fail_environment)
    monkeypatch.setattr(
        MODULE, "apply_workflow_permissions", lambda *args: calls.append("permissions"))
    monkeypatch.setattr(MODULE, "apply_ruleset", lambda *args: calls.append("ruleset"))
    monkeypatch.setattr(MODULE.sys, "argv", [str(SCRIPT), "--apply"])

    assert MODULE.main() == 1
    assert calls == ["environment"]
    assert "environment rejected" in capsys.readouterr().err
