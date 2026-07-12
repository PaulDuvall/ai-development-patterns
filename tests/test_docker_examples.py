"""Behavioral tests for the runnable, provider-free Docker examples."""

import errno
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).parent.parent
PARALLEL = ROOT / "examples" / "parallel-agents"
RUNNER = PARALLEL / "scripts" / "agent_runner.py"
COORDINATOR = PARALLEL / "scripts" / "coordinator.py"
MERGE_SCRIPT = PARALLEL / "scripts" / "merge-parallel-work.sh"
TASKS = PARALLEL / "config" / "tasks.yaml"
SANDBOX = ROOT / "examples" / "security-sandbox"
HEALTHCHECK = SANDBOX / "healthcheck.py"


HEALTHCHECK_SPEC = importlib.util.spec_from_file_location(
    "sandbox_healthcheck", HEALTHCHECK)
SANDBOX_HEALTHCHECK = importlib.util.module_from_spec(HEALTHCHECK_SPEC)
HEALTHCHECK_SPEC.loader.exec_module(SANDBOX_HEALTHCHECK)


def run_git(repository, *arguments):
    """Run Git in an isolated test repository and return standard output."""
    return subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def initialize_git_repository(path):
    """Create a repository with deterministic local test identity."""
    path.mkdir()
    run_git(path, "init", "--initial-branch=main")
    run_git(path, "config", "user.name", "Example Tester")
    run_git(path, "config", "user.email", "example@example.com")
    (path / ".gitignore").write_text("\n", encoding="utf-8")


class ProbeSocket:
    """Small context-managed socket double for egress-probe tests."""

    def __init__(self, error_number=None):
        self.error_number = error_number
        self.timeout = None
        self.endpoint = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def settimeout(self, timeout):
        self.timeout = timeout

    def connect(self, endpoint):
        self.endpoint = endpoint
        if self.error_number is not None:
            raise OSError(self.error_number, os.strerror(self.error_number))


@pytest.mark.parametrize(
    ("task_id", "artifact"),
    [
        ("frontend-components", "components/TaskList.tsx"),
        ("backend-api", "server.js"),
        ("database-schema", "schema.prisma"),
        ("test-suite", "test-plan.md"),
    ],
)
def test_parallel_runner_generates_stable_local_artifacts(
        tmp_path, task_id, artifact):
    """Every configured simulation task runs locally without a model provider."""
    workspace = tmp_path / task_id
    memory = tmp_path / "shared" / "agent-memory.json"
    environment = {**os.environ, "AGENT_ID": f"test-{task_id}"}
    command = [
        sys.executable,
        str(RUNNER),
        "--task-file", str(TASKS),
        "--task-id", task_id,
        "--workspace", str(workspace),
        "--shared-memory", str(memory),
    ]

    first = subprocess.run(
        command, check=True, capture_output=True, text=True, env=environment)
    first_artifact = (workspace / artifact).read_text(encoding="utf-8")
    first_memory = memory.read_text(encoding="utf-8")
    second = subprocess.run(
        command, check=True, capture_output=True, text=True, env=environment)

    result = json.loads(first.stdout)
    memory_document = json.loads(first_memory)
    configured_task = next(
        task for task in yaml.safe_load(TASKS.read_text(encoding="utf-8"))[
            "tasks"]
        if task["id"] == task_id
    )
    assert result == json.loads(second.stdout)
    assert result["mode"] == "deterministic-local-simulator"
    assert result["execution"] == "simulated"
    assert result["status"] == "fixture_generated"
    assert result["dependencies"] == configured_task["dependencies"]
    assert result["model_calls"] == 0
    assert result["provider_api_calls"] == 0
    assert artifact in result["artifacts"]
    assert memory_document["agents"][f"test-{task_id}"] == {
        "artifacts": [artifact],
        "dependencies": configured_task["dependencies"],
        "execution": "simulated",
        "status": "fixture_generated",
        "task_id": task_id,
    }
    assert (workspace / artifact).read_text(encoding="utf-8") == first_artifact
    assert memory.read_text(encoding="utf-8") == first_memory


def test_parallel_runner_rejects_unknown_tasks(tmp_path):
    """An unconfigured task cannot silently produce a plausible artifact."""
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--task-file", str(TASKS),
            "--task-id", "not-configured",
            "--workspace", str(tmp_path / "workspace"),
            "--shared-memory", str(tmp_path / "memory.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "unknown task" in result.stderr


def test_parallel_runner_rejects_fixture_contract_drift(tmp_path):
    """A config artifact cannot drift from the reviewed simulator bytes."""
    configuration = yaml.safe_load(TASKS.read_text(encoding="utf-8"))
    configuration["tasks"][0]["fixture_contract"]["artifacts"][0][
        "sha256"] = "0" * 64
    tampered = tmp_path / "tasks.yaml"
    tampered.write_text(yaml.safe_dump(configuration), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--task-file", str(tampered),
            "--task-id", "frontend-components",
            "--workspace", str(tmp_path / "workspace"),
            "--shared-memory", str(tmp_path / "memory.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "SHA-256 does not match the simulator fixture" in result.stderr


def test_parallel_coordinator_writes_a_stable_one_shot_report(tmp_path):
    """The coordinator summarizes actual artifacts and shared-memory state."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "artifact.txt").write_text("local result\n", encoding="utf-8")
    memory = tmp_path / "shared-memory.json"
    memory.write_text(
        json.dumps({
            "version": 1,
            "agents": {"frontend": {
                "dependencies": [],
                "execution": "simulated",
                "status": "fixture_generated",
            }},
        }),
        encoding="utf-8",
    )
    report_dir = tmp_path / "reports"
    command = [
        sys.executable,
        str(COORDINATOR),
        "--watch-dir", str(workspace),
        "--report-dir", str(report_dir),
        "--shared-memory", str(memory),
        "--once",
    ]

    subprocess.run(command, check=True, capture_output=True, text=True)
    report_path = report_dir / "parallel-agent-status.json"
    first = report_path.read_text(encoding="utf-8")
    subprocess.run(command, check=True, capture_output=True, text=True)
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report_path.read_text(encoding="utf-8") == first
    assert report["agents"] == {"frontend": {
        "dependencies": [],
        "execution": "simulated",
        "status": "fixture_generated",
    }}
    assert report["artifacts"] == ["artifact.txt"]
    assert report["execution"] == "simulated"
    assert report["model_calls"] == 0
    assert report["provider_api_calls"] == 0


def test_parallel_image_runtime_has_no_provider_sdk_or_credentials():
    """The simulator image cannot accidentally become a paid provider client."""
    requirements = (
        PARALLEL / "docker" / "requirements.txt"
    ).read_text(encoding="utf-8").casefold()
    runtime_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (RUNNER, COORDINATOR)
    ).casefold()

    assert "openai" not in requirements
    assert "anthropic" not in requirements
    assert "api.openai.com" not in runtime_text
    assert "api.anthropic.com" not in runtime_text
    assert "openai_api_key" not in runtime_text
    assert "anthropic_api_key" not in runtime_text
    assert not (PARALLEL / "scripts" / "shared_memory.py").exists()


@pytest.mark.parametrize(
    ("error_number", "isolated"),
    [
        (errno.ENETUNREACH, True),
        (errno.EACCES, True),
        (errno.ECONNREFUSED, False),
    ],
)
def test_sandbox_network_probe_only_accepts_explicit_policy_denial(
        monkeypatch, error_number, isolated):
    """Missing/unreachable services cannot be mistaken for proven isolation."""
    fake_socket = ProbeSocket(error_number)
    monkeypatch.setattr(
        SANDBOX_HEALTHCHECK.socket,
        "socket",
        lambda *_arguments: fake_socket,
    )
    monkeypatch.setattr(
        SANDBOX_HEALTHCHECK.socket,
        "if_nameindex",
        lambda: [(1, "lo")],
    )

    result, detail = SANDBOX_HEALTHCHECK.probe_network_isolation()

    assert result is isolated
    assert fake_socket.endpoint == ("1.1.1.1", 443)
    assert fake_socket.timeout == 2.0
    if isolated:
        assert "kernel blocked" in detail
    else:
        assert "isolation not proven" in detail


def test_sandbox_network_probe_rejects_internal_bridge_interfaces(monkeypatch):
    """No-route errors cannot bless a container that still has peer networking."""
    fake_socket = ProbeSocket(errno.ENETUNREACH)
    monkeypatch.setattr(
        SANDBOX_HEALTHCHECK.socket,
        "socket",
        lambda *_arguments: fake_socket,
    )
    monkeypatch.setattr(
        SANDBOX_HEALTHCHECK.socket,
        "if_nameindex",
        lambda: [(1, "lo"), (2, "eth0")],
    )

    isolated, detail = SANDBOX_HEALTHCHECK.probe_network_isolation()

    assert isolated is False
    assert "non-loopback interface(s) are present: eth0" in detail


def test_sandbox_network_probe_rejects_reachable_egress(monkeypatch):
    """A successful TCP connection must fail the isolation health check."""
    fake_socket = ProbeSocket()
    monkeypatch.setattr(
        SANDBOX_HEALTHCHECK.socket,
        "socket",
        lambda *_arguments: fake_socket,
    )

    isolated, detail = SANDBOX_HEALTHCHECK.probe_network_isolation()

    assert isolated is False
    assert detail == "TCP egress reached 1.1.1.1:443"


def test_sandbox_network_probe_rejects_dns_and_malformed_configuration(
        monkeypatch):
    """Ambiguous DNS/tooling configuration fails closed before probing."""
    monkeypatch.setenv("SANDBOX_NETWORK_PROBE_HOST", "example.invalid")
    isolated, detail = SANDBOX_HEALTHCHECK.probe_network_isolation()

    assert isolated is False
    assert "must be a numeric IP address" in detail


def test_sandbox_detached_compose_service_has_an_explicit_keepalive():
    """The smallest detached sandbox cannot fall through an interactive shell."""
    compose = (
        SANDBOX / "docker-compose.basic.yml"
    ).read_text(encoding="utf-8")

    assert "/workspace/init-workspace.sh && exec tail -f /dev/null" in compose
    assert "network_mode: none" in compose


def test_sandbox_generator_templates_match_the_tracked_runtime_files():
    """The convenience script cannot regenerate obsolete security checks."""
    generator = (SANDBOX / "ai-sandbox.sh").read_text(encoding="utf-8")

    def embedded(marker):
        start_marker = f'cat > "${marker}" << \'EOF\'\n'
        start = generator.index(start_marker) + len(start_marker)
        end = generator.index("\nEOF", start)
        return generator[start:end] + "\n"

    assert embedded("healthcheck_file") == HEALTHCHECK.read_text(
        encoding="utf-8")
    assert embedded("init_file") == (
        SANDBOX / "init-workspace.sh").read_text(encoding="utf-8")


def test_sandbox_manager_is_fail_closed_and_never_installs_binaries():
    """The helper validates prerequisites and propagates insecure-state failure."""
    manager = (SANDBOX / "ai-sandbox.sh").read_text(encoding="utf-8")

    assert "require_docker_compose" in manager
    assert "install_docker_compose" not in manager
    assert "releases/download" not in manager
    assert "shell_profile" not in manager
    assert "local validation_failed=false" in manager
    assert 'if [[ "$validation_failed" == true ]]' in manager
    assert 'log_error "Security validation failed"' in manager
    assert "claude --help" not in manager
    assert "sudo usermod" not in manager
    assert "if sudo " not in manager
    assert "open /Applications/Docker.app" not in manager
    assert "if colima start" not in manager


def run_fake_sandbox_validation(mode):
    """Run the sourced manager against a deterministic fake Docker CLI."""
    manager = SANDBOX / "ai-sandbox.sh"
    shell = f"""
source {shlex.quote(str(manager))}
FAKE_MODE={shlex.quote(mode)}
docker() {{
    if [[ "$1" == "ps" ]]; then
        printf '%s\n' "$SANDBOX_NAME"
        return 0
    fi
    if [[ "$1" == "inspect" ]]; then
        case "$*" in
            *NetworkMode*)
                [[ "$FAKE_MODE" == secure ]] && echo none || echo bridge
                ;;
            *CapDrop*)
                [[ "$FAKE_MODE" == secure ]] && echo '[ALL]' || echo '[]'
                ;;
            *'.Mounts'*)
                if [[ "$FAKE_MODE" != secure ]]; then
                    echo '/home/example/.ssh|/workspace/stolen-credentials'
                fi
                ;;
            *Memory*)
                [[ "$FAKE_MODE" == secure ]] && echo 4294967296 || echo 0
                ;;
        esac
        return 0
    fi
    if [[ "$1" == "exec" ]]; then
        case "$*" in
            *' id -u')
                [[ "$FAKE_MODE" == secure ]] && echo 1000 || echo 0
                return 0
                ;;
            *'/workspace/src')
                [[ "$FAKE_MODE" == secure ]]
                return
                ;;
            *'/workspace/healthcheck.py')
                if [[ "$FAKE_MODE" == secure ]]; then
                    echo 'Synthetic health: PASS'
                    return 0
                fi
                echo 'Synthetic health: FAIL'
                return 1
                ;;
        esac
    fi
    return 1
}}
validate_security
"""
    return subprocess.run(
        ["bash", "-c", shell],
        capture_output=True,
        check=False,
        text=True,
    )


def test_sandbox_manager_validation_passes_only_a_secure_container():
    completed = run_fake_sandbox_validation("secure")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Security validation complete" in completed.stdout
    assert "Security validation failed" not in completed.stdout


def test_sandbox_manager_validation_accumulates_every_failure():
    completed = run_fake_sandbox_validation("insecure")

    assert completed.returncode == 1
    for finding in (
        "Network isolation: DISABLED",
        "Non-root user: DISABLED",
        "Capabilities: NOT PROPERLY DROPPED",
        "Sensitive mount detected",
        "Memory limit: NOT SET",
        "Source directory: WRITABLE",
        "Fail-closed container health check: FAILED",
        "Security validation failed",
    ):
        assert finding in completed.stdout
    assert "Security validation complete" not in completed.stdout


def test_parallel_merge_stages_a_conservative_json_resolution(tmp_path):
    """Non-overlapping JSON edits merge and leave no unmerged index entries."""
    repository = tmp_path / "repository"
    initialize_git_repository(repository)
    document = repository / "settings.json"
    document.write_text(
        json.dumps({"common": 1, "ours": 0, "theirs": 0}) + "\n",
        encoding="utf-8",
    )
    run_git(repository, "add", ".")
    run_git(repository, "commit", "-m", "base")
    run_git(repository, "branch", "agent/json-conflict")

    document.write_text(
        json.dumps({"common": 1, "ours": 1, "theirs": 0}) + "\n",
        encoding="utf-8",
    )
    run_git(repository, "commit", "-am", "main change")
    run_git(repository, "switch", "agent/json-conflict")
    document.write_text(
        json.dumps({"common": 1, "ours": 0, "theirs": 1}) + "\n",
        encoding="utf-8",
    )
    run_git(repository, "commit", "-am", "agent change")
    run_git(repository, "switch", "main")

    environment = {
        **os.environ,
        "MAIN_BRANCH": "main",
        "REPORTS_DIR": str(repository / "reports"),
    }
    subprocess.run(
        [
            "bash",
            "-c",
            'source "$1"; merge_agent_branch agent/json-conflict',
            "merge-test",
            str(MERGE_SCRIPT),
        ],
        cwd=repository,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(document.read_text(encoding="utf-8")) == {
        "common": 1,
        "ours": 1,
        "theirs": 1,
    }
    assert run_git(repository, "branch", "--show-current") == "main"
    assert run_git(repository, "ls-files", "--unmerged") == ""
    assert run_git(repository, "branch", "--list", "temp-merge-*") == ""
    assert len(run_git(repository, "show", "-s", "--format=%P").split()) == 2
    reports = sorted((repository / "reports").glob("merge_*.json"))
    assert len(reports) == 1
    assert json.loads(reports[0].read_text(encoding="utf-8"))["status"] == (
        "success")


def test_parallel_merge_handles_multiple_noop_branches_and_cleans_up(tmp_path):
    """Report files cannot turn a later already-merged branch into an empty commit."""
    repository = tmp_path / "repository"
    initialize_git_repository(repository)
    (repository / "tracked.txt").write_text("base\n", encoding="utf-8")
    run_git(repository, "add", ".")
    run_git(repository, "commit", "-m", "base")
    original_head = run_git(repository, "rev-parse", "HEAD")
    run_git(repository, "branch", "agent/noop-one")
    run_git(repository, "branch", "agent/noop-two")

    environment = {
        **os.environ,
        "MAIN_BRANCH": "main",
        # Deliberately leave generated reports untracked inside the repository.
        "REPORTS_DIR": str(repository / "reports"),
    }
    subprocess.run(
        [
            "bash",
            "-c",
            (
                'source "$1"; '
                "merge_agent_branch agent/noop-one; "
                "merge_agent_branch agent/noop-two"
            ),
            "merge-test",
            str(MERGE_SCRIPT),
        ],
        cwd=repository,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    assert run_git(repository, "rev-parse", "HEAD") == original_head
    assert run_git(repository, "branch", "--show-current") == "main"
    assert run_git(repository, "branch", "--list", "temp-merge-*") == ""
    reports = sorted((repository / "reports").glob("merge_*.json"))
    assert len(reports) == 2
    assert {
        json.loads(path.read_text(encoding="utf-8"))["status"]
        for path in reports
    } == {"no_changes"}
