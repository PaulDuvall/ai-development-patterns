#!/usr/bin/env python3
"""Semantically validate candidate GitHub workflows as inert data.

The trusted base parses candidate YAML only after installing its own pinned
PyYAML dependency.  Candidate Python, tests, actions, and scripts are never
loaded or executed.
"""

import argparse
import hashlib
import os
import re
import runpy
import stat
import sys
from pathlib import Path

import yaml


MAX_WORKFLOW_BYTES = 512 * 1024
MAX_WORKFLOW_FILES = 128
MAX_TRUST_ROOT_BYTES = 1024 * 1024
MAX_TRUST_ROOT_FILES = 512
MAX_TRUST_ROOT_ENTRIES = 1024
MAX_TRUST_ROOT_TOTAL_BYTES = 25 * 1024 * 1024
WORKFLOW_SUFFIXES = frozenset({".yml", ".yaml"})
REQUIRED_TRUST_ROOT_FILES = (
    ".agents/skills/evaluate-pattern-adoption/SKILL.md",
    ".agents/skills/evaluate-pattern-adoption/references/evidence-methodology.md",
    ".codex/agents/adoption-researcher.toml",
    ".codex/agents/adoption-verifier.toml",
    ".codex/config.toml",
    ".github/trusted-policy-requirements.txt",
    ".github/workflows/trusted-evidence-validation.yml",
    "AGENTS.md",
    "pyproject.toml",
    "pytest.ini",
    "scripts/build-verification-inventory.py",
    "scripts/configure-repository-rules.py",
    "scripts/evidence_content.py",
    "scripts/export-research-candidate.py",
    "scripts/finalize-local-verification.py",
    "scripts/generate-verification-status.py",
    "scripts/hydrate-evidence-content.py",
    "scripts/local_verification.py",
    "scripts/plan-local-verification.py",
    "scripts/record-local-search-event.py",
    "scripts/scan-candidate-secrets.py",
    "scripts/sync-verification-decisions.py",
    "scripts/validate-evidence.py",
    "scripts/validate-research-scope.py",
    "scripts/validate-workflow-policy.py",
    "tests/requirements.txt",
    "tests/test_local_verification.py",
    "tests/test_verification_workflows.py",
    "tests/test_workflow_policy.py",
)
REQUIRED_TRUST_ROOT_DIRECTORIES = (
    ".agents/skills/evaluate-pattern-adoption",
    ".codex",
    ".github/workflows",
    "scripts",
    "tests",
)
OPTIONAL_TRUST_ROOT_FILES = (
    "conftest.py",
    "sitecustomize.py",
    "usercustomize.py",
)

CONFIGURATION = runpy.run_path(
    str(Path(__file__).with_name("configure-repository-rules.py")))
# This allowlist is shared with the trusted repository Actions settings. A new
# action repository must be admitted in a separate, OWNER-approved upgrade.
APPROVED_EXTERNAL_ACTION_REPOSITORIES = frozenset(
    CONFIGURATION["APPROVED_EXTERNAL_ACTION_REPOSITORIES"])
RETIRED_ACTIONS_SECRETS = tuple(CONFIGURATION["RETIRED_ACTIONS_SECRETS"])
RETIRED_ACTIONS_VARIABLES = tuple(CONFIGURATION["RETIRED_ACTIONS_VARIABLES"])
RETIRED_CONFIGURATION_MARKERS = frozenset({
    *RETIRED_ACTIONS_SECRETS,
    *RETIRED_ACTIONS_VARIABLES,
})
RETIRED_MARKERS_CASEFOLDED = tuple(sorted(
    (marker.casefold(), marker)
    for marker in RETIRED_CONFIGURATION_MARKERS
))

COMMIT_SHA = re.compile(r"[0-9a-f]{40}", re.IGNORECASE)
SAFE_LOCATION_KEY = re.compile(r"[A-Za-z0-9_-]{1,64}")
PROVIDER_ACTION_MARKERS = (
    "openai",
    "anthropic",
    "claude",
    "codex",
    "gemini",
    "bedrock",
    "vertex-ai",
    "ai-inference",
    "huggingface",
    "ollama",
    "copilot",
)
HOSTED_EVALUATOR_MARKERS = (
    ".claude/commands/verify-patterns.md",
    ".codex/agents/adoption-",
    ".github/codex/evidence-research.toml",
    ".agents/skills/evaluate-pattern-adoption",
    "adoption-researcher",
    "adoption-verifier",
    "evidence-research",
    "evidence-refresh",
    "evidence-paid-research",
    "evaluator",
    "model-evaluation",
    "model-evaluator",
    "model-action",
    "research-agent",
    "scripts/check-claude-execution.py",
    "scripts/check-provider-preflight.py",
    "scripts/check-research-workspace.py",
    "scripts/finalize-local-verification.py",
    "scripts/plan-local-verification.py",
    "scripts/record-local-search-event.py",
    "verify-patterns.yml",
)
PROVIDER_CREDENTIAL = re.compile(
    r"\b(?:OPENAI|ANTHROPIC|CLAUDE|CODEX|GEMINI|GOOGLE_AI|"
    r"AZURE_OPENAI|BEDROCK)[A-Z0-9_]*"
    r"(?:API_KEY|TOKEN|SECRET|CREDENTIAL|OAUTH)[A-Z0-9_]*\b",
    re.IGNORECASE,
)
ACTIONS_SECRET_OR_VARIABLE = re.compile(
    r"\$\{\{[^}\r\n]*\b(?:secrets|vars)\b",
    re.IGNORECASE,
)
COPILOT_MARKER = re.compile(
    r"(?:@github/copilot\b|\bgithub[_-]copilot\b)", re.IGNORECASE)
MODEL_CLI = re.compile(
    r"(?:"
    r"\bcodex\s+(?:exec|sandbox)\b|"
    r"\bclaude(?:\s+(?:-p|--print|--model|review|code))?\b|"
    r"\bgemini\s+(?:--prompt|-p|chat|run)\b|"
    r"\b(?:openai|anthropic)\s+(?:api|chat|responses?|messages?|run)\b|"
    r"\b(?:npx|npm\s+exec|pnpm\s+dlx|yarn\s+dlx|bunx|pipx\s+run|uvx)"
    r"\s+(?:@openai/codex|@anthropic-ai/claude-code|@google/gemini-cli)\b|"
    r"\bpython(?:3(?:\.\d+)?)?\s+-m\s+(?:openai|anthropic)\b|"
    r"\b(?:pip|pip3|python(?:3(?:\.\d+)?)?\s+-m\s+pip)\s+install"
    r"(?:\s+[^\s]+)*\s+(?:openai|anthropic|google-generativeai)\b|"
    r"\b(?:npm|pnpm|yarn|bun)\s+(?:install|add)\s+"
    r"(?:@openai/codex|@anthropic-ai/claude-code|@google/gemini-cli)\b|"
    r"\bgh\s+models\s+(?:run|eval|evaluate)\b|"
    r"\bgh\s+copilot\b|"
    r"\bcopilot\s+(?:-p|--prompt|suggest|explain|run|agent)\b|"
    r"\b(?:npx|npm\s+exec|pnpm\s+dlx|yarn\s+dlx|bunx)\s+"
    r"@github/copilot(?:-cli)?\b|"
    r"\bollama\s+(?:run|serve|pull)\b|"
    r"\bgcloud(?:\s+beta)?\s+(?:ai|vertex)\b|"
    r"\baws\s+bedrock-runtime\s+invoke-model\b"
    r")",
    re.IGNORECASE,
)
PROVIDER_API_ENDPOINT = re.compile(
    r"(?:"
    r"api\.openai\.com|"
    r"api\.anthropic\.com|"
    r"api(?:\.[a-z0-9-]+)?\.githubcopilot\.com|"
    r"copilot-proxy\.githubusercontent\.com|"
    r"copilot\.github\.com|"
    r"models\.github\.ai|"
    r"generativelanguage\.googleapis\.com|"
    r"api-inference\.huggingface\.co|"
    r"[a-z0-9.-]+\.openai\.azure\.com|"
    r"bedrock-runtime\.[a-z0-9-]+\.amazonaws\.com|"
    r"(?:localhost|127\.0\.0\.1):11434/api/(?:chat|generate)"
    r")",
    re.IGNORECASE,
)
PROVIDER_SDK = re.compile(
    r"(?:"
    r"\b(?:from|import)\s+(?:openai|anthropic|google\.(?:genai|generativeai))\b|"
    r"\b(?:from|import)\s+github[_-]copilot\b|"
    r"\bfrom\s+['\"](?:openai|@anthropic-ai/sdk|@google/genai)['\"]|"
    r"\bfrom\s+['\"]@github/copilot(?:-sdk)?['\"]|"
    r"\brequire\(\s*['\"](?:openai|@anthropic-ai/sdk|@google/genai|"
    r"@github/copilot(?:-sdk)?)['\"]\s*\)"
    r")",
    re.IGNORECASE,
)


class WorkflowPolicyError(ValueError):
    """Raised when candidate YAML cannot be handled safely and completely."""


class WorkflowLoader(yaml.SafeLoader):
    """Safe YAML 1.2-like loader that rejects aliases and duplicate keys."""

    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            event = self.peek_event()
            raise WorkflowPolicyError(
                f"YAML aliases are forbidden at line {event.start_mark.line + 1}")
        return super().compose_node(parent, index)

    def construct_mapping(self, node, deep=False):
        if not isinstance(node, yaml.MappingNode):
            raise WorkflowPolicyError("only standard YAML mappings are supported")
        seen = set()
        for key_node, _ in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                raise WorkflowPolicyError(
                    f"YAML merge keys are forbidden at line "
                    f"{key_node.start_mark.line + 1}")
            key = self.construct_object(key_node, deep=True)
            if not isinstance(key, str):
                raise WorkflowPolicyError(
                    f"mapping keys must be strings at line "
                    f"{key_node.start_mark.line + 1}")
            if key in seen:
                raise WorkflowPolicyError(
                    f"duplicate mapping key is forbidden at line "
                    f"{key_node.start_mark.line + 1}")
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


# PyYAML follows YAML 1.1 and otherwise resolves ``on``/``off`` as booleans.
# GitHub workflow keys use YAML 1.2 behavior, where only true/false are boolean.
WorkflowLoader.yaml_implicit_resolvers = {
    first: [
        resolver for resolver in resolvers
        if resolver[0] != "tag:yaml.org,2002:bool"
    ]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
WorkflowLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|false)$", re.IGNORECASE),
    list("tTfF"),
)


def iter_workflow_files(directory):
    """Return sorted regular, bounded ``.yml`` and ``.yaml`` files."""
    root = Path(directory)
    try:
        root_stat = root.lstat()
    except OSError as exc:
        raise WorkflowPolicyError(
            f"cannot inspect workflow directory: {root}") from exc
    if stat.S_ISLNK(root_stat.st_mode):
        raise WorkflowPolicyError(
            f"workflow directory must not be a symbolic link: {root}")
    if not stat.S_ISDIR(root_stat.st_mode):
        raise WorkflowPolicyError(
            f"workflow path is not a directory: {root}")

    paths = []

    def walk_error(exc):
        raise WorkflowPolicyError(
            f"cannot enumerate workflow directory: {root}") from exc

    for current, directories, filenames in os.walk(
            root, topdown=True, followlinks=False, onerror=walk_error):
        current_path = Path(current)
        directories.sort()
        filenames.sort()
        for name in directories:
            path = current_path / name
            if stat.S_ISLNK(path.lstat().st_mode):
                raise WorkflowPolicyError(
                    f"symbolic link is not allowed in workflow directory: {path}")
        for name in filenames:
            path = current_path / name
            file_stat = path.lstat()
            if stat.S_ISLNK(file_stat.st_mode):
                raise WorkflowPolicyError(
                    f"symbolic link is not allowed in workflow directory: {path}")
            if path.suffix.casefold() not in WORKFLOW_SUFFIXES:
                continue
            if not stat.S_ISREG(file_stat.st_mode):
                raise WorkflowPolicyError(
                    f"workflow is not a regular file: {path}")
            if file_stat.st_size > MAX_WORKFLOW_BYTES:
                raise WorkflowPolicyError(
                    f"workflow exceeds {MAX_WORKFLOW_BYTES} bytes: {path}")
            paths.append(path)
            if len(paths) > MAX_WORKFLOW_FILES:
                raise WorkflowPolicyError(
                    f"workflow directory exceeds {MAX_WORKFLOW_FILES} files")

    if not paths:
        raise WorkflowPolicyError(
            f"workflow directory contains no .yml or .yaml files: {root}")
    return sorted(paths)


def load_workflow_document(path):
    """Parse one workflow with the trusted strict loader."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise WorkflowPolicyError(
            f"workflow is not UTF-8 text: {path}") from exc
    if "\x00" in text:
        raise WorkflowPolicyError(f"workflow contains a NUL byte: {path}")
    try:
        document = yaml.load(text, Loader=WorkflowLoader)
    except WorkflowPolicyError:
        raise
    except yaml.YAMLError as exc:
        raise WorkflowPolicyError(
            f"workflow is invalid or unsupported YAML: {path}") from exc
    if not isinstance(document, dict):
        raise WorkflowPolicyError(
            f"workflow root must be a mapping: {path}")
    return document


def safe_child_location(location, key, index):
    """Build a useful location without echoing arbitrary candidate content."""
    if SAFE_LOCATION_KEY.fullmatch(key):
        return f"{location}.{key}"
    return f"{location}.key[{index}]"


def scalar_findings(path, location, value, command=False):
    """Inspect one decoded scalar without retaining or printing its content."""
    findings = []
    folded = value.casefold()
    for folded_marker, marker in RETIRED_MARKERS_CASEFOLDED:
        if folded_marker in folded:
            findings.append(
                f"{path}:{location}: retired Actions configuration marker "
                f"is forbidden ({marker})")
    if PROVIDER_CREDENTIAL.search(value):
        findings.append(
            f"{path}:{location}: provider credential marker is forbidden")
    if ACTIONS_SECRET_OR_VARIABLE.search(value):
        findings.append(
            f"{path}:{location}: repository Actions secret/variable "
            "reference is forbidden")
    if COPILOT_MARKER.search(value):
        findings.append(
            f"{path}:{location}: GitHub Copilot marker is forbidden")
    if PROVIDER_API_ENDPOINT.search(value):
        findings.append(
            f"{path}:{location}: provider API endpoint is forbidden")
    if command and MODEL_CLI.search(value):
        findings.append(
            f"{path}:{location}: model/provider CLI invocation is forbidden")
    if command and PROVIDER_SDK.search(value):
        findings.append(
            f"{path}:{location}: provider SDK invocation is forbidden")
    if command and any(
            marker in folded for marker in HOSTED_EVALUATOR_MARKERS):
        findings.append(
            f"{path}:{location}: hosted evaluator invocation is forbidden")
    return findings


def action_reference_findings(path, location, reference):
    """Validate one decoded ``uses`` reference against the base allowlist."""
    folded = reference.casefold()
    findings = []
    if any(marker in folded for marker in PROVIDER_ACTION_MARKERS):
        findings.append(
            f"{path}:{location}: model/provider action is forbidden")
    if any(marker in folded for marker in HOSTED_EVALUATOR_MARKERS):
        findings.append(
            f"{path}:{location}: hosted evaluator action is forbidden")
    if reference.startswith("./"):
        findings.append(f"{path}:{location}: local actions are forbidden")
        return findings
    if folded.startswith("docker://"):
        findings.append(f"{path}:{location}: Docker actions are forbidden")
        return findings

    if "@" not in reference:
        findings.append(
            f"{path}:{location}: external action is not pinned to a commit SHA")
        action_repository = folded
    else:
        action_repository, revision = reference.rsplit("@", 1)
        action_repository = action_repository.casefold()
        if COMMIT_SHA.fullmatch(revision) is None:
            findings.append(
                f"{path}:{location}: external action is not pinned to a commit SHA")
    if action_repository not in APPROVED_EXTERNAL_ACTION_REPOSITORIES:
        findings.append(
            f"{path}:{location}: external action repository is not approved")
    return findings


def inspect_value(path, value, location="$", command=False):
    """Recursively inspect every decoded mapping, sequence, and scalar."""
    if isinstance(value, dict):
        findings = []
        sensitive_keys = set()
        folded_keys = {
            key.casefold() for key in value
            if isinstance(key, str)
        }
        if {"uses", "run"} <= folded_keys:
            findings.append(
                f"{path}:{location}: a mapping cannot contain both uses and run")
        for index, (key, child) in enumerate(value.items()):
            if not isinstance(key, str):
                raise WorkflowPolicyError(
                    f"mapping key is not a string: {path}:{location}")
            child_location = safe_child_location(location, key, index)
            findings.extend(scalar_findings(
                path, f"{child_location}.key", key))
            folded_key = key.casefold()
            if folded_key in {"uses", "run"}:
                if folded_key in sensitive_keys:
                    raise WorkflowPolicyError(
                        f"duplicate semantic key is forbidden: "
                        f"{path}:{child_location}")
                sensitive_keys.add(folded_key)
                if not isinstance(child, str):
                    findings.append(
                        f"{path}:{child_location}: {folded_key} must be a string")
                    continue
                findings.extend(scalar_findings(
                    path, child_location, child,
                    command=folded_key == "run"))
                if folded_key == "uses":
                    findings.extend(action_reference_findings(
                        path, child_location, child))
                continue
            if (folded_key == "models" and isinstance(child, str)
                    and child.casefold() in {"read", "write"}):
                findings.append(
                    f"{path}:{child_location}: GitHub Models permission is forbidden")
            if folded_key == "copilot-requests":
                findings.append(
                    f"{path}:{child_location}: GitHub Copilot requests "
                    "permission is forbidden")
            findings.extend(inspect_value(
                path, child, child_location, command=command))
        return findings

    if isinstance(value, list):
        return [
            finding
            for index, child in enumerate(value)
            for finding in inspect_value(
                path, child, f"{location}[{index}]", command=command)
        ]

    if isinstance(value, str):
        return scalar_findings(path, location, value, command=command)
    if value is None or isinstance(value, (bool, int, float)):
        return []
    raise WorkflowPolicyError(
        f"unsupported YAML value type: {path}:{location}")


def scan_workflow(path):
    """Return semantic policy findings for one inert workflow file."""
    return inspect_value(path, load_workflow_document(path))


def validate_directory(directory):
    """Return every policy finding under one candidate workflow directory."""
    return [
        finding
        for path in iter_workflow_files(directory)
        for finding in scan_workflow(path)
    ]


def iter_action_references(value):
    """Yield decoded action references from an already validated document."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key.casefold() == "uses" and isinstance(child, str):
                yield child
            yield from iter_action_references(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_action_references(child)


def trust_root_inventory(root_path):
    """Return a bounded recursive trust inventory plus unsafe-entry findings."""
    root = Path(root_path)
    try:
        root_stat = root.lstat()
    except OSError as exc:
        raise WorkflowPolicyError(
            f"cannot inspect trust-root checkout: {root}") from exc
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        raise WorkflowPolicyError(
            f"trust-root checkout must be a regular directory: {root}")

    inventory = {}
    findings = []
    file_count = 0
    entry_count = 0
    total_bytes = 0

    def add_file(path, relative, required):
        nonlocal file_count, entry_count, total_bytes
        if relative in inventory:
            return
        try:
            file_stat = path.lstat()
        except OSError:
            if required:
                findings.append(
                    f"{path}: required candidate trust-root entry is missing")
            return
        if stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISREG(
                file_stat.st_mode):
            findings.append(
                f"{path}: trust-root entry must be a regular file")
            return
        if file_stat.st_size > MAX_TRUST_ROOT_BYTES:
            findings.append(
                f"{path}: trust-root file exceeds {MAX_TRUST_ROOT_BYTES} bytes")
            return
        file_count += 1
        entry_count += 1
        total_bytes += file_stat.st_size
        if file_count > MAX_TRUST_ROOT_FILES:
            raise WorkflowPolicyError(
                f"trust-root inventory exceeds {MAX_TRUST_ROOT_FILES} files")
        if entry_count > MAX_TRUST_ROOT_ENTRIES:
            raise WorkflowPolicyError(
                f"trust-root inventory exceeds {MAX_TRUST_ROOT_ENTRIES} entries")
        if total_bytes > MAX_TRUST_ROOT_TOTAL_BYTES:
            raise WorkflowPolicyError(
                "trust-root inventory exceeds its total byte bound")
        inventory[relative] = (
            "file",
            file_stat.st_size,
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )

    for relative in REQUIRED_TRUST_ROOT_FILES:
        add_file(root / relative, relative, required=True)
    for relative in OPTIONAL_TRUST_ROOT_FILES:
        add_file(root / relative, relative, required=False)

    for relative_directory in REQUIRED_TRUST_ROOT_DIRECTORIES:
        directory = root / relative_directory
        try:
            directory_stat = directory.lstat()
        except OSError:
            findings.append(
                f"{directory}: required candidate trust-root entry is missing")
            continue
        if stat.S_ISLNK(directory_stat.st_mode) or not stat.S_ISDIR(
                directory_stat.st_mode):
            findings.append(
                f"{directory}: trust-root entry must be a regular directory")
            continue
        inventory[f"{relative_directory}/"] = ("directory", 0, "")
        entry_count += 1

        def walk_error(exc):
            raise WorkflowPolicyError(
                f"cannot enumerate protected trust-root directory: {directory}") from exc

        for current, directories, filenames in os.walk(
                directory, topdown=True, followlinks=False,
                onerror=walk_error):
            current_path = Path(current)
            directories.sort()
            filenames.sort()
            retained_directories = []
            for name in directories:
                path = current_path / name
                entry_stat = path.lstat()
                child_relative = path.relative_to(root).as_posix()
                if stat.S_ISLNK(entry_stat.st_mode) or not stat.S_ISDIR(
                        entry_stat.st_mode):
                    findings.append(
                        f"{path}: trust-root entry must be a regular directory")
                    continue
                inventory[f"{child_relative}/"] = ("directory", 0, "")
                entry_count += 1
                if entry_count > MAX_TRUST_ROOT_ENTRIES:
                    raise WorkflowPolicyError(
                        f"trust-root inventory exceeds "
                        f"{MAX_TRUST_ROOT_ENTRIES} entries")
                retained_directories.append(name)
            directories[:] = retained_directories
            for name in filenames:
                path = current_path / name
                add_file(
                    path, path.relative_to(root).as_posix(), required=True)
    return inventory, findings


def validate_trust_root_presence(candidate_root):
    """Require a safe, bounded candidate copy of the complete trust closure."""
    root = Path(candidate_root)
    _, findings = trust_root_inventory(root)
    return findings


def validate_trust_root_integrity(
        candidate_root, trusted_root, allow_trust_root_upgrade=False):
    """Compare recursive candidate inventory and bytes with the trusted base."""
    candidate = Path(candidate_root)
    trusted = Path(trusted_root)
    trusted_inventory, trusted_findings = trust_root_inventory(trusted)
    if trusted_findings:
        raise WorkflowPolicyError(
            "trusted base contains an unsafe or incomplete trust-root inventory")
    candidate_inventory, _ = trust_root_inventory(candidate)
    if allow_trust_root_upgrade:
        return []

    findings = []
    for relative in sorted({*trusted_inventory, *candidate_inventory}):
        if candidate_inventory.get(relative) != trusted_inventory.get(relative):
            safe_relative = relative.encode(
                "unicode_escape", errors="backslashreplace").decode("ascii")
            findings.append(
                f"{candidate}/{safe_relative}: protected trust-root inventory "
                "or bytes differ from the trusted base without exact OWNER approval")
    return findings


def validate_candidate_repository(
        candidate_root, trusted_root, workflow_directory,
        allow_trust_root_upgrade=False):
    """Validate candidate workflows and the complete protected trust closure."""
    root = Path(candidate_root).absolute()
    trusted = Path(trusted_root).absolute()
    workflows = Path(workflow_directory).absolute()
    expected = root / ".github" / "workflows"
    if workflows != expected:
        raise WorkflowPolicyError(
            "workflow directory must be candidate_root/.github/workflows")
    return [
        *validate_trust_root_presence(root),
        *validate_trust_root_integrity(
            root, trusted, allow_trust_root_upgrade),
        *validate_directory(workflows),
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate-root",
        required=True,
        help="Candidate checkout root whose trust-root files must remain present",
    )
    parser.add_argument(
        "--trusted-root",
        required=True,
        help="Trusted base checkout used for byte-for-byte closure comparison",
    )
    parser.add_argument(
        "--allow-trust-root-upgrade",
        action="store_true",
        help="Permit changed closure bytes after exact commit-bound OWNER approval",
    )
    parser.add_argument(
        "workflow_directory",
        help="Candidate .github/workflows directory to parse as inert data",
    )
    args = parser.parse_args(argv)
    try:
        findings = validate_candidate_repository(
            args.candidate_root,
            args.trusted_root,
            args.workflow_directory,
            allow_trust_root_upgrade=args.allow_trust_root_upgrade,
        )
    except (OSError, WorkflowPolicyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if findings:
        print("Candidate workflow policy validation failed:", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1
    print("Candidate workflow policy validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
