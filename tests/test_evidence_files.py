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

REPO_ROOT = Path(__file__).parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate-evidence.py"
EVIDENCE_DIR = REPO_ROOT / "verification" / "evidence"


def run_validator(directory):
    """Run the evidence validator against a directory; return CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--dir", str(directory)],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )


EVIDENCE_TEMPLATE = """\
pattern: Example Pattern
slug: {slug}
verified: 2026-01-01
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
        verdict=verdict, url=url, date=date,
    )
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
