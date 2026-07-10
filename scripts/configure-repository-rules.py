#!/usr/bin/env python3
"""Configure repository controls required by evidence automation.

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
    """Keep the default token read-only while allowing the publisher to open PRs."""
    return {
        "default_workflow_permissions": "read",
        "can_approve_pull_request_reviews": True,
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the ruleset to GitHub")
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
                    },
                    indent=2,
                )
            )
            print("Dry run only; pass --apply to update GitHub.")
            return 0
        apply_workflow_permissions(repo, workflow_permissions)
        result = apply_ruleset(repo, payload)
    except (OSError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Configured Actions publisher permission and ruleset {result['name']!r} "
        f"(id {result['id']}) for {repo}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
