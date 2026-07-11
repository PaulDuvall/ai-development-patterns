"""Regression contract for the July 2026 catalog consolidation."""

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).parent.parent
README = ROOT / "README.md"
EXPERIMENTS = ROOT / "experiments" / "README.md"
EVIDENCE = ROOT / "verification" / "evidence"

EXPECTED_STABLE = (
    ("agent-readiness", "Agent Readiness"),
    ("codified-rules", "Codified Rules"),
    ("security-sandbox", "Security Sandbox"),
    ("developer-lifecycle", "Developer Lifecycle"),
    ("tool-integration", "Tool Integration"),
    ("issue-generation", "Issue Generation"),
    ("spec-driven-development", "Spec-Driven Development"),
    ("planned-implementation", "Planned Implementation"),
    ("incremental-generation", "Incremental Generation"),
    ("agent-memory", "Agent Memory"),
    ("agent-hooks", "Agent Hooks"),
    ("custom-commands", "Custom Commands"),
    ("progressive-disclosure", "Progressive Disclosure"),
    ("atomic-decomposition", "Atomic Decomposition"),
    ("guided-refactoring", "Guided Refactoring"),
    ("agent-observability", "Agent Observability"),
    ("image-spec", "Image Spec"),
    ("adversarial-evaluator", "Adversarial Evaluator"),
    ("parallel-agents", "Parallel Agents"),
    ("error-resolution", "Error Resolution"),
    ("model-routing", "Model Routing"),
    ("code-research", "Code Research"),
    ("bounded-autonomy", "Bounded Autonomy"),
    ("policy-generation", "Policy Generation"),
    ("evidence-automation", "Evidence Automation"),
    ("centralized-rules", "Centralized Rules"),
    ("drift-remediation", "Drift Remediation"),
    ("debt-forecasting", "Debt Forecasting"),
    ("guided-chaos", "Guided Chaos"),
)

EXPECTED_EXPLORATORY = (
    ("handoff-protocols", "Handoff Protocols"),
    ("testing-orchestration", "Testing Orchestration"),
    ("workflow-orchestration", "Workflow Orchestration"),
    ("review-automation", "Review Automation"),
    ("test-promotion", "Test Promotion"),
    ("feedback-flywheel", "Feedback Flywheel"),
    ("long-running-orchestration", "Long-Running Orchestration"),
    ("guided-architecture", "Guided Architecture"),
    ("autonomous-remediation", "Autonomous Remediation"),
    ("chatops-security", "ChatOps Security"),
    ("autonomous-soc", "Autonomous SOC"),
    ("security-orchestration", "Security Orchestration"),
    ("autonomous-acceptance", "Autonomous Acceptance"),
    ("pipeline-synthesis", "Pipeline Synthesis"),
    ("dependency-migration", "Dependency Migration"),
    ("incident-automation", "Incident Automation"),
    ("flake-management", "Flake Management"),
    ("on-call-handoff", "On-Call Handoff"),
)

# old slug: (new slug, document, heading level)
CANONICAL_RENAMES = {
    "event-automation": ("agent-hooks", README, "##"),
    "observable-development": ("agent-observability", README, "##"),
    "context-optimization": ("model-routing", README, "##"),
    "asynchronous-research": ("code-research", README, "##"),
    "chaos-engineering": ("guided-chaos", README, "###"),
    "suite-health": ("flake-management", EXPERIMENTS, "###"),
    "handoff-automation": ("on-call-handoff", EXPERIMENTS, "###"),
    "autonomous-defense": ("autonomous-soc", EXPERIMENTS, "###"),
}

PROMOTED = {
    "bounded-autonomy",
    "model-routing",
    "code-research",
    "drift-remediation",
    "guided-chaos",
    "evidence-automation",
    "debt-forecasting",
}

PROMOTION_REDIRECTS = {
    "bounded-autonomy": "bounded-autonomy",
    "context-optimization": "model-routing",
    "asynchronous-research": "code-research",
    "drift-remediation": "drift-remediation",
    "chaos-engineering": "guided-chaos",
    "evidence-automation": "evidence-automation",
    "debt-forecasting": "debt-forecasting",
}

DEMOTED = {
    "security-orchestration",
    "autonomous-remediation",
}

EXPERIMENT_ROW = re.compile(
    r"^\|\s*\*\*\[([^]]+)\]\(#([a-z0-9-]+)\)\*\*\s*\|",
    re.MULTILINE,
)


def load_stable():
    registry = yaml.safe_load((ROOT / "patterns.yaml").read_text(encoding="utf-8"))
    return tuple((pattern["id"], pattern["name"]) for pattern in registry["patterns"])


def load_exploratory():
    content = EXPERIMENTS.read_text(encoding="utf-8")
    return tuple((slug, name) for name, slug in EXPERIMENT_ROW.findall(content))


def active_catalog():
    return dict(load_stable() + load_exploratory())


def test_exact_approved_catalogs_are_pinned():
    assert load_stable() == EXPECTED_STABLE
    assert load_exploratory() == EXPECTED_EXPLORATORY
    assert len(active_catalog()) == 47


def test_eight_canonical_renames_keep_only_a_compatibility_anchor():
    catalog = active_catalog()

    assert len(CANONICAL_RENAMES) == 8
    for old_slug, (new_slug, document, heading_level) in CANONICAL_RENAMES.items():
        new_name = catalog[new_slug]
        content = document.read_text(encoding="utf-8")
        assert f'<a id="{old_slug}"></a>\n{heading_level} {new_name}' in content
        assert old_slug not in catalog
        assert not (EVIDENCE / f"{old_slug}.yaml").exists()

        evidence = yaml.safe_load(
            (EVIDENCE / f"{new_slug}.yaml").read_text(encoding="utf-8"))
        assert evidence["slug"] == new_slug
        assert evidence["pattern"] == new_name


def test_approved_promotions_and_demotions_have_exact_current_placement():
    stable_slugs = {slug for slug, _ in load_stable()}
    exploratory_slugs = {slug for slug, _ in load_exploratory()}
    readme_content = README.read_text(encoding="utf-8")
    experimental_content = EXPERIMENTS.read_text(encoding="utf-8")

    assert len(PROMOTED) == 7
    assert PROMOTED <= stable_slugs
    assert PROMOTED.isdisjoint(exploratory_slugs)
    assert set(PROMOTION_REDIRECTS.values()) == PROMOTED
    for former_slug, current_slug in PROMOTION_REDIRECTS.items():
        assert f'<a id="{former_slug}"></a>' in experimental_content
        assert f'](../README.md#{current_slug})' in experimental_content
    assert len(DEMOTED) == 2
    assert DEMOTED <= exploratory_slugs
    assert DEMOTED.isdisjoint(stable_slugs)
    for slug in DEMOTED:
        assert f'<a id="{slug}"></a>' in readme_content
        assert f'](experiments/README.md#{slug})' in readme_content


def test_merge_retirements_and_material_replacement_remain_distinct():
    catalog = active_catalog()
    experimental_content = EXPERIMENTS.read_text(encoding="utf-8")

    # Deployment Synthesis was merged into Pipeline Synthesis with an inbound-link alias.
    assert '<a id="deployment-synthesis"></a>\n### Pipeline Synthesis' in experimental_content
    assert "deployment-synthesis" not in catalog
    assert not (EVIDENCE / "deployment-synthesis.yaml").exists()

    # Release Synthesis was retired without an active catalog or evidence record.
    assert "release-synthesis" not in catalog
    assert not (EVIDENCE / "release-synthesis.yaml").exists()
    assert '<a id="release-synthesis"></a>' not in experimental_content

    # Dependency Migration is a new, pending mechanism, not an Upgrade Advisor alias.
    pending = yaml.safe_load(
        (ROOT / "verification" / "pending-evidence.yaml").read_text(
            encoding="utf-8"))["pending"]
    assert pending == ["dependency-migration"]
    assert catalog["dependency-migration"] == "Dependency Migration"
    assert not (EVIDENCE / "dependency-migration.yaml").exists()
    assert "upgrade-advisor" not in catalog
    assert not (EVIDENCE / "upgrade-advisor.yaml").exists()
    assert '<a id="upgrade-advisor"></a>' not in README.read_text(encoding="utf-8")
    assert '<a id="upgrade-advisor"></a>' not in experimental_content
