"""Structural regression tests for evidence workflow trust boundaries."""

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
VERIFY = WORKFLOWS / "verify-patterns.yml"
TRUSTED = WORKFLOWS / "trusted-evidence-validation.yml"
EVIDENCE = WORKFLOWS / "evidence-validation.yml"
CLAUDE_REVIEW = WORKFLOWS / "claude-code-review.yml"


def load_workflow(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def named_step(job, name):
    return next(step for step in job["steps"] if step.get("name") == name)


def test_every_external_action_is_pinned_to_a_commit_sha():
    unpinned = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
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
        for path in WORKFLOWS.glob("*.yml")
    }
    combined = "\n".join(workflow_text.values())
    forbidden = (
        "openai/codex-action@",
        "@openai/codex@",
        "codex exec",
        "codex sandbox",
        "EVIDENCE_OPENAI_API_KEY",
        "EVIDENCE_ANTHROPIC_API_KEY",
        "OPENAI_EVIDENCE_MODEL",
        "ANTHROPIC_EVIDENCE_MODEL",
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
    assert anthropic_action_files == {"claude-code-review.yml"}
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
        "scripts/finalize-local-verification.py",
        "tests/test_local_research_scope.py",
        "tests/test_local_verification.py",
    } <= watched

    jobs_text = str(workflow["jobs"])
    assert "plan-local-verification.py" not in jobs_text
    assert "finalize-local-verification.py" not in jobs_text
    assert "evaluate-pattern-adoption" not in jobs_text


def test_optional_claude_review_is_opt_in_and_skips_without_a_key():
    workflow = load_workflow(CLAUDE_REVIEW)
    job = workflow["jobs"]["claude-review"]
    assert job["if"] == "vars.ENABLE_ANTHROPIC_REVIEW == 'true'"
    credential = named_step(job, "Detect optional Anthropic credential")
    assert credential["env"]["ANTHROPIC_API_KEY"] == (
        "${{ secrets.CLAUDE_REVIEW_API_KEY }}")
    assert 'if [ -n "$ANTHROPIC_API_KEY" ]' in credential["run"]
    assert "configured=$configured" in credential["run"]
    action = named_step(job, "Run Claude Code Review")
    assert "steps.anthropic-credential.outputs.configured == 'true'" in (
        action["if"])
    assert action["with"]["anthropic_api_key"] == (
        "${{ secrets.CLAUDE_REVIEW_API_KEY }}")


def test_no_workflow_can_restore_a_legacy_shared_provider_secret():
    workflow_text = "\n".join(
        path.read_text(encoding="utf-8") for path in WORKFLOWS.glob("*.yml"))
    assert "secrets.OPENAI_API_KEY" not in workflow_text
    assert "secrets.ANTHROPIC_API_KEY" not in workflow_text


def test_trusted_pr_workflow_executes_only_base_branch_validation_code():
    workflow = load_workflow(TRUSTED)
    assert "pull_request_target" in workflow["on"]
    job = workflow["jobs"]["trusted-evidence"]
    candidate_checkout = named_step(job, "Checkout candidate as inert data")
    assert candidate_checkout["with"]["repository"] == (
        "${{ steps.resolve.outputs.head_repo }}")
    assert candidate_checkout["with"]["ref"] == (
        "${{ steps.resolve.outputs.head_sha }}")
    commands = "\n".join(str(step.get("run", "")) for step in job["steps"])
    assert "trusted/scripts/validate-evidence.py" in commands
    assert "trusted/scripts/generate-verification-status.py" in commands
    assert "candidate/scripts/" not in commands
    assert 'context="Trusted evidence checks"' in commands
    status = named_step(job, "Recompute candidate status with trusted generator")
    assert "trusted/scripts/generate-verification-status.py --root candidate" in status["run"]
    assert 'marker = "\\n## How to refresh\\n"' in status["run"]
    assert "submitted_derived != recomputed_derived" in status["run"]
    assert "candidate/scripts/generate-verification-status.py" not in status["run"]


def test_required_evidence_check_has_no_pull_request_path_filter():
    workflow = load_workflow(EVIDENCE)
    assert workflow["on"]["pull_request"] == {"branches": ["main"]}
