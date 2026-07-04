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
