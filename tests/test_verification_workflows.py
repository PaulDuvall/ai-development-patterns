"""Structural regression tests for the evidence workflow trust boundaries."""

import re
import tomllib
from pathlib import Path

import yaml


ROOT = Path(__file__).parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
VERIFY = WORKFLOWS / "verify-patterns.yml"
TRUSTED = WORKFLOWS / "trusted-evidence-validation.yml"
EVIDENCE = WORKFLOWS / "evidence-validation.yml"
CODEX_CONFIG = ROOT / ".github" / "codex" / "evidence-research.toml"


def load_workflow(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def named_step(job, name):
    return next(step for step in job["steps"] if step.get("name") == name)


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


def test_openai_is_the_explicit_default_provider():
    workflow = load_workflow(VERIFY)
    provider = workflow["on"]["workflow_dispatch"]["inputs"]["provider"]
    assert provider == {
        "description": "Evidence research provider",
        "type": "choice",
        "options": ["openai", "anthropic"],
        "default": "openai",
    }
    prepare = workflow["jobs"]["prepare"]
    inputs = named_step(prepare, "Validate and normalize inputs")
    assert inputs["env"]["REQUESTED_PROVIDER"] == "${{ inputs.provider || 'openai' }}"
    assert prepare["outputs"]["provider"] == "${{ steps.inputs.outputs.provider }}"
    assert prepare["outputs"]["contract_sha256"] == "${{ steps.contract.outputs.sha256 }}"
    checkout = named_step(prepare, "Checkout trusted base revision")
    assert checkout["with"]["ref"] == "${{ github.sha }}"
    assert 'providers = {"openai", "anthropic"}' in inputs["run"]
    assert "unsupported provider" in inputs["run"]
    assert "evidence-v2-openai-codex-v1" in inputs["run"]
    assert "evidence-v2-anthropic-claude-v1" in inputs["run"]
    assert "+sha256.{contract_sha256}" in inputs["run"]


def test_provider_jobs_are_mutually_exclusive_and_least_privilege():
    workflow = load_workflow(VERIFY)
    openai = workflow["jobs"]["research-openai"]
    anthropic = workflow["jobs"]["research-anthropic"]
    assert openai["permissions"] == {"contents": "read"}
    assert anthropic["permissions"] == {"contents": "read", "id-token": "write"}
    assert "outputs.provider == 'openai'" in openai["if"]
    assert "outputs.provider == 'anthropic'" in anthropic["if"]
    for job in (openai, anthropic):
        checkout = named_step(job, "Checkout without persisted credentials")
        assert checkout["with"]["persist-credentials"] == "false"
        assert job["timeout-minutes"] == "120"

    validation = workflow["jobs"]["validate-candidate"]
    assert validation["needs"] == [
        "prepare", "research-openai", "research-anthropic"]
    assert validation["if"].startswith("!cancelled()")
    assert "research-openai.result == 'success'" in validation["if"]
    assert "research-anthropic.result == 'success'" in validation["if"]


def test_openai_research_uses_pinned_bounded_codex_action():
    workflow = load_workflow(VERIFY)
    research = workflow["jobs"]["research-openai"]
    credential = named_step(research, "Require OpenAI API credential")
    assert credential["env"]["OPENAI_API_KEY"] == "${{ secrets.OPENAI_API_KEY }}"
    action = named_step(research, "Collect candidate evidence with OpenAI")
    step_names = [step.get("name") for step in research["steps"]]
    assert step_names.index("Prepare isolated OpenAI research account") < (
        step_names.index("Collect candidate evidence with OpenAI"))
    isolation = named_step(research, "Prepare isolated OpenAI research account")
    assert "-m 0750" in isolation["run"]
    assert "/home/evidence-agent/workspace" in isolation["run"]
    assert "-m 0755" in isolation["run"]
    assert "/home/evidence-agent/.codex" in isolation["run"]
    assert step_names.index("Collect candidate evidence with OpenAI") < (
        step_names.index("Terminate isolated research processes and proxy"))
    assert step_names.index("Terminate isolated research processes and proxy") < (
        step_names.index("Export isolated fixed-path candidate bundle"))
    cleanup = named_step(
        research, "Terminate isolated research processes and proxy")
    assert cleanup["if"] == "always()"
    assert "pkill -KILL -u" in cleanup["run"]
    assert "odex-responses-api-proxy" in cleanup["run"]
    assert cleanup["run"].count("for _ in {1..20}") == 2
    assert action["uses"] == (
        "openai/codex-action@52fe01ec70a42f454c9d2ebd47598f9fd6893d56")
    inputs = action["with"]
    assert inputs["openai-api-key"] == "${{ secrets.OPENAI_API_KEY }}"
    assert inputs["codex-version"] == "0.144.1"
    assert inputs["codex-home"] == "/home/evidence-agent/.codex"
    assert inputs["working-directory"] == "/home/evidence-agent/workspace"
    assert inputs["model"] == "${{ needs.prepare.outputs.model }}"
    assert inputs["effort"] == "medium"
    assert inputs["permission-profile"] == "evidence-research"
    assert inputs["safety-strategy"] == "unprivileged-user"
    assert inputs["codex-user"] == "evidence-agent"
    assert inputs["codex-args"] == '["--ephemeral", "--strict-config"]'
    assert "output-file" not in inputs
    assert "allow-bots" not in inputs
    assert "Do not inspect environment variables" in inputs["prompt"]
    assert "final-message" not in VERIFY.read_text(encoding="utf-8")


def test_codex_research_profile_is_candidate_scoped_and_network_guarded():
    config = tomllib.loads(CODEX_CONFIG.read_text(encoding="utf-8"))
    assert config["project_doc_max_bytes"] == 0
    assert config["web_search"] == "live"
    assert config["default_permissions"] == "evidence-research"
    assert config["allow_login_shell"] is False
    assert config["shell_environment_policy"] == {
        "inherit": "core", "ignore_default_excludes": False}
    profile = config["permissions"]["evidence-research"]
    assert profile["extends"] == ":workspace"
    assert profile["filesystem"][
        "/home/runner/work/_temp/_runner_file_commands"] == "deny"
    assert profile["filesystem"]["/home/runner/work/_actions"] == "deny"
    roots = profile["filesystem"][":workspace_roots"]
    assert roots["."] == "read"
    assert roots[".git"] == roots[".beads"] == "deny"
    assert {
        path for path, permission in roots.items() if permission == "write"
    } == {
        "README.md", "index.html", "assets/js/patterns-data.js",
        "experiments/NOTES.md", "verification/DECISIONS.md",
        "verification/STATUS.md", "verification/pending-evidence.yaml",
        "verification/evidence",
    }
    assert profile["network"]["enabled"] is True
    assert profile["network"]["domains"] == {"*": "allow"}


def test_anthropic_research_retains_wif_and_fail_closed_guard():
    workflow = load_workflow(VERIFY)
    research = workflow["jobs"]["research-anthropic"]
    action = named_step(research, "Collect candidate evidence with Anthropic")
    assert action["with"]["github_token"] == "${{ github.token }}"
    assert "ANTHROPIC_FEDERATION_RULE_ID" in action["with"]["anthropic_api_key"]
    guard = named_step(research, "Require successful Claude execution")
    assert guard["env"]["CLAUDE_EXECUTION_FILE"] == (
        "${{ steps.research.outputs.execution_file }}")
    assert guard["run"] == "python3 scripts/check-claude-execution.py"
    assert "show_full_output" not in action["with"]


def test_both_providers_scan_then_upload_the_same_fixed_candidate_bundle():
    workflow = load_workflow(VERIFY)
    paths = None
    for job_name, action_name in (
            ("research-openai", "Collect candidate evidence with OpenAI"),
            ("research-anthropic", "Collect candidate evidence with Anthropic")):
        steps = workflow["jobs"][job_name]["steps"]
        names = [step.get("name") for step in steps]
        assert names.index(action_name) < names.index("Scan fixed-path candidate bundle")
        assert names.index("Scan fixed-path candidate bundle") < names.index(
            "Upload fixed-path candidate bundle")
        upload = named_step(
            workflow["jobs"][job_name], "Upload fixed-path candidate bundle")
        assert upload["with"]["name"] == "verification-candidate"
        if paths is None:
            paths = upload["with"]["path"]
        assert upload["with"]["path"] == paths


def test_research_has_exact_scope_and_actual_model_provenance_gate():
    text = VERIFY.read_text(encoding="utf-8")
    assert "Enforce exact research scope and current-run provenance" in text
    assert "evidence scope mismatch; missing=" in text
    assert "EVIDENCE_SCOPE_SLUGS" in text
    assert "EXPECTED_MODEL: ${{ needs.prepare.outputs.model }}" in text
    assert "EXPECTED_PROMPT_VERSION: ${{ needs.prepare.outputs.prompt_version }}" in text
    assert "verifier.model does not match this run" in text
    assert "verifier.prompt_version does not match" in text
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
