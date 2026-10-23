"""Structural regression tests for evidence workflow trust boundaries."""

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
VERIFY = WORKFLOWS / "verify-patterns.yml"
TRUSTED = WORKFLOWS / "trusted-evidence-validation.yml"
EVIDENCE = WORKFLOWS / "evidence-validation.yml"
PATTERN_VALIDATION = WORKFLOWS / "pattern-validation.yml"
DOCKER_COMPATIBILITY = WORKFLOWS / "docker-example-compatibility.yml"
PAGES = WORKFLOWS / "deploy-pages.yml"

# Every external action, pinned to the exact commit and the version its comment
# claims. .github/workflows/ is trust root, so a pin cannot change without an
# owner approval round; this table makes it impossible to change one without
# also editing a test, and a new action fails here until it is listed. Each SHA
# was resolved from the upstream tag with `git ls-remote --tags`, not copied
# from a bot's pull request body. Verify a bump the same way before editing.
EXPECTED_ACTION_PINS = {
    "actions/checkout":
        ("3d3c42e5aac5ba805825da76410c181273ba90b1", "v7.0.1"),
    "actions/configure-pages":
        ("45bfe0192ca1faeb007ade9deae92b16b8254a0d", "v6"),
    "actions/dependency-review-action":
        ("a1d282b36b6f3519aa1f3fc636f609c47dddb294", "v5.0.0"),
    "actions/deploy-pages":
        ("368f82528645a54fb793d4d04e342629a3f51346", "v5"),
    "actions/github-script":
        ("3a2844b7e9c422d3c10d287c895573f7108da1b3", "v9.0.0"),
    "actions/setup-node":
        ("949feb2413d6458794dcd2491c4babbbce0c15c1", "v7.1.0"),
    "actions/setup-python":
        ("5fda3b95a4ea91299a34e894583c3862153e4b97", "v7.0.0"),
    "actions/upload-artifact":
        ("cf430e030ddbb5b0abf93d22962f4752f3646cd9", "v7.0.2"),
    "actions/upload-pages-artifact":
        ("fc324d3547104276b827a68afc52ff2a11cc49c9", "v5"),
}

ACTION_USE = re.compile(
    r"\buses:\s*(?P<repository>[^\s#@]+)@(?P<revision>[^\s#]+)"
    r"(?:\s*#\s*(?P<comment>\S+))?")


def workflow_paths():
    """Return every filename extension GitHub recognizes as a workflow."""
    return sorted({*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")})


def load_workflow(path):
    """Load a workflow while preserving YAML scalar values as strings."""
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def named_step(job, name):
    """Return the job step with the requested display name."""
    return next(step for step in job["steps"] if step.get("name") == name)


def test_every_external_action_is_pinned_to_a_commit_sha():
    """Every third-party workflow action is pinned to an immutable commit."""
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


def test_every_external_action_matches_its_expected_pin():
    """No action pin moves, and no new action arrives, without a test edit.

    The generic test above only proves a pin is *some* commit, which any SHA
    satisfies including a hostile one. This fixes which commit, so changing a
    pin or adding an action is a deliberate edit a reviewer sees, matching the
    approval the trust root already requires for .github/workflows/.
    """
    seen = {}
    mismatched = []
    for path in workflow_paths():
        for line_number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1):
            match = ACTION_USE.search(line)
            if not match or match.group("repository").startswith(
                    ("./", "docker://")):
                continue
            repository = match.group("repository")
            found = (match.group("revision"), match.group("comment"))
            seen.setdefault(repository, set()).add(found)
            expected = EXPECTED_ACTION_PINS.get(repository)
            if expected is None:
                continue
            if found != expected:
                mismatched.append(
                    f"{path.name}:{line_number}: {repository} is "
                    f"{found[0]} # {found[1]}, expected "
                    f"{expected[0]} # {expected[1]}")

    assert set(seen) == set(EXPECTED_ACTION_PINS), (
        "unlisted actions in use: "
        f"{sorted(set(seen) - set(EXPECTED_ACTION_PINS))}; "
        "listed but unused: "
        f"{sorted(set(EXPECTED_ACTION_PINS) - set(seen))}")
    assert not mismatched, "action pins out of date:\n" + "\n".join(mismatched)

    inconsistent = {
        repository: sorted(pins) for repository, pins in seen.items()
        if len(pins) > 1
    }
    assert not inconsistent, (
        f"one action pinned several ways, so a bump can miss a call site: "
        f"{inconsistent}")


def test_model_backed_pattern_evaluation_is_local_only():
    """Hosted workflows contain no model-backed evaluation path or credentials."""
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
    """Deterministic evidence validation remains model- and secret-free."""
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
    """The weekly workflow only validates and rechecks committed evidence."""
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
    """Local evaluator changes trigger validation without running the evaluator."""
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
    """No workflow references legacy shared model-provider secrets."""
    workflow_text = "\n".join(
        path.read_text(encoding="utf-8") for path in workflow_paths())
    assert "secrets.OPENAI_API_KEY" not in workflow_text
    assert "secrets.ANTHROPIC_API_KEY" not in workflow_text


def test_general_validation_runs_once_and_has_a_stable_result_only_gate():
    """General validation runs once and exposes only its stable aggregate gate."""
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
        f"actions/setup-node@{EXPECTED_ACTION_PINS['actions/setup-node'][0]}")
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
        if step.get("id") == "tests"
    ]
    assert [step["name"] for step in test_steps] == [
        "Run deterministic repository test suites"]
    test_command = test_steps[0]["run"]
    assert "cd examples/spec-driven-development" in test_command
    assert "spec-driven-junit.xml" in test_command
    assert "spec-driven-report.json" in test_command
    assert 'if [ "$spec_status" -ne 0 ] || ' in test_command
    assert '"$repository_status" -ne 0' in test_command
    assert 'echo "spec_status=$spec_status"' in test_command
    assert 'echo "repository_status=$repository_status"' in test_command
    prompt = named_step(validation, "Generate local-agent fix prompt")
    assert prompt["env"] == {
        "SPEC_STATUS": "${{ steps.tests.outputs.spec_status }}",
        "REPOSITORY_STATUS": "${{ steps.tests.outputs.repository_status }}",
    }
    assert "embedded Spec-Driven Development gate failed" in prompt["run"]
    assert "cd examples/spec-driven-development" in prompt["run"]
    assert "spec-driven-report.json" in prompt["run"]
    assert "--rerun-command" in prompt["run"]
    assert "tests/test-results/report.json" in prompt["run"]
    report = named_step(validation, "Upload deterministic test reports")
    assert report["with"]["path"] == "tests/test-results/"
    assert report["with"]["if-no-files-found"] == "error"


def test_external_links_run_only_weekly_or_when_manually_requested():
    """External link checks run only on schedule or explicit manual request."""
    workflow = load_workflow(PATTERN_VALIDATION)
    links = workflow["jobs"]["external-links"]

    assert "github.event_name == 'schedule'" in links["if"]
    assert "inputs.check_external_links" in links["if"]
    assert named_step(links, "Check external README links")[
        "continue-on-error"] == "true"


def test_live_docker_builds_are_optional_network_compatibility_checks():
    """Mutable image/package pulls stay outside the required deterministic gate."""
    deterministic_text = PATTERN_VALIDATION.read_text(encoding="utf-8")
    compatibility_text = DOCKER_COMPATIBILITY.read_text(encoding="utf-8")
    workflow = load_workflow(DOCKER_COMPATIBILITY)

    assert "docker build --pull" not in deterministic_text
    assert workflow["on"]["workflow_dispatch"] == ""
    assert workflow["on"]["schedule"] == [{"cron": "30 6 * * 1"}]
    assert workflow["permissions"] == {"contents": "read"}
    assert set(workflow["jobs"]) == {"docker-compatibility"}
    pull_request = workflow["on"]["pull_request"]
    assert pull_request["branches"] == ["main"]
    assert pull_request["types"] == [
        "opened", "synchronize", "reopened", "ready_for_review"]
    assert {
        "examples/parallel-agents/**",
        "examples/security-sandbox/**",
        ".github/workflows/docker-example-compatibility.yml",
    } <= set(pull_request["paths"])

    job = workflow["jobs"]["docker-compatibility"]
    assert job["name"] == "Docker example compatibility"
    assert job["timeout-minutes"] == "30"
    commands = "\n".join(
        step.get("run", "") for step in job["steps"])
    assert commands.count("docker build --pull") == 2
    assert "python /scripts/agent_runner.py --help" in commands
    assert "python /scripts/coordinator.py --help" in commands
    assert "--task-id database-schema" in commands
    assert "--shared-memory /tmp/shared/agent-memory.json" in commands
    assert "parallel-agent-status.json" in commands
    assert r'\"execution\": \"simulated\"' in commands
    assert r'\"status\": \"fixture_generated\"' in commands
    assert "python /workspace/healthcheck.py" in commands
    assert "docker compose --file \"$compose_file\" up" in commands
    assert "--detach --no-build ai-development" in commands
    assert "/workspace/generated /workspace/logs" in commands
    assert "touch /workspace/src/.compatibility-write" in commands
    assert "down" in commands and "--volumes --remove-orphans" in commands
    assert "docker network create --internal" in commands
    assert "accepted an attached internal bridge" in commands
    assert "SANDBOX_NETWORK_PROBE_HOST" in commands
    assert "${{ secrets." not in compatibility_text
    assert "${{ vars." not in compatibility_text


def test_pattern_validation_failure_issue_has_remediation_checklist():
    """New and repeat failure notices tell maintainers how to recover."""
    workflow = load_workflow(PATTERN_VALIDATION)
    notification = workflow["jobs"]["notify-failure"]
    script = named_step(
        notification, "Create issue on failure (skip if duplicate)"
    )["with"]["script"]

    assert "### Remediation checklist" in script
    assert 'python3 -m pytest -m "not slow" -x -q' in script
    assert (
        "cd examples/spec-driven-development && python3 -m pytest -x -q"
        in script
    )
    assert "python3 scripts/validate-pattern-names.py" in script
    assert "python3 scripts/generate-patterns-data.py --check" in script
    assert "Local agent fix instructions" in script
    assert "Validation gate" in script
    assert script.count("${remediation}") == 2


def test_pages_pushes_are_scoped_to_site_inputs():
    """Pages deployment push triggers are limited to site-relevant inputs."""
    workflow = load_workflow(PAGES)
    paths = set(workflow["on"]["push"]["paths"])

    assert {
        "README.md", "index.html", "*.md", "LICENSE", "patterns.yaml",
        "assets/**", "docs/**", "examples/**", "experiments/**",
        "verification/**",
    } <= paths
    assert ".beads/**" not in paths


def test_required_evidence_check_has_no_pull_request_path_filter():
    """The required evidence check runs for every pull request path."""
    workflow = load_workflow(EVIDENCE)
    assert workflow["on"]["pull_request"] == {"branches": ["main"]}


def test_workflow_policy_changes_run_in_deterministic_evidence_validation():
    """Workflow policy changes trigger deterministic evidence validation."""
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
    """Retired hosted-evaluation fanout helpers remain removed."""
    retired = (
        "scripts/activate-verification-unit.py",
        "scripts/assemble-verification-units.py",
        "scripts/export-research-candidate.py",
        "scripts/export-verification-unit.py",
        "tests/test_research_candidate_export.py",
        "tests/test_verification_units.py",
    )
    assert all(not (ROOT / relative).exists() for relative in retired)

    workflow = load_workflow(EVIDENCE)
    watched = set(workflow["on"]["push"]["paths"])
    command = named_step(
        workflow["jobs"]["deterministic-evidence"],
        "Run fast evidence tests")["run"]
    assert not watched.intersection(retired)
    assert all(relative not in command for relative in retired)


def test_generated_repair_prompt_reproduces_the_non_network_suite(tmp_path):
    """Generated repair prompts prescribe the reproducible non-network suite."""
    report = tmp_path / "report.json"
    report.write_text(json.dumps({
        "summary": {"total": 1, "passed": 0, "failed": 1, "error": 0},
        "tests": [{
            "nodeid": "tests/test_pattern_compliance.py::test_example",
            "outcome": "failed",
            "call": {"longrepr": "example failure"},
        }],
    }), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate-audit-prompt.py"),
         str(report)],
        capture_output=True,
        check=False,
        text=True,
    )

    assert completed.returncode == 1
    assert 'python3 -m pytest -m "not slow" -x -q' in completed.stdout
    assert "python3 -m pytest -x -q" not in completed.stdout


def test_generated_repair_prompt_can_target_an_embedded_suite(tmp_path):
    """Nested-suite reports prescribe their own exact local reproduction."""
    report = tmp_path / "spec-report.json"
    report.write_text(json.dumps({
        "summary": {"total": 1, "passed": 0, "failed": 1, "error": 0},
        "tests": [{
            "nodeid": "tests/test_validation.py::test_example",
            "outcome": "failed",
            "call": {"longrepr": "embedded failure"},
        }],
    }), encoding="utf-8")
    rerun = (
        "cd examples/spec-driven-development && "
        "python3 -m pytest -x -q"
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate-audit-prompt.py"),
            "--rerun-command", rerun,
            str(report),
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert completed.returncode == 1
    assert rerun in completed.stdout
    assert '-m "not slow"' not in completed.stdout


def test_generated_repair_prompt_ignores_successful_skips_and_xfails(tmp_path):
    """Expected non-pass outcomes do not become false remediation failures."""
    report = tmp_path / "successful-non-pass-report.json"
    report.write_text(json.dumps({
        "exitcode": 0,
        "summary": {
            "total": 3,
            "passed": 1,
            "skipped": 1,
            "xfailed": 1,
            "failed": 0,
            "error": 0,
        },
        "collectors": [{
            "nodeid": "tests/test_optional.py",
            "outcome": "skipped",
        }],
        "tests": [
            {
                "nodeid": "tests/test_optional.py::test_platform_only",
                "outcome": "skipped",
            },
            {
                "nodeid": "tests/test_expected.py::test_known_limitation",
                "outcome": "xfailed",
            },
        ],
    }), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate-audit-prompt.py"),
            str(report),
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert completed.returncode == 0
    assert completed.stdout == ""
    assert "All audit checks passed." in completed.stderr


def test_generated_repair_prompt_reports_collection_failures(tmp_path):
    """Import/collection errors cannot be mislabeled as an all-passing audit."""
    report = tmp_path / "collection-report.json"
    report.write_text(json.dumps({
        "exitcode": 2,
        "summary": {"total": 0, "passed": 0, "failed": 0, "error": 1},
        "collectors": [{
            "nodeid": "tests/test_broken.py",
            "outcome": "failed",
            "longrepr": "ImportError: broken test module",
        }],
        "tests": [],
    }), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate-audit-prompt.py"),
            str(report),
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert completed.returncode == 1
    assert "collection: tests/test_broken.py" in completed.stdout
    assert "ImportError: broken test module" in completed.stdout
    assert "All audit checks passed" not in completed.stderr


def test_generated_repair_prompt_reports_unclassified_session_failures(tmp_path):
    """A nonzero pytest exit without nodes still yields useful remediation."""
    report = tmp_path / "session-report.json"
    report.write_text(json.dumps({
        "exitcode": 3,
        "summary": {"total": 0, "passed": 0, "failed": 0, "error": 0},
        "collectors": [],
        "tests": [],
    }), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate-audit-prompt.py"),
            str(report),
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert completed.returncode == 1
    assert "pytest session" in completed.stdout
    assert "exit code 3" in completed.stdout
