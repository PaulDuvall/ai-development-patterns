"""
Tests for verification/evidence/*.yaml schema compliance.

Delegates to scripts/validate-evidence.py so CI enforces the same rules the
/verify-patterns pipeline runs locally: computed adoption_score, verdict, and
naming_alignment must recompute cleanly, and evidence entries must be complete.
"""

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import requests
import yaml

REPO_ROOT = Path(__file__).parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate-evidence.py"
EVIDENCE_DIR = REPO_ROOT / "verification" / "evidence"
REGISTRY = REPO_ROOT / "patterns.yaml"
ALLOWLIST = REPO_ROOT / "verification" / "pending-evidence.yaml"


def run_validator(directory, *extra_args):
    """Run the evidence validator against a directory; return CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--dir", str(directory), *extra_args],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )


def registry_args(directory, registry):
    """CLI args for a hermetic registry check (no real experiments file)."""
    return ("--registry", str(registry),
            "--experiments", str(directory / "no-experiments.md"))


def write_registry(directory, ids=("example",)):
    """Write a minimal patterns.yaml-shaped registry; return its path."""
    body = "patterns:\n" + "".join(f"- id: {i}\n  name: {i}\n" for i in ids)
    path = directory / "patterns.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def write_allowlist(directory, slugs):
    """Write a pending-evidence allowlist; return its path."""
    body = "pending:\n" + "".join(f"- {s}\n" for s in slugs)
    path = directory / "pending-evidence.yaml"
    path.write_text(body, encoding="utf-8")
    return path


EVIDENCE_TEMPLATE = """\
pattern: Example Pattern
slug: {slug}
last_checked: 2026-01-01
adoption_score: {score}
naming_alignment: {alignment}
evidence:
  - tier: T4
    match: named
    source: "Example blog"
    url: {url}
    date: '{date}'
    retrieved: '2026-01-01'
    claim: "Example claim"
verdict: {verdict}
"""


def write_evidence(directory, filename="example.yaml", slug="example", score=2,
                   alignment="strong", verdict="unverified",
                   url="https://example.com/post", date="2026-01-01"):
    """Write a single-entry evidence file (defaults recompute cleanly)."""
    content = EVIDENCE_TEMPLATE.format(
        slug=slug, score=score, alignment=alignment,
        verdict=verdict, url=url, date=date or "2026-01-01",
    )
    if date is None:  # undated source: the date field is omitted entirely
        lines = [l for l in content.splitlines() if not l.strip().startswith("date:")]
        content = "\n".join(lines) + "\n"
    (directory / filename).write_text(content, encoding="utf-8")


def test_validator_exists():
    """The evidence schema guard script must be present."""
    assert VALIDATOR.is_file(), f"missing {VALIDATOR}"


def test_all_evidence_files_valid():
    """Every committed evidence file must pass the schema guard."""
    if not EVIDENCE_DIR.is_dir():
        pytest.skip("no evidence directory committed yet")
    result = run_validator(EVIDENCE_DIR)
    assert result.returncode == 0, (
        f"evidence validation failed:\n{result.stdout}\n{result.stderr}"
    )


def test_catalog_and_evidence_stay_aligned():
    """Every catalog slug has evidence or is pending; no evidence is orphaned."""
    if not EVIDENCE_DIR.is_dir():
        pytest.skip("no evidence directory committed yet")
    result = run_validator(
        EVIDENCE_DIR, "--registry", str(REGISTRY), "--allowlist", str(ALLOWLIST))
    assert result.returncode == 0, (
        f"catalog/evidence alignment failed:\n{result.stdout}\n{result.stderr}"
    )


def make_evidence_dir(tmp_path):
    """Return an evidence subdirectory so registry files stay out of the glob."""
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    return evidence_dir


def test_registry_flags_orphan_evidence(tmp_path):
    """An evidence file whose slug left the catalog must fail, not linger."""
    evidence_dir = make_evidence_dir(tmp_path)
    write_evidence(evidence_dir)
    registry = write_registry(tmp_path, ids=("other-pattern",))
    result = run_validator(evidence_dir, *registry_args(tmp_path, registry))
    assert result.returncode == 1
    assert "orphan evidence file 'example.yaml'" in result.stdout


def test_registry_flags_uncovered_pattern(tmp_path):
    """A catalog pattern with no evidence file and no allowlist entry must fail."""
    evidence_dir = make_evidence_dir(tmp_path)
    write_evidence(evidence_dir)
    registry = write_registry(tmp_path, ids=("example", "uncovered"))
    result = run_validator(evidence_dir, *registry_args(tmp_path, registry))
    assert result.returncode == 1
    assert "pattern 'uncovered' has no evidence file" in result.stdout


def test_registry_allowlist_permits_missing_evidence(tmp_path):
    """An allowlisted pattern may lack evidence without failing the run."""
    evidence_dir = make_evidence_dir(tmp_path)
    write_evidence(evidence_dir)
    registry = write_registry(tmp_path, ids=("example", "uncovered"))
    allowlist = write_allowlist(tmp_path, ["uncovered"])
    result = run_validator(
        evidence_dir, *registry_args(tmp_path, registry), "--allowlist", str(allowlist))
    assert result.returncode == 0, result.stdout


def test_registry_notes_prunable_allowlist_entry(tmp_path):
    """A pattern with evidence AND an allowlist entry passes but prints a NOTE."""
    evidence_dir = make_evidence_dir(tmp_path)
    write_evidence(evidence_dir)
    registry = write_registry(tmp_path, ids=("example",))
    allowlist = write_allowlist(tmp_path, ["example"])
    result = run_validator(
        evidence_dir, *registry_args(tmp_path, registry), "--allowlist", str(allowlist))
    assert result.returncode == 0, result.stdout
    assert "remove it from the pending allowlist" in result.stdout


def test_registry_includes_experimental_patterns(tmp_path):
    """Slugs from the experiments reference table count as catalog patterns."""
    evidence_dir = make_evidence_dir(tmp_path)
    write_evidence(evidence_dir, filename="exp-pattern.yaml", slug="exp-pattern")
    registry = write_registry(tmp_path, ids=())
    experiments = tmp_path / "experiments.md"
    experiments.write_text(
        "| **[Exp Pattern](#exp-pattern)** | Intermediate | Workflow | d | x |\n",
        encoding="utf-8")
    result = run_validator(
        evidence_dir, "--registry", str(registry), "--experiments", str(experiments))
    assert result.returncode == 0, result.stdout


def test_validator_accepts_omitted_entry_date(tmp_path):
    """Undated sources omit 'date'; only 'retrieved' is mandatory."""
    write_evidence(tmp_path, date=None)
    result = run_validator(tmp_path)
    assert result.returncode == 0, result.stdout


def test_validator_requires_last_checked(tmp_path):
    """A file with neither last_checked nor legacy verified must fail."""
    bad = textwrap.dedent("""\
        pattern: Example Pattern
        slug: no-date
        adoption_score: 0
        naming_alignment: none
        evidence: none found
        verdict: unverified
    """)
    (tmp_path / "no-date.yaml").write_text(bad, encoding="utf-8")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "missing required field 'last_checked'" in result.stdout


def test_validator_rejects_both_check_date_fields(tmp_path):
    """Carrying last_checked AND legacy verified together must fail."""
    bad = textwrap.dedent("""\
        pattern: Example Pattern
        slug: both-dates
        last_checked: 2026-01-01
        verified: 2026-01-01
        adoption_score: 0
        naming_alignment: none
        evidence: none found
        verdict: unverified
    """)
    (tmp_path / "both-dates.yaml").write_text(bad, encoding="utf-8")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "use 'last_checked' only" in result.stdout


def test_validator_accepts_legacy_verified_field(tmp_path):
    """Files written before the rename (verified:) stay valid until regenerated."""
    good = textwrap.dedent("""\
        pattern: Example Pattern
        slug: legacy
        verified: 2026-01-01
        adoption_score: 0
        naming_alignment: none
        evidence: none found
        verdict: unverified
    """)
    (tmp_path / "legacy.yaml").write_text(good, encoding="utf-8")
    result = run_validator(tmp_path)
    assert result.returncode == 0, result.stdout


def test_validator_errors_on_missing_directory(tmp_path):
    """A missing --dir must exit non-zero, not report a clean pass."""
    result = run_validator(tmp_path / "does-not-exist")
    assert result.returncode == 1
    assert "not found" in result.stdout


def test_validator_reports_invalid_yaml(tmp_path):
    """Malformed YAML must fail that file without crashing the run."""
    (tmp_path / "broken.yaml").write_text("pattern: [unclosed\n", encoding="utf-8")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "invalid YAML" in result.stdout


def test_validator_rejects_non_mapping_entry(tmp_path):
    """A bare-string evidence entry must be a validation error, not a crash."""
    bad = textwrap.dedent("""\
        pattern: Example Pattern
        slug: bad-entry
        verified: 2026-01-01
        adoption_score: 0
        naming_alignment: none
        evidence:
          - just a string, not a mapping
        verdict: unverified
    """)
    (tmp_path / "bad-entry.yaml").write_text(bad, encoding="utf-8")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "must be a mapping" in result.stdout


def test_validator_rejects_asserted_verdict(tmp_path):
    """A verdict that does not recompute from the entries must fail."""
    bad = textwrap.dedent("""\
        pattern: Example Pattern
        slug: bad-verdict
        verified: 2026-01-01
        adoption_score: 2
        naming_alignment: strong
        evidence:
          - tier: T4
            match: named
            source: "Example blog"
            url: https://example.com/post
            date: 2026-01-01
            retrieved: 2026-01-01
            claim: "Example claim"
        verdict: verified
    """)
    (tmp_path / "bad-verdict.yaml").write_text(bad, encoding="utf-8")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "recomputes to" in result.stdout


def test_validator_requires_mechanism_quote(tmp_path):
    """Aliased/unnamed entries without a mechanism_quote must fail."""
    bad = textwrap.dedent("""\
        pattern: Example Pattern
        slug: no-quote
        verified: 2026-01-01
        adoption_score: 2
        naming_alignment: none
        evidence:
          - tier: T4
            match: unnamed
            source: "Example blog"
            url: https://example.com/post
            date: 2026-01-01
            retrieved: 2026-01-01
            claim: "Example claim"
        verdict: unverified
    """)
    (tmp_path / "no-quote.yaml").write_text(bad, encoding="utf-8")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "mechanism_quote" in result.stdout


def test_validator_enforces_tier_cap(tmp_path):
    """More than 3 entries in a single tier must fail validation."""
    entry = textwrap.dedent("""\
          - tier: T5
            match: named
            source: "Example discussion {n}"
            url: https://example.com/post-{n}
            date: 2026-01-01
            retrieved: 2026-01-01
            claim: "Example claim {n}"
    """)
    entries = "".join(entry.replace("{n}", str(n)) for n in range(4))
    bad = textwrap.dedent("""\
        pattern: Example Pattern
        slug: over-cap
        verified: 2026-01-01
        adoption_score: 4
        naming_alignment: strong
        evidence:
    """) + entries + "verdict: weak\n"
    (tmp_path / "over-cap.yaml").write_text(bad, encoding="utf-8")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "max 3" in result.stdout


def test_validator_baseline_fixture_passes(tmp_path):
    """The shared fixture must be valid so the mutation tests test one thing."""
    write_evidence(tmp_path)
    result = run_validator(tmp_path)
    assert result.returncode == 0, result.stdout


def test_validator_rejects_asserted_score(tmp_path):
    """An adoption_score that does not recompute from the entries must fail."""
    write_evidence(tmp_path, score=14)
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "adoption_score is 14, recomputes to 2" in result.stdout


def test_validator_rejects_asserted_naming_alignment(tmp_path):
    """A naming_alignment that does not recompute must fail."""
    write_evidence(tmp_path, alignment="none")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "naming_alignment is 'none', recomputes to 'strong'" in result.stdout


def test_validator_rejects_filename_slug_mismatch(tmp_path):
    """A file whose name differs from its slug breaks one-writer-per-resource."""
    write_evidence(tmp_path, filename="wrong-name.yaml")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "does not match slug" in result.stdout


def test_validator_rejects_null_slug(tmp_path):
    """A present-but-null slug must not bypass the filename-match check."""
    write_evidence(tmp_path, slug="null")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "'slug' must be non-empty" in result.stdout


def test_validator_rejects_impossible_calendar_date(tmp_path):
    """A well-shaped but impossible date (month 13, Feb 30) must fail."""
    write_evidence(tmp_path, date="2026-02-30")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "must be ISO 8601" in result.stdout


def test_validator_rejects_date_after_retrieved(tmp_path):
    """A source cannot carry a date later than the day it was retrieved."""
    write_evidence(tmp_path, date="2026-02-01")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "must not be after 'retrieved'" in result.stdout


def test_validator_rejects_placeholder_url(tmp_path):
    """The spec example's 'https://...' placeholder must never validate."""
    write_evidence(tmp_path, url="https://...")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "concrete http(s) URL" in result.stdout


def test_validator_rejects_empty_evidence_list(tmp_path):
    """'evidence: []' must be rejected in favor of the 'none found' encoding."""
    empty = textwrap.dedent("""\
        pattern: Example Pattern
        slug: empty-list
        verified: 2026-01-01
        adoption_score: 0
        naming_alignment: none
        evidence: []
        verdict: unverified
    """)
    (tmp_path / "empty-list.yaml").write_text(empty, encoding="utf-8")
    result = run_validator(tmp_path)
    assert result.returncode == 1
    assert "none found" in result.stdout


def test_validator_accepts_none_found(tmp_path):
    """A searched-but-empty file using 'none found' must pass."""
    good = textwrap.dedent("""\
        pattern: Example Pattern
        slug: nothing-found
        verified: 2026-01-01
        adoption_score: 0
        naming_alignment: none
        evidence: none found
        verdict: unverified
    """)
    (tmp_path / "nothing-found.yaml").write_text(good, encoding="utf-8")
    result = run_validator(tmp_path)
    assert result.returncode == 0, result.stdout


def fetch_status(url):
    """Return an HTTP status (falling back HEAD->GET) or an exception name."""
    headers = {"User-Agent": "Mozilla/5.0 (ai-development-patterns link check)"}
    try:
        response = requests.head(url, timeout=10, allow_redirects=True, headers=headers)
        if response.status_code >= 400:
            response = requests.get(url, timeout=10, allow_redirects=True,
                                    headers=headers, stream=True)
        return response.status_code
    except requests.RequestException as exc:
        return type(exc).__name__


def collect_evidence_urls():
    """Map each unique evidence URL to the first file that cites it."""
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
    """Verified verdicts must not silently rest on dead links (weekly check)."""
    if not EVIDENCE_DIR.is_dir():
        pytest.skip("no evidence directory committed yet")
    bot_guarded = {401, 403, 429}  # alive but refusing automated clients
    failures = []
    for url, filename in collect_evidence_urls().items():
        status = fetch_status(url)
        if isinstance(status, int) and (status < 400 or status in bot_guarded):
            continue
        failures.append(f"{filename}: {url} -> {status}")
    assert not failures, "evidence link rot detected:\n" + "\n".join(failures)
