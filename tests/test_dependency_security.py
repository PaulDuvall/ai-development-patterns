"""Regression tests for dependency maintenance and review coverage."""

import json
import re
import tomllib
from pathlib import Path

import yaml


ROOT = Path(__file__).parent.parent
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
DEPENDENCY_WORKFLOW = ROOT / ".github" / "workflows" / "dependency-security.yml"
PATTERN_VALIDATION_WORKFLOW = (
    ROOT / ".github" / "workflows" / "pattern-validation.yml")
DOCKER_COMPATIBILITY_WORKFLOW = (
    ROOT / ".github" / "workflows" / "docker-example-compatibility.yml")
PROJECT = ROOT / "pyproject.toml"
TEST_REQUIREMENTS = ROOT / "tests" / "requirements.txt"
GATEWAY_ROOT = (
    ROOT / "examples" / "centralized-rules" / "gateway-strategy")
PARALLEL_AGENT_ROOT = ROOT / "examples" / "parallel-agents"
SECURITY_SANDBOX_ROOT = ROOT / "examples" / "security-sandbox"

PYTHON_DIRECTORIES = {
    "/",
    "/.github",
    "/examples/parallel-agents/docker",
    "/examples/security-sandbox",
    "/examples/spec-driven-development",
    "/experiments/examples/test-promotion",
    "/tests",
}
NPM_DIRECTORIES = {
    "/examples/centralized-rules/gateway-strategy/ai-dev-cli",
    "/examples/centralized-rules/gateway-strategy/ai-gateway",
    "/examples/centralized-rules/gateway-strategy/org-ai-client",
}
DOCKER_DIRECTORIES = {
    "/examples/parallel-agents/docker",
    "/examples/security-sandbox",
}


def dependabot_update(ecosystem):
    """Return the single updater for an ecosystem."""
    document = yaml.safe_load(DEPENDABOT.read_text(encoding="utf-8"))
    matches = [
        update for update in document["updates"]
        if update["package-ecosystem"] == ecosystem
    ]
    assert len(matches) == 1
    return matches[0]


def repository_directory(path):
    """Render a manifest parent as a Dependabot repository directory."""
    relative = path.parent.relative_to(ROOT).as_posix()
    return "/" if relative == "." else f"/{relative}"


def test_dependabot_covers_all_dependency_manifest_directories():
    """Nested example manifests must not fall outside update coverage."""
    assert set(dependabot_update("pip")["directories"]) == PYTHON_DIRECTORIES
    assert set(dependabot_update("npm")["directories"]) == NPM_DIRECTORIES
    assert set(dependabot_update("docker")["directories"]) == DOCKER_DIRECTORIES
    discovered_docker = {
        repository_directory(path)
        for path in ROOT.rglob("Dockerfile*")
        if not {".git", ".venv", "node_modules"} & set(path.parts)
    }
    assert discovered_docker == DOCKER_DIRECTORIES
    discovered_python = {
        repository_directory(path)
        for pattern in ("pyproject.toml", "requirements*.txt")
        for path in ROOT.rglob(pattern)
        if not {".venv", "node_modules"} & set(path.parts)
    }
    assert discovered_python == PYTHON_DIRECTORIES
    discovered_npm = {
        repository_directory(path)
        for path in ROOT.rglob("package.json")
        if "node_modules" not in path.parts
    }
    assert discovered_npm == NPM_DIRECTORIES


def test_dependabot_groups_compatible_updates_without_grouping_majors():
    """Minor/patch and security updates are grouped; majors stay reviewable."""
    for ecosystem, version_group, security_group in (
        ("pip", "python-minor-patch", "python-security"),
        ("npm", "npm-minor-patch", "npm-security"),
        ("docker", "docker-minor-patch", "docker-security"),
    ):
        groups = dependabot_update(ecosystem)["groups"]
        assert groups[version_group]["patterns"] == ["*"]
        assert set(groups[version_group]["update-types"]) == {"minor", "patch"}
        assert groups[version_group]["group-by"] == "dependency-name"
        assert groups[security_group]["applies-to"] == "security-updates"
        assert groups[security_group]["patterns"] == ["*"]

    actions = dependabot_update("github-actions")["groups"]
    assert set(actions["actions-minor-patch"]["update-types"]) == {
        "minor", "patch"}


def test_docker_examples_use_current_supported_python_base_families():
    """Interpreter updates must not retain a near-EOL Debian base."""
    parallel = (
        PARALLEL_AGENT_ROOT / "docker" / "Dockerfile.ai-agent"
    ).read_text(encoding="utf-8")
    sandbox = (
        SECURITY_SANDBOX_ROOT / "Dockerfile.ai-sandbox"
    ).read_text(encoding="utf-8")

    assert re.search(r"^FROM python:3\.14-slim$", parallel, re.MULTILINE)
    assert re.search(
        r"^FROM python:3\.13-slim-bookworm$", sandbox, re.MULTILINE)
    assert "https://deb.nodesource.com/setup_24.x" in parallel
    assert "setup_20.x" not in parallel
    assert "bullseye" not in parallel.casefold()
    assert "bullseye" not in sandbox.casefold()


def test_parallel_agent_build_context_contains_every_copied_path():
    """Compose and the Dockerfile must agree on the example-root context."""
    compose = yaml.safe_load(
        (PARALLEL_AGENT_ROOT / "docker-compose.parallel-agents.yml").read_text(
            encoding="utf-8"))
    builds = {
        (service["build"]["context"], service["build"]["dockerfile"])
        for service in compose["services"].values()
    }
    assert builds == {(".", "docker/Dockerfile.ai-agent")}
    assert {
        service["image"] for service in compose["services"].values()
    } == {"ai-development-patterns/parallel-agent:local"}
    assert compose["services"]["agent-backend"]["depends_on"] == {
        "agent-database": {"condition": "service_completed_successfully"},
    }
    assert compose["services"]["agent-tests"]["depends_on"] == {
        "agent-frontend": {"condition": "service_completed_successfully"},
        "agent-backend": {"condition": "service_completed_successfully"},
    }

    dockerfile = (
        PARALLEL_AGENT_ROOT / "docker" / "Dockerfile.ai-agent"
    ).read_text(encoding="utf-8")
    assert "COPY docker/requirements.txt /tmp/requirements.txt" in dockerfile
    assert "COPY scripts/ /scripts/" in dockerfile
    assert (PARALLEL_AGENT_ROOT / "docker" / "requirements.txt").is_file()
    for entrypoint in ("agent_runner.py", "coordinator.py"):
        assert (PARALLEL_AGENT_ROOT / "scripts" / entrypoint).is_file()
        assert f"/scripts/{entrypoint}" in str(compose)
    assert (
        PARALLEL_AGENT_ROOT / ".dockerignore"
    ).read_text(encoding="utf-8").splitlines() == [
        "**",
        "!docker/",
        "!docker/Dockerfile.ai-agent",
        "!docker/requirements.txt",
        "!scripts/",
        "!scripts/agent_runner.py",
        "!scripts/coordinator.py",
    ]


def test_security_sandbox_build_context_and_compose_image_are_bounded():
    """Every sandbox variant reuses one image built from an exact allowlist."""
    compose_paths = [
        SECURITY_SANDBOX_ROOT / "docker-compose.basic.yml",
        SECURITY_SANDBOX_ROOT / "docker-compose.ai-sandbox.yml",
        SECURITY_SANDBOX_ROOT / "docker-compose.parallel-agents.yml",
    ]
    services = [
        service
        for path in compose_paths
        for service in yaml.safe_load(
            path.read_text(encoding="utf-8"))["services"].values()
    ]

    assert {
        (service["build"]["context"], service["build"]["dockerfile"])
        for service in services
    } == {(".", "Dockerfile.ai-sandbox")}
    assert {service["image"] for service in services} == {
        "ai-development-patterns/security-sandbox:local"}
    assert all(service["network_mode"] == "none" for service in services)
    assert all(service["init"] is True for service in services)
    assert all(
        "/workspace/init-workspace.sh && exec tail -f /dev/null"
        in " ".join(service["command"])
        for service in services
    )
    assert (
        SECURITY_SANDBOX_ROOT / ".dockerignore"
    ).read_text(encoding="utf-8").splitlines() == [
        "**",
        "!Dockerfile.ai-sandbox",
        "!requirements-sandbox.txt",
        "!healthcheck.py",
        "!init-workspace.sh",
    ]

    dockerfile = (
        SECURITY_SANDBOX_ROOT / "Dockerfile.ai-sandbox"
    ).read_text(encoding="utf-8")
    for copied in (
        "requirements-sandbox.txt",
        "healthcheck.py",
        "init-workspace.sh",
    ):
        assert re.search(
            rf"^COPY(?:\s+--chown=\S+)?\s+{re.escape(copied)}\s+",
            dockerfile,
            re.MULTILINE,
        )
    assert "COPY --chown=" not in dockerfile
    assert "chown -R aiuser:aiuser /workspace" not in dockerfile
    assert "chown root:root" in dockerfile
    assert "/workspace/healthcheck.py" in dockerfile
    assert "/workspace/init-workspace.sh" in dockerfile
    assert "chmod 555" in dockerfile


def test_parallel_agent_documentation_matches_the_provider_free_image():
    """The runnable tutorial must match its one zero-cost simulator image."""
    docs = (PARALLEL_AGENT_ROOT / "README.md").read_text(encoding="utf-8")
    requirements = (
        PARALLEL_AGENT_ROOT / "docker" / "requirements.txt"
    ).read_text(encoding="utf-8")

    assert "Python 3.14 and Node.js 24 LTS" in docs
    assert "zero model calls and zero provider API calls" in docs
    assert "does not need an OpenAI" in docs
    assert "agent_runner.py" in docs
    assert "coordinator.py" in docs
    assert "cat > scripts/" not in docs
    assert requirements.splitlines() == ["PyYAML==6.0.3"]
    build = (
        "docker build --pull \\\n"
        "  --tag ai-development-patterns/parallel-agent:local \\\n"
        "  --file docker/Dockerfile.ai-agent ."
    )
    assert docs.count(build) == 1


def test_network_compatibility_builds_both_docker_examples():
    """Live pulls are weekly/manual compatibility checks, not deterministic CI."""
    deterministic = PATTERN_VALIDATION_WORKFLOW.read_text(encoding="utf-8")
    workflow = yaml.load(
        DOCKER_COMPATIBILITY_WORKFLOW.read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    steps = workflow["jobs"]["docker-compatibility"]["steps"]
    step = next(
        item for item in steps
        if item.get("name") == (
            "Build maintained Docker examples from live upstreams"))
    run = step["run"]

    assert "docker build --pull" not in deterministic
    assert step["env"] == {"DOCKER_BUILDKIT": "1"}
    assert run.count("docker build --pull") == 2
    assert (
        "docker build --pull \\\n"
        "  --tag ai-development-patterns/parallel-agent:compatibility \\\n"
        "  --file examples/parallel-agents/docker/Dockerfile.ai-agent \\\n"
        "  examples/parallel-agents"
    ) in run
    assert (
        "docker build --pull \\\n"
        "  --tag ai-development-patterns/security-sandbox:compatibility \\\n"
        "  --file examples/security-sandbox/Dockerfile.ai-sandbox \\\n"
        "  examples/security-sandbox"
    ) in run


def test_node_example_manifests_have_consistent_lockfiles():
    """Every maintained npm example must commit its exact transitive graph."""
    for directory in sorted(NPM_DIRECTORIES):
        path = ROOT / directory.lstrip("/")
        manifest = json.loads((path / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((path / "package-lock.json").read_text(encoding="utf-8"))
        root_package = lock["packages"][""]

        assert lock["lockfileVersion"] == 3
        assert lock["name"] == manifest["name"]
        assert lock["version"] == manifest["version"]
        assert root_package.get("dependencies", {}) == manifest.get(
            "dependencies", {})
        assert root_package.get("devDependencies", {}) == manifest.get(
            "devDependencies", {})


def test_direct_python_runtime_dependencies_are_declared_and_test_pinned():
    """Runtime imports must not rely on undeclared transitive dependencies."""
    project = tomllib.loads(PROJECT.read_text(encoding="utf-8"))
    declared = set(project["project"]["dependencies"])
    pinned_for_tests = {
        line.strip()
        for line in TEST_REQUIREMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert {
        "beautifulsoup4==4.15.0",
        "idna==3.18",
        "PyYAML==6.0.3",
        "requests==2.34.2",
        "urllib3==2.7.0",
    } == declared
    assert declared <= pinned_for_tests


def test_dependency_review_fails_on_moderate_new_vulnerabilities():
    """Every PR gets a read-only, commit-pinned dependency review check."""
    workflow = yaml.load(
        DEPENDENCY_WORKFLOW.read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    assert workflow["on"]["pull_request"] == {
        "branches": ["main"],
        "types": [
            "opened", "synchronize", "reopened", "ready_for_review", "edited"],
    }
    assert workflow["permissions"] == {"contents": "read"}
    job = workflow["jobs"]["dependency-review"]
    review = next(
        step for step in job["steps"]
        if step.get("name") == "Reject newly introduced vulnerable dependencies"
    )
    assert re.fullmatch(
        r"actions/dependency-review-action@[0-9a-f]{40}", review["uses"])
    assert review["with"]["fail-on-severity"] == "moderate"
    assert set(
        scope.strip() for scope in review["with"]["fail-on-scopes"].split(",")
    ) == {"runtime", "development", "unknown"}
    assert review["with"]["vulnerability-check"] == "true"
    assert review["with"]["comment-summary-in-pr"] == "never"


def test_gateway_example_is_locked_local_and_cost_guarded():
    """The provider-backed example must be safe-by-default and reproducible."""
    server = (GATEWAY_ROOT / "ai-gateway" / "src" / "server.ts").read_text(
        encoding="utf-8")
    cli = (GATEWAY_ROOT / "ai-dev-cli" / "src" / "cli.ts").read_text(
        encoding="utf-8")
    docs = (GATEWAY_ROOT / "README-GATEWAY.md").read_text(encoding="utf-8")

    assert "AI_GATEWAY_TOKEN" in server and "timingSafeEqual" in server
    assert 'express.json({ limit: "32kb" })' in server
    assert "MAX_REQUESTS_PER_MINUTE = 10" in server
    assert 'from "express-rate-limit"' in server
    assert "rateLimit({" in server
    assert 'requireGatewayAuth(expectedGatewayToken())' in server
    assert "taskRateLimit" in server
    assert "createRequestBudget" in server
    route = server[server.index("  app.post("):server.index("    async (req, res)")]
    assert route.index("taskRateLimit") < route.index("requireGatewayAuth")
    assert 'process.env.AI_GATEWAY_HOST || "127.0.0.1"' in server
    assert "ALLOW_REMOTE_AI_GATEWAY" in server
    assert "app.listen(port, host" in server
    assert '"Authorization": `Bearer ${gatewayToken()}`' in cli
    assert 'http://127.0.0.1:3000' in cli
    assert docs.count("npm ci && npm run build") == 3
    assert "Never expose the example directly to an untrusted network" in docs

    package = json.loads(
        (GATEWAY_ROOT / "ai-gateway" / "package.json").read_text(
            encoding="utf-8"))
    assert package["dependencies"]["express-rate-limit"] == "^8.5.2"
    assert package["scripts"]["test"] == "node --test dist/server.test.js"

    validation = DEPENDENCY_WORKFLOW.parent.joinpath(
        "pattern-validation.yml").read_text(encoding="utf-8")
    assert "npm run test --if-present" in validation
