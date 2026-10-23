"""Regression tests for dependency maintenance and review coverage."""

import json
import re
import tomllib
from pathlib import Path

import yaml

from utils.requirements import pinned_distributions, requirement_lines


ROOT = Path(__file__).parent.parent
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
DEPENDENCY_WORKFLOW = ROOT / ".github" / "workflows" / "dependency-security.yml"
TRUSTED_EVIDENCE_WORKFLOW = (
    ROOT / ".github" / "workflows" / "trusted-evidence-validation.yml")
LIFECYCLE_VALIDATOR = ROOT / "scripts" / "validate-package-lifecycle.py"
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

# Lowest express-rate-limit release whose behavior the gateway example relies on.
# Routine patch/minor bumps are expected; a downgrade below this floor or a major
# bump would change the rate-limiting contract the example documents.
GATEWAY_RATE_LIMIT_FLOOR = (8, 6, 1)
CARET_RANGE = re.compile(r"^\^(\d+)\.(\d+)\.(\d+)$")

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


def dependabot_updates(ecosystem):
    """Return every updater for an ecosystem, in file order.

    An ecosystem may be split across several updaters so that one pull request
    can never mix a protected manifest with a free one.
    """
    document = yaml.safe_load(DEPENDABOT.read_text(encoding="utf-8"))
    matches = [
        update for update in document["updates"]
        if update["package-ecosystem"] == ecosystem
    ]
    assert matches, f"no dependabot updater for {ecosystem}"
    return matches


def updater_directories(update):
    """Return one updater's repository directories."""
    return set(update.get("directories") or [update["directory"]])


def dependabot_directories(ecosystem):
    """Return every directory an ecosystem covers, across its updaters."""
    covered = set()
    for update in dependabot_updates(ecosystem):
        directories = updater_directories(update)
        assert not covered & directories, (
            f"{ecosystem} lists {covered & directories} in more than one updater")
        covered |= directories
    return covered


def does_version_updates(update):
    """Return whether an updater still opens version-update pull requests."""
    return update["open-pull-requests-limit"] > 0


def trust_root_policy():
    """Load the trusted workflow policy module for its protected inventory."""
    spec = importlib.util.spec_from_file_location(
        "workflow_policy", WORKFLOW_POLICY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def protects(policy, relative_path):
    """Return whether the trust root protects a repository-relative path."""
    if relative_path in set(policy.REQUIRED_TRUST_ROOT_FILES):
        return True
    return any(
        relative_path.startswith(f"{directory}/")
        for directory in policy.REQUIRED_TRUST_ROOT_DIRECTORIES
    )


def manifests_in(ecosystem, repository_directory_path):
    """Return the repository-relative manifests Dependabot would edit."""
    base = ROOT if repository_directory_path == "/" else (
        ROOT / repository_directory_path.lstrip("/"))
    patterns = {
        "pip": ("pyproject.toml", "requirements*.txt"),
        "npm": ("package.json", "package-lock.json"),
        "docker": ("Dockerfile*",),
        "github-actions": (),
    }[ecosystem]
    found = {
        path.relative_to(ROOT).as_posix()
        for pattern in patterns for path in base.glob(pattern)
    }
    if ecosystem == "github-actions":
        found = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / ".github" / "workflows").glob("*.y*ml")
        }
    return found


def assert_caret_pinned_at_least(spec, floor):
    """Assert an npm spec is a caret range no older than ``floor``.

    Args:
        spec: The version spec declared in package.json, e.g. ``"^8.6.2"``.
        floor: Lowest acceptable ``(major, minor, patch)`` tuple.

    Raises:
        AssertionError: If the spec is not a caret range, drops below the
            floor, or crosses a major boundary. Routine patch and minor
            bumps pass so dependency updates do not require a test edit.
    """
    match = CARET_RANGE.match(spec)
    assert match, f"expected a caret range like ^8.6.1, got {spec!r}"
    version = tuple(int(part) for part in match.groups())
    assert version[0] == floor[0], (
        f"major bump from {floor} to {version} changes the pinned contract")
    assert version >= floor, f"{version} is older than the pinned floor {floor}"


def repository_directory(path):
    """Render a manifest parent as a Dependabot repository directory."""
    relative = path.parent.relative_to(ROOT).as_posix()
    return "/" if relative == "." else f"/{relative}"


def test_dependabot_covers_all_dependency_manifest_directories():
    """Nested example manifests must not fall outside update coverage."""
    assert dependabot_directories("pip") == PYTHON_DIRECTORIES
    assert dependabot_directories("npm") == NPM_DIRECTORIES
    assert dependabot_directories("docker") == DOCKER_DIRECTORIES
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
        updating = [
            update for update in dependabot_updates(ecosystem)
            if does_version_updates(update)
        ]
        assert updating, f"{ecosystem} opens no version updates at all"
        for update in updating:
            groups = update["groups"]
            assert groups[version_group]["patterns"] == ["*"]
            assert set(groups[version_group]["update-types"]) == {
                "minor", "patch"}
            assert groups[version_group]["group-by"] == "dependency-name"
            assert groups[security_group]["applies-to"] == "security-updates"
            assert groups[security_group]["patterns"] == ["*"]

        for update in dependabot_updates(ecosystem):
            if does_version_updates(update):
                continue
            # A version group on a limit-0 updater is dead config that reads as
            # though those bumps still arrive. Security grouping stays live.
            assert version_group not in update.get("groups", {})
            assert update["groups"][security_group]["applies-to"] == (
                "security-updates")


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
        r"^FROM python:3\.14-slim-bookworm$", sandbox, re.MULTILINE)
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
    assert pinned_distributions(requirement_lines(requirements)) == {"pyyaml"}
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
    pinned_for_tests = set(
        requirement_lines(TEST_REQUIREMENTS.read_text(encoding="utf-8")))

    assert pinned_distributions(declared) == {
        "beautifulsoup4",
        "idna",
        "pyyaml",
        "requests",
        "urllib3",
    }
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


def gateway_server_source():
    """Return the gateway example's server.ts source."""
    return (GATEWAY_ROOT / "ai-gateway" / "src" / "server.ts").read_text(
        encoding="utf-8")


def test_gateway_example_authenticates_and_caps_cost():
    """The gateway must authenticate, throttle, and bound request cost."""
    server = gateway_server_source()

    assert "AI_GATEWAY_TOKEN" in server and "timingSafeEqual" in server
    assert 'express.json({ limit: "32kb" })' in server
    assert "MAX_REQUESTS_PER_MINUTE = 10" in server
    assert 'from "express-rate-limit"' in server
    assert "rateLimit({" in server
    assert 'requireGatewayAuth(expectedGatewayToken())' in server
    assert "taskRateLimit" in server
    assert "createRequestBudget" in server


def test_gateway_example_throttles_before_authenticating():
    """Throttling must precede auth so unauthenticated floods stay cheap."""
    server = gateway_server_source()

    route = server[server.index("  app.post("):server.index("    async (req, res)")]
    assert route.index("taskRateLimit") < route.index("requireGatewayAuth")


def test_gateway_example_binds_locally_by_default():
    """The example must not reach an untrusted network without an opt-in."""
    server = gateway_server_source()
    cli = (GATEWAY_ROOT / "ai-dev-cli" / "src" / "cli.ts").read_text(
        encoding="utf-8")
    docs = (GATEWAY_ROOT / "README-GATEWAY.md").read_text(encoding="utf-8")

    assert 'process.env.AI_GATEWAY_HOST || "127.0.0.1"' in server
    assert "ALLOW_REMOTE_AI_GATEWAY" in server
    assert "app.listen(port, host" in server
    assert '"Authorization": `Bearer ${gatewayToken()}`' in cli
    assert 'http://127.0.0.1:3000' in cli
    assert docs.count("npm ci && npm run build") == 3
    assert "Never expose the example directly to an untrusted network" in docs


def test_gateway_example_is_locked_and_reproducible():
    """The example's dependencies and build steps must stay reproducible."""
    package = json.loads(
        (GATEWAY_ROOT / "ai-gateway" / "package.json").read_text(
            encoding="utf-8"))
    assert_caret_pinned_at_least(
        package["dependencies"]["express-rate-limit"],
        GATEWAY_RATE_LIMIT_FLOOR)
    assert package["scripts"]["test"] == "node --test dist/server.test.js"

    validation = DEPENDENCY_WORKFLOW.parent.joinpath(
        "pattern-validation.yml").read_text(encoding="utf-8")
    assert "npm run test --if-present" in validation
