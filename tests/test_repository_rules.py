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
    status_rule = next(
        rule for rule in payload["rules"]
        if rule["type"] == "required_status_checks")
    assert status_rule["parameters"]["required_status_checks"] == [
        {
            "context": MODULE.REQUIRED_CHECK,
            "integration_id": MODULE.GITHUB_ACTIONS_INTEGRATION_ID,
        }
    ]
    assert status_rule["parameters"][
        "strict_required_status_checks_policy"] is True


def test_ruleset_requires_pull_requests_and_blocks_force_pushes():
    rules = MODULE.ruleset_payload()["rules"]
    types = {rule["type"] for rule in rules}

    assert "pull_request" in types
    assert "non_fast_forward" in types
    pull_request = next(
        rule for rule in rules if rule["type"] == "pull_request")
    assert pull_request["parameters"][
        "required_review_thread_resolution"] is True
    assert pull_request["parameters"]["required_approving_review_count"] == 0


def test_workflow_token_defaults_to_read_and_cannot_publish_or_approve_prs():
    assert MODULE.workflow_permissions_payload() == {
        "default_workflow_permissions": "read",
        "can_approve_pull_request_reviews": False,
    }


def test_retired_configuration_covers_every_hosted_evaluator_credential():
    assert set(MODULE.RETIRED_ACTIONS_SECRETS) == {
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "EVIDENCE_OPENAI_API_KEY",
        "EVIDENCE_ANTHROPIC_API_KEY",
        "VERIFY_PATTERNS_PAT",
        "VERIFY_PATTERNS_APP_PRIVATE_KEY",
        "CLAUDE_ASSISTANT_API_KEY",
    }
    assert set(MODULE.RETIRED_ACTIONS_VARIABLES) == {
        "ANTHROPIC_FEDERATION_RULE_ID",
        "ANTHROPIC_ORGANIZATION_ID",
        "ANTHROPIC_SERVICE_ACCOUNT_ID",
        "ANTHROPIC_WORKSPACE_ID",
        "EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID",
        "EVIDENCE_ANTHROPIC_ORGANIZATION_ID",
        "EVIDENCE_ANTHROPIC_SERVICE_ACCOUNT_ID",
        "EVIDENCE_ANTHROPIC_WORKSPACE_ID",
        "OPENAI_EVIDENCE_MODEL",
        "ANTHROPIC_EVIDENCE_MODEL",
        "VERIFY_PATTERNS_APP_ID",
        "ENABLE_ANTHROPIC_ASSISTANT",
    }
    assert MODULE.OBSOLETE_ACTIONS_ENVIRONMENTS == (
        "evidence-paid-research",)

    # These belong to separate, optional GitHub integrations and must survive.
    assert {"CLAUDE_REVIEW_API_KEY"}.isdisjoint(
        MODULE.RETIRED_ACTIONS_SECRETS)
    assert {"ENABLE_ANTHROPIC_REVIEW"}.isdisjoint(
        MODULE.RETIRED_ACTIONS_VARIABLES)


def test_retired_evaluator_and_general_assistant_credentials_are_deleted(
        monkeypatch):
    calls = []

    def fake_gh_json(*args, input_data=None):
        calls.append(args)
        endpoint = args[-1]
        if endpoint.endswith("actions/secrets?per_page=100"):
            return {
                "secrets": [
                    {"name": "EVIDENCE_OPENAI_API_KEY"},
                    {"name": "VERIFY_PATTERNS_APP_PRIVATE_KEY"},
                    {"name": "CLAUDE_ASSISTANT_API_KEY"},
                    {"name": "CLAUDE_REVIEW_API_KEY"},
                ]
            }
        if endpoint.endswith("actions/variables?per_page=100"):
            return {
                "variables": [
                    {"name": "EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID"},
                    {"name": "OPENAI_EVIDENCE_MODEL"},
                    {"name": "ENABLE_ANTHROPIC_ASSISTANT"},
                ]
            }
        return None

    monkeypatch.setattr(MODULE, "gh_json", fake_gh_json)

    assert MODULE.delete_retired_actions_credentials("owner/repo") == {
        "secrets": [
            "EVIDENCE_OPENAI_API_KEY",
            "VERIFY_PATTERNS_APP_PRIVATE_KEY",
            "CLAUDE_ASSISTANT_API_KEY",
        ],
        "variables": [
            "EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID",
            "OPENAI_EVIDENCE_MODEL",
            "ENABLE_ANTHROPIC_ASSISTANT",
        ],
    }
    delete_endpoints = [call[-1] for call in calls if "DELETE" in call]
    assert delete_endpoints == [
        "repos/owner/repo/actions/secrets/EVIDENCE_OPENAI_API_KEY",
        "repos/owner/repo/actions/secrets/VERIFY_PATTERNS_APP_PRIVATE_KEY",
        "repos/owner/repo/actions/secrets/CLAUDE_ASSISTANT_API_KEY",
        "repos/owner/repo/actions/variables/EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID",
        "repos/owner/repo/actions/variables/OPENAI_EVIDENCE_MODEL",
        "repos/owner/repo/actions/variables/ENABLE_ANTHROPIC_ASSISTANT",
    ]
    assert all("CLAUDE_REVIEW" not in endpoint for endpoint in delete_endpoints)
    assert all("ENABLE_ANTHROPIC_REVIEW" not in endpoint for endpoint in delete_endpoints)


def test_obsolete_evaluator_environment_is_deleted_when_present(monkeypatch):
    calls = []

    def fake_gh_json(*args, input_data=None):
        calls.append(args)
        if args[-1].endswith("environments?per_page=100"):
            return {
                "environments": [
                    {"name": "github-pages"},
                    {"name": "evidence-paid-research"},
                ]
            }
        return None

    monkeypatch.setattr(MODULE, "gh_json", fake_gh_json)

    assert MODULE.delete_obsolete_actions_environments("owner/repo") == [
        "evidence-paid-research"]
    assert [call[-1] for call in calls if "DELETE" in call] == [
        "repos/owner/repo/environments/evidence-paid-research"]


def test_obsolete_evaluator_environment_cleanup_is_idempotent(monkeypatch):
    calls = []

    def fake_gh_json(*args, input_data=None):
        calls.append(args)
        return {"environments": [{"name": "github-pages"}]}

    monkeypatch.setattr(MODULE, "gh_json", fake_gh_json)

    assert MODULE.delete_obsolete_actions_environments("owner/repo") == []
    assert not any("DELETE" in call for call in calls)


def test_apply_retires_evaluator_state_before_repository_controls(
        monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(
        MODULE, "repository_name", lambda: "PaulDuvall/ai-development-patterns")
    monkeypatch.setattr(
        MODULE, "delete_retired_actions_credentials",
        lambda repo: calls.append(("credentials", repo, None)) or {
            "secrets": [], "variables": []})
    monkeypatch.setattr(
        MODULE, "delete_obsolete_actions_environments",
        lambda repo: calls.append(("environments", repo, None)) or [])
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
        "credentials", "environments", "permissions", "ruleset"]
    assert "configured Actions permissions and ruleset" in capsys.readouterr().out


def test_apply_fails_closed_when_retired_state_cleanup_fails(
        monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(
        MODULE, "repository_name", lambda: "PaulDuvall/ai-development-patterns")

    def fail_cleanup(repo):
        calls.append("credentials")
        raise RuntimeError("credential cleanup rejected")

    monkeypatch.setattr(MODULE, "delete_retired_actions_credentials", fail_cleanup)
    monkeypatch.setattr(
        MODULE, "delete_obsolete_actions_environments",
        lambda *args: calls.append("environments"))
    monkeypatch.setattr(
        MODULE, "apply_workflow_permissions",
        lambda *args: calls.append("permissions"))
    monkeypatch.setattr(
        MODULE, "apply_ruleset", lambda *args: calls.append("ruleset"))
    monkeypatch.setattr(MODULE.sys, "argv", [str(SCRIPT), "--apply"])

    assert MODULE.main() == 1
    assert calls == ["credentials"]
    assert "credential cleanup rejected" in capsys.readouterr().err


def test_dry_run_reports_every_retirement_without_writing(monkeypatch, capsys):
    monkeypatch.setattr(
        MODULE, "repository_name", lambda: "PaulDuvall/ai-development-patterns")
    monkeypatch.setattr(MODULE.sys, "argv", [str(SCRIPT)])

    assert MODULE.main() == 0
    output = capsys.readouterr().out
    assert "Dry run only" in output
    assert '"EVIDENCE_OPENAI_API_KEY"' in output
    assert '"EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID"' in output
    assert '"evidence-paid-research"' in output
