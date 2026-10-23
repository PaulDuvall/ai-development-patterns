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


def test_provenance_is_independent_of_verdict_and_of_age():
    """Provenance reflects the committed file, not the adoption verdict or age."""
    module = load_generator()

    assert module.evidence_provenance(evidence(checked="2026-04-11")) == "complete"
    # A decade-old check is still 'complete': age is the 90-day gate's concern,
    # not this view's. Baking age in here desynchronized the committed file with
    # no commit and sent CI to regenerate the table instead of refreshing evidence.
    assert module.evidence_provenance(evidence(checked="2016-01-01")) == "complete"
    assert module.evidence_provenance(evidence(provenance="legacy-import")) == "needs refresh"
    assert module.evidence_provenance(evidence(checked="not-a-date")) == "needs refresh"


def test_render_status_never_reads_the_clock(monkeypatch):
    """STATUS.md must be a pure function of its committed inputs.

    Guards the regression that broke the weekly run: a clock-derived column made
    --check fail on a calendar boundary rather than on an input change.
    """
    module = load_generator()

    class NoClockDate(datetime.date):
        @classmethod
        def today(cls):
            raise AssertionError("the status view must not read the clock")

    monkeypatch.setattr(module.datetime, "date", NoClockDate)

    rendered = module.render_status()

    assert "| Pattern | Verdict | Score | Naming | Last checked | Provenance " in rendered


def test_summary_does_not_equate_assessed_with_verified(monkeypatch):
    """Coverage, verdict, pending, and provenance counts remain distinct."""
    module = load_generator()
    records = {
        "verified": evidence("verified", "2026-07-01"),
        "weak": evidence("weak", "2026-01-01"),
        "legacy": evidence("weak", "2026-07-01", "legacy-import"),
        "unverified": evidence("unverified", "2026-07-01"),
    }
    monkeypatch.setattr(module, "load_evidence", records.get)
    patterns = [(slug.title(), slug) for slug in (*records, "pending")]

    counts = module.summarize_patterns(patterns)

    assert counts == {
        "assessed": 4,
        "verified": 1,
        "weak": 2,
        "unverified": 1,
        "pending": 1,
        "needs refresh": 1,
    }


def test_render_table_exposes_counts_and_row_provenance(monkeypatch):
    """The Markdown heading and rows make provenance gaps visible."""
    module = load_generator()
    records = {
        "legacy": evidence("weak", "2026-07-01", "legacy-import"),
        "ok": evidence("verified", "2026-07-01"),
    }
    monkeypatch.setattr(module, "load_evidence", records.get)

    rendered = module.render_table(
        "Example",
        [("Legacy", "legacy"), ("Ok", "ok"), ("Pending", "pending")], {},
    )

    assert "2 of 3 assessed: 1 verified · 1 weak · 0 unverified · 1 pending" in rendered
    assert "1 need refresh" in rendered
    assert "stale" not in rendered
    assert "| Legacy | weak | 10 | strong | 2026-07-01 | needs refresh |" in rendered
    assert "| Ok | verified | 10 | strong | 2026-07-01 | complete |" in rendered
    assert "| Pending | pending | — | — | — | — |" in rendered


def test_configure_repo_root_retargets_all_derived_paths(tmp_path):
    module = load_generator()
    module.configure_repo_root(tmp_path)

    assert module.REPO_ROOT == tmp_path.resolve()
    assert module.STATUS_PATH == tmp_path.resolve() / "verification" / "STATUS.md"
    assert module.EVIDENCE_DIR == tmp_path.resolve() / "verification" / "evidence"
    assert module.DECISIONS_PATH == tmp_path.resolve() / "verification" / "DECISIONS.md"
