"""Structural regression tests for evidence workflow trust boundaries."""

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
VERIFY = WORKFLOWS / "verify-patterns.yml"
TRUSTED = WORKFLOWS / "trusted-evidence-validation.yml"
EVIDENCE = WORKFLOWS / "evidence-validation.yml"
PATTERN_VALIDATION = WORKFLOWS / "pattern-validation.yml"
PAGES = WORKFLOWS / "deploy-pages.yml"


def workflow_paths():
    """Return every filename extension GitHub recognizes as a workflow."""
    return sorted({*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")})


def load_workflow(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def named_step(job, name):
    return next(step for step in job["steps"] if step.get("name") == name)


def test_every_external_action_is_pinned_to_a_commit_sha():
    unpinned = []
    for path in workflow_paths():
        for line_number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1):
            match = re.search(r"\buses:\s*([^\s#]+)", line)
            if not match or match.group(1).startswith(("./", "docker://")):
                continue
            reference = match.group(1).rsplit("@", 1)[-1]
            if re.fullmatch(r"[0-9a-f]{40}", reference) is None:
                unpinned.append(
                    f"{path.name}:{line_number}: {match.group(1)}")
    assert not unpinned, "unpinned Actions:\n" + "\n".join(unpinned)


def test_model_backed_pattern_evaluation_is_local_only():
    assert not VERIFY.exists()

    workflow_text = {
        path.name: path.read_text(encoding="utf-8")
        for path in workflow_paths()
    }
    combined = "\n".join(workflow_text.values())
    forbidden = (
        "openai/codex-action@",
        "@openai/codex@",
        "codex exec",
        "codex sandbox",
        "EVIDENCE_OPENAI_API_KEY",
        "EVIDENCE_ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "VERIFY_PATTERNS_PAT",
        "VERIFY_PATTERNS_APP_PRIVATE_KEY",
        "CLAUDE_ASSISTANT_API_KEY",
        "CLAUDE_REVIEW_API_KEY",
        "CLAUDE_CODE_OAUTH_TOKEN",
        "OPENAI_EVIDENCE_MODEL",
        "ANTHROPIC_EVIDENCE_MODEL",
        "ANTHROPIC_FEDERATION_RULE_ID",
        "ANTHROPIC_ORGANIZATION_ID",
        "ANTHROPIC_SERVICE_ACCOUNT_ID",
        "ANTHROPIC_WORKSPACE_ID",
        "VERIFY_PATTERNS_APP_ID",
        "ENABLE_ANTHROPIC_ASSISTANT",
        "ENABLE_ANTHROPIC_REVIEW",
        "EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID",
        "evidence-paid-research",
        ".github/codex/evidence-research.toml",
        ".claude/commands/verify-patterns.md",
        "scripts/check-provider-preflight.py",
        "scripts/check-claude-execution.py",
        "scripts/check-research-workspace.py",
    )
    for marker in forbidden:
        assert marker not in combined

    anthropic_action_files = {
        name for name, text in workflow_text.items()
        if "anthropics/claude-code-action@" in text
    }
    assert not anthropic_action_files
    assert not (WORKFLOWS / "claude-code-review.yml").exists()
    assert not (WORKFLOWS / "claude.yml").exists()


def test_deterministic_evidence_workflow_has_no_model_credentials_or_actions():
    text = EVIDENCE.read_text(encoding="utf-8")
    workflow = load_workflow(EVIDENCE)
    jobs_text = str(workflow["jobs"]).casefold()

    assert "${{ secrets." not in text
    assert "${{ vars." not in text
    assert "openai" not in jobs_text
    assert "anthropic" not in jobs_text
    assert "codex" not in jobs_text
    assert "git push" not in text
    assert "gh pr create" not in text
    assert "environment:" not in text
    assert "codex-permission-profile" not in workflow["jobs"]


def test_weekly_actions_only_recompute_and_recheck_committed_evidence():
    workflow = load_workflow(EVIDENCE)
    assert workflow["on"]["schedule"] == [{"cron": "0 6 * * 1"}]
    assert workflow["permissions"] == {"contents": "read"}
    assert set(workflow["jobs"]) == {
        "deterministic-evidence",
        "evidence-links",
        "reconcile-evidence-gaps",
        "notify-failure",
        "close-resolved-failures",
    }

    deterministic = workflow["jobs"]["deterministic-evidence"]
    recompute = named_step(deterministic, "Recompute adoption verdicts")["run"]
    freshness = named_step(
        deterministic, "Enforce 90-day freshness on the weekly run")
    status = named_step(deterministic, "Check generated status")["run"]
    assert "scripts/validate-evidence.py" in recompute
    assert freshness["if"] == "github.event_name == 'schedule'"
    assert "scripts/validate-evidence.py" in freshness["run"]
    assert "--max-age-days 90" in freshness["run"]
    assert status == "python3 scripts/generate-verification-status.py --check"

    links = workflow["jobs"]["evidence-links"]
    assert "github.event_name == 'schedule'" in links["if"]
    assert "inputs.check_links" in links["if"]
    recheck = named_step(links, "Re-fetch evidence URLs")["run"]
    assert "tests/test_evidence_files.py" in recheck
    assert "tests/test_evidence_content.py" in recheck
    assert "-m slow" in recheck


def test_local_evaluator_inputs_are_watched_but_never_executed_by_actions():
    workflow = load_workflow(EVIDENCE)
    watched = set(workflow["on"]["push"]["paths"])
    assert {
        ".agents/skills/evaluate-pattern-adoption/**",
        ".codex/agents/**",
        ".codex/config.toml",
        "verification/local-runs/**",
        "scripts/local_verification.py",
        "scripts/plan-local-verification.py",
        "scripts/record-local-search-event.py",
        "scripts/finalize-local-verification.py",
        "tests/test_local_research_scope.py",
        "tests/test_local_verification.py",
    } <= watched

    jobs_text = str(workflow["jobs"])
    assert "plan-local-verification.py" not in jobs_text
    assert "record-local-search-event.py" not in jobs_text
    assert "finalize-local-verification.py" not in jobs_text
    assert "evaluate-pattern-adoption" not in jobs_text


def test_no_workflow_can_restore_a_legacy_shared_provider_secret():
    workflow_text = "\n".join(
        path.read_text(encoding="utf-8") for path in workflow_paths())
    assert "secrets.OPENAI_API_KEY" not in workflow_text
    assert "secrets.ANTHROPIC_API_KEY" not in workflow_text


def test_trusted_pr_workflow_executes_only_base_branch_validation_code():
    workflow = load_workflow(TRUSTED)
    assert "pull_request_target" in workflow["on"]
    assert "workflow_dispatch" not in workflow["on"]
    assert workflow["permissions"] == {}
    job = workflow["jobs"]["trusted-evidence"]
    assert job["if"] == "github.event_name == 'pull_request_target'"
    assert job["permissions"] == {
        "contents": "read",
        "issues": "read",
        "pull-requests": "read",
        "statuses": "write",
    }
    base_checkout = named_step(job, "Checkout trusted base")
    candidate_checkout = named_step(job, "Checkout candidate as inert data")
    assert base_checkout["with"]["ref"] == (
        "${{ github.event.pull_request.base.sha }}")
    assert candidate_checkout["with"]["repository"] == (
        "${{ github.event.pull_request.head.repo.full_name }}")
    assert candidate_checkout["with"]["ref"] == (
        "${{ github.event.pull_request.head.sha }}")
    assert candidate_checkout["with"]["allow-unsafe-pr-checkout"] == "true"
    assert "allow-unsafe-pr-checkout" not in base_checkout["with"]
    assert TRUSTED.read_text(encoding="utf-8").count(
        "allow-unsafe-pr-checkout: true") == 1
    commands = "\n".join(str(step.get("run", "")) for step in job["steps"])
    policy = named_step(
        job, "Enforce candidate workflow policy with trusted code")
    assert policy["id"] == "workflow-policy"
    assert policy["if"] == "steps.resolve.outputs.eligible == 'true'"
    assert policy["env"]["TRUST_ROOT_APPROVED"] == (
        "${{ steps.resolve.outputs.trust_root_approved }}")
    assert "python3 trusted/scripts/validate-workflow-policy.py" in policy["run"]
    assert "--trusted-root trusted" in policy["run"]
    assert "--candidate-root candidate" in policy["run"]
    assert "upgrade_args+=(--allow-trust-root-upgrade)" in policy["run"]
    assert 'if [ "$TRUST_ROOT_APPROVED" = true ]' in policy["run"]
    assert '"${upgrade_args[@]}"' in policy["run"]
    assert "candidate/.github/workflows" in policy["run"]
    step_names = [step["name"] for step in job["steps"]]
    assert step_names.index(
        "Install minimal trusted workflow-policy dependency") < (
            step_names.index(
                "Enforce candidate workflow policy with trusted code"))
    assert step_names.index(
        "Enforce candidate workflow policy with trusted code") < (
            step_names.index("Install trusted validation dependencies"))
    assert "trusted/scripts/validate-evidence.py" in commands
    assert "trusted/scripts/generate-verification-status.py" in commands
    assert "trusted/scripts/validate-workflow-policy.py" in commands
    assert "candidate/scripts/" not in commands
    assert "candidate/tests/" not in commands
    assert 'context="Trusted evidence checks"' in commands
    publish = named_step(
        job, "Publish trusted result on the candidate revision")
    assert publish["env"]["HEAD_SHA"] == (
        "${{ github.event.pull_request.head.sha }}")
    assert "steps.resolve.outputs.head_sha" not in str(job)
    assert "steps.resolve.outputs.head_repo" not in str(job)
    assert "steps.resolve.outputs.base_sha" not in str(job)
    assert "steps.resolve.outcome == 'failure'" in publish["if"]
    assert "steps.resolve.outputs.eligible == 'true'" in publish["if"]
    assert "steps.resolve.outcome != 'success'" in publish["env"]["FAILED"]
    assert "steps.workflow-policy.outcome != 'success'" in publish["env"][
        "FAILED"]
    assert "steps.install-policy.outcome != 'success'" in publish["env"][
        "FAILED"]
    status = named_step(job, "Recompute candidate status with trusted generator")
    assert "trusted/scripts/generate-verification-status.py --root candidate" in status["run"]
    assert 'marker = "\\n## How to refresh\\n"' in status["run"]
    assert "submitted_derived != recomputed_derived" in status["run"]
    assert "candidate/scripts/generate-verification-status.py" not in status["run"]


def test_trusted_pr_workflow_no_ops_when_pr_is_no_longer_eligible():
    workflow = load_workflow(TRUSTED)
    trigger_types = workflow["on"]["pull_request_target"]["types"]
    job = workflow["jobs"]["trusted-evidence"]
    resolve = named_step(job, "Resolve immutable pull request revisions")

    assert trigger_types == [
        "opened", "synchronize", "reopened", "ready_for_review", "edited"]
    assert 'eligible=false' in resolve["run"]
    assert 'echo "eligible=$eligible"' in resolve["run"]
    assert "successful no-op" in resolve["run"]

    for step in job["steps"]:
        if step["name"] == "Resolve immutable pull request revisions":
            continue
        assert "steps.resolve.outputs.eligible == 'true'" in step["if"]


def test_trust_root_upgrade_requires_exact_commit_bound_owner_comment():
    workflow = load_workflow(TRUSTED)
    validation = workflow["jobs"]["trusted-evidence"]
    resolve = named_step(validation, "Resolve immutable pull request revisions")
    rerun = workflow["jobs"]["rerun-trust-root-validation"]
    rerun_step = named_step(
        rerun, "Rerun completed validation for the current pull request head")

    assert workflow["on"]["issue_comment"]["types"] == [
        "created", "edited", "deleted"]
    assert "github.event_name" in workflow["concurrency"]["group"]
    assert "github.event.issue.number" in workflow["concurrency"]["group"]
    assert resolve["env"] == {
        "GH_TOKEN": "${{ github.token }}",
        "EVENT_PR_NUMBER": "${{ github.event.pull_request.number }}",
        "EVENT_HEAD_SHA": "${{ github.event.pull_request.head.sha }}",
        "EVENT_HEAD_REPO": (
            "${{ github.event.pull_request.head.repo.full_name }}"),
        "EVENT_BASE_SHA": "${{ github.event.pull_request.base.sha }}",
        "EVENT_BASE_REF": "${{ github.event.pull_request.base.ref }}",
    }
    assert '[ "$current_head_sha" = "$EVENT_HEAD_SHA" ]' in resolve["run"]
    assert '[ "$current_head_repo" = "$EVENT_HEAD_REPO" ]' in resolve["run"]
    assert '[ "$current_base_sha" = "$EVENT_BASE_SHA" ]' in resolve["run"]
    assert '[ "$current_base_ref" = "$EVENT_BASE_REF" ]' in resolve["run"]
    assert 'expected="APPROVE TRUST ROOT ${EVENT_HEAD_SHA}"' in resolve["run"]
    assert "gh api --paginate --slurp" in resolve["run"]
    assert '.body == $expected' in resolve["run"]
    assert '.author_association == "OWNER"' in resolve["run"]
    assert "trust_root_approved=true" in resolve["run"]
    assert 'echo "trust_root_approved=$trust_root_approved"' in resolve["run"]
    assert "head_sha=" not in "\n".join(
        line.strip() for line in resolve["run"].splitlines()
        if line.strip().startswith("echo "))

    assert "github.event.issue.pull_request != null" in rerun["if"]
    assert "github.event.comment.author_association == 'OWNER'" in rerun["if"]
    assert "startsWith" not in rerun["if"]
    assert rerun["permissions"] == {
        "actions": "write",
        "pull-requests": "read",
        "statuses": "write",
    }
    assert all("uses" not in step for step in rerun["steps"])
    assert rerun_step["env"]["PR_NUMBER"] == (
        "${{ github.event.issue.number }}")
    rerun_command = rerun_step["run"]
    assert "pulls/${PR_NUMBER}" in rerun_command
    invalidate = '"repos/${GITHUB_REPOSITORY}/statuses/${head_sha}"'
    rerun_api = '"repos/${GITHUB_REPOSITORY}/actions/runs/${run_id}/rerun"'
    assert invalidate in rerun_command
    assert "-f state=failure" in rerun_command
    assert '-f context="Trusted evidence checks"' in rerun_command
    assert rerun_command.index(invalidate) < rerun_command.index(rerun_api)
    assert rerun_step["env"]["RUN_URL"] == (
        "${{ github.server_url }}/${{ github.repository }}/actions/runs/"
        "${{ github.run_id }}")
    assert "event=pull_request_target&status=completed" in rerun_command
    assert "head_sha=${head_sha}" in rerun_command
    assert ".number == $pr and .head.sha == $sha" in rerun_command
    assert 'actions/runs/${run_id}/rerun' in rerun_command
    assert "actions/checkout" not in str(rerun)
    assert "candidate" not in rerun_command


def test_trusted_validation_does_not_publish_success_for_stale_events():
    workflow = load_workflow(TRUSTED)
    validation = workflow["jobs"]["trusted-evidence"]
    resolve = named_step(validation, "Resolve immutable pull request revisions")
    publish = named_step(
        validation, "Publish trusted result on the candidate revision")

    assert "eligible=false" in resolve["run"]
    assert "steps.resolve.outputs.eligible == 'true'" in publish["if"]
    assert "steps.resolve.outcome == 'failure'" in publish["if"]
    assert "steps.resolve.outputs.eligible != 'true'" not in publish["if"]


def test_general_validation_runs_once_and_has_a_stable_result_only_gate():
    workflow = load_workflow(PATTERN_VALIDATION)
    jobs = workflow["jobs"]
    validation = jobs["deterministic-validation"]
    gate = jobs["validation-gate"]

    assert workflow["on"]["pull_request"] == {
        "branches": ["main"],
        "types": [
            "opened", "synchronize", "reopened", "ready_for_review", "edited"],
    }
    assert gate["name"] == "Validation gate"
    assert gate["needs"] == ["deterministic-validation"]
    assert gate["if"] == "always()"
    assert all("uses" not in step for step in gate["steps"])
    assert "needs.deterministic-validation.result" in str(gate["steps"])

    setup = named_step(validation, "Set up Python 3.11")
    assert setup["with"]["cache"] == "pip"
    assert setup["with"]["cache-dependency-path"] == (
        "tests/requirements.txt")
    setup_node = named_step(validation, "Set up Node.js 24")
    assert setup_node["uses"] == (
        "actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e")
    assert setup_node["with"]["node-version"] == "24"
    assert setup_node["with"]["cache"] == "npm"
    assert setup_node["with"]["cache-dependency-path"].splitlines() == [
        "examples/centralized-rules/gateway-strategy/ai-dev-cli/package-lock.json",
        "examples/centralized-rules/gateway-strategy/ai-gateway/package-lock.json",
        "examples/centralized-rules/gateway-strategy/org-ai-client/package-lock.json",
    ]
    npm_build = named_step(validation, "Install and build locked npm examples")
    assert "npm ci --ignore-scripts --no-audit --no-fund" in npm_build["run"]
    assert "npm run build" in npm_build["run"]
    for directory in setup_node["with"]["cache-dependency-path"].splitlines():
        assert directory.removesuffix("/package-lock.json") in npm_build["run"]
    test_steps = [
        step for step in validation["steps"]
        if "python3 -m pytest" in str(step.get("run", ""))
    ]
    assert [step["name"] for step in test_steps] == [
        "Run deterministic repository tests once"]
    report = named_step(validation, "Upload deterministic test reports")
    assert report["with"]["path"] == "tests/test-results/"
    assert report["with"]["if-no-files-found"] == "error"


def test_external_links_run_only_weekly_or_when_manually_requested():
    workflow = load_workflow(PATTERN_VALIDATION)
    links = workflow["jobs"]["external-links"]

    assert "github.event_name == 'schedule'" in links["if"]
    assert "inputs.check_external_links" in links["if"]
    assert named_step(links, "Check external README links")[
        "continue-on-error"] == "true"


def test_pattern_validation_failure_issue_has_remediation_checklist():
    """New and repeat failure notices tell maintainers how to recover."""
    workflow = load_workflow(PATTERN_VALIDATION)
    notification = workflow["jobs"]["notify-failure"]
    script = named_step(
        notification, "Create issue on failure (skip if duplicate)"
    )["with"]["script"]

    assert "### Remediation checklist" in script
    assert 'python3 -m pytest -m "not slow" -x -q' in script
    assert "python3 scripts/validate-pattern-names.py" in script
    assert "python3 scripts/generate-patterns-data.py --check" in script
    assert "Local agent fix instructions" in script
    assert "Validation gate" in script
    assert script.count("${remediation}") == 2


def test_pages_pushes_are_scoped_to_site_inputs():
    workflow = load_workflow(PAGES)
    paths = set(workflow["on"]["push"]["paths"])

    assert {
        "README.md", "index.html", "*.md", "LICENSE", "patterns.yaml",
        "assets/**", "docs/**", "examples/**", "experiments/**",
        "verification/**",
    } <= paths
    assert ".beads/**" not in paths


def test_required_evidence_check_has_no_pull_request_path_filter():
    workflow = load_workflow(EVIDENCE)
    assert workflow["on"]["pull_request"] == {"branches": ["main"]}


def test_workflow_policy_changes_run_in_deterministic_evidence_validation():
    workflow = load_workflow(EVIDENCE)
    watched = set(workflow["on"]["push"]["paths"])
    assert {
        ".github/requirements.txt",
        "scripts/configure-repository-rules.py",
        "scripts/validate-workflow-policy.py",
        "tests/test_workflow_policy.py",
    } <= watched
    command = named_step(
        workflow["jobs"]["deterministic-evidence"],
        "Run fast evidence tests")["run"]
    assert "tests/test_workflow_policy.py" in command
    assert "tests/test_repository_rules.py" in command


def test_retired_hosted_fanout_helpers_are_absent():
    retired = (
        "scripts/activate-verification-unit.py",
        "scripts/assemble-verification-units.py",
        "scripts/export-verification-unit.py",
        "tests/test_research_candidate_export.py",
        "tests/test_verification_units.py",
    )
    compatibility_anchor = "scripts/export-research-candidate.py"
    assert all(not (ROOT / relative).exists() for relative in retired)
    # The old trusted validator on main requires this byte-identical file for
    # the transition PR. It has no caller and is deleted after that validator
    # no longer lists it as required.
    assert (ROOT / compatibility_anchor).is_file()

    workflow = load_workflow(EVIDENCE)
    watched = set(workflow["on"]["push"]["paths"])
    command = named_step(
        workflow["jobs"]["deterministic-evidence"],
        "Run fast evidence tests")["run"]
    assert not watched.intersection(retired)
    assert all(relative not in command for relative in retired)
    assert compatibility_anchor not in watched
    assert compatibility_anchor not in command


def test_generated_repair_prompt_reproduces_the_non_network_suite():
    source = (ROOT / "scripts" / "generate-audit-prompt.py").read_text(
        encoding="utf-8")
    assert 'python3 -m pytest -m \\"not slow\\" -x -q' in source
    assert "python3 -m pytest -x -q" not in source
