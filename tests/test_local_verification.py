"""Tests for the local-only, human-approved Codex evaluation planner."""

import argparse
import datetime
import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def load_script(name):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PLAN = load_script("plan-local-verification.py")
LOCAL = load_script("local_verification.py")
FINALIZE = load_script("finalize-local-verification.py")
RECORD = load_script("record-local-search-event.py")


def plan_args(**overrides):
    values = {
        "scope": "stable",
        "pattern": None,
        "limit": 10,
        "stale_days": 90,
        "include_discovery": False,
        "surface": "codex-app",
        "model": "codex-managed",
        "inflight_slugs": None,
        "today": "2026-07-10",
        "attest_chatgpt": True,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def clear_paid_environment(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    for name in PLAN.REFUSED_API_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(PLAN, "discover_inflight_slugs", lambda root: set())


def test_project_agent_configuration_enforces_bounded_read_only_workers():
    config = tomllib.loads(
        (ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
    assert config["agents"] == {"max_threads": 4, "max_depth": 1}

    expected = {"adoption-researcher": "adoption_researcher",
                "adoption-verifier": "adoption_verifier"}
    for filename, name in expected.items():
        agent = tomllib.loads(
            (ROOT / ".codex" / "agents" / f"{filename}.toml").read_text(
                encoding="utf-8"))
        assert agent["name"] == name
        assert agent["sandbox_mode"] == "read-only"
        assert "model" not in agent
        assert "spawn subagents" in agent["developer_instructions"]
    verifier = tomllib.loads(
        (ROOT / ".codex" / "agents" / "adoption-verifier.toml").read_text(
            encoding="utf-8"))["developer_instructions"]
    assert "Do not perform a web search" in verifier
    assert "exact source URLs already present" in verifier


def test_skill_contains_both_exact_human_gates_and_no_hosted_fallback():
    skill = (ROOT / ".agents" / "skills" / "evaluate-pattern-adoption" /
             "SKILL.md").read_text(encoding="utf-8")

    assert "APPROVE LOCAL EVALUATION <plan-id>" in skill
    assert "APPROVE DRAFT EVIDENCE PR <plan-id>" in skill
    assert "no more than three research subagents" in skill
    assert "never auto-merge" in skill.casefold()
    assert "GitHub Actions" in skill
    assert "must not start Codex" in skill
    assert "record-local-search-event.py" in skill
    assert "raw tool output" in skill
    assert "two per deterministic batch" in skill
    assert "Do not retry, replace, or follow up with a researcher" in skill
    assert "third verifier turn requires a new exact plan approval" in skill


def make_tiny_repo(root):
    (root / "scripts").mkdir(parents=True)
    (root / "verification" / "evidence").mkdir(parents=True)
    (root / "experiments").mkdir()
    (root / ".agents" / "skills" / "evaluate-pattern-adoption" /
     "references").mkdir(parents=True)
    (root / ".codex" / "agents").mkdir(parents=True)
    (root / "scripts" / "build-verification-inventory.py").write_bytes(
        (ROOT / "scripts" / "build-verification-inventory.py").read_bytes())
    (root / "patterns.yaml").write_text(yaml.safe_dump({
        "patterns": [{
            "id": "stable-pattern",
            "name": "Stable Pattern",
            "category": "development",
            "maturity": "beginner",
        }],
    }), encoding="utf-8")
    (root / "experiments" / "README.md").write_text(
        "| **[Exploratory Pattern](#exploratory-pattern)** | Beginner | development |\n",
        encoding="utf-8")
    (root / ".agents" / "skills" / "evaluate-pattern-adoption" /
     "SKILL.md").write_text("local evaluation contract\n", encoding="utf-8")
    (root / ".agents" / "skills" / "evaluate-pattern-adoption" /
     "references" / "evidence-methodology.md").write_text(
        "local evidence methodology\n", encoding="utf-8")
    for name in ("adoption-researcher.toml", "adoption-verifier.toml"):
        (root / ".codex" / "agents" / name).write_text(
            f"name = {name!r}\n", encoding="utf-8")
    (root / ".gitignore").write_text(
        ".verify-worklist\n"
        "__pycache__/\n"
        "verification/pattern-inventory.yaml\n"
        "verification/run-plan/\n",
        encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
    subprocess.run(
        ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
        cwd=root, check=True)


def test_real_catalog_exposes_all_explicit_local_scopes():
    inventory_module = PLAN.inventory_module(ROOT)
    catalog = inventory_module.load_catalog(
        ROOT / "patterns.yaml", ROOT / "experiments" / "README.md")
    inventory = inventory_module.build_inventory(
        catalog, ROOT / "verification" / "evidence", set(),
        datetime.date(2026, 7, 10), 90)

    assert len(PLAN.selected_for_scope(
        inventory, "stable", None, 10, inventory_module)) == 29
    assert len(PLAN.selected_for_scope(
        inventory, "exploratory", None, 10, inventory_module)) == 18
    assert len(PLAN.selected_for_scope(
        inventory, "all", None, 10, inventory_module)) == 47
    assert len(PLAN.selected_for_scope(
        inventory, "stale", None, 10, inventory_module)) <= 10
    assert PLAN.selected_for_scope(
        inventory, "discovery", None, 10, inventory_module) == []
    assert [item["name"] for item in PLAN.selected_for_scope(
        inventory, "single", "Security Sandbox", 10, inventory_module)] == [
            "Security Sandbox"]


def test_exact_scopes_fail_visibly_instead_of_silently_dropping_inflight_work():
    inventory_module = PLAN.inventory_module(ROOT)
    inventory = [
        {
            "name": "Stable Pattern", "slug": "stable-pattern",
            "location": "main", "in_flight": True,
        },
        {
            "name": "Exploratory Pattern", "slug": "exploratory-pattern",
            "location": "experimental", "in_flight": False,
        },
    ]

    with pytest.raises(ValueError, match="stable scope is blocked.*stable-pattern"):
        PLAN.selected_for_scope(
            inventory, "stable", None, 10, inventory_module)
    with pytest.raises(ValueError, match="all scope is blocked.*stable-pattern"):
        PLAN.selected_for_scope(
            inventory, "all", None, 10, inventory_module)
    with pytest.raises(ValueError, match="single scope is blocked.*stable-pattern"):
        PLAN.selected_for_scope(
            inventory, "single", "Stable Pattern", 10, inventory_module)


def test_open_pr_file_metadata_drives_inflight_evidence_deduplication():
    pull_requests = [
        {"number": 70, "files": [
            {"path": "verification/evidence/security-sandbox.yaml"},
            {"path": "verification/STATUS.md"},
        ]},
        {"number": 71, "files": [
            {"path": "verification/evidence/agent-memory.yaml"},
            {"path": "verification/evidence/security-sandbox.yaml"},
        ]},
    ]

    assert PLAN.inflight_slugs_from_prs(pull_requests) == {
        "agent-memory", "security-sandbox"}


@pytest.mark.parametrize("name", sorted(PLAN.REFUSED_API_ENV))
def test_planner_rejects_every_provider_api_credential(monkeypatch, name):
    clear_paid_environment(monkeypatch)
    monkeypatch.setenv(name, "configured")

    with pytest.raises(ValueError, match="refusing API-key-backed evaluation"):
        PLAN.refuse_hosted_or_api_execution()


def test_planner_rejects_github_actions_even_without_api_keys(monkeypatch):
    clear_paid_environment(monkeypatch)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    with pytest.raises(ValueError, match="forbidden in GitHub Actions"):
        PLAN.refuse_hosted_or_api_execution()


def test_contract_digest_is_bound_to_content_not_checkout_path(tmp_path):
    first = tmp_path / "first" / "SKILL.md"
    second = tmp_path / "second" / "SKILL.md"
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_text("same contract\n", encoding="utf-8")
    second.write_text("same contract\n", encoding="utf-8")

    assert LOCAL.contract_digest([first]) == LOCAL.contract_digest([second])
    second.write_text("changed contract\n", encoding="utf-8")
    assert LOCAL.contract_digest([first]) != LOCAL.contract_digest([second])


def test_plan_is_deterministic_before_exact_human_approval(tmp_path, monkeypatch):
    clear_paid_environment(monkeypatch)
    make_tiny_repo(tmp_path)

    manifest, run_ref, inventory = PLAN.create_plan(
        plan_args(scope="all"), root=tmp_path)

    assert len(inventory) == 2
    assert manifest["selected_slugs"] == ["stable-pattern", "exploratory-pattern"]
    assert manifest["include_discovery"] is True
    assert manifest["approval"] == {
        "status": "pending",
        "approved_at": None,
        "plan_id": manifest["plan_id"],
    }
    assert (tmp_path / run_ref).is_file()
    with pytest.raises(ValueError, match="has not been human-approved"):
        LOCAL.load_manifest(tmp_path, run_ref)
    with pytest.raises(ValueError, match="approval must exactly equal"):
        PLAN.approve_plan(tmp_path / run_ref, "yes", root=tmp_path)

    confirmation = f"APPROVE LOCAL EVALUATION {manifest['plan_id']}"
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(ValueError, match="forbidden in GitHub Actions"):
        PLAN.approve_plan(tmp_path / run_ref, confirmation, root=tmp_path)
    monkeypatch.delenv("GITHUB_ACTIONS")
    approved, approved_ref, digest = PLAN.approve_plan(
        tmp_path / run_ref, confirmation, root=tmp_path)
    loaded, path, actual_digest = LOCAL.load_manifest(
        tmp_path, approved_ref, digest)

    assert loaded == approved
    assert loaded["approval"]["status"] == "approved"
    assert actual_digest == digest
    assert oct(path.stat().st_mode & 0o777) == "0o444"


def test_planner_discloses_agent_turns_and_execution_before_approval(
        monkeypatch, capsys):
    selected = [f"pattern-{index}" for index in range(4)]
    manifest = {
        "plan_id": "a" * 64,
        "selected_slugs": selected,
        "include_discovery": True,
        "execution": {
            "provider": "openai",
            "surface": "codex-app",
            "auth_mode": "chatgpt-operator-attested",
            "model": "codex-managed",
        },
    }
    inventory = [
        {
            "slug": slug,
            "location": "main" if index < 2 else "experimental",
            "in_flight": False,
        }
        for index, slug in enumerate(selected)
    ]
    monkeypatch.setattr(
        PLAN, "create_plan",
        lambda _args: (manifest, "verification/local-runs/plan.yaml", inventory))
    monkeypatch.setattr(
        sys, "argv",
        [str(PLAN.__file__), "plan", "--scope", "all", "--attest-chatgpt"])

    assert PLAN.main() == 0
    output = capsys.readouterr().out
    assert "Researcher subagent turns: 5" in output
    assert "Maximum verifier subagent turns: 4 (2 per batch of up to 3 patterns)" in output
    assert "Maximum total subagent turns: 9" in output
    assert "Maximum live searches: 60" in output
    assert "Execution provider: openai" in output
    assert "Execution surface: codex-app" in output
    assert "Execution auth mode: chatgpt-operator-attested" in output
    assert "Execution model: codex-managed" in output
    assert "APPROVE LOCAL EVALUATION " + "a" * 64 in output


def approved_tiny_plan(tmp_path, monkeypatch, *, scope="stable"):
    clear_paid_environment(monkeypatch)
    make_tiny_repo(tmp_path)
    manifest, run_ref, _ = PLAN.create_plan(plan_args(scope=scope), root=tmp_path)
    approved, _, digest = PLAN.approve_plan(
        tmp_path / run_ref,
        f"APPROVE LOCAL EVALUATION {manifest['plan_id']}", root=tmp_path)
    return approved, run_ref, digest


def test_search_receipts_create_sanitized_bound_hash_chained_ledger(
        tmp_path, monkeypatch):
    manifest, run_ref, digest = approved_tiny_plan(tmp_path, monkeypatch)
    receipts = (
        ("name", "stable pattern adoption", ["https://one.example/result"]),
        (
            "mechanism", "bounded agent workflow industry",
            ["https://two.example/a", "https://two.example/b"]),
        ("artifact", "github agent workflow config", []),
    )
    for mode, query, candidates in receipts:
        ledger_ref, _ = RECORD.record_event(
            tmp_path, run_ref, digest, "stable-pattern", mode,
            "web.search_query", query, candidates)

    ledger, _ = LOCAL.load_search_ledger(
        tmp_path, ledger_ref, manifest, run_ref, digest, require_complete=True)

    assert ledger["run_id"] == manifest["run_id"]
    assert ledger["run_manifest_sha256"] == digest
    assert ledger["research_contract_sha256"] == (
        manifest["execution"]["prompt_version"].rsplit(".", 1)[1])
    assert LOCAL.search_projection(ledger, "stable-pattern") == {
        "name": {"queries": ["stable pattern adoption"], "candidate_count": 1},
        "mechanism": {
            "queries": ["bounded agent workflow industry"], "candidate_count": 2},
        "artifact": {"queries": ["github agent workflow config"], "candidate_count": 0},
    }
    serialized = (tmp_path / ledger_ref).read_text(encoding="utf-8")
    assert oct((tmp_path / ledger_ref).stat().st_mode & 0o777) == "0o600"
    assert "https://one.example/result" not in serialized
    assert "https://two.example" not in serialized
    assert ledger["events"][1]["previous_event_sha256"] == (
        ledger["events"][0]["event_sha256"])


@pytest.mark.parametrize(
    ("query", "candidate_urls"),
    [
        ("authorization: bearer abcdefghijklmnopqrstuvwxyz", []),
        ("safe query", ["https://example.com/?access_token=secret"]),
        ("safe query", ["https://user:password@example.com/result"]),
    ],
)
def test_search_receipt_rejects_credentials_without_retaining_them(
        tmp_path, monkeypatch, query, candidate_urls):
    _, run_ref, digest = approved_tiny_plan(tmp_path, monkeypatch)

    with pytest.raises(ValueError, match="credential|credential-free"):
        RECORD.record_event(
            tmp_path, run_ref, digest, "stable-pattern", "name",
            "web.search_query", query, candidate_urls)

    run_id = LOCAL.load_manifest(tmp_path, run_ref, digest)[0]["run_id"]
    ledger_path = tmp_path / LOCAL.search_ledger_ref_for_id(run_id)
    assert not ledger_path.exists()


def test_search_ledger_preserves_repeated_queries_and_rejects_hash_tampering(
        tmp_path, monkeypatch):
    manifest, run_ref, digest = approved_tiny_plan(tmp_path, monkeypatch)
    ledger_ref, _ = RECORD.record_event(
        tmp_path, run_ref, digest, "stable-pattern", "name",
        "web.search_query", "stable pattern", ["https://one.example/result"])
    with pytest.raises(ValueError, match="is missing modes"):
        LOCAL.load_search_ledger(
            tmp_path, ledger_ref, manifest, run_ref, digest,
            require_complete=True)
    for mode, candidate_urls in (
            ("name", ["https://two.example/result"]),
            ("mechanism", []),
            ("artifact", [])):
        RECORD.record_event(
            tmp_path, run_ref, digest, "stable-pattern", mode,
            "web.search_query", "stable pattern", candidate_urls)

    ledger, _ = LOCAL.load_search_ledger(
        tmp_path, ledger_ref, manifest, run_ref, digest, require_complete=True)

    assert [event["sequence"] for event in ledger["events"]] == [1, 2, 3, 4]
    assert len({event["event_sha256"] for event in ledger["events"]}) == 4
    assert LOCAL.search_projection(ledger, "stable-pattern") == {
        "name": {
            "queries": ["stable pattern", "stable pattern"],
            "candidate_count": 2,
        },
        "mechanism": {"queries": ["stable pattern"], "candidate_count": 0},
        "artifact": {"queries": ["stable pattern"], "candidate_count": 0},
    }

    path = tmp_path / ledger_ref
    ledger["events"][0]["candidate_count"] = 9
    path.write_text(yaml.safe_dump(ledger, sort_keys=False), encoding="utf-8")
    with pytest.raises(ValueError, match="event_sha256 does not match"):
        LOCAL.load_search_ledger(
            tmp_path, ledger_ref, manifest, run_ref, digest)


def test_search_receipt_refuses_hosted_execution(tmp_path, monkeypatch):
    manifest, run_ref, digest = approved_tiny_plan(tmp_path, monkeypatch)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    with pytest.raises(ValueError, match="forbidden in GitHub Actions"):
        RECORD.record_event(
            tmp_path, run_ref, digest, "stable-pattern", "name",
            "web.search_query", "stable pattern", [])

    assert not (
        tmp_path / LOCAL.search_ledger_ref_for_id(manifest["run_id"])).exists()


def test_planner_requires_explicit_chatgpt_auth_attestation(
        tmp_path, monkeypatch):
    clear_paid_environment(monkeypatch)
    make_tiny_repo(tmp_path)

    with pytest.raises(ValueError, match="--attest-chatgpt is required"):
        PLAN.create_plan(plan_args(attest_chatgpt=False), root=tmp_path)


@pytest.mark.parametrize(
    "overrides",
    [
        {"limit": 0},
        {"stale_days": 0},
        {"model": "   "},
    ],
)
def test_planner_rejects_invalid_bounds_and_model(
        tmp_path, monkeypatch, overrides):
    clear_paid_environment(monkeypatch)
    make_tiny_repo(tmp_path)

    with pytest.raises(ValueError, match="positive|non-empty"):
        PLAN.create_plan(plan_args(**overrides), root=tmp_path)


def test_planner_refuses_a_dirty_worktree(tmp_path, monkeypatch):
    clear_paid_environment(monkeypatch)
    make_tiny_repo(tmp_path)
    (tmp_path / "unrelated.txt").write_text("dirty\n", encoding="utf-8")

    with pytest.raises(ValueError, match="requires a dedicated clean worktree"):
        PLAN.create_plan(plan_args(), root=tmp_path)


def test_manifest_destination_rejects_symlinked_parents(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    verification = tmp_path / "repo" / "verification"
    verification.parent.mkdir()
    verification.symlink_to(outside, target_is_directory=True)
    run_ref = (
        "verification/local-runs/"
        "codex-local-123e4567-e89b-42d3-a456-426614174000.yaml")

    with pytest.raises(ValueError, match="parent must be a real directory"):
        PLAN.prepare_new_manifest_path(tmp_path / "repo", run_ref)

    assert list(outside.iterdir()) == []


def test_planner_requires_the_fetched_origin_main_tip(tmp_path, monkeypatch):
    clear_paid_environment(monkeypatch)
    make_tiny_repo(tmp_path)
    (tmp_path / "new.txt").write_text("new commit\n", encoding="utf-8")
    subprocess.run(["git", "add", "new.txt"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "ahead of main"], cwd=tmp_path, check=True)

    with pytest.raises(ValueError, match="must start at the fetched origin/main tip"):
        PLAN.create_plan(plan_args(), root=tmp_path)


def test_stale_plan_stops_without_approval_when_every_gap_is_inflight(
        tmp_path, monkeypatch):
    clear_paid_environment(monkeypatch)
    make_tiny_repo(tmp_path)
    monkeypatch.setattr(
        PLAN, "discover_inflight_slugs",
        lambda root: {"stable-pattern", "exploratory-pattern"})

    with pytest.raises(ValueError, match="no eligible stale evidence work"):
        PLAN.create_plan(plan_args(scope="stale"), root=tmp_path)

    assert not (tmp_path / "verification" / "local-runs").exists()


def test_approval_refuses_contract_drift_after_planning(tmp_path, monkeypatch):
    clear_paid_environment(monkeypatch)
    make_tiny_repo(tmp_path)
    manifest, run_ref, _ = PLAN.create_plan(plan_args(), root=tmp_path)
    skill = (tmp_path / ".agents" / "skills" /
             "evaluate-pattern-adoption" / "SKILL.md")
    skill.write_text("changed contract\n", encoding="utf-8")

    with pytest.raises(ValueError, match="contract changed after planning"):
        PLAN.approve_plan(
            tmp_path / run_ref,
            f"APPROVE LOCAL EVALUATION {manifest['plan_id']}",
            root=tmp_path)


def test_finalizer_rejects_a_different_head_before_mutating_files(
        tmp_path, monkeypatch):
    make_tiny_repo(tmp_path)
    old_head = PLAN.git_base_sha(tmp_path)
    (tmp_path / "new.txt").write_text("new commit\n", encoding="utf-8")
    subprocess.run(["git", "add", "new.txt"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "different head"], cwd=tmp_path, check=True)
    monkeypatch.setattr(FINALIZE, "load_manifest", lambda *args: ({
        "base_sha": old_head,
    }, None, "a" * 64))

    with pytest.raises(ValueError, match="HEAD changed after planning"):
        FINALIZE.finalize(tmp_path, "ignored", "a" * 64)


def test_finalizer_restores_shared_files_when_a_check_fails(
        tmp_path, monkeypatch):
    make_tiny_repo(tmp_path)
    verification = tmp_path / "verification"
    shared = {
        "pending-evidence.yaml": "# gaps\npending:\n- stable-pattern\n",
        "DECISIONS.md": "original decisions\n",
        "STATUS.md": "original status\n",
    }
    for name, content in shared.items():
        (verification / name).write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "verification"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "shared files"], cwd=tmp_path, check=True)
    head = PLAN.git_base_sha(tmp_path)
    manifest = {
        "base_sha": head,
        "run_id": "codex-local:123e4567-e89b-42d3-a456-426614174000",
        "checked_date": "2026-07-10",
        "execution": {
            "provider": "openai",
            "model": "codex-managed",
            "prompt_version": f"evidence-v2-codex-local-v1+sha256.{'a' * 64}",
        },
        "selected_slugs": ["stable-pattern"],
        "scope": "stable",
        "include_discovery": False,
    }
    monkeypatch.setattr(
        FINALIZE, "load_manifest",
        lambda *args: (manifest, None, "a" * 64))
    monkeypatch.setattr(
        FINALIZE, "load_search_ledger", lambda *args, **kwargs: ({"events": []}, None))
    monkeypatch.setattr(FINALIZE, "reconcile_selected_searches", lambda *args: None)
    monkeypatch.setattr(FINALIZE.SCOPE, "validate", lambda *args, **kwargs: set())

    def fail_run(*args):
        raise subprocess.CalledProcessError(1, ["failing-check"])

    monkeypatch.setattr(FINALIZE, "run", fail_run)

    with pytest.raises(subprocess.CalledProcessError):
        FINALIZE.finalize(tmp_path, "ignored", "a" * 64)

    for name, content in shared.items():
        assert (verification / name).read_text(encoding="utf-8") == content


@pytest.mark.parametrize(
    ("scope", "selected", "include_discovery", "expected_kind"),
    [
        ("stale", ["stable-pattern"], False, "evidence"),
        ("stable", ["stable-pattern"], False, "evidence"),
        ("exploratory", ["stable-pattern"], False, "evidence"),
        ("all", ["stable-pattern"], True, "evidence"),
        ("single", ["stable-pattern"], False, "evidence"),
        ("discovery", [], True, "discovery"),
    ],
)
def test_finalizer_success_path_covers_every_scope(
        tmp_path, monkeypatch, scope, selected, include_discovery,
        expected_kind):
    make_tiny_repo(tmp_path)
    verification = tmp_path / "verification"
    (verification / "pending-evidence.yaml").write_text(
        "pending:\n- stable-pattern\n", encoding="utf-8")
    (verification / "DECISIONS.md").write_text(
        "decisions\n", encoding="utf-8")
    (verification / "STATUS.md").write_text("status\n", encoding="utf-8")
    subprocess.run(["git", "add", "verification"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "shared files"], cwd=tmp_path, check=True)
    head = PLAN.git_base_sha(tmp_path)
    manifest = {
        "base_sha": head,
        "run_id": "codex-local:123e4567-e89b-42d3-a456-426614174000",
        "checked_date": "2026-07-10",
        "execution": {
            "provider": "openai",
            "model": "codex-managed",
            "prompt_version": f"evidence-v2-codex-local-v1+sha256.{'a' * 64}",
        },
        "selected_slugs": selected,
        "scope": scope,
        "include_discovery": include_discovery,
    }
    calls = []
    monkeypatch.setattr(
        FINALIZE, "load_manifest",
        lambda *args: (manifest, None, "a" * 64))
    monkeypatch.setattr(
        FINALIZE, "load_search_ledger", lambda *args, **kwargs: ({"events": []}, None))
    monkeypatch.setattr(FINALIZE, "reconcile_selected_searches", lambda *args: None)
    monkeypatch.setattr(
        FINALIZE.SCOPE, "validate",
        lambda *args, **kwargs: calls.append((args, kwargs)) or set())
    monkeypatch.setattr(
        FINALIZE, "run", lambda command, root: calls.append((command, root)))

    assert FINALIZE.finalize(tmp_path, "ignored", "a" * 64) == selected

    scope_args, scope_kwargs = calls[0]
    assert scope_args[1] == expected_kind
    assert scope_kwargs["allow_discovery"] is include_discovery
    pending = yaml.safe_load(
        (verification / "pending-evidence.yaml").read_text(encoding="utf-8"))
    assert pending["pending"] == ([] if selected else ["stable-pattern"])
    assert len([call for call in calls[1:] if isinstance(call[0], list)]) == 5


def test_pending_update_preserves_context_and_removes_only_selected(tmp_path):
    path = tmp_path / "verification" / "pending-evidence.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(
        "# machine-checked gaps\npending:\n- first\n- second\n- third\n",
        encoding="utf-8")

    FINALIZE.remove_pending(tmp_path, ["second"])

    assert path.read_text(encoding="utf-8") == (
        "# machine-checked gaps\npending:\n- first\n- third\n")
