"""Tests for the generated verification status semantics."""

import datetime
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
GENERATOR = REPO_ROOT / "scripts" / "generate-verification-status.py"


def load_generator():
    """Load the hyphenated generator script as a Python module."""
    spec = importlib.util.spec_from_file_location("verification_status", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evidence(verdict="verified", checked="2026-01-01", provenance="complete"):
    """Return the minimal fields consumed by the status generator."""
    return {
        "last_checked": checked,
        "provenance_status": provenance,
        "verdict": verdict,
        "adoption_score": 10,
        "naming_alignment": "strong",
    }


def test_freshness_distinguishes_current_stale_and_needs_refresh():
    """Freshness is independent of the adoption verdict."""
    module = load_generator()
    today = datetime.date(2026, 7, 10)

    assert module.evidence_freshness(
        evidence(checked="2026-04-11"), today) == "current"
    assert module.evidence_freshness(
        evidence(checked="2026-04-10"), today) == "stale"
    assert module.evidence_freshness(
        evidence(provenance="legacy-import"), today) == "needs refresh"


def test_summary_does_not_equate_assessed_with_verified(monkeypatch):
    """Coverage, verdict, pending, and freshness counts remain distinct."""
    module = load_generator()
    records = {
        "verified": evidence("verified", "2026-07-01"),
        "weak": evidence("weak", "2026-01-01"),
        "legacy": evidence("weak", "2026-07-01", "legacy-import"),
        "unverified": evidence("unverified", "2026-07-01"),
    }
    monkeypatch.setattr(module, "load_evidence", records.get)
    patterns = [(slug.title(), slug) for slug in (*records, "pending")]

    counts = module.summarize_patterns(patterns, datetime.date(2026, 7, 10))

    assert counts == {
        "assessed": 4,
        "verified": 1,
        "weak": 2,
        "unverified": 1,
        "pending": 1,
        "stale": 1,
        "needs refresh": 1,
    }


def test_render_table_exposes_counts_and_row_freshness(monkeypatch):
    """The Markdown heading and rows make provenance gaps visible."""
    module = load_generator()
    records = {
        "legacy": evidence("weak", "2026-07-01", "legacy-import"),
    }
    monkeypatch.setattr(module, "load_evidence", records.get)

    rendered = module.render_table(
        "Example", [("Legacy", "legacy"), ("Pending", "pending")], {},
        datetime.date(2026, 7, 10),
    )

    assert "1 of 2 assessed: 0 verified · 1 weak · 0 unverified · 1 pending" in rendered
    assert "0 stale · 1 need refresh" in rendered
    assert "| Legacy | weak | 10 | strong | 2026-07-01 | needs refresh |" in rendered
    assert "| Pending | pending | — | — | — | — |" in rendered


def test_configure_repo_root_retargets_all_derived_paths(tmp_path):
    module = load_generator()
    module.configure_repo_root(tmp_path)

    assert module.REPO_ROOT == tmp_path.resolve()
    assert module.STATUS_PATH == tmp_path.resolve() / "verification" / "STATUS.md"
    assert module.EVIDENCE_DIR == tmp_path.resolve() / "verification" / "evidence"
    assert module.DECISIONS_PATH == tmp_path.resolve() / "verification" / "DECISIONS.md"
