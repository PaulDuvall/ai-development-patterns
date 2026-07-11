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
CLAUDE_REVIEW = WORKFLOWS / "claude-code-review.yml"
CLAUDE_ASSISTANT = WORKFLOWS / "claude.yml"
CODEX_CONFIG = ROOT / ".github" / "codex" / "evidence-research.toml"
METHODOLOGY = ROOT / ".claude" / "commands" / "verify-patterns.md"


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
    assert prepare["outputs"]["allow_open_verification_pr"] == (
        "${{ steps.inputs.outputs.allow_open_verification_pr }}")
    assert prepare["outputs"]["checked_date"] == "${{ steps.inputs.outputs.checked_date }}"
    checkout = named_step(prepare, "Checkout trusted base revision")
    assert checkout["with"]["ref"] == "${{ github.sha }}"
    assert 'providers = {"openai", "anthropic"}' in inputs["run"]
    assert "unsupported provider" in inputs["run"]
    assert "evidence-v2-openai-codex-v1" in inputs["run"]
    assert "evidence-v2-anthropic-claude-v1" in inputs["run"]
    assert "+sha256.{contract_sha256}" in inputs["run"]
    assert inputs["env"]["OPENAI_MODEL"] == (
        "${{ vars.OPENAI_EVIDENCE_MODEL || 'gpt-5.6-luna' }}")


def test_paid_scope_and_model_overrides_require_explicit_manual_acknowledgement():
    workflow = load_workflow(VERIFY)
    dispatch = workflow["on"]["workflow_dispatch"]["inputs"]
    for name in ("confirm_full_catalog", "allow_high_cost_model"):
        assert dispatch[name]["type"] == "boolean"
        assert dispatch[name]["default"] == "false"

    inputs = named_step(
        workflow["jobs"]["prepare"], "Validate and normalize inputs")
    assert inputs["env"]["REQUESTED_CONFIRM_FULL"] == (
        "${{ inputs.confirm_full_catalog && 'true' || 'false' }}")
    assert inputs["env"]["REQUESTED_ALLOW_HIGH_COST_MODEL"] == (
        "${{ inputs.allow_high_cost_model && 'true' || 'false' }}")
    script = inputs["run"]
    assert "full mode requires confirm_full_catalog=true" in script
    assert "confirm_full_catalog may only acknowledge a manual full run" in script
    for model in ("gpt-5.6-luna", "gpt-5.4-mini", "gpt-5.4-nano"):
        assert model in script
    assert "outside the reviewed cost-sensitive" in script
    assert "allow_high_cost_model=true" in script


def test_paid_provider_calls_require_protected_human_approval():
    workflow = load_workflow(VERIFY)
    prepare = workflow["jobs"]["prepare"]
    approval = workflow["jobs"]["authorize-paid-research"]

    assert approval["name"] == "Human approval for paid research"
    assert approval["needs"] == "prepare"
    assert "needs.prepare.result == 'success'" in approval["if"]
    assert "needs.prepare.outputs.has_units == 'true'" in approval["if"]
    assert approval["environment"] == {
        "name": "evidence-paid-research",
        "deployment": "false",
    }
    assert approval["permissions"] == {"actions": "read"}
    assert approval["outputs"] == {
        "approved_attempt": "${{ steps.authorization.outputs.approved_attempt }}",
        "approved_plan_id": "${{ steps.authorization.outputs.approved_plan_id }}",
    }
    protection = named_step(
        approval, "Verify approval environment remains protected")["run"]
    assert "required_reviewers" in protection
    assert ".reviewer.login | ascii_downcase" in protection
    assert '$owner | ascii_downcase' in protection
    assert ".deployment_branch_policy.protected_branches == true" in protection
    assert "custom_branch_policies == false" in protection
    assert ".can_admins_bypass == false" in protection
    assert "must require the repository owner, protected branches" in protection
    authorization = named_step(
        approval, "Bind human authorization to this plan and run attempt")
    assert authorization["id"] == "authorization"
    assert "approved_attempt=attempt-${GITHUB_RUN_ATTEMPT}" in authorization["run"]
    assert "approved_plan_id=$PLAN_ID" in authorization["run"]
    assert authorization["env"]["PLAN_ID"] == "${{ needs.prepare.outputs.plan_id }}"

    summary = named_step(prepare, "Build deterministic inventory and worklist")["run"]
    assert "Human approval required before paid research" in summary
    assert "No OpenAI or Anthropic preflight or research call will start" in summary
    assert "evidence-paid-research" in summary
    assert "Provider/model" in summary
    assert "one billable provider preflight" in summary
    assert "No reviewed dollar estimate is available for this OpenAI model" in summary
    assert "Anthropic worker bounds" in summary
    assert "No reviewed dollar estimate is available for Anthropic" in summary
    assert "No paid research selected" in summary
    assert "No environment approval, provider preflight, or research call" in summary

    for provider in ("openai", "anthropic"):
        preflight = workflow["jobs"][f"preflight-{provider}"]
        assert preflight["needs"] == ["prepare", "authorize-paid-research"]
        assert "needs.authorize-paid-research.result == 'success'" in preflight["if"]
        assert "approved_plan_id == needs.prepare.outputs.plan_id" in preflight["if"]
        assert "approved_attempt == format('attempt-{0}', github.run_attempt)" in preflight["if"]

        research = workflow["jobs"][f"research-{provider}"]
        assert research["needs"] == [
            "prepare", "authorize-paid-research", f"preflight-{provider}"]
        assert "needs.authorize-paid-research.result == 'success'" in research["if"]
        assert "approved_plan_id == needs.prepare.outputs.plan_id" in research["if"]
        assert "approved_attempt == format('attempt-{0}', github.run_attempt)" in research["if"]

    workflow_text = VERIFY.read_text(encoding="utf-8")
    assert "secrets.EVIDENCE_OPENAI_API_KEY" in workflow_text
    assert "secrets.EVIDENCE_ANTHROPIC_API_KEY" in workflow_text
    assert "secrets.OPENAI_API_KEY" not in workflow_text
    assert "secrets.ANTHROPIC_API_KEY" not in workflow_text
    for legacy_variable in (
        "ANTHROPIC_FEDERATION_RULE_ID",
        "ANTHROPIC_ORGANIZATION_ID",
        "ANTHROPIC_SERVICE_ACCOUNT_ID",
        "ANTHROPIC_WORKSPACE_ID",
    ):
        assert f"vars.{legacy_variable}" not in workflow_text

    paid_markers = (
        "secrets.EVIDENCE_OPENAI_API_KEY",
        "secrets.EVIDENCE_ANTHROPIC_API_KEY",
        "EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID",
        "openai/codex-action@",
        "anthropics/claude-code-action@",
    )
    jobs_with_provider_access = {
        name for name, job in workflow["jobs"].items()
        if any(marker in str(job) for marker in paid_markers)
    }
    assert jobs_with_provider_access == {
        "preflight-openai",
        "preflight-anthropic",
        "research-openai",
        "research-anthropic",
    }


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
    assert "steps.anthropic-credential.outputs.configured == 'true'" in action["if"]
    assert action["with"]["anthropic_api_key"] == (
        "${{ secrets.CLAUDE_REVIEW_API_KEY }}")


def test_optional_claude_assistant_skips_without_its_dedicated_key():
    workflow = load_workflow(CLAUDE_ASSISTANT)
    job = workflow["jobs"]["claude"]
    assert "vars.ENABLE_ANTHROPIC_ASSISTANT == 'true'" in job["if"]
    assert "github.actor == github.repository_owner" in job["if"]
    credential = named_step(job, "Detect optional Claude assistant credential")
    assert credential["env"]["ANTHROPIC_API_KEY"] == (
        "${{ secrets.CLAUDE_ASSISTANT_API_KEY }}")
    assert 'if [ -n "$ANTHROPIC_API_KEY" ]' in credential["run"]
    assert "configured=$configured" in credential["run"]
    checkout = named_step(job, "Checkout repository")
    action = named_step(job, "Run Claude Code")
    expected_if = "steps.anthropic-credential.outputs.configured == 'true'"
    assert checkout["if"] == expected_if
    assert action["if"] == expected_if
    assert action["with"]["anthropic_api_key"] == (
        "${{ secrets.CLAUDE_ASSISTANT_API_KEY }}")


def test_no_workflow_can_restore_a_legacy_shared_provider_secret():
    workflow_text = "\n".join(
        path.read_text(encoding="utf-8") for path in WORKFLOWS.glob("*.yml"))
    assert "secrets.OPENAI_API_KEY" not in workflow_text
    assert "secrets.ANTHROPIC_API_KEY" not in workflow_text


def test_open_verification_pr_gate_is_default_closed_and_rechecked_before_publish():
    workflow = load_workflow(VERIFY)
    dispatch_input = workflow["on"]["workflow_dispatch"]["inputs"][
        "allow_open_verification_pr"]
    assert dispatch_input["type"] == "boolean"
    assert dispatch_input["default"] == "false"

    prepare = workflow["jobs"]["prepare"]
    collect = named_step(prepare, "Collect in-flight evidence slugs")
    assert collect["env"]["ALLOW_OPEN_VERIFICATION_PR"] == (
        "${{ steps.inputs.outputs.allow_open_verification_pr }}")
    assert "An older verification PR is still open" in collect["run"]
    assert "Manual override accepted" in collect["run"]
    assert "rerun only failed jobs" in collect["run"]

    publish = workflow["jobs"]["publish"]
    recheck = named_step(publish, "Recheck open verification PR gate")
    assert recheck["env"]["ALLOW_OPEN_VERIFICATION_PR"] == (
        "${{ needs.prepare.outputs.allow_open_verification_pr }}")
    assert "Another verification PR appeared during research" in recheck["run"]
    assert "verify/refresh-${GITHUB_RUN_ID}" in recheck["run"]

    methodology = (ROOT / "verification" / "README.md").read_text(encoding="utf-8")
    assert "-f allow_open_verification_pr=true" in methodology
    assert "publisher repeats that check after research" in methodology


def test_research_contract_fingerprints_methodology_and_verdict_code():
    workflow = load_workflow(VERIFY)
    contract = named_step(
        workflow["jobs"]["prepare"], "Fingerprint reviewed research contract")

    for path in (
            ".github/workflows/verify-patterns.yml",
            ".github/codex/evidence-research.toml",
            ".claude/commands/verify-patterns.md",
            "pattern-spec.md",
            "verification/README.md",
            "scripts/check-provider-preflight.py",
            "scripts/evidence_content.py",
            "scripts/hydrate-evidence-content.py",
            "scripts/validate-evidence.py",
            "tests/requirements.txt"):
        assert path in contract["run"]


def test_provider_jobs_are_mutually_exclusive_and_least_privilege():
    workflow = load_workflow(VERIFY)
    openai = workflow["jobs"]["research-openai"]
    anthropic = workflow["jobs"]["research-anthropic"]
    assert openai["permissions"] == {"contents": "read"}
    assert anthropic["permissions"] == {"contents": "read", "id-token": "write"}
    assert "outputs.provider == 'openai'" in openai["if"]
    assert "outputs.provider == 'anthropic'" in anthropic["if"]
    assert openai["needs"] == [
        "prepare", "authorize-paid-research", "preflight-openai"]
    assert anthropic["needs"] == [
        "prepare", "authorize-paid-research", "preflight-anthropic"]
    assert "needs.preflight-openai.result == 'success'" in openai["if"]
    assert "needs.preflight-anthropic.result == 'success'" in anthropic["if"]
    for job, timeout_minutes in ((openai, "45"), (anthropic, "60")):
        checkout = named_step(job, "Checkout without persisted credentials")
        assert checkout["with"]["persist-credentials"] == "false"
        assert job["timeout-minutes"] == timeout_minutes
        assert job["strategy"]["fail-fast"] == "true"
        assert job["strategy"]["max-parallel"] == "1"
        assert job["strategy"]["matrix"] == (
            "${{ fromJSON(needs.prepare.outputs.execution_matrix) }}")
        assert "outputs.has_units == 'true'" in job["if"]

    validation = workflow["jobs"]["validate-candidate"]
    assert validation["needs"] == [
        "prepare", "research-openai", "research-anthropic"]
    assert validation["if"].startswith("!cancelled()")
    assert "research-openai.result == 'success'" in validation["if"]
    assert "research-anthropic.result == 'success'" in validation["if"]


def test_provider_preflights_gate_research_before_matrix_fanout():
    workflow = load_workflow(VERIFY)
    openai = workflow["jobs"]["preflight-openai"]
    anthropic = workflow["jobs"]["preflight-anthropic"]

    assert openai["needs"] == ["prepare", "authorize-paid-research"]
    assert anthropic["needs"] == ["prepare", "authorize-paid-research"]
    assert "needs.authorize-paid-research.result == 'success'" in openai["if"]
    assert "needs.authorize-paid-research.result == 'success'" in anthropic["if"]
    assert openai["permissions"] == {"contents": "read"}
    assert anthropic["permissions"] == {
        "contents": "read", "id-token": "write"}
    assert "outputs.provider == 'openai'" in openai["if"]
    assert "outputs.provider == 'anthropic'" in anthropic["if"]
    for job in (openai, anthropic):
        assert "outputs.has_units == 'true'" in job["if"]
        assert job["timeout-minutes"] == "10"
        checkout = named_step(job, "Checkout trusted base revision")
        assert checkout["with"]["ref"] == "${{ needs.prepare.outputs.base_sha }}"
        assert checkout["with"]["persist-credentials"] == "false"
        assert all(
            "actions/upload-artifact@" not in step.get("uses", "")
            for step in job["steps"])

    openai_probe = named_step(
        openai, "Verify OpenAI credential, model, and quota")
    assert openai_probe["env"] == {
        "OPENAI_API_KEY": "${{ secrets.EVIDENCE_OPENAI_API_KEY }}",
        "PROVIDER_MODEL": "${{ needs.prepare.outputs.model }}",
    }
    assert "scripts/check-provider-preflight.py" in openai_probe["run"]
    assert "--provider openai" in openai_probe["run"]
    assert '--model "$PROVIDER_MODEL"' in openai_probe["run"]

    key_probe = named_step(
        anthropic, "Verify Anthropic API-key credential, model, and quota")
    assert key_probe["if"] == "vars.EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID == ''"
    assert key_probe["env"] == {
        "ANTHROPIC_API_KEY": "${{ secrets.EVIDENCE_ANTHROPIC_API_KEY }}",
        "PROVIDER_MODEL": "${{ needs.prepare.outputs.model }}",
    }
    assert "scripts/check-provider-preflight.py" in key_probe["run"]
    assert "--provider anthropic" in key_probe["run"]
    assert '--model "$PROVIDER_MODEL"' in key_probe["run"]

    federation = named_step(
        anthropic, "Probe Anthropic workload identity, model, and quota")
    assert federation["if"] == "vars.EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID != ''"
    assert federation["uses"] == (
        "anthropics/claude-code-action@a6a5b60a078a0af52612aac63e05e3f95fd4ff64")
    inputs = federation["with"]
    assert inputs["github_token"] == "${{ github.token }}"
    assert inputs["anthropic_federation_rule_id"] == (
        "${{ vars.EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID }}")
    assert inputs["anthropic_organization_id"] == (
        "${{ vars.EVIDENCE_ANTHROPIC_ORGANIZATION_ID }}")
    assert inputs["anthropic_service_account_id"] == (
        "${{ vars.EVIDENCE_ANTHROPIC_SERVICE_ACCOUNT_ID }}")
    assert inputs["anthropic_workspace_id"] == (
        "${{ vars.EVIDENCE_ANTHROPIC_WORKSPACE_ID }}")
    assert "--model ${{ needs.prepare.outputs.model }}" in inputs["claude_args"]
    assert "--max-turns 1" in inputs["claude_args"]
    assert '--tools ""' in inputs["claude_args"]
    guard = named_step(
        anthropic, "Require successful Anthropic workload-identity preflight")
    assert guard["if"] == "vars.EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID != ''"
    assert guard["env"]["CLAUDE_EXECUTION_FILE"] == (
        "${{ steps.anthropic-federation-preflight.outputs.execution_file }}")
    assert guard["run"] == "python3 scripts/check-claude-execution.py"

    expected_observers = {
        "prepare", "authorize-paid-research", "preflight-openai", "preflight-anthropic",
        "research-openai", "research-anthropic", "validate-candidate",
        "assemble-candidate", "publish",
    }
    for name in ("notify-failure", "close-resolved-failures"):
        assert set(workflow["jobs"][name]["needs"]) == expected_observers


def test_publish_overrides_skipped_unused_provider_propagation():
    workflow = load_workflow(VERIFY)
    publish = workflow["jobs"]["publish"]
    condition = publish["if"]

    assert publish["needs"] == ["prepare", "assemble-candidate"]
    assert condition.startswith("!cancelled()")
    assert "needs.prepare.result == 'success'" in condition
    assert "needs.assemble-candidate.result == 'success'" in condition
    assert "needs.assemble-candidate.outputs.has_changes == 'true'" in condition


def test_publish_requires_a_new_dispatch_when_the_default_branch_advances():
    workflow = load_workflow(VERIFY)
    guard = named_step(
        workflow["jobs"]["publish"], "Require unchanged default-branch base")

    assert "dispatch a new run against the new base" in guard["run"]
    assert "rerun against the new base" not in guard["run"]


def test_publish_retry_reuses_pr_from_the_same_source_run():
    workflow = load_workflow(VERIFY)
    publish = workflow["jobs"]["publish"]
    step = named_step(publish, "Commit, push, and open pull request")
    script = step["run"]

    assert "gh api --paginate" in script
    assert 'f"Source run: {run_url}"' in script
    assert "verify/refresh-{re.escape(run_id)}-[0-9]+" in script
    assert "Reusing candidate PR from this source run" in script
    assert "candidate_tree=$(git write-tree)" in script
    assert "head_tree" in script
    assert "The existing source-run PR no longer matches" in script
    assert "git/matching-refs/heads/verify/refresh-${GITHUB_RUN_ID}-" in script
    assert "A same-run branch exists with a different candidate tree" in script
    assert 'head="${GITHUB_REPOSITORY_OWNER}:${branch}"' in script
    assert 'pull["head"]["repo"]["full_name"] == os.environ["GITHUB_REPOSITORY"]' in script
    assert "Existing branch PR does not match the validated candidate tree" in script
    assert 'gh pr list --head "$branch"' not in script
    assert script.index("gh api --paginate") < script.index(
        'git switch --create "$branch"')
    reconcile = named_step(
        publish, "Reconcile main-catalog evidence-gap issues")["run"]
    assert '"git", "diff", "--cached", "--name-only", os.environ["BASE_SHA"]' in (
        reconcile)


def test_discovery_docs_match_the_single_run_level_publisher():
    workflow = load_workflow(VERIFY)
    publish = named_step(
        workflow["jobs"]["publish"], "Commit, push, and open pull request")["run"]
    methodology = METHODOLOGY.read_text(encoding="utf-8")

    assert 'branch="verify/refresh-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"' in publish
    assert 'git commit -m "docs(verification): refresh adoption evidence"' in publish
    assert "branch `verify/refresh-<github-run-id>-<run-attempt>`" in methodology
    assert "`docs(verification): refresh adoption evidence`" in methodology
    assert "discover/<yyyymmdd>-<run-id>" not in methodology
    assert "docs(experiments): queue" not in methodology


def test_openai_research_uses_pinned_bounded_codex_action():
    workflow = load_workflow(VERIFY)
    research = workflow["jobs"]["research-openai"]
    action = named_step(research, "Collect candidate evidence with OpenAI")
    step_names = [step.get("name") for step in research["steps"]]
    assert "Require OpenAI API credential" not in step_names
    assert step_names.index("Prepare isolated OpenAI research account") < (
        step_names.index("Verify isolated research write boundary"))
    assert step_names.index("Verify isolated research write boundary") < (
        step_names.index("Smoke-test pinned Codex permission profile without credentials"))
    assert step_names.index("Smoke-test pinned Codex permission profile without credentials") < (
        step_names.index("Collect candidate evidence with OpenAI"))
    checkpoint = named_step(
        research, "Restore same-run fixed-path research checkpoint")
    assert checkpoint["uses"] == (
        "actions/cache/restore@0057852bfaa89a56745cba8c7296529d2fc39830")
    assert checkpoint["with"]["path"] == "candidate-unit"
    assert "${{ github.run_id }}" in checkpoint["with"]["key"]
    assert "${{ needs.prepare.outputs.plan_id }}" in checkpoint["with"]["key"]
    assert "${{ matrix.unit_id }}" in checkpoint["with"]["key"]
    isolation = named_step(research, "Prepare isolated OpenAI research account")
    assert "-m 0750" in isolation["run"]
    assert "/home/evidence-agent/workspace" in isolation["run"]
    assert "-m 0755" in isolation["run"]
    assert "/home/evidence-agent/.codex" in isolation["run"]
    assert "/home/evidence-agent/.codex/tmp/arg0" in isolation["run"]
    assert "/home/evidence-agent/.codex/installation_id" in isolation["run"]
    assert "-o evidence-agent -g evidence-agent -m 0700" in isolation["run"]
    assert "-o evidence-agent -g evidence-agent -m 0644" in isolation["run"]
    assert "chown -hR root:root" in isolation["run"]
    assert "chmod -R a=rX" in isolation["run"]
    assert "chmod 0640" in isolation["run"]
    assert "verification/evidence" in isolation["run"]
    assert "for metadata in .git .agents .codex .beads" in isolation["run"]
    assert "install -d -o root -g root -m 0555" in isolation["run"]
    assert "chown root:root /home/evidence-agent" in isolation["run"]
    assert "-o root -g root -m 0644" in isolation["run"]
    assert isolation["env"] == {
        "UNIT_KIND": "${{ matrix.kind }}",
        "UNIT_SLUG": "${{ matrix.slug }}",
    }
    assert 'relative="verification/evidence/${UNIT_SLUG}.yaml"' in isolation["run"]
    assert 'relative="experiments/NOTES.md"' in isolation["run"]
    assert "writable_files=(" not in isolation["run"]
    assert 'chown -hR evidence-agent:evidence-agent "$evidence_dir"' not in isolation["run"]
    boundary = named_step(research, "Verify isolated research write boundary")
    assert "sudo -u evidence-agent python3" in boundary["run"]
    assert "scripts/check-research-workspace.py" in boundary["run"]
    assert '--writable-file "$relative"' in boundary["run"]
    node = named_step(research, "Set up Node.js 24 for Codex sandbox preflight")
    assert node["uses"] == (
        "actions/setup-node@53b83947a5a98c8d113130e565377fae1a50d02f")
    assert node["with"]["node-version"] == "24"
    python_env = named_step(research, "Build read-only research Python environment")
    assert "$(command -v python3)" in python_env["run"]
    assert "/opt/evidence-python/bin/python -m pip install" in python_env["run"]
    assert "chown -hR root:root /opt/evidence-python" in python_env["run"]
    assert "chmod -R a=rX /opt/evidence-python" in python_env["run"]
    smoke = named_step(
        research, "Smoke-test pinned Codex permission profile without credentials")
    assert '"@openai/codex@0.144.1"' in smoke["run"]
    assert "sudo -u evidence-agent env -i" in smoke["run"]
    assert "CODEX_HOME=/home/evidence-agent/.codex" in smoke["run"]
    assert ".codex-preflight" not in smoke["run"]
    assert "timeout 30s" in smoke["run"]
    assert "mcp-server --strict-config" in smoke["run"]
    assert "exec" in smoke["run"]
    assert "resume \"$missing_thread\" 'startup smoke'" in smoke["run"]
    assert "no rollout found for thread id" in smoke["run"]
    assert "failed to initialize in-process app-server client" in smoke["run"]
    assert "sandbox" in smoke["run"]
    assert "--permission-profile evidence-research" in smoke["run"]
    assert "-- python3 -c" in smoke["run"]
    assert "import bs4, requests, sys, yaml" in smoke["run"]
    assert "/usr/bin/touch /home/evidence-agent/.codex/installation_id" in (
        smoke["run"])
    assert "OPENAI_API_KEY" not in smoke.get("env", {})
    assert step_names.index("Collect candidate evidence with OpenAI") < (
        step_names.index("Terminate isolated research processes and proxy"))
    assert step_names.index("Terminate isolated research processes and proxy") < (
        step_names.index("Export isolated fixed-path research unit"))
    cleanup = named_step(
        research, "Terminate isolated research processes and proxy")
    assert cleanup["if"] == "always()"
    assert "pkill -KILL -u" in cleanup["run"]
    assert "odex-responses-api-proxy" in cleanup["run"]
    assert cleanup["run"].count("for _ in {1..20}") == 2
    assert action["uses"] == (
        "openai/codex-action@52fe01ec70a42f454c9d2ebd47598f9fd6893d56")
    inputs = action["with"]
    assert inputs["openai-api-key"] == "${{ secrets.EVIDENCE_OPENAI_API_KEY }}"
    assert inputs["codex-version"] == "0.144.1"
    assert inputs["codex-home"] == "/home/evidence-agent/.codex"
    assert inputs["working-directory"] == "/home/evidence-agent/workspace"
    assert inputs["model"] == "${{ needs.prepare.outputs.model }}"
    assert inputs["effort"] == "low"
    assert inputs["permission-profile"] == "evidence-research"
    assert inputs["safety-strategy"] == "unprivileged-user"
    assert inputs["codex-user"] == "evidence-agent"
    assert inputs["codex-args"] == '["--ephemeral", "--strict-config"]'
    assert action["if"] == "steps.research-checkpoint.outputs.cache-hit != 'true'"
    assert "Make at most 12 live web-search calls" in inputs["prompt"]
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
    assert config["features"]["rollout_budget"] == {
        "enabled": True,
        "limit_tokens": 300000,
        "reminder_at_remaining_tokens": [100000, 50000, 25000],
        "sampling_token_weight": 6.25,
        "prefill_token_weight": 1.0,
    }
    shell_environment = config["shell_environment_policy"]
    assert shell_environment["inherit"] == "core"
    assert shell_environment["ignore_default_excludes"] is False
    assert shell_environment["set"] == {
        "PATH": "/opt/evidence-python/bin:/usr/local/bin:/usr/bin:/bin"}
    profile = config["permissions"]["evidence-research"]
    assert profile["extends"] == ":workspace"
    assert profile["filesystem"][
        "/home/runner/work/_temp/_runner_file_commands"] == "deny"
    assert profile["filesystem"]["/home/runner/work/_actions"] == "deny"
    roots = profile["filesystem"][":workspace_roots"]
    assert roots == {".": "write", ".git": "deny", ".beads": "deny"}
    write_roots = {
        path for path, permission in roots.items() if permission == "write"
    }
    assert write_roots == {"."}
    for relative in write_roots:
        target = ROOT / relative
        assert target.is_dir() and not target.is_symlink(), (
            f"Codex 0.144.1 Linux write root must be a real directory: {relative}")
    assert profile["network"]["enabled"] is True
    assert profile["network"]["domains"] == {"*": "allow"}


def test_evidence_validation_smokes_real_codex_profile_without_a_key():
    workflow = load_workflow(EVIDENCE)
    job = workflow["jobs"]["codex-permission-profile"]
    assert workflow["permissions"] == {"contents": "read"}
    assert "permissions" not in job
    node = named_step(job, "Set up Node.js 24")
    assert node["uses"] == (
        "actions/setup-node@53b83947a5a98c8d113130e565377fae1a50d02f")
    python = named_step(job, "Set up Python 3.11")
    assert python["uses"] == (
        "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1")
    python_env = named_step(job, "Build read-only research Python environment")
    assert "/opt/evidence-python/bin/python -m pip install" in python_env["run"]
    assert "chown -hR root:root /opt/evidence-python" in python_env["run"]
    smoke = named_step(
        job, "Compile and launch the pinned Codex sandbox without credentials")
    assert smoke["env"]["CODEX_HOME"] == "${{ runner.temp }}/codex-profile-preflight"
    assert '"@openai/codex@0.144.1"' in smoke["run"]
    assert "profile_user=codex-profile-agent" in smoke["run"]
    assert "profile_workspace=/home/$profile_user/workspace" in smoke["run"]
    assert '--cd "$profile_workspace"' in smoke["run"]
    assert '"$profile_home/tmp/arg0"' in smoke["run"]
    assert '"$profile_home/installation_id"' in smoke["run"]
    assert 'sudo -u "$profile_user" env -i' in smoke["run"]
    assert "mcp-server --strict-config" in smoke["run"]
    assert "no rollout found for thread id" in smoke["run"]
    assert "failed to initialize in-process app-server client" in smoke["run"]
    assert "--permission-profile evidence-research" in smoke["run"]
    assert "import bs4, requests, sys, yaml" in smoke["run"]
    assert '"$CODEX_HOME/sandbox-write-probe"' in smoke["run"]
    assert "OPENAI_API_KEY" not in smoke.get("env", {})


def test_anthropic_research_retains_wif_and_fail_closed_guard():
    workflow = load_workflow(VERIFY)
    research = workflow["jobs"]["research-anthropic"]
    action = named_step(research, "Collect candidate evidence with Anthropic")
    assert action["with"]["github_token"] == "${{ github.token }}"
    assert "EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID" in (
        action["with"]["anthropic_api_key"])
    assert action["with"]["anthropic_federation_rule_id"] == (
        "${{ vars.EVIDENCE_ANTHROPIC_FEDERATION_RULE_ID }}")
    guard = named_step(research, "Require successful Claude execution")
    assert guard["env"]["CLAUDE_EXECUTION_FILE"] == (
        "${{ steps.research.outputs.execution_file }}")
    assert guard["run"] == (
        "python3 /opt/evidence-tools/check-claude-execution.py")
    assert "show_full_output" not in action["with"]
    immutable = named_step(research, "Install immutable Anthropic research tools")
    assert "/opt/evidence-tools" in immutable["run"]
    assert "-o root -g root -m 0555" in immutable["run"]
    assert "hydrate-evidence-content.py" in immutable["run"]
    boundary = named_step(research, "Restrict Anthropic checkout to the exact unit path")
    assert boundary["id"] == "anthropic-boundary"
    assert 'git config --global --add safe.directory "$workspace"' in boundary["run"]
    assert boundary["run"].index("safe.directory") < boundary["run"].index(
        'chown -hR root:root "$workspace"')
    assert "chown -hR root:root" in boundary["run"]
    assert 'relative="verification/evidence/${UNIT_SLUG}.yaml"' in boundary["run"]
    assert 'relative="experiments/NOTES.md"' in boundary["run"]
    assert 'echo "edit_rule=Edit(/${relative})"' in boundary["run"]
    assert "Bash" not in action["with"]["claude_args"]
    assert '--permission-mode dontAsk' in action["with"]["claude_args"]
    assert '--tools "Read,Edit,WebSearch,WebFetch"' in (
        action["with"]["claude_args"])
    assert '--strict-mcp-config' in action["with"]["claude_args"]
    assert '--disallowedTools "mcp__*"' in action["with"]["claude_args"]
    assert "Read(/**)" in action["with"]["claude_args"]
    assert "steps.anthropic-boundary.outputs.edit_rule" in (
        action["with"]["claude_args"])
    assert all(tool not in action["with"]["claude_args"] for tool in (
        "Write", "Glob", "Grep", "Task"))
    hydrate = named_step(research, "Hydrate trusted evidence retrieval metadata")
    assert "matrix.kind == 'evidence'" in hydrate["if"]
    assert "research-checkpoint.outputs.cache-hit != 'true'" in hydrate["if"]
    assert "/opt/evidence-tools/hydrate-evidence-content.py" in hydrate["run"]
    scope = named_step(research, "Validate proposed research unit scope")
    assert "/opt/evidence-tools/validate-research-scope.py" in scope["run"]
    restore = named_step(research, "Restore Anthropic checkout ownership")
    assert restore["if"] == "always()"


def test_both_providers_export_scan_and_upload_unique_fixed_units():
    workflow = load_workflow(VERIFY)
    for job_name, action_name in (
            ("research-openai", "Collect candidate evidence with OpenAI"),
            ("research-anthropic", "Collect candidate evidence with Anthropic")):
        steps = workflow["jobs"][job_name]["steps"]
        names = [step.get("name") for step in steps]
        assert names.index(action_name) < names.index("Scan fixed-path research unit")
        assert names.index("Scan fixed-path research unit") < names.index(
            "Upload fixed-path research unit")
        upload = named_step(
            workflow["jobs"][job_name], "Upload fixed-path research unit")
        assert upload["with"]["name"] == (
            "verification-unit-${{ needs.prepare.outputs.plan_id }}-"
            "${{ matrix.unit_id }}")
        expected_path = ("candidate-unit/" if job_name == "research-openai"
                         else "${{ runner.temp }}/candidate-unit/")
        assert upload["with"]["path"] == expected_path
        assert upload["with"]["overwrite"] == "true"
        activate = named_step(workflow["jobs"][job_name], "Activate exact research unit")
        assert "activate-verification-unit.py" in activate["run"]


def test_both_providers_reuse_only_same_run_fixed_path_checkpoints():
    workflow = load_workflow(VERIFY)
    for job_name, expected_path in (
            ("research-openai", "candidate-unit"),
            ("research-anthropic", "${{ runner.temp }}/candidate-unit")):
        job = workflow["jobs"][job_name]
        restore = named_step(job, "Restore same-run fixed-path research checkpoint")
        save = named_step(job, "Save same-run fixed-path research checkpoint")
        expected_key = (
            "verification-unit-${{ github.run_id }}-"
            "${{ needs.prepare.outputs.plan_id }}-${{ matrix.unit_id }}")
        assert restore["uses"] == (
            "actions/cache/restore@0057852bfaa89a56745cba8c7296529d2fc39830")
        assert save["uses"] == (
            "actions/cache/save@0057852bfaa89a56745cba8c7296529d2fc39830")
        assert restore["with"]["path"] == expected_path
        assert save["with"]["path"] == expected_path
        assert restore["with"]["key"] == expected_key
        assert save["with"]["key"] == expected_key
        assert restore["with"]["fail-on-cache-miss"] == "false"
        assert save["if"] == (
            "steps.research-checkpoint.outputs.cache-hit != 'true'")

        model_name = (
            "Collect candidate evidence with OpenAI"
            if job_name == "research-openai"
            else "Collect candidate evidence with Anthropic")
        assert named_step(job, model_name)["if"] == (
            "steps.research-checkpoint.outputs.cache-hit != 'true'")


def test_both_providers_hydrate_after_model_and_before_manifest_export():
    workflow = load_workflow(VERIFY)
    cases = (
        (
            "research-openai",
            "Collect candidate evidence with OpenAI",
            "Export isolated fixed-path research unit",
            "/opt/evidence-python/bin/python",
        ),
        (
            "research-anthropic",
            "Collect candidate evidence with Anthropic",
            "Export fixed-path research unit",
            "/opt/evidence-tools/hydrate-evidence-content.py",
        ),
    )
    for job_name, model_step, export_step, trusted_runtime in cases:
        job = workflow["jobs"][job_name]
        names = [step.get("name") for step in job["steps"]]
        hydrate = named_step(job, "Hydrate trusted evidence retrieval metadata")
        assert "matrix.kind == 'evidence'" in hydrate["if"]
        assert "research-checkpoint.outputs.cache-hit != 'true'" in hydrate["if"]
        assert hydrate["env"]["CHECKED_DATE"] == (
            "${{ needs.prepare.outputs.checked_date }}")
        assert "hydrate-evidence-content.py" in hydrate["run"]
        assert trusted_runtime in hydrate["run"]
        assert '--retrieved-date "$CHECKED_DATE"' in hydrate["run"]
        assert names.index(model_step) < names.index(
            "Hydrate trusted evidence retrieval metadata") < names.index(export_step)
        if job_name == "research-openai":
            assert names.index("Terminate isolated research processes and proxy") < (
                names.index("Hydrate trusted evidence retrieval metadata"))

        prompt = named_step(job, model_step)["with"]["prompt"]
        assert "Trusted post-processing" in prompt
        assert "populate resolved_url and content_sha256 by running" not in prompt


def test_research_has_exact_scope_and_actual_model_provenance_gate():
    text = VERIFY.read_text(encoding="utf-8")
    assert "Enforce exact unit scope and current-run provenance" in text
    assert "Enforce complete aggregate scope and provenance" in text
    assert "evidence scope mismatch; missing=" in text
    assert "EXPECTED_MODEL: ${{ needs.prepare.outputs.model }}" in text
    assert text.count("EXPECTED_CHECKED_DATE: ${{ needs.prepare.outputs.checked_date }}") >= 3
    assert text.count('--expected-checked-date "$EXPECTED_CHECKED_DATE"') >= 3
    methodology = METHODOLOGY.read_text(encoding="utf-8")
    assert "immutable required `last_checked` date supplied in the unit prompt" in methodology
    assert "remains authoritative across UTC midnight" in methodology
    assert "EXPECTED_PROMPT_VERSION: ${{ needs.prepare.outputs.prompt_version }}" in text
    assert "scripts/validate-research-scope.py" in text
    assert "verify-patterns-execution-log" not in text


def test_prepare_emits_one_pattern_execution_matrix():
    workflow = load_workflow(VERIFY)
    prepare = workflow["jobs"]["prepare"]
    assert prepare["outputs"]["execution_matrix"] == (
        "${{ steps.inventory.outputs.execution_matrix }}")
    assert prepare["outputs"]["plan_id"] == "${{ steps.inventory.outputs.plan_id }}"
    assert prepare["outputs"]["has_units"] == "${{ steps.inventory.outputs.has_units }}"
    assert prepare["outputs"]["unit_count"] == "${{ steps.inventory.outputs.unit_count }}"
    inventory = named_step(prepare, "Build deterministic inventory and worklist")
    assert 'if [ "$MODE" = "full" ]; then limit=0; fi' in inventory["run"]
    assert "--matrix-output verification/run-plan/execution-matrix.json" in inventory["run"]
    assert "--unit-dir verification/run-plan/units" in inventory["run"]
    assert "hashlib.sha256(matrix_bytes).hexdigest()" in inventory["run"]
    assert "Independent research units" in inventory["run"]


def test_single_pattern_membership_is_checked_by_combined_catalog_inventory():
    workflow = load_workflow(VERIFY)
    prepare = workflow["jobs"]["prepare"]
    inputs = named_step(prepare, "Validate and normalize inputs")["run"]
    inventory = named_step(prepare, "Build deterministic inventory and worklist")["run"]

    assert "single-pattern mode requires an exact catalog pattern name" in inputs
    assert 'names = {item["name"] for item in registry["patterns"]}' not in inputs
    assert 'arguments+=(--pattern "$PATTERN")' in inventory
    assert "scripts/build-verification-inventory.py" in inventory


def test_validation_matrix_is_fail_closed_and_assembly_is_single_writer():
    workflow = load_workflow(VERIFY)
    validation = workflow["jobs"]["validate-candidate"]
    assert validation["strategy"] == {
        "fail-fast": "false",
        "max-parallel": "6",
        "matrix": "${{ fromJSON(needs.prepare.outputs.execution_matrix) }}",
    }
    raw = named_step(validation, "Download candidate unit")
    assert raw["with"]["name"] == (
        "verification-unit-${{ needs.prepare.outputs.plan_id }}-"
        "${{ matrix.unit_id }}")
    validated = named_step(validation, "Upload independently validated unit")
    assert validated["with"]["name"] == (
        "validated-verification-unit-${{ needs.prepare.outputs.plan_id }}-"
        "${{ matrix.unit_id }}")
    assert validated["with"]["overwrite"] == "true"
    validation_names = [step.get("name") for step in validation["steps"]]
    assert validation_names.index("Install validation dependencies") < (
        validation_names.index("Enforce exact unit scope and current-run provenance"))

    assembly = workflow["jobs"]["assemble-candidate"]
    assert assembly["needs"] == ["prepare", "validate-candidate"]
    assert "needs.validate-candidate.result == 'success'" in assembly["if"]
    download = named_step(assembly, "Download every validated unit separately")
    assert download["with"]["pattern"] == (
        "validated-verification-unit-${{ needs.prepare.outputs.plan_id }}-*")
    assert download["with"]["merge-multiple"] == "false"
    assemble = named_step(assembly, "Assemble exact validated unit set")["run"]
    assert "assemble-verification-units.py" in assemble
    assembly_step = named_step(assembly, "Assemble exact validated unit set")
    assert assembly_step["env"]["PLAN_ID"] == "${{ needs.prepare.outputs.plan_id }}"
    assert '--plan-id "$PLAN_ID"' in assemble
    assert "sync-verification-decisions.py" in named_step(
        assembly, "Synchronize evidence-derived decision signals")["run"]
    assembly_names = [step.get("name") for step in assembly["steps"]]
    assert assembly_names.index("Install validation dependencies") < (
        assembly_names.index("Assemble exact validated unit set"))
    assert named_step(assembly, "Upload final validated candidate")["with"]["name"] == (
        "validated-verification-candidate-${{ needs.prepare.outputs.plan_id }}")

    plan_upload = named_step(
        workflow["jobs"]["prepare"], "Upload deterministic research plan")
    assert plan_upload["with"]["name"] == (
        "verification-research-plan-${{ steps.inventory.outputs.plan_id }}")
    assert plan_upload["with"]["overwrite"] == "true"

    publish_download = named_step(
        workflow["jobs"]["publish"], "Download validated candidate")
    assert publish_download["with"]["name"] == (
        "validated-verification-candidate-${{ needs.prepare.outputs.plan_id }}")


def test_refresh_hydrates_once_while_weekly_validation_rechecks_urls():
    refresh = load_workflow(VERIFY)
    validation_names = {
        step.get("name") for step in refresh["jobs"]["validate-candidate"]["steps"]}
    assert "Verify unit semantic evidence content" not in validation_names
    assert "EVIDENCE_HASH_STRICT" not in VERIFY.read_text(encoding="utf-8")

    evidence = load_workflow(EVIDENCE)
    links = evidence["jobs"]["evidence-links"]
    assert "github.event_name == 'schedule'" in links["if"]
    assert "inputs.check_links" in links["if"]
    recheck = named_step(links, "Re-fetch evidence URLs")["run"]
    assert "tests/test_evidence_content.py" in recheck
    assert "-m slow" in recheck

    methodology = METHODOLOGY.read_text(encoding="utf-8")
    assert "trusted provider code hydrates" in methodology
    assert "without immediately re-fetching the same URLs" in methodology
    assert "weekly evidence-link workflow re-fetches" in methodology


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
    assert "scripts/check-claude-execution.py" in workflow["on"]["push"]["paths"]
    assert "scripts/check-provider-preflight.py" in workflow["on"]["push"]["paths"]
    assert "scripts/hydrate-evidence-content.py" in workflow["on"]["push"]["paths"]
    assert "tests/test_provider_preflight.py" in workflow["on"]["push"]["paths"]
