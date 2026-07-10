"""Tests for the deterministic schema-v2 adoption-evidence validator."""

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path
import warnings

import pytest
import yaml


REPO_ROOT = Path(__file__).parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate-evidence.py"
EVIDENCE_DIR = REPO_ROOT / "verification" / "evidence"
REGISTRY = REPO_ROOT / "patterns.yaml"
ALLOWLIST = REPO_ROOT / "verification" / "pending-evidence.yaml"
DECISIONS = REPO_ROOT / "verification" / "DECISIONS.md"
CONTENT_SPEC = importlib.util.spec_from_file_location(
    "evidence_content_for_links", REPO_ROOT / "scripts" / "evidence_content.py")
CONTENT = importlib.util.module_from_spec(CONTENT_SPEC)
CONTENT_SPEC.loader.exec_module(CONTENT)


def run_validator(directory, *extra_args):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--dir", str(directory), *extra_args],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )


def make_evidence_dir(tmp_path):
    directory = tmp_path / "evidence"
    directory.mkdir()
    return directory


def complete_search(**overrides):
    search = {
        "run_id": "github-actions:123",
        "run_url": (
            "https://github.com/PaulDuvall/ai-development-patterns/actions/runs/123"),
        "provider": "openai",
        "model": "example-verifier",
        "prompt_version": "v2",
        "checked_at": "2026-07-01",
        "modes": {
            "name": {"queries": ["example pattern"], "candidate_count": 2},
            "mechanism": {"queries": ["example mechanism"], "candidate_count": 2},
            "artifact": {"queries": ["example config"], "candidate_count": 1},
        },
    }
    search.update(overrides)
    return search


def legacy_search():
    return {
        "run_id": "legacy-import",
        "checked_at": "2026-07-01",
        "modes": {
            mode: {"queries": [], "candidate_count": None}
            for mode in ("name", "mechanism", "artifact")
        },
    }


def evidence_entry(tier="T1", group="vendor-a", *, complete=True,
                   match="named", url=None, source_kind=None):
    kinds = {
        "T1": "shipped_product",
        "T2": "official_documentation",
        "T3": "peer_reviewed_research",
        "T4": "practitioner_report",
        "T5": "social_discussion",
    }
    url = url or f"https://{group}.example/evidence/{tier.lower()}"
    entry = {
        "tier": tier,
        "match": match,
        "mechanism_quote": "The source demonstrates the complete example mechanism.",
        "source": f"{group} source",
        "source_kind": source_kind or kinds[tier],
        "organization": group.replace("-", " ").title(),
        "independence_group": group,
        "url": url,
        "resolved_url": url,
        "date": "2026-06-30",
        "retrieved": "2026-07-01",
        "claim": "The source demonstrates industry use of the pattern.",
        "content_sha256": (
            hashlib.sha256(f"{group}:{tier}".encode()).hexdigest() if complete else None),
        "verifier": ({
            "method": "automated",
            "model": "example-verifier",
            "prompt_version": "v2",
            "run_url": (
                "https://github.com/PaulDuvall/ai-development-patterns/actions/runs/123"),
        } if complete else {
            "method": "legacy-import",
            "model": None,
            "prompt_version": None,
            "run_url": None,
        }),
    }
    return entry


def dimensions(entries):
    implementation = {e["independence_group"] for e in entries if e["tier"] == "T1"}
    adoption = {
        e["independence_group"] for e in entries if e["tier"] in {"T3", "T4"}
    }
    return {
        "implementation_available": bool(implementation),
        "independent_adoption": any(a != i for a in adoption for i in implementation),
        "independence_groups": len({e["independence_group"] for e in entries}),
    }


def evidence_document(slug="example", pattern="Example Pattern", *,
                      provenance="complete", entries=None):
    if entries is None:
        entries = [
            evidence_entry("T1", "vendor-a", complete=provenance == "complete"),
            evidence_entry("T3", "research-b", complete=provenance == "complete"),
        ]
    score = sum({"T1": 5, "T2": 4, "T3": 3, "T4": 2, "T5": 1}[e["tier"]]
                for e in entries)
    counts = {}
    for entry in entries:
        counts[entry["tier"]] = counts.get(entry["tier"], 0) + 1
    if provenance != "complete":
        verdict = "weak"
    elif score <= 2:
        verdict = "unverified"
    elif provenance == "complete" \
            and sum({"T1": 5, "T2": 4, "T3": 3, "T4": 2}.get(e["tier"], 0)
                    for e in entries) >= 8 \
            and dimensions(entries)["implementation_available"] \
            and dimensions(entries)["independent_adoption"]:
        verdict = "verified"
    else:
        verdict = "weak"
    named = sum(e["match"] == "named" for e in entries)
    aliased = sum(e["match"] == "aliased" for e in entries)
    if not entries or (not named and not aliased):
        alignment = "none"
    elif not named:
        alignment = "aliased"
    else:
        alignment = "strong" if named * 2 > len(entries) else "weak"
    document = {
        "schema_version": 2,
        "provenance_status": provenance,
        "pattern": pattern,
        "slug": slug,
        "last_checked": "2026-07-01",
        "search": complete_search() if provenance == "complete" else legacy_search(),
        "adoption_score": score,
        "tier_counts": counts,
        "adoption_dimensions": dimensions(entries),
        "naming_alignment": alignment,
        "evidence": entries if entries else "none found",
        "verdict": verdict,
    }
    if provenance == "legacy-import":
        document.update({
            "legacy_run_url": (
                "https://github.com/PaulDuvall/ai-development-patterns/pull/19"),
            "legacy_limitations": "Original query strings and content digests were not retained.",
        })
    return document


def write_document(directory, document, filename=None):
    path = directory / (filename or f"{document['slug']}.yaml")
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def write_registry(directory, patterns=(("example", "Example Pattern"),)):
    path = directory / "patterns.yaml"
    value = {"patterns": [{"id": slug, "name": name} for slug, name in patterns]}
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    return path


def write_allowlist(directory, slugs):
    path = directory / "pending.yaml"
    path.write_text(yaml.safe_dump({"pending": slugs}, sort_keys=False), encoding="utf-8")
    return path


def registry_args(directory, registry):
    return "--registry", str(registry), "--experiments", str(directory / "missing.md")


def assert_fails(directory, message, *args):
    result = run_validator(directory, *args)
    assert result.returncode == 1, result.stdout
    assert message in result.stdout


def test_validator_exists():
    assert VALIDATOR.is_file()


def test_all_committed_evidence_files_are_valid_v2():
    if not EVIDENCE_DIR.is_dir():
        pytest.skip("no evidence directory committed yet")
    result = run_validator(EVIDENCE_DIR)
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"


def test_catalog_and_evidence_stay_aligned():
    if not EVIDENCE_DIR.is_dir():
        pytest.skip("no evidence directory committed yet")
    result = run_validator(
        EVIDENCE_DIR, "--registry", str(REGISTRY), "--allowlist", str(ALLOWLIST))
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"


def test_complete_v2_fixture_passes(tmp_path):
    write_document(tmp_path, evidence_document())
    result = run_validator(tmp_path)
    assert result.returncode == 0, result.stdout


def test_legacy_import_is_explicit_and_cannot_verify(tmp_path):
    document = evidence_document(provenance="legacy-import")
    assert document["verdict"] == "weak"
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 0, result.stdout


def test_legacy_verified_field_and_schema_v1_are_rejected(tmp_path):
    document = evidence_document()
    document["schema_version"] = 1
    document["verified"] = document.pop("last_checked")
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "schema_version must be integer 2" in result.stdout
    assert "legacy 'verified' is forbidden" in result.stdout


@pytest.mark.parametrize("version", [2.0, True])
def test_schema_version_requires_exact_integer_type(tmp_path, version):
    document = evidence_document()
    document["schema_version"] = version
    write_document(tmp_path, document)
    assert_fails(tmp_path, "schema_version must be integer 2")


def test_duplicate_yaml_keys_are_rejected(tmp_path):
    path = write_document(tmp_path, evidence_document())
    path.write_text(path.read_text() + "verdict: weak\n", encoding="utf-8")
    assert_fails(tmp_path, "duplicate key 'verdict'")


def test_yaml_aliases_are_rejected(tmp_path):
    path = write_document(tmp_path, evidence_document())
    text = path.read_text(encoding="utf-8").replace(
        "adoption_dimensions:\n", "adoption_dimensions: &dimensions\n", 1)
    text += "terminology_variants: *dimensions\n"
    path.write_text(text, encoding="utf-8")
    assert_fails(tmp_path, "aliases are not allowed")


@pytest.mark.parametrize("mode", ["name", "mechanism", "artifact"])
def test_complete_search_requires_all_three_auditable_modes(tmp_path, mode):
    document = evidence_document()
    del document["search"]["modes"][mode]
    write_document(tmp_path, document)
    assert_fails(tmp_path, f"missing required mode '{mode}'")


def test_complete_search_requires_queries_counts_and_run_url(tmp_path):
    document = evidence_document()
    document["search"]["modes"]["name"] = {"queries": [], "candidate_count": None}
    document["search"].pop("run_url")
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "'queries' must be a non-empty list" in result.stdout
    assert "'candidate_count' must be a non-negative integer" in result.stdout
    assert "requires this repository's canonical Actions run_url" in result.stdout


def test_complete_search_has_twelve_query_cap(tmp_path):
    document = evidence_document()
    document["search"]["modes"]["name"]["queries"] = [f"query {i}" for i in range(11)]
    write_document(tmp_path, document)
    assert_fails(tmp_path, "13 queries exceeds max 12")


def test_complete_search_run_and_verifier_are_bound_to_same_actions_run(tmp_path):
    document = evidence_document()
    document["search"]["run_id"] = "arbitrary"
    document["search"]["run_url"] = "https://example.com/not-an-actions-run"
    document["evidence"][0]["verifier"]["run_url"] = (
        "https://github.com/PaulDuvall/ai-development-patterns/actions/runs/999")
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "requires run_id 'github-actions:<run-number>'" in result.stdout
    assert "requires this repository's canonical Actions run_url" in result.stdout
    assert "must equal search.run_url" in result.stdout


def test_actions_run_number_must_match_run_id(tmp_path):
    document = evidence_document()
    document["search"]["run_id"] = "github-actions:999"
    write_document(tmp_path, document)
    assert_fails(tmp_path, "run_id must match the run number in run_url")


def test_complete_search_requires_execution_provenance(tmp_path):
    document = evidence_document(entries=[])
    del document["search"]["provider"]
    document["search"]["model"] = ""
    document["search"]["prompt_version"] = None
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "missing required field 'provider'" in result.stdout
    assert "'model' must be a non-empty string" in result.stdout
    assert "'prompt_version' must be a non-empty string" in result.stdout


def test_verifier_model_and_prompt_match_search_contract(tmp_path):
    document = evidence_document()
    document["evidence"][0]["verifier"]["model"] = "different-model"
    document["evidence"][1]["verifier"]["prompt_version"] = "different-prompt"
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "'model' must equal search.model" in result.stdout
    assert "'prompt_version' must equal search.prompt_version" in result.stdout


def test_admitted_evidence_requires_nonzero_candidate_pool(tmp_path):
    document = evidence_document()
    for mode in document["search"]["modes"].values():
        mode["candidate_count"] = 0
    write_document(tmp_path, document)
    assert_fails(tmp_path, "total candidate_count must be at least")


def test_legacy_search_cannot_claim_unrecorded_queries(tmp_path):
    document = evidence_document(provenance="legacy-import")
    document["search"]["modes"]["name"]["queries"] = ["invented query"]
    document["search"]["modes"]["name"]["candidate_count"] = 1
    write_document(tmp_path, document)
    assert_fails(tmp_path, "legacy-import requires queries: []")


def test_legacy_import_cannot_claim_search_exhaustion(tmp_path):
    document = evidence_document(provenance="legacy-import", entries=[])
    assert document["verdict"] == "weak"
    write_document(tmp_path, document)
    assert_fails(tmp_path, "'none found' requires complete three-mode search provenance")


def test_complete_entries_require_source_and_verifier_provenance(tmp_path):
    document = evidence_document()
    entry = document["evidence"][0]
    del entry["organization"]
    entry["content_sha256"] = "not-a-hash"
    entry["verifier"]["run_url"] = None
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "missing required field 'organization'" in result.stdout
    assert "64 lowercase hex" in result.stdout
    assert "'run_url' must be this repository's canonical Actions URL" in result.stdout


def test_source_kind_must_match_tier(tmp_path):
    document = evidence_document()
    document["evidence"][0]["source_kind"] = "social_discussion"
    write_document(tmp_path, document)
    assert_fails(tmp_path, "source_kind for T1")


def test_complete_entries_all_require_mechanism_quote(tmp_path):
    entries = [evidence_entry("T4", "practitioner-a")]
    entries[0].pop("mechanism_quote")
    write_document(tmp_path, evidence_document(entries=entries))
    assert_fails(tmp_path, "mechanism_quote is required")


def test_complete_mechanism_quote_has_offline_minimum_length(tmp_path):
    document = evidence_document()
    document["evidence"][0]["mechanism_quote"] = "tiny"
    write_document(tmp_path, document)
    assert_fails(tmp_path, "must normalize to at least 20 characters")


def test_terminology_variants_have_exact_machine_readable_schema(tmp_path):
    document = evidence_document()
    document["terminology_variants"] = [
        {"term": "Industry Name", "used_by": "Vendor", "url": "https://vendor.example/name"},
        {"term": "industry name", "used_by": "", "url": "http://127.0.0.1/name"},
        {"term": "Extra", "used_by": "Team", "url": "https://team.example/name", "note": "x"},
    ]
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "duplicate terminology term" in result.stdout
    assert "'used_by' must be a non-empty string" in result.stdout
    assert "'url' must be a concrete public" in result.stdout
    assert "unknown field 'note'" in result.stdout


def test_legacy_aliased_entry_still_requires_quote(tmp_path):
    entry = evidence_entry("T4", "practitioner-a", complete=False, match="aliased")
    entry.pop("mechanism_quote")
    write_document(
        tmp_path, evidence_document(provenance="legacy-import", entries=[entry]))
    assert_fails(tmp_path, "mechanism_quote is required")


def test_computed_fields_are_not_assertions(tmp_path):
    document = evidence_document()
    document["adoption_score"] = 99
    document["tier_counts"] = {"T1": 99}
    document["adoption_dimensions"]["independent_adoption"] = False
    document["naming_alignment"] = "none"
    document["verdict"] = "weak"
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 1
    for field in ("adoption_score", "tier_counts", "adoption_dimensions",
                  "naming_alignment", "verdict"):
        assert field in result.stdout


def test_computed_field_types_are_strict_not_python_truthy_equivalents(tmp_path):
    document = evidence_document(entries=[])
    document["adoption_score"] = False  # bool compares equal to integer zero in Python
    document["adoption_dimensions"]["implementation_available"] = 0
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "'adoption_score' must be a non-negative integer" in result.stdout
    assert "implementation_available must be boolean" in result.stdout


def test_t5_mentions_cannot_unlock_verified(tmp_path):
    entries = [evidence_entry("T1", "vendor-a")]
    entries.extend(evidence_entry("T5", f"social-{i}") for i in range(3))
    document = evidence_document(entries=entries)
    assert document["adoption_score"] == 8
    assert document["verdict"] == "weak"
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 0, result.stdout


def test_t5_cannot_supply_the_last_point_for_verification(tmp_path):
    entries = [
        evidence_entry("T1", "vendor-a"),
        evidence_entry("T4", "practitioner-b"),
        evidence_entry("T5", "social-c"),
    ]
    document = evidence_document(entries=entries)
    assert document["adoption_score"] == 8
    assert document["adoption_dimensions"]["independent_adoption"] is True
    assert document["verdict"] == "weak"
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 0, result.stdout


def test_vendor_material_without_independent_adoption_stays_weak(tmp_path):
    entries = [
        evidence_entry("T1", "vendor-a"),
        evidence_entry("T2", "vendor-b"),
    ]
    document = evidence_document(entries=entries)
    assert document["adoption_score"] == 9
    assert document["verdict"] == "weak"
    write_document(tmp_path, document)
    assert run_validator(tmp_path).returncode == 0


def test_independent_implementation_and_adoption_can_verify(tmp_path):
    document = evidence_document()
    assert document["adoption_dimensions"] == {
        "implementation_available": True,
        "independent_adoption": True,
        "independence_groups": 2,
    }
    assert document["verdict"] == "verified"
    write_document(tmp_path, document)
    assert run_validator(tmp_path).returncode == 0


def test_independence_group_can_only_score_once(tmp_path):
    entries = [evidence_entry("T1", "same-org"), evidence_entry("T3", "same-org")]
    write_document(tmp_path, evidence_document(entries=entries))
    assert_fails(tmp_path, "independence_group 'same-org' already scored")


def test_one_organization_cannot_invent_multiple_independence_groups(tmp_path):
    entries = [evidence_entry("T1", "product-team"), evidence_entry("T3", "research-team")]
    for entry in entries:
        entry["organization"] = "Same Company, Inc."
    write_document(tmp_path, evidence_document(entries=entries))
    assert_fails(tmp_path, "organization 'Same Company, Inc.' uses independence_group")


def test_tier_cap_is_enforced(tmp_path):
    entries = [evidence_entry("T5", f"group-{i}") for i in range(4)]
    write_document(tmp_path, evidence_document(entries=entries))
    assert_fails(tmp_path, "max 3")


def test_canonical_resolved_urls_are_globally_unique(tmp_path):
    first = evidence_document(entries=[
        evidence_entry("T4", "first", url="https://Example.com/source/?b=2&a=1#part")])
    second = evidence_document(slug="second", pattern="Second Pattern", entries=[
        evidence_entry("T4", "second", url="https://example.com/source?a=1&b=2")])
    write_document(tmp_path, first)
    write_document(tmp_path, second)
    assert_fails(tmp_path, "FAIL URLs: canonical URL")


def test_filename_must_match_slug(tmp_path):
    write_document(tmp_path, evidence_document(), filename="wrong.yaml")
    assert_fails(tmp_path, "does not match slug")


def test_date_relationships_and_future_checks(tmp_path):
    document = evidence_document()
    document["evidence"][0]["date"] = "2026-07-02"
    document["evidence"][0]["retrieved"] = "2026-07-01"
    document["last_checked"] = "2999-01-01"
    document["search"]["checked_at"] = "2999-01-01"
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "'date' must not be after 'retrieved'" in result.stdout
    assert "'last_checked' must not be in the future" in result.stdout


def test_complete_run_retrieval_date_must_match_check_date(tmp_path):
    document = evidence_document()
    document["evidence"][0]["retrieved"] = "2026-06-29"
    write_document(tmp_path, document)
    assert_fails(tmp_path, "requires 'retrieved' == 'last_checked'")


def test_max_age_days_can_make_freshness_a_gate(tmp_path):
    write_document(tmp_path, evidence_document())
    assert_fails(tmp_path, "days old (max 1)", "--max-age-days", "1")


def test_none_found_requires_complete_search_provenance(tmp_path):
    document = evidence_document(entries=[])
    write_document(tmp_path, document)
    result = run_validator(tmp_path)
    assert result.returncode == 0, result.stdout
    assert document["adoption_dimensions"]["independence_groups"] == 0
    assert document["verdict"] == "unverified"


def test_empty_evidence_directory_fails_closed(tmp_path):
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "no evidence YAML files found" in result.stdout


def test_mixed_type_top_level_keys_are_cleanly_rejected(tmp_path):
    path = write_document(tmp_path, evidence_document())
    path.write_text(path.read_text(encoding="utf-8") + "42: unexpected\n", encoding="utf-8")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "unknown top-level field '42'" in result.stdout
    assert "Traceback" not in result.stderr


def test_registry_enforces_canonical_name_as_well_as_slug(tmp_path):
    evidence_dir = make_evidence_dir(tmp_path)
    write_document(evidence_dir, evidence_document(pattern="Wrong Name"))
    registry = write_registry(tmp_path)
    assert_fails(
        evidence_dir, "does not match canonical catalog name",
        *registry_args(tmp_path, registry))


def test_registry_flags_orphan_and_uncovered_patterns(tmp_path):
    evidence_dir = make_evidence_dir(tmp_path)
    write_document(evidence_dir, evidence_document())
    registry = write_registry(tmp_path, (("other", "Other Pattern"),))
    result = run_validator(evidence_dir, *registry_args(tmp_path, registry))
    assert result.returncode == 1
    assert "orphan evidence file 'example.yaml'" in result.stdout
    assert "pattern 'other' has no evidence file" in result.stdout


def test_allowlist_permits_only_known_missing_patterns(tmp_path):
    evidence_dir = make_evidence_dir(tmp_path)
    write_document(evidence_dir, evidence_document())
    registry = write_registry(
        tmp_path, (("example", "Example Pattern"), ("pending", "Pending Pattern")))
    allowlist = write_allowlist(tmp_path, ["pending"])
    result = run_validator(
        evidence_dir, *registry_args(tmp_path, registry), "--allowlist", str(allowlist))
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    ("pending", "message"),
    [
        (["example"], "both evidence and a pending allowlist entry"),
        (["unknown"], "unknown pending allowlist entry"),
        (["pending", "pending"], "duplicate allowlist entry"),
    ],
)
def test_allowlist_overlap_unknown_and_duplicates_are_fatal(tmp_path, pending, message):
    evidence_dir = make_evidence_dir(tmp_path)
    write_document(evidence_dir, evidence_document())
    registry = write_registry(
        tmp_path, (("example", "Example Pattern"), ("pending", "Pending Pattern")))
    allowlist = write_allowlist(tmp_path, pending)
    assert_fails(
        evidence_dir, message, *registry_args(tmp_path, registry),
        "--allowlist", str(allowlist))


def test_registry_includes_experimental_name_and_slug(tmp_path):
    evidence_dir = make_evidence_dir(tmp_path)
    write_document(
        evidence_dir, evidence_document(slug="exp-pattern", pattern="Exp Pattern"))
    registry = write_registry(tmp_path, ())
    experiments = tmp_path / "experiments.md"
    experiments.write_text(
        "| **[Exp Pattern](#exp-pattern)** | Intermediate | Workflow | d | x |\n",
        encoding="utf-8")
    result = run_validator(
        evidence_dir, "--registry", str(registry), "--experiments", str(experiments))
    assert result.returncode == 0, result.stdout


def test_missing_directory_and_invalid_yaml_fail_cleanly(tmp_path):
    result = run_validator(tmp_path / "missing")
    assert result.returncode == 1
    assert "not found" in result.stdout
    (tmp_path / "broken.yaml").write_text("pattern: [unclosed\n", encoding="utf-8")
    assert_fails(tmp_path, "invalid YAML")


def fetch_status(url):
    try:
        CONTENT.fetch(url, timeout=10)
        return 200
    except CONTENT.requests.HTTPError as exc:
        return exc.response.status_code if exc.response is not None else type(exc).__name__
    except (
            CONTENT.requests.RequestException, CONTENT.UnsafeURL,
            CONTENT.ResponseTooLarge, CONTENT.UnsupportedContent) as exc:
        return type(exc).__name__


def collect_evidence_urls():
    urls = {}
    for path in sorted(EVIDENCE_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        evidence = data.get("evidence")
        for entry in evidence if isinstance(evidence, list) else []:
            url = entry.get("url") if isinstance(entry, dict) else None
            if url:
                urls.setdefault(url, path.name)
    return urls


@pytest.mark.slow
def test_evidence_urls_alive():
    """Complete and imported sources must not silently rot between refreshes."""
    if not EVIDENCE_DIR.is_dir():
        pytest.skip("no evidence directory committed yet")
    bot_guarded = {401, 403, 429}
    failures = []
    for url, filename in collect_evidence_urls().items():
        status = fetch_status(url)
        if isinstance(status, int) and status < 400:
            continue
        if status in bot_guarded:
            warnings.warn(
                f"{filename}: {url} -> HTTP {status}; source could not be machine-verified",
                stacklevel=1,
            )
            continue
        failures.append(f"{filename}: {url} -> {status}")
    assert not failures, "evidence link rot detected:\n" + "\n".join(failures)


def test_naming_discussions_have_ledger_rows():
    if not EVIDENCE_DIR.is_dir():
        pytest.skip("no evidence directory committed yet")
    assert DECISIONS.is_file()
    ledger = DECISIONS.read_text(encoding="utf-8")
    missing = []
    for path in sorted(EVIDENCE_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data.get("verdict") == "verified" and data.get("naming_alignment") != "strong":
            if data.get("pattern") not in ledger:
                missing.append(data.get("pattern"))
    assert not missing, "missing naming-decision rows: " + ", ".join(missing)


def test_status_view_in_sync():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "generate-verification-status.py"),
         "--check"],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    assert result.returncode == 0, f"{result.stdout}{result.stderr}"
