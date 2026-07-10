"""Structural regression tests for the evidence workflow trust boundaries."""

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
VERIFY = WORKFLOWS / "verify-patterns.yml"
TRUSTED = WORKFLOWS / "trusted-evidence-validation.yml"
EVIDENCE = WORKFLOWS / "evidence-validation.yml"


def load_workflow(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_every_external_action_is_pinned_to_a_commit_sha():
    unpinned = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = re.search(r"\buses:\s*([^\s#]+)", line)
            if not match or match.group(1).startswith(("./", "docker://")):
                continue
            reference = match.group(1).rsplit("@", 1)[-1]
            if re.fullmatch(r"[0-9a-f]{40}", reference) is None:
                unpinned.append(f"{path.name}:{line_number}: {match.group(1)}")
    assert not unpinned, "unpinned Actions:\n" + "\n".join(unpinned)


def test_research_has_read_only_github_token_and_exact_scope_gate():
    workflow = load_workflow(VERIFY)
    research = workflow["jobs"]["research"]
    assert research["permissions"]["contents"] == "read"
    action_step = next(
        step for step in research["steps"] if step.get("name") == "Collect candidate evidence")
    assert action_step["with"]["github_token"] == "${{ github.token }}"
    text = VERIFY.read_text(encoding="utf-8")
    assert "Enforce exact research scope and current-run provenance" in text
    assert "evidence scope mismatch; missing=" in text
    assert "EVIDENCE_SCOPE_SLUGS" in text
    assert "verify-patterns-execution-log" not in text


def test_trusted_pr_workflow_executes_only_base_branch_validation_code():
    workflow = load_workflow(TRUSTED)
    assert "pull_request_target" in workflow["on"]
    job = workflow["jobs"]["trusted-evidence"]
    candidate_checkout = next(
        step for step in job["steps"] if step.get("name") == "Checkout candidate as inert data")
    assert candidate_checkout["with"]["repository"] == (
        "${{ steps.resolve.outputs.head_repo }}")
    assert candidate_checkout["with"]["ref"] == "${{ steps.resolve.outputs.head_sha }}"
    commands = "\n".join(str(step.get("run", "")) for step in job["steps"])
    assert "trusted/scripts/validate-evidence.py" in commands
    assert "trusted/scripts/generate-verification-status.py" in commands
    assert "candidate/scripts/" not in commands
    assert 'context="Trusted evidence checks"' in commands


def test_required_evidence_check_has_no_pull_request_path_filter():
    workflow = load_workflow(EVIDENCE)
    assert workflow["on"]["pull_request"] == {"branches": ["main"]}
