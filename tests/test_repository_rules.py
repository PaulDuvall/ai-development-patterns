"""Tests for the codified GitHub repository-rules configuration."""

import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parent.parent / "scripts" / "configure-repository-rules.py"
SPEC = importlib.util.spec_from_file_location("configure_repository_rules", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_ruleset_targets_default_branch_and_every_required_check():
    payload = MODULE.ruleset_payload()

    assert payload["enforcement"] == "active"
    assert payload["conditions"]["ref_name"]["include"] == ["~DEFAULT_BRANCH"]
    status_rule = next(
        rule for rule in payload["rules"]
        if rule["type"] == "required_status_checks")
    assert status_rule["parameters"]["required_status_checks"] == [
        {
            "context": context,
            "integration_id": MODULE.GITHUB_ACTIONS_INTEGRATION_ID,
        }
        for context in MODULE.REQUIRED_CHECKS
    ]
    assert MODULE.REQUIRED_CHECKS == (
        "Trusted evidence checks", "Validation gate", "Dependency Review")
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


def test_ruleset_protects_main_without_deadlocking_public_fork_prs():
    types = {rule["type"] for rule in MODULE.ruleset_payload()["rules"]}

    assert "deletion" in types
    assert "code_scanning" not in types


def test_workflow_token_defaults_to_read_and_cannot_publish_or_approve_prs():
    assert MODULE.workflow_permissions_payload() == {
        "default_workflow_permissions": "read",
        "can_approve_pull_request_reviews": False,
    }


def test_actions_policy_is_selected_sha_pinned_and_matches_trusted_allowlist():
    assert MODULE.ACTIONS_PERMISSIONS_PAYLOAD == {
        "enabled": True,
        "allowed_actions": "selected",
        "sha_pinning_required": True,
    }
    assert MODULE.SELECTED_ACTIONS_PAYLOAD == {
        "github_owned_allowed": False,
        "verified_allowed": False,
        "patterns_allowed": [
            *(f"{repository}@*" for repository in
              MODULE.APPROVED_EXTERNAL_ACTION_REPOSITORIES),
            "github/codeql-action@*",
        ],
    }
    assert MODULE.APPROVED_EXTERNAL_ACTION_REPOSITORIES == (
        "actions/checkout",
        "actions/configure-pages",
        "actions/dependency-review-action",
        "actions/deploy-pages",
        "actions/github-script",
        "actions/setup-node",
        "actions/setup-python",
        "actions/upload-artifact",
        "actions/upload-pages-artifact",
    )


def test_actions_policy_is_applied_and_verified(monkeypatch):
    calls = []

    def fake_gh_json(*args, input_data=None):
        calls.append((args, input_data))
        if input_data is None:
            return {
                **MODULE.ACTIONS_PERMISSIONS_PAYLOAD,
                "selected_actions_url": (
                    "https://api.github.com/repositories/42/actions/"
                    "permissions/selected-actions"),
            }
        return None

    monkeypatch.setattr(MODULE, "gh_json", fake_gh_json)

    retained = MODULE.apply_actions_permissions("owner/repo")

    assert retained["sha_pinning_required"] is True
    assert calls == [
        (
            (
                "api", "--method", "PUT",
                "repos/owner/repo/actions/permissions", "--input", "-",
            ),
            MODULE.ACTIONS_PERMISSIONS_PAYLOAD,
        ),
        (("api", "repos/owner/repo/actions/permissions"), None),
    ]


def test_actions_policy_fails_when_sha_pinning_is_not_retained(monkeypatch):
    monkeypatch.setattr(MODULE, "gh_json", lambda *args, input_data=None: (
        None if input_data is not None else {
            "enabled": True,
            "allowed_actions": "selected",
            "sha_pinning_required": False,
            "selected_actions_url": (
                "https://api.github.com/repositories/42/actions/permissions/"
                "selected-actions"),
        }
    ))

    with pytest.raises(RuntimeError, match="SHA-pinned"):
        MODULE.apply_actions_permissions("owner/repo")


def test_selected_actions_allowlist_is_applied_and_verified(monkeypatch):
    calls = []

    def fake_gh_json(*args, input_data=None):
        calls.append((args, input_data))
        if input_data is None:
            return {
                "github_owned_allowed": False,
                "verified_allowed": False,
                "patterns_allowed": list(
                    reversed(MODULE.SELECTED_ACTION_PATTERNS)),
            }
        return None

    monkeypatch.setattr(MODULE, "gh_json", fake_gh_json)

    MODULE.apply_selected_actions("owner/repo")

    assert calls == [
        (
            (
                "api", "--method", "PUT",
                "repos/owner/repo/actions/permissions/selected-actions",
                "--input", "-",
            ),
            MODULE.SELECTED_ACTIONS_PAYLOAD,
        ),
        (
            (
                "api",
                "repos/owner/repo/actions/permissions/selected-actions",
            ),
            None,
        ),
    ]


@pytest.mark.parametrize("retained_override", [
    {"github_owned_allowed": True},
    {"verified_allowed": True},
    {
        "patterns_allowed": [
            *MODULE.SELECTED_ACTION_PATTERNS,
            "unreviewed/action@*",
        ],
    },
])
def test_selected_actions_fails_when_policy_is_broader_than_exact_allowlist(
        monkeypatch, retained_override):
    monkeypatch.setattr(MODULE, "gh_json", lambda *args, input_data=None: (
        None if input_data is not None else {
            **MODULE.SELECTED_ACTIONS_PAYLOAD,
            **retained_override,
        }
    ))

    with pytest.raises(RuntimeError, match="exact selected-actions"):
        MODULE.apply_selected_actions("owner/repo")


def test_every_external_fork_workflow_requires_approval(monkeypatch):
    calls = []

    def fake_gh_json(*args, input_data=None):
        calls.append((args, input_data))
        if input_data is None:
            return {"approval_policy": "all_external_contributors"}
        return None

    monkeypatch.setattr(MODULE, "gh_json", fake_gh_json)

    MODULE.apply_fork_pr_approval_policy("owner/repo")

    assert calls[0][1] == {
        "approval_policy": "all_external_contributors"}
    assert calls[1] == (
        (
            "api",
            "repos/owner/repo/actions/permissions/"
            "fork-pr-contributor-approval",
        ),
        None,
    )


def test_workflow_token_permissions_are_applied_and_verified(monkeypatch):
    calls = []
    payload = MODULE.workflow_permissions_payload()

    def fake_gh_json(*args, input_data=None):
        calls.append((args, input_data))
        return payload if input_data is None else None

    monkeypatch.setattr(MODULE, "gh_json", fake_gh_json)

    MODULE.apply_workflow_permissions("owner/repo", payload)

    assert calls[0][1] == payload
    assert calls[1] == (
        ("api", "repos/owner/repo/actions/permissions/workflow"), None)


def test_github_models_is_a_fail_closed_manual_precondition():
    precondition = MODULE.github_models_manual_precondition("owner/repo")

    assert precondition["required_state"] == "disabled"
    assert precondition["verification"] == "manual_repository_settings_check"
    assert precondition["settings_url"] == (
        "https://github.com/owner/repo/settings/models")
    assert "no public REST or GraphQL" in precondition["reason"]
    with pytest.raises(RuntimeError, match="must be disabled manually"):
        MODULE.require_github_models_disabled_attestation(
            "owner/repo", attested=False)
    assert MODULE.require_github_models_disabled_attestation(
        "owner/repo", attested=True) is None


def test_retired_configuration_covers_every_hosted_evaluator_credential():
    assert set(MODULE.RETIRED_ACTIONS_SECRETS) == {
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "EVIDENCE_OPENAI_API_KEY",
        "EVIDENCE_ANTHROPIC_API_KEY",
        "VERIFY_PATTERNS_PAT",
        "VERIFY_PATTERNS_APP_PRIVATE_KEY",
        "CLAUDE_ASSISTANT_API_KEY",
        "CLAUDE_REVIEW_API_KEY",
        "CLAUDE_CODE_OAUTH_TOKEN",
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
        "ENABLE_ANTHROPIC_REVIEW",
    }
    assert MODULE.OBSOLETE_ACTIONS_ENVIRONMENTS == (
        "evidence-paid-research",)


def test_retired_evaluator_and_assistant_credentials_are_deleted(
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
                    {"name": "CLAUDE_CODE_OAUTH_TOKEN"},
                ]
            }
        if endpoint.endswith("actions/variables?per_page=100"):
            return {
                "variables": [
                    {"name": "EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID"},
                    {"name": "OPENAI_EVIDENCE_MODEL"},
                    {"name": "ENABLE_ANTHROPIC_ASSISTANT"},
                    {"name": "ENABLE_ANTHROPIC_REVIEW"},
                ]
            }
        return None

    monkeypatch.setattr(MODULE, "gh_json", fake_gh_json)

    assert MODULE.delete_retired_actions_credentials("owner/repo") == {
        "secrets": [
            "EVIDENCE_OPENAI_API_KEY",
            "VERIFY_PATTERNS_APP_PRIVATE_KEY",
            "CLAUDE_ASSISTANT_API_KEY",
            "CLAUDE_REVIEW_API_KEY",
            "CLAUDE_CODE_OAUTH_TOKEN",
        ],
        "variables": [
            "EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID",
            "OPENAI_EVIDENCE_MODEL",
            "ENABLE_ANTHROPIC_ASSISTANT",
            "ENABLE_ANTHROPIC_REVIEW",
        ],
    }
    delete_endpoints = [call[-1] for call in calls if "DELETE" in call]
    assert delete_endpoints == [
        "repos/owner/repo/actions/secrets/EVIDENCE_OPENAI_API_KEY",
        "repos/owner/repo/actions/secrets/VERIFY_PATTERNS_APP_PRIVATE_KEY",
        "repos/owner/repo/actions/secrets/CLAUDE_ASSISTANT_API_KEY",
        "repos/owner/repo/actions/secrets/CLAUDE_REVIEW_API_KEY",
        "repos/owner/repo/actions/secrets/CLAUDE_CODE_OAUTH_TOKEN",
        "repos/owner/repo/actions/variables/EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID",
        "repos/owner/repo/actions/variables/OPENAI_EVIDENCE_MODEL",
        "repos/owner/repo/actions/variables/ENABLE_ANTHROPIC_ASSISTANT",
        "repos/owner/repo/actions/variables/ENABLE_ANTHROPIC_REVIEW",
    ]


def test_security_configuration_enables_core_and_best_effort_controls(
        monkeypatch):
    calls = []

    def fake_gh_json(*args, input_data=None):
        calls.append((args, input_data))
        if input_data == {
            "security_and_analysis": {
                "secret_scanning_validity_checks": {"status": "enabled"},
            },
        }:
            raise RuntimeError("feature unavailable")
        if args[-1] == "repos/owner/repo" and input_data is None:
            return {
                "security_and_analysis": {
                    "secret_scanning": {"status": "enabled"},
                    "secret_scanning_push_protection": {"status": "enabled"},
                    "secret_scanning_non_provider_patterns": {
                        "status": "enabled"},
                    "secret_scanning_validity_checks": {"status": "disabled"},
                }
            }
        return {"ok": True}

    monkeypatch.setattr(MODULE, "gh_json", fake_gh_json)

    assert MODULE.apply_secret_protection("owner/repo") == {
        "secret_scanning_non_provider_patterns": True,
        "secret_scanning_validity_checks": False,
    }
    assert calls[0][1] == MODULE.SECRET_PROTECTION_PAYLOAD
    assert calls[1][1] == {
        "security_and_analysis": {
            "secret_scanning_non_provider_patterns": {"status": "enabled"},
        },
    }
    assert calls[2][1] == {
        "security_and_analysis": {
            "secret_scanning_validity_checks": {"status": "enabled"},
        },
    }
    assert calls[3] == (("api", "repos/owner/repo"), None)


def test_security_configuration_fails_when_github_does_not_retain_core(
        monkeypatch):
    def fake_gh_json(*args, input_data=None):
        if args[-1] == "repos/owner/repo" and input_data is None:
            return {
                "security_and_analysis": {
                    "secret_scanning": {"status": "enabled"},
                    "secret_scanning_push_protection": {"status": "disabled"},
                }
            }
        return {"ok": True}

    monkeypatch.setattr(MODULE, "gh_json", fake_gh_json)

    with pytest.raises(RuntimeError, match="did not retain required"):
        MODULE.apply_secret_protection("owner/repo")


def test_codeql_default_setup_uses_extended_relevant_language_suite(
        monkeypatch):
    calls = []
    monkeypatch.setattr(
        MODULE, "gh_json",
        lambda *args, input_data=None: (
            calls.append((args, input_data)) or {
                "state": "configured",
                "query_suite": "extended",
                "threat_model": "remote",
                "languages": [
                    "actions", "javascript", "javascript-typescript",
                    "python", "typescript"],
            }
        ))

    MODULE.apply_codeql_default_setup("owner/repo")

    assert calls == [
        (
            (
                "api", "--method", "PATCH",
                "repos/owner/repo/code-scanning/default-setup",
                "--input", "-",
            ),
            {
                "state": "configured",
                "query_suite": "extended",
                "threat_model": "remote",
                "languages": ["actions", "javascript-typescript", "python"],
            },
        )
    ]


def test_codeql_configuration_fails_when_github_does_not_retain_it(
        monkeypatch):
    monkeypatch.setattr(MODULE, "gh_json", lambda *args, **kwargs: {
        "state": "configured",
        "query_suite": "default",
        "threat_model": "remote",
        "languages": ["actions", "javascript-typescript", "python"],
    })

    with pytest.raises(RuntimeError, match="did not retain required CodeQL"):
        MODULE.apply_codeql_default_setup("owner/repo")


def test_codeql_configuration_fails_when_a_requested_language_is_missing(
        monkeypatch):
    monkeypatch.setattr(MODULE, "gh_json", lambda *args, **kwargs: {
        "state": "configured",
        "query_suite": "extended",
        "threat_model": "remote",
        "languages": ["javascript-typescript", "python"],
    })

    with pytest.raises(RuntimeError, match="did not retain required CodeQL"):
        MODULE.apply_codeql_default_setup("owner/repo")


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
        MODULE, "apply_actions_permissions",
        lambda repo: calls.append(("actions", repo, None)))
    monkeypatch.setattr(
        MODULE, "apply_selected_actions",
        lambda repo: calls.append(("selected-actions", repo, None)))
    monkeypatch.setattr(
        MODULE, "apply_fork_pr_approval_policy",
        lambda repo: calls.append(("fork-approval", repo, None)))
    monkeypatch.setattr(
        MODULE, "apply_workflow_permissions",
        lambda repo, payload: calls.append(("permissions", repo, payload)))
    monkeypatch.setattr(
        MODULE, "apply_secret_protection",
        lambda repo: calls.append(("secret-protection", repo, None)) or {
            "secret_scanning_non_provider_patterns": True,
            "secret_scanning_validity_checks": True,
        })
    monkeypatch.setattr(
        MODULE, "apply_codeql_default_setup",
        lambda repo: calls.append(("codeql", repo, None)))
    monkeypatch.setattr(
        MODULE, "apply_ruleset",
        lambda repo, payload: (
            calls.append(("ruleset", repo, payload)) or
            {"name": MODULE.RULESET_NAME, "id": 18778612}
        ))
    monkeypatch.setattr(
        MODULE.sys,
        "argv",
        [str(SCRIPT), "--apply", "--attest-github-models-disabled"],
    )

    assert MODULE.main() == 0
    assert [call[0] for call in calls] == [
        "credentials", "environments", "actions", "selected-actions",
        "fork-approval", "permissions", "secret-protection", "codeql",
        "ruleset"]
    assert "secret protection, CodeQL" in capsys.readouterr().out


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
        MODULE, "apply_actions_permissions",
        lambda *args: calls.append("actions"))
    monkeypatch.setattr(
        MODULE, "apply_selected_actions",
        lambda *args: calls.append("selected-actions"))
    monkeypatch.setattr(
        MODULE, "apply_fork_pr_approval_policy",
        lambda *args: calls.append("fork-approval"))
    monkeypatch.setattr(
        MODULE, "apply_workflow_permissions",
        lambda *args: calls.append("permissions"))
    monkeypatch.setattr(
        MODULE, "apply_secret_protection",
        lambda *args: calls.append("secret-protection"))
    monkeypatch.setattr(
        MODULE, "apply_codeql_default_setup",
        lambda *args: calls.append("codeql"))
    monkeypatch.setattr(
        MODULE, "apply_ruleset", lambda *args: calls.append("ruleset"))
    monkeypatch.setattr(
        MODULE.sys,
        "argv",
        [str(SCRIPT), "--apply", "--attest-github-models-disabled"],
    )

    assert MODULE.main() == 1
    assert calls == ["credentials"]
    assert "credential cleanup rejected" in capsys.readouterr().err


def test_apply_stops_before_writes_without_models_attestation(
        monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(
        MODULE, "repository_name", lambda: "PaulDuvall/ai-development-patterns")
    monkeypatch.setattr(
        MODULE, "delete_retired_actions_credentials",
        lambda *args: calls.append("write"))
    monkeypatch.setattr(MODULE.sys, "argv", [str(SCRIPT), "--apply"])

    assert MODULE.main() == 1
    assert calls == []
    error = capsys.readouterr().err
    assert "settings/models" in error
    assert "--attest-github-models-disabled" in error


def test_dry_run_reports_safe_summaries_without_credential_names(
        monkeypatch, capsys):
    monkeypatch.setattr(
        MODULE, "repository_name", lambda: "PaulDuvall/ai-development-patterns")
    monkeypatch.setattr(MODULE.sys, "argv", [str(SCRIPT)])

    assert MODULE.main() == 0
    output = capsys.readouterr().out
    assert "Dry run only" in output
    assert f'"secret_count": {len(MODULE.RETIRED_ACTIONS_SECRETS)}' in output
    assert f'"variable_count": {len(MODULE.RETIRED_ACTIONS_VARIABLES)}' in output
    assert all(name not in output for name in MODULE.RETIRED_ACTIONS_SECRETS)
    assert all(
        setting not in output
        for setting in MODULE.SECRET_PROTECTION_PAYLOAD["security_and_analysis"]
    )
    assert all(name not in output for name in MODULE.RETIRED_ACTIONS_VARIABLES)
    assert '"evidence-paid-research"' in output
    assert '"query_suite": "extended"' in output
    assert '"threat_model": "remote"' in output
    assert '"allowed_actions": "selected"' in output
    assert '"sha_pinning_required": true' in output
    assert '"approval_policy": "all_external_contributors"' in output
    assert '"verified_allowed": false' in output
    assert '"required_state": "disabled"' in output
