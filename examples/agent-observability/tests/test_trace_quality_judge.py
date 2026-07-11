"""Tests for trace quality, operational metrics, and failure diagnosis."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sample_agent_runs import failed_agent_run, successful_agent_run  # noqa: E402
from trace_diagnostics import diagnosis_bundle  # noqa: E402
from trace_metrics import budget_alerts, summarize_trace  # noqa: E402
from trace_quality_judge import (  # noqa: E402
    TraceQualityVerdict,
    rate_trace_quality,
)


def test_complete_trace_is_diagnostically_useful():
    verdict = rate_trace_quality(successful_agent_run())
    assert verdict.is_useful
    assert verdict.missing == ()


def test_failed_trace_requires_error_event_and_has_one():
    verdict = rate_trace_quality(failed_agent_run())
    assert "agent.error" not in verdict.missing


def test_missing_evaluation_lowers_quality():
    events = [
        event
        for event in successful_agent_run()
        if event["event_type"] != "evaluation.result"
    ]
    verdict = rate_trace_quality(events)
    assert not verdict.is_useful
    assert "evaluation.result" in verdict.missing


def test_pluggable_independent_judge_overrides_fallback():
    def reviewer(events):
        return TraceQualityVerdict(0.9, (), f"reviewed {len(events)} events")

    verdict = rate_trace_quality(successful_agent_run(), judge=reviewer)
    assert verdict.is_useful
    assert verdict.reason.startswith("reviewed")


def test_metrics_capture_cost_latency_tokens_tools_and_handoff():
    summary = summarize_trace(successful_agent_run())
    assert summary["outcome"] == "ok"
    assert summary["cost_usd"] == 0.024
    assert summary["input_tokens"] == 1800
    assert summary["output_tokens"] == 420
    assert summary["tools"] == {"apply_patch": 1, "pytest": 1}
    assert summary["handoffs"] == 1


def test_budget_alerts_are_deterministic():
    summary = summarize_trace(successful_agent_run())
    alerts = budget_alerts(
        summary,
        max_cost_usd=0.01,
        max_duration_ms=1000,
        max_output_tokens=300,
    )
    assert alerts == [
        "cost_budget_exceeded",
        "latency_budget_exceeded",
        "output_token_budget_exceeded",
    ]


def test_failure_bundle_preserves_timeline_and_artifact_references():
    bundle = diagnosis_bundle(failed_agent_run())
    assert bundle["summary"]["outcome"] == "error"
    assert bundle["failed_spans"]
    assert "artifacts/pytest-failure.txt" in bundle["artifact_references"]
    assert any(event["event_type"] == "agent.error" for event in bundle["timeline"])


def test_failure_bundle_redacts_untrusted_loaded_artifact_references():
    events = failed_agent_run()
    events[1]["attributes"]["request_ref"] = "Bearer abcdefghijklmnop"
    bundle = diagnosis_bundle(events)
    assert "abcdefghijklmnop" not in str(bundle)
    assert "[REDACTED]" in str(bundle)
