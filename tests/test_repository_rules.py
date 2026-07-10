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
