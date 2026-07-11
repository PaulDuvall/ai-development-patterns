"""Tests for the trusted semantic candidate workflow scanner."""

import importlib.util
import os
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "validate-workflow-policy.py"
CONFIG_SCRIPT = ROOT / "scripts" / "configure-repository-rules.py"
SPEC = importlib.util.spec_from_file_location("workflow_policy", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CONFIG_SPEC = importlib.util.spec_from_file_location(
    "configure_repository_rules_for_policy", CONFIG_SCRIPT)
CONFIG = importlib.util.module_from_spec(CONFIG_SPEC)
CONFIG_SPEC.loader.exec_module(CONFIG)


def write_workflow(directory, name, body):
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def basic_workflow(step):
    return (
        "name: policy fixture\n"
        "on: workflow_dispatch\n"
        "jobs:\n"
        "  check:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        f"      {step}\n"
    )


def populate_minimal_trust_root(root):
    for relative in MODULE.REQUIRED_TRUST_ROOT_DIRECTORIES:
        (root / relative).mkdir(parents=True, exist_ok=True)
    for relative in MODULE.REQUIRED_TRUST_ROOT_FILES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"trusted fixture: {relative}\n", encoding="utf-8")


def test_current_deterministic_workflows_pass_policy():
    assert MODULE.validate_directory(ROOT / ".github" / "workflows") == []
    assert MODULE.validate_candidate_repository(
        ROOT, ROOT, ROOT / ".github" / "workflows") == []


def test_nested_yaml_provider_surface_is_scanned_and_rejected(tmp_path):
    workflow = write_workflow(
        tmp_path,
        "nested/provider.yaml",
        basic_workflow(
            "- uses: anthropics/claude-code-action@" + "a" * 40)
        + "      - run: codex exec --full-auto\n"
        + "        env:\n"
        + "          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}\n"
        + "      - run: curl https://api.openai.com/v1/responses\n",
    )

    findings = MODULE.validate_directory(tmp_path)

    assert any("model/provider action is forbidden" in item for item in findings)
    assert any("model/provider CLI invocation is forbidden" in item for item in findings)
    assert any("retired Actions configuration marker" in item for item in findings)
    assert any("provider credential marker is forbidden" in item for item in findings)
    assert any("provider API endpoint is forbidden" in item for item in findings)
    assert all(str(workflow) in item for item in findings)


def test_candidate_cannot_weaken_pytest_to_bypass_policy(tmp_path):
    workflows = tmp_path / ".github" / "workflows"
    write_workflow(
        workflows,
        "unsafe.yml",
        basic_workflow("- run: codex exec 'perform hosted evaluation'"),
    )
    write_workflow(
        tmp_path,
        "tests/test_verification_workflows.py",
        "def test_policy():\n    assert True\n",
    )

    findings = MODULE.validate_directory(workflows)

    assert findings
    assert any("model/provider CLI invocation is forbidden" in item
               for item in findings)


@pytest.mark.parametrize("command, expected", [
    ("python3 scripts/evidence-research.py", "hosted evaluator invocation"),
    ("python3 -m pip install openai", "model/provider CLI invocation"),
    ("aws bedrock-runtime invoke-model --model-id example",
     "model/provider CLI invocation"),
    ("gh models run openai/gpt-4.1", "model/provider CLI invocation"),
    ("curl https://models.github.ai/inference/chat/completions",
     "provider API endpoint"),
    ("from openai import OpenAI", "provider SDK invocation"),
    ('const Anthropic = require("@anthropic-ai/sdk")',
     "provider SDK invocation"),
    ("gh copilot suggest 'write tests'", "model/provider CLI invocation"),
    ("curl https://api.githubcopilot.com/chat/completions",
     "provider API endpoint"),
    ("import github_copilot", "provider SDK invocation"),
    ("npx @github/copilot --prompt test", "GitHub Copilot marker"),
])
def test_other_clear_hosted_provider_invocations_are_rejected(
        tmp_path, command, expected):
    write_workflow(
        tmp_path,
        "hosted-evaluator.yml",
        basic_workflow(f"- run: {command}"),
    )

    assert any(
        expected in item for item in MODULE.validate_directory(tmp_path))


def test_github_models_permission_is_rejected(tmp_path):
    write_workflow(
        tmp_path,
        "github-models.yml",
        "name: hosted model\non: workflow_dispatch\n"
        "permissions:\n  models: read\n"
        "jobs:\n  check:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: deterministic-check\n",
    )

    assert any(
        "GitHub Models permission is forbidden" in item
        for item in MODULE.validate_directory(tmp_path))


def test_github_copilot_requests_permission_is_rejected(tmp_path):
    write_workflow(
        tmp_path,
        "copilot.yml",
        "name: hosted copilot\non: workflow_dispatch\n"
        "permissions:\n  copilot-requests: write\n"
        "jobs:\n  check:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: deterministic-check\n",
    )

    assert any(
        "GitHub Copilot requests permission is forbidden" in item
        for item in MODULE.validate_directory(tmp_path))


def test_unpinned_external_action_is_rejected(tmp_path):
    write_workflow(
        tmp_path,
        "unpinned.yml",
        basic_workflow("- uses: actions/checkout@v7"),
    )

    assert any(
        "external action is not pinned to a commit SHA" in item
        for item in MODULE.validate_directory(tmp_path)
    )


def test_quoted_and_flow_action_keys_cannot_bypass_pinning(tmp_path):
    write_workflow(
        tmp_path,
        "quoted.yml",
        basic_workflow('- "uses": actions/checkout@v7'),
    )
    write_workflow(
        tmp_path,
        "flow.yaml",
        basic_workflow("- {name: checkout, uses: actions/checkout@v7}"),
    )

    findings = MODULE.validate_directory(tmp_path)

    assert sum("external action is not pinned" in item
               for item in findings) == 2


def test_one_line_flow_steps_cannot_bypass_semantic_policy(tmp_path):
    write_workflow(
        tmp_path,
        "one-line.yml",
        "name: flow attack\non: workflow_dispatch\n"
        "jobs:\n  check:\n    runs-on: ubuntu-latest\n"
        "    steps: [{uses: attacker/hosted-model-action@v1}, "
        "{run: codex exec expensive}]\n",
    )

    findings = MODULE.validate_directory(tmp_path)

    assert any("external action repository is not approved" in item
               for item in findings)
    assert any("model/provider CLI invocation is forbidden" in item
               for item in findings)


def test_pinned_deterministic_action_is_accepted(tmp_path):
    write_workflow(
        tmp_path,
        "pinned.yaml",
        basic_workflow("- uses: actions/checkout@" + "9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"),
    )

    assert MODULE.validate_directory(tmp_path) == []


def test_action_allowlist_exactly_matches_current_trusted_workflows():
    repositories = set()
    for path in MODULE.iter_workflow_files(
            ROOT / ".github" / "workflows"):
        document = MODULE.load_workflow_document(path)
        for reference in MODULE.iter_action_references(document):
            if reference.startswith("./") or reference.casefold().startswith(
                    "docker://"):
                continue
            repositories.add(reference.rsplit("@", 1)[0].casefold())

    assert repositories == MODULE.APPROVED_EXTERNAL_ACTION_REPOSITORIES
    assert MODULE.APPROVED_EXTERNAL_ACTION_REPOSITORIES == frozenset(
        CONFIG.APPROVED_EXTERNAL_ACTION_REPOSITORIES)


def test_local_action_cannot_hide_a_provider_call(tmp_path):
    workflows = tmp_path / ".github" / "workflows"
    write_workflow(
        workflows,
        "local.yml",
        basic_workflow("- uses: ./.github/actions/check"),
    )
    write_workflow(
        tmp_path,
        ".github/actions/check/action.yml",
        "name: hidden call\nruns:\n  using: composite\n  steps:\n"
        "    - shell: bash\n"
        "      run: curl https://api.openai.com/v1/responses\n",
    )

    assert any(
        "local actions are forbidden" in item
        for item in MODULE.validate_directory(workflows))


def test_docker_action_is_forbidden_even_when_digest_pinned(tmp_path):
    write_workflow(
        tmp_path,
        "docker.yml",
        basic_workflow(
            "- uses: docker://ghcr.io/example/check@sha256:" + "a" * 64),
    )

    assert any(
        "Docker actions are forbidden" in item
        for item in MODULE.validate_directory(tmp_path))


def test_pinned_unapproved_external_action_is_rejected(tmp_path):
    write_workflow(
        tmp_path,
        "unapproved.yml",
        basic_workflow(
            "- uses: third-party/deterministic-check@" + "b" * 40),
    )

    findings = MODULE.validate_directory(tmp_path)

    assert any("external action repository is not approved" in item
               for item in findings)
    assert not any("not pinned to a commit SHA" in item for item in findings)


@pytest.mark.parametrize("reference", [
    "${{ secrets.INNOCUOUS_ALIAS }}",
    "${{ vars.RENAMED_PROVIDER_CREDENTIAL }}",
    "${{ secrets['INDIRECT_ALIAS'] }}",
    "${{ toJSON(secrets) }}",
])
def test_renamed_repository_credentials_and_variables_are_rejected(
        tmp_path, reference):
    write_workflow(
        tmp_path,
        "credential.yml",
        basic_workflow("- run: deterministic-check")
        + f"        env:\n          VALUE: {reference}\n",
    )

    assert any(
        "repository Actions secret/variable reference is forbidden" in item
        for item in MODULE.validate_directory(tmp_path)
    )


def test_builtin_github_token_is_allowed(tmp_path):
    write_workflow(
        tmp_path,
        "github-token.yml",
        basic_workflow("- run: gh api /rate_limit")
        + "        env:\n          GH_TOKEN: ${{ github.token }}\n",
    )

    assert MODULE.validate_directory(tmp_path) == []


def test_quoted_and_indented_block_run_keys_are_scanned(tmp_path):
    write_workflow(
        tmp_path,
        "quoted-run.yml",
        basic_workflow('- "run": codex exec prohibited'),
    )
    write_workflow(
        tmp_path,
        "indented-block.yaml",
        "name: block fixture\non: workflow_dispatch\n"
        "jobs:\n  check:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: |2-\n          codex exec prohibited\n",
    )

    findings = MODULE.validate_directory(tmp_path)

    assert sum("model/provider CLI invocation is forbidden" in item
               for item in findings) == 2


def test_yaml_alias_is_rejected_before_semantic_inspection(tmp_path):
    write_workflow(
        tmp_path,
        "alias.yml",
        "name: shape fixture\non: workflow_dispatch\n"
        "x-command: &candidate_command deterministic-check\n"
        "jobs:\n  check:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: *candidate_command\n",
    )

    with pytest.raises(MODULE.WorkflowPolicyError, match="aliases"):
        MODULE.validate_directory(tmp_path)


def test_escaped_and_explicit_keys_are_semantically_inspected(tmp_path):
    write_workflow(
        tmp_path,
        "escaped.yml",
        "name: escaped fixture\non: workflow_dispatch\n"
        "jobs:\n  check:\n    runs-on: ubuntu-latest\n"
        "    steps:\n"
        '      - "\\x75ses": attacker/model-action@' + "c" * 40 + "\n"
        '      - "\\x72un": codex exec prohibited\n',
    )
    write_workflow(
        tmp_path,
        "explicit.yaml",
        "name: explicit fixture\non: workflow_dispatch\n"
        "jobs:\n  check:\n    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - ? uses\n"
        "        : attacker/deterministic-check@" + "d" * 40 + "\n"
        "      - ? run\n"
        "        : codex exec prohibited\n",
    )

    findings = MODULE.validate_directory(tmp_path)

    assert sum("external action repository is not approved" in item
               for item in findings) == 2
    assert sum("model/provider CLI invocation is forbidden" in item
               for item in findings) == 2


def test_duplicate_mapping_keys_are_rejected(tmp_path):
    write_workflow(
        tmp_path,
        "duplicate.yml",
        "name: duplicate fixture\non: workflow_dispatch\n"
        "jobs:\n  check:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - uses: actions/checkout@" + "a" * 40 + "\n"
        "        uses: attacker/model-action@" + "b" * 40 + "\n",
    )

    with pytest.raises(MODULE.WorkflowPolicyError, match="duplicate"):
        MODULE.validate_directory(tmp_path)


def test_candidate_trust_root_files_must_remain_present(tmp_path):
    findings = MODULE.validate_trust_root_presence(tmp_path)

    assert len(findings) == (
        len(MODULE.REQUIRED_TRUST_ROOT_FILES)
        + len(MODULE.REQUIRED_TRUST_ROOT_DIRECTORIES))
    assert all("required candidate trust-root entry is missing" in item
               for item in findings)


@pytest.mark.parametrize("relative,replacement", [
    ("scripts/validate-workflow-policy.py", "# weakened scanner\n"),
    (".github/workflows/trusted-evidence-validation.yml",
     "name: weakened workflow\n"),
    ("tests/requirements.txt",
     "PyYAML==6.0.3\nmalicious-package==1\n"),
])
def test_protected_runtime_replacement_requires_exact_owner_upgrade(
        tmp_path, relative, replacement):
    trusted = tmp_path / "trusted"
    candidate = tmp_path / "candidate"
    populate_minimal_trust_root(trusted)
    populate_minimal_trust_root(candidate)
    (candidate / relative).write_text(replacement, encoding="utf-8")

    findings = MODULE.validate_trust_root_integrity(candidate, trusted)

    assert any("without exact OWNER approval" in item for item in findings)
    assert MODULE.validate_trust_root_integrity(
        candidate, trusted, allow_trust_root_upgrade=True) == []


@pytest.mark.parametrize("relative", [
    "scripts/yaml.py",
    "scripts/yaml/__init__.py",
    "scripts/sitecustomize.py",
    "sitecustomize.py",
    "usercustomize.py",
    "conftest.py",
])
def test_added_import_shadow_or_startup_hook_requires_owner_upgrade(
        tmp_path, relative):
    trusted = tmp_path / "trusted"
    candidate = tmp_path / "candidate"
    populate_minimal_trust_root(trusted)
    populate_minimal_trust_root(candidate)
    write_workflow(candidate, relative, "raise SystemExit('executed')\n")

    findings = MODULE.validate_trust_root_integrity(candidate, trusted)

    assert any("without exact OWNER approval" in item for item in findings)


def test_owner_upgrade_never_permits_required_runtime_deletion(tmp_path):
    trusted = tmp_path / "trusted"
    candidate = tmp_path / "candidate"
    populate_minimal_trust_root(trusted)
    populate_minimal_trust_root(candidate)
    (candidate / "scripts" / "validate-workflow-policy.py").unlink()

    findings = MODULE.validate_trust_root_presence(candidate)

    assert any("required candidate trust-root entry is missing" in item
               for item in findings)
    assert MODULE.validate_trust_root_integrity(
        candidate, trusted, allow_trust_root_upgrade=True) == []


def test_protected_tree_rejects_symbolic_links(tmp_path):
    populate_minimal_trust_root(tmp_path)
    link = tmp_path / "scripts" / "shadow.py"
    try:
        os.symlink(tmp_path / "AGENTS.md", link)
    except (NotImplementedError, OSError):
        pytest.skip("symbolic links are unavailable on this platform")

    assert any(
        "trust-root entry must be a regular file" in item
        for item in MODULE.validate_trust_root_presence(tmp_path))


def test_protected_tree_file_and_entry_bounds_fail_closed(
        tmp_path, monkeypatch):
    populate_minimal_trust_root(tmp_path)
    monkeypatch.setattr(MODULE, "MAX_TRUST_ROOT_FILES", 1)
    with pytest.raises(MODULE.WorkflowPolicyError, match="files"):
        MODULE.trust_root_inventory(tmp_path)

    monkeypatch.setattr(MODULE, "MAX_TRUST_ROOT_FILES", 1000)
    monkeypatch.setattr(MODULE, "MAX_TRUST_ROOT_ENTRIES", 1)
    with pytest.raises(MODULE.WorkflowPolicyError, match="entries"):
        MODULE.trust_root_inventory(tmp_path)


def test_protected_tree_definition_covers_hosted_and_local_trust_roots():
    assert set(MODULE.REQUIRED_TRUST_ROOT_DIRECTORIES) == {
        ".agents/skills/evaluate-pattern-adoption",
        ".codex",
        ".github/workflows",
        "scripts",
        "tests",
    }
    assert {
        ".agents/skills/evaluate-pattern-adoption/SKILL.md",
        ".agents/skills/evaluate-pattern-adoption/references/evidence-methodology.md",
        ".codex/agents/adoption-researcher.toml",
        ".codex/agents/adoption-verifier.toml",
        ".github/trusted-policy-requirements.txt",
        ".github/workflows/trusted-evidence-validation.yml",
        "AGENTS.md",
        "pyproject.toml",
        "pytest.ini",
        "scripts/finalize-local-verification.py",
        "scripts/plan-local-verification.py",
        "scripts/record-local-search-event.py",
        "scripts/validate-workflow-policy.py",
        "tests/requirements.txt",
        "tests/test_workflow_policy.py",
    } <= set(MODULE.REQUIRED_TRUST_ROOT_FILES)
    assert set(MODULE.OPTIONAL_TRUST_ROOT_FILES) == {
        "conftest.py", "sitecustomize.py", "usercustomize.py"}



def test_workflow_files_must_be_regular_and_bounded(tmp_path):
    target = write_workflow(
        tmp_path,
        "target.yml",
        basic_workflow("- run: python3 -m pytest"),
    )
    link = tmp_path / "linked.yaml"
    try:
        os.symlink(target, link)
    except (NotImplementedError, OSError):
        pytest.skip("symbolic links are unavailable on this platform")

    with pytest.raises(MODULE.WorkflowPolicyError, match="symbolic link"):
        MODULE.iter_workflow_files(tmp_path)

    link.unlink()
    write_workflow(
        tmp_path,
        "oversized.yaml",
        "#" * (MODULE.MAX_WORKFLOW_BYTES + 1),
    )
    with pytest.raises(MODULE.WorkflowPolicyError, match="exceeds"):
        MODULE.iter_workflow_files(tmp_path)


def test_retired_markers_are_shared_with_repository_configuration():
    assert set(MODULE.RETIRED_ACTIONS_SECRETS) == set(
        CONFIG.RETIRED_ACTIONS_SECRETS)
    assert set(MODULE.RETIRED_ACTIONS_VARIABLES) == set(
        CONFIG.RETIRED_ACTIONS_VARIABLES)
    assert MODULE.RETIRED_CONFIGURATION_MARKERS == frozenset({
        *CONFIG.RETIRED_ACTIONS_SECRETS,
        *CONFIG.RETIRED_ACTIONS_VARIABLES,
    })
