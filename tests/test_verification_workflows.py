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


def test_optional_claude_review_is_opt_in_and_skips_without_a_key():
    workflow = load_workflow(CLAUDE_REVIEW)
    job = workflow["jobs"]["claude-review"]
    assert job["if"] == "vars.ENABLE_ANTHROPIC_REVIEW == 'true'"
    credential = named_step(job, "Detect optional Anthropic credential")
    assert credential["env"]["ANTHROPIC_API_KEY"] == (
        "${{ secrets.ANTHROPIC_API_KEY }}")
    assert 'if [ -n "$ANTHROPIC_API_KEY" ]' in credential["run"]
    assert "configured=$configured" in credential["run"]
    action = named_step(job, "Run Claude Code Review")
    assert "steps.anthropic-credential.outputs.configured == 'true'" in action["if"]


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
            "scripts/evidence_content.py",
            "scripts/hydrate-evidence-content.py",
            "scripts/validate-evidence.py"):
        assert path in contract["run"]


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
        assert job["strategy"]["fail-fast"] == "false"
        assert job["strategy"]["max-parallel"] == "3"
        assert job["strategy"]["matrix"] == (
            "${{ fromJSON(needs.prepare.outputs.execution_matrix) }}")
        assert "outputs.has_units == 'true'" in job["if"]

    validation = workflow["jobs"]["validate-candidate"]
    assert validation["needs"] == [
        "prepare", "research-openai", "research-anthropic"]
    assert validation["if"].startswith("!cancelled()")
    assert "research-openai.result == 'success'" in validation["if"]
    assert "research-anthropic.result == 'success'" in validation["if"]


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
    credential = named_step(research, "Require OpenAI API credential")
    assert credential["env"]["OPENAI_API_KEY"] == "${{ secrets.OPENAI_API_KEY }}"
    action = named_step(research, "Collect candidate evidence with OpenAI")
    step_names = [step.get("name") for step in research["steps"]]
    assert step_names.index("Prepare isolated OpenAI research account") < (
        step_names.index("Verify isolated research write boundary"))
    assert step_names.index("Verify isolated research write boundary") < (
        step_names.index("Smoke-test pinned Codex permission profile without credentials"))
    assert step_names.index("Smoke-test pinned Codex permission profile without credentials") < (
        step_names.index("Collect candidate evidence with OpenAI"))
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
    assert "ANTHROPIC_FEDERATION_RULE_ID" in action["with"]["anthropic_api_key"]
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
    assert hydrate["if"] == "matrix.kind == 'evidence'"
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


def test_research_has_exact_scope_and_actual_model_provenance_gate():
    text = VERIFY.read_text(encoding="utf-8")
    assert "Enforce exact unit scope and current-run provenance" in text
    assert "Enforce complete aggregate scope and provenance" in text
    assert "evidence scope mismatch; missing=" in text
    assert "EVIDENCE_SCOPE_SLUGS" in text
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


def test_strict_network_validation_is_bound_to_each_immutable_unit():
    workflow = load_workflow(VERIFY)
    validation = workflow["jobs"]["validate-candidate"]
    strict = named_step(validation, "Verify unit semantic evidence content")
    assert strict["env"]["EVIDENCE_HASH_STRICT"] == "1"
    assert strict["env"]["EVIDENCE_SCOPE_SLUGS"] == (
        "${{ matrix.selected_slugs_json }}")

    assembly_names = {
        step.get("name") for step in workflow["jobs"]["assemble-candidate"]["steps"]}
    assert "Verify aggregate semantic evidence content" not in assembly_names

    methodology = METHODOLOGY.read_text(encoding="utf-8")
    assert "Validate every evidence unit in a clean checkout" in methodology
    assert "unit manifest binds those checked bytes" in methodology
    assert "without re-fetching the same URLs" in methodology


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
    assert "scripts/hydrate-evidence-content.py" in workflow["on"]["push"]["paths"]
