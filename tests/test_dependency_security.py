"""Regression tests for dependency maintenance and review coverage."""

import json
import re
import tomllib
from pathlib import Path

import yaml


ROOT = Path(__file__).parent.parent
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
DEPENDENCY_WORKFLOW = ROOT / ".github" / "workflows" / "dependency-security.yml"
PROJECT = ROOT / "pyproject.toml"
TEST_REQUIREMENTS = ROOT / "tests" / "requirements.txt"
GATEWAY_ROOT = (
    ROOT / "examples" / "centralized-rules" / "gateway-strategy")

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
    assert 'process.env.AI_GATEWAY_HOST || "127.0.0.1"' in server
    assert "ALLOW_REMOTE_AI_GATEWAY" in server
    assert "app.listen(PORT, HOST" in server
    assert '"Authorization": `Bearer ${gatewayToken()}`' in cli
    assert 'http://127.0.0.1:3000' in cli
    assert docs.count("npm ci && npm run build") == 3
    assert "Never expose the example directly to an untrusted network" in docs
