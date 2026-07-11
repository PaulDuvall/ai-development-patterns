#!/usr/bin/env python3
"""Configure repository controls required by evidence validation.

The command is a dry run unless ``--apply`` is supplied. Authentication and
repository discovery are delegated to the GitHub CLI so no credential is read
or persisted by this script.
"""

import argparse
import json
import subprocess
import sys


RULESET_NAME = "Protect main with adoption evidence validation"
REQUIRED_CHECK = "Trusted evidence checks"
GITHUB_ACTIONS_INTEGRATION_ID = 15368
OBSOLETE_ACTIONS_ENVIRONMENTS = ("evidence-paid-research",)
RETIRED_ACTIONS_SECRETS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "EVIDENCE_OPENAI_API_KEY",
    "EVIDENCE_ANTHROPIC_API_KEY",
    "VERIFY_PATTERNS_PAT",
    "VERIFY_PATTERNS_APP_PRIVATE_KEY",
    "CLAUDE_ASSISTANT_API_KEY",
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
                            "context": REQUIRED_CHECK,
                            "integration_id": GITHUB_ACTIONS_INTEGRATION_ID,
                        }
                    ],
                },
            },
            {"type": "non_fast_forward"},
        ],
    }


def workflow_permissions_payload():
    """Keep the default token read-only and forbid Actions-authored PR approval."""
    return {
        "default_workflow_permissions": "read",
        "can_approve_pull_request_reviews": False,
    }


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
    """Apply the Actions setting used by the scoped publisher-token fallback."""
    return gh_json(
        "api",
        "--method",
        "PUT",
        f"repos/{repo}/actions/permissions/workflow",
        "--input",
        "-",
        input_data=payload,
    )


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
        help="write controls and remove retired evaluator configuration",
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
                        "workflow_permissions": workflow_permissions,
                        "retired_actions_credentials": {
                            "secrets": list(RETIRED_ACTIONS_SECRETS),
                            "variables": list(RETIRED_ACTIONS_VARIABLES),
                        },
                        "obsolete_actions_environments": list(
                            OBSOLETE_ACTIONS_ENVIRONMENTS),
                    },
                    indent=2,
                )
            )
            print("Dry run only; pass --apply to update GitHub.")
            return 0
        removed_credentials = delete_retired_actions_credentials(repo)
        removed_environments = delete_obsolete_actions_environments(repo)
        apply_workflow_permissions(repo, workflow_permissions)
        result = apply_ruleset(repo, payload)
    except (OSError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Removed {sum(map(len, removed_credentials.values()))} retired evaluator "
        f"credential(s) and {len(removed_environments)} obsolete environment(s); "
        f"configured Actions permissions and ruleset {result['name']!r} "
        f"(id {result['id']}) for {repo}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
