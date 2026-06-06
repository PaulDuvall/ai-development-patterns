"""Tests for the log-quality judge (inferential sensor, heuristic backend)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from log_quality_judge import (  # noqa: E402
    LogQualityVerdict,
    heuristic_judge,
    rate_log_quality,
)


def _entry(operation, **context):
    return {"operation": operation, "correlation_id": "req_1", "context": context}


def test_empty_logs_score_zero():
    verdict = rate_log_quality([])
    assert verdict.score == 0.0
    assert not verdict.is_useful
    assert "no logs emitted" in verdict.missing


def test_complete_logs_are_useful():
    entries = [
        _entry("payment_start", amount=10),
        _entry("payment_success", amount=10),
    ]
    verdict = rate_log_quality(entries)
    assert verdict.is_useful
    assert verdict.missing == []


def test_error_without_context_flags_missing_fields():
    entries = [_entry("payment_error")]  # no error_type / error_message
    verdict = rate_log_quality(entries)
    assert "error_type" in verdict.missing
    assert "error_message" in verdict.missing
    assert not verdict.is_useful


def test_error_with_context_is_useful():
    entries = [_entry("payment_error", error_type="ValueError", error_message="bad")]
    verdict = rate_log_quality(entries)
    assert verdict.is_useful


def test_missing_correlation_id_lowers_score():
    entries = [{"operation": "payment_start", "context": {}}]
    verdict = rate_log_quality(entries)
    assert "correlation_id" in verdict.missing


def test_pluggable_judge_overrides_default():
    stub = lambda entries: LogQualityVerdict(1.0, [], "stub")
    verdict = rate_log_quality([], judge=stub)
    assert verdict.reason == "stub"


def test_heuristic_judge_is_deterministic():
    entries = [_entry("payment_start", amount=10)]
    assert heuristic_judge(entries).score == heuristic_judge(entries).score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
