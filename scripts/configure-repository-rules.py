#!/usr/bin/env python3
"""Configure repository validation and security controls.

The command is a dry run unless ``--apply`` is supplied. Authentication and
repository discovery are delegated to the GitHub CLI so no credential is read
or persisted by this script.
"""

import argparse
import json
import subprocess
import sys


RULESET_NAME = "Protect main with adoption evidence validation"
REQUIRED_CHECKS = (
    "Trusted evidence checks",
    "Validation gate",
    "Dependency Review",
)
GITHUB_ACTIONS_INTEGRATION_ID = 15368
APPROVED_EXTERNAL_ACTION_REPOSITORIES = (
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
CODEQL_DEFAULT_SETUP_ACTION_REPOSITORY = "github/codeql-action"
SELECTED_ACTION_PATTERNS = tuple(
    f"{repository}@*"
    for repository in (
        *APPROVED_EXTERNAL_ACTION_REPOSITORIES,
        CODEQL_DEFAULT_SETUP_ACTION_REPOSITORY,
    )
)
ACTIONS_PERMISSIONS_PAYLOAD = {
    "enabled": True,
    "allowed_actions": "selected",
    "sha_pinning_required": True,
}
SELECTED_ACTIONS_PAYLOAD = {
    "github_owned_allowed": False,
    "verified_allowed": False,
    "patterns_allowed": list(SELECTED_ACTION_PATTERNS),
}
FORK_PR_APPROVAL_PAYLOAD = {
    "approval_policy": "all_external_contributors",
}
GITHUB_MODELS_DOCUMENTATION_URL = (
    "https://docs.github.com/en/repositories/managing-your-repositorys-settings-"
    "and-features/managing-repository-settings/managing-github-models-in-your-"
    "repository"
)
SECRET_PROTECTION_PAYLOAD = {
    "security_and_analysis": {
        "secret_scanning": {"status": "enabled"},
        "secret_scanning_push_protection": {"status": "enabled"},
    },
}
BEST_EFFORT_SECRET_PROTECTION = (
    "secret_scanning_non_provider_patterns",
    "secret_scanning_validity_checks",
)
REQUIRED_SECRET_PROTECTION = (
    "secret_scanning",
    "secret_scanning_push_protection",
)
CODEQL_DEFAULT_SETUP_PAYLOAD = {
    "state": "configured",
    "query_suite": "extended",
    "threat_model": "remote",
    "languages": ["actions", "javascript-typescript", "python"],
}
OBSOLETE_ACTIONS_ENVIRONMENTS = ("evidence-paid-research",)
RETIRED_ACTIONS_SECRETS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "EVIDENCE_OPENAI_API_KEY",
    "EVIDENCE_ANTHROPIC_API_KEY",
    "VERIFY_PATTERNS_PAT",
    "VERIFY_PATTERNS_APP_PRIVATE_KEY",
    "CLAUDE_ASSISTANT_API_KEY",
    "CLAUDE_REVIEW_API_KEY",
    "CLAUDE_CODE_OAUTH_TOKEN",
)
RETIRED_ACTIONS_VARIABLES = (
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
)


def gh_json(*args, input_data=None):
    """Run ``gh`` and decode its JSON response."""
    command = ["gh", *args]
    result = subprocess.run(
        command,
        input=json.dumps(input_data) if input_data is not None else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "gh command failed")
    return json.loads(result.stdout) if result.stdout.strip() else None


def repository_name():
    """Return the authenticated checkout's ``owner/name``."""
    data = gh_json("repo", "view", "--json", "nameWithOwner")
    return data["nameWithOwner"]


def ruleset_payload():
    """Return the complete idempotent repository-rules definition."""
    return {
        "name": RULESET_NAME,
        "target": "branch",
        "enforcement": "active",
        "conditions": {
            "ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []},
        },
        "rules": [
            {
                "type": "pull_request",
                "parameters": {
                    "allowed_merge_methods": ["merge", "squash", "rebase"],
                    "dismiss_stale_reviews_on_push": False,
                    "require_code_owner_review": False,
                    "require_last_push_approval": False,
                    "required_approving_review_count": 0,
                    "required_review_thread_resolution": True,
                },
            },
            {
                "type": "required_status_checks",
                "parameters": {
                    "do_not_enforce_on_create": True,
                    "strict_required_status_checks_policy": True,
                    "required_status_checks": [
                        {
                            "context": context,
                            "integration_id": GITHUB_ACTIONS_INTEGRATION_ID,
                        }
                        for context in REQUIRED_CHECKS
                    ],
                },
            },
            # Default CodeQL setup excludes fork pull requests. A native
            # code_scanning merge rule would deadlock public fork
            # contributions that cannot produce analysis for their revision.
            {"type": "deletion"},
            {"type": "non_fast_forward"},
        ],
    }


def workflow_permissions_payload():
    """Keep the default token read-only and forbid Actions-authored PR approval."""
    return {
        "default_workflow_permissions": "read",
        "can_approve_pull_request_reviews": False,
    }


def github_models_manual_precondition(repo):
    """Describe the fail-closed manual control for the preview Models feature."""
    return {
        "required_state": "disabled",
        "verification": "manual_repository_settings_check",
        "settings_url": f"https://github.com/{repo}/settings/models",
        "documentation_url": GITHUB_MODELS_DOCUMENTATION_URL,
        "apply_attestation_flag": "--attest-github-models-disabled",
        "reason": (
            "GitHub documents only a repository Settings UI control; no public "
            "REST or GraphQL repository-setting endpoint is available"
        ),
    }


def require_github_models_disabled_attestation(repo, attested):
    """Stop before writes unless an administrator checked the documented UI."""
    if attested:
        return
    precondition = github_models_manual_precondition(repo)
    raise RuntimeError(
        "GitHub Models must be disabled manually at "
        f"{precondition['settings_url']} before apply; then rerun with "
        f"{precondition['apply_attestation_flag']}"
    )


def find_existing(repo):
    """Return the matching ruleset, if one is already configured."""
    rulesets = gh_json("api", f"repos/{repo}/rulesets") or []
    return next((item for item in rulesets if item.get("name") == RULESET_NAME), None)


def apply_ruleset(repo, payload):
    """Create or replace the named ruleset and return GitHub's response."""
    existing = find_existing(repo)
    if existing:
        endpoint = f"repos/{repo}/rulesets/{existing['id']}"
        method = "PUT"
    else:
        endpoint = f"repos/{repo}/rulesets"
        method = "POST"
    return gh_json("api", "--method", method, endpoint, "--input", "-", input_data=payload)


def apply_workflow_permissions(repo, payload):
    """Apply and verify least-privilege default Actions token settings."""
    gh_json(
        "api",
        "--method",
        "PUT",
        f"repos/{repo}/actions/permissions/workflow",
        "--input",
        "-",
        input_data=payload,
    )
    retained = gh_json(
        "api", f"repos/{repo}/actions/permissions/workflow") or {}
    if any(retained.get(key) != value for key, value in payload.items()):
        raise RuntimeError(
            "GitHub did not retain required workflow token permissions")
    return retained


def apply_actions_permissions(repo):
    """Enable Actions with selected-only, commit-SHA-pinned execution."""
    endpoint = f"repos/{repo}/actions/permissions"
    gh_json(
        "api", "--method", "PUT", endpoint, "--input", "-",
        input_data=ACTIONS_PERMISSIONS_PAYLOAD,
    )
    retained = gh_json("api", endpoint) or {}
    expected = ACTIONS_PERMISSIONS_PAYLOAD
    selected_url = retained.get("selected_actions_url")
    if any(retained.get(key) != value for key, value in expected.items()) \
            or not isinstance(selected_url, str) \
            or not selected_url.endswith(
                "/actions/permissions/selected-actions"):
        raise RuntimeError(
            "GitHub did not retain selected-only SHA-pinned Actions permissions")
    return retained


def apply_selected_actions(repo):
    """Apply and verify the exact base-owned external-action allowlist."""
    endpoint = f"repos/{repo}/actions/permissions/selected-actions"
    gh_json(
        "api", "--method", "PUT", endpoint, "--input", "-",
        input_data=SELECTED_ACTIONS_PAYLOAD,
    )
    retained = gh_json("api", endpoint) or {}
    retained_patterns = retained.get("patterns_allowed")
    exact_patterns = (
        isinstance(retained_patterns, list)
        and len(retained_patterns) == len(SELECTED_ACTION_PATTERNS)
        and set(retained_patterns) == set(SELECTED_ACTION_PATTERNS)
    )
    if retained.get("github_owned_allowed") is not False \
            or retained.get("verified_allowed") is not False \
            or not exact_patterns:
        raise RuntimeError(
            "GitHub did not retain the exact selected-actions allowlist")
    return retained


def apply_fork_pr_approval_policy(repo):
    """Require maintainer approval for every external fork workflow run."""
    endpoint = (
        f"repos/{repo}/actions/permissions/fork-pr-contributor-approval")
    gh_json(
        "api", "--method", "PUT", endpoint, "--input", "-",
        input_data=FORK_PR_APPROVAL_PAYLOAD,
    )
    retained = gh_json("api", endpoint) or {}
    if retained.get("approval_policy") != "all_external_contributors":
        raise RuntimeError(
            "GitHub did not retain all-external-contributors fork approval")
    return retained


def apply_secret_protection(repo):
    """Enable secret protection and verify the state GitHub actually retained."""
    gh_json(
        "api",
        "--method",
        "PATCH",
        f"repos/{repo}",
        "--input",
        "-",
        input_data=SECRET_PROTECTION_PAYLOAD,
    )
    attempted = {}
    for setting in BEST_EFFORT_SECRET_PROTECTION:
        try:
            gh_json(
                "api",
                "--method",
                "PATCH",
                f"repos/{repo}",
                "--input",
                "-",
                input_data={
                    "security_and_analysis": {
                        setting: {"status": "enabled"},
                    },
                },
            )
        except RuntimeError:
            # Availability varies by repository visibility and GitHub rollout.
            attempted[setting] = False
        else:
            attempted[setting] = True

    repository = gh_json("api", f"repos/{repo}") or {}
    retained = repository.get("security_and_analysis") or {}
    missing_required = [
        setting for setting in REQUIRED_SECRET_PROTECTION
        if (retained.get(setting) or {}).get("status") != "enabled"
    ]
    if missing_required:
        raise RuntimeError(
            "GitHub did not retain required secret-protection controls")
    return {
        setting: attempted.get(setting, False)
        and (retained.get(setting) or {}).get("status") == "enabled"
        for setting in BEST_EFFORT_SECRET_PROTECTION
    }


def apply_codeql_default_setup(repo):
    """Configure CodeQL default setup and verify GitHub retained core settings."""
    result = gh_json(
        "api",
        "--method",
        "PATCH",
        f"repos/{repo}/code-scanning/default-setup",
        "--input",
        "-",
        input_data=CODEQL_DEFAULT_SETUP_PAYLOAD,
    )
    expected = {
        key: CODEQL_DEFAULT_SETUP_PAYLOAD[key]
        for key in ("state", "query_suite", "threat_model")
    }
    requested_languages = set(CODEQL_DEFAULT_SETUP_PAYLOAD["languages"])
    retained_languages = result.get("languages") if isinstance(result, dict) else None
    if not isinstance(result, dict) or any(
            result.get(key) != value for key, value in expected.items()) \
            or not isinstance(retained_languages, list) \
            or not requested_languages.issubset(retained_languages):
        raise RuntimeError("GitHub did not retain required CodeQL default setup")
    return result


def delete_retired_actions_credentials(repo):
    """Remove generic credentials that historical workflow definitions can read."""
    secret_data = gh_json(
        "api", f"repos/{repo}/actions/secrets?per_page=100") or {}
    variable_data = gh_json(
        "api", f"repos/{repo}/actions/variables?per_page=100") or {}
    configured_secrets = {
        item["name"] for item in secret_data.get("secrets", [])}
    configured_variables = {
        item["name"] for item in variable_data.get("variables", [])}
    removed = {"secrets": [], "variables": []}

    for name in RETIRED_ACTIONS_SECRETS:
        if name not in configured_secrets:
            continue
        gh_json(
            "api", "--method", "DELETE",
            f"repos/{repo}/actions/secrets/{name}")
        removed["secrets"].append(name)

    for name in RETIRED_ACTIONS_VARIABLES:
        if name not in configured_variables:
            continue
        gh_json(
            "api", "--method", "DELETE",
            f"repos/{repo}/actions/variables/{name}")
        removed["variables"].append(name)

    return removed


def delete_obsolete_actions_environments(repo):
    """Remove environments used only by the retired hosted evaluator."""
    environment_data = gh_json(
        "api", f"repos/{repo}/environments?per_page=100") or {}
    configured = {
        item["name"] for item in environment_data.get("environments", [])}
    removed = []

    for name in OBSOLETE_ACTIONS_ENVIRONMENTS:
        if name not in configured:
            continue
        gh_json(
            "api", "--method", "DELETE",
            f"repos/{repo}/environments/{name}")
        removed.append(name)

    return removed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write controls and remove retired automation configuration",
    )
    parser.add_argument(
        "--attest-github-models-disabled",
        action="store_true",
        help=(
            "attest that an administrator verified GitHub Models is disabled "
            "in repository Settings (required with --apply)"
        ),
    )
    args = parser.parse_args()

    try:
        repo = repository_name()
        payload = ruleset_payload()
        workflow_permissions = workflow_permissions_payload()
        if not args.apply:
            print(
                json.dumps(
                    {
                        "repository": repo,
                        "ruleset": payload,
                        "actions_permissions": ACTIONS_PERMISSIONS_PAYLOAD,
                        "selected_actions": SELECTED_ACTIONS_PAYLOAD,
                        "fork_pr_contributor_approval": FORK_PR_APPROVAL_PAYLOAD,
                        "workflow_permissions": workflow_permissions,
                        "github_models": github_models_manual_precondition(repo),
                        "retired_actions_credentials": {
                            "secret_count": len(RETIRED_ACTIONS_SECRETS),
                            "variable_count": len(RETIRED_ACTIONS_VARIABLES),
                        },
                        "obsolete_actions_environments": list(
                            OBSOLETE_ACTIONS_ENVIRONMENTS),
                        "secret_protection": {
                            "required_control_count": len(
                                REQUIRED_SECRET_PROTECTION),
                            "best_effort_control_count": len(
                                BEST_EFFORT_SECRET_PROTECTION),
                        },
                        "codeql_default_setup": CODEQL_DEFAULT_SETUP_PAYLOAD,
                    },
                    indent=2,
                )
            )
            print("Dry run only; pass --apply to update GitHub.")
            return 0
        require_github_models_disabled_attestation(
            repo, args.attest_github_models_disabled)
        removed_credentials = delete_retired_actions_credentials(repo)
        removed_environments = delete_obsolete_actions_environments(repo)
        apply_actions_permissions(repo)
        apply_selected_actions(repo)
        apply_fork_pr_approval_policy(repo)
        apply_workflow_permissions(repo, workflow_permissions)
        optional_secret_controls = apply_secret_protection(repo)
        apply_codeql_default_setup(repo)
        result = apply_ruleset(repo, payload)
    except (OSError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Removed {sum(map(len, removed_credentials.values()))} retired evaluator "
        f"credential(s) and {len(removed_environments)} obsolete environment(s); "
        f"configured selected SHA-pinned Actions, external-fork approval, "
        f"token permissions, secret protection, CodeQL, and "
        f"ruleset {result['name']!r} "
        f"(id {result['id']}) for {repo}"
    )
    unavailable_count = sum(
        not enabled for enabled in optional_secret_controls.values())
    if unavailable_count:
        print(
            f"{unavailable_count} optional secret-protection control(s) were "
            "unavailable; core scanning and push protection remain enabled."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
