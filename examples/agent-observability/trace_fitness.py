"""Deterministic schema and diagnostic-quality checks for agent traces."""

from __future__ import annotations

import re
from typing import Any

from agent_tracing import (
    ALLOWED_STATUSES,
    REDACTED,
    SCHEMA_VERSION,
    SENSITIVE_KEYS,
)


BASE_FIELDS = frozenset(
    {
        "schema_version",
        "timestamp",
        "trace_id",
        "span_id",
        "run_id",
        "session_id",
        "event_type",
        "status",
    }
)
KNOWN_EVENT_TYPES = frozenset(
    {
        "agent.run.start",
        "agent.run.end",
        "model.call",
        "tool.call",
        "agent.handoff",
        "evaluation.result",
        "agent.error",
    }
)
SECRET_PATTERN = re.compile(
    r"(?i)(bearer\s+[A-Za-z0-9._~+/=-]+|\bsk-[A-Za-z0-9_-]{12,}\b|"
    r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{12,}\b)"
)


def validate_trace(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return structured violations; an empty list means the trace passes."""
    if not events:
        return [_violation(None, "empty_trace")]

    violations: list[dict[str, Any]] = []
    span_ids = [event.get("span_id") for event in events if event.get("span_id")]
    known_spans = set(span_ids)
    trace_ids = {event.get("trace_id") for event in events}
    run_ids = {event.get("run_id") for event in events}

    if len(trace_ids) != 1:
        violations.append(_violation(None, "multiple_trace_ids"))
    if len(run_ids) != 1:
        violations.append(_violation(None, "multiple_run_ids"))
    if len(span_ids) != len(known_spans):
        violations.append(_violation(None, "duplicate_span_id"))

    starts = [event for event in events if event.get("event_type") == "agent.run.start"]
    ends = [event for event in events if event.get("event_type") == "agent.run.end"]
    if len(starts) != 1:
        violations.append(_violation(None, "expected_one_run_start"))
    if len(ends) != 1:
        violations.append(_violation(None, "expected_one_run_end"))
    if events[0].get("event_type") != "agent.run.start":
        violations.append(_violation(events[0].get("span_id"), "run_start_not_first"))
    if events[-1].get("event_type") != "agent.run.end":
        violations.append(_violation(events[-1].get("span_id"), "run_end_not_last"))

    seen_spans: set[str] = set()
    for event in events:
        span_id = event.get("span_id")
        event_type = event.get("event_type")
        missing = sorted(BASE_FIELDS - event.keys())
        if missing:
            violations.append(_violation(span_id, "missing_base_fields", missing))
        if event.get("schema_version") != SCHEMA_VERSION:
            violations.append(
                _violation(span_id, "unsupported_schema_version", event.get("schema_version"))
            )
        if event_type not in KNOWN_EVENT_TYPES:
            violations.append(_violation(span_id, "unknown_event_type", event_type))
        parent = event.get("parent_span_id")
        if event_type == "agent.run.start" and parent is not None:
            violations.append(_violation(span_id, "root_has_parent"))
        if event_type != "agent.run.start":
            if parent not in known_spans:
                violations.append(_violation(span_id, "unknown_parent_span", parent))
            elif parent not in seen_spans:
                violations.append(_violation(span_id, "parent_span_not_yet_emitted", parent))
        violations.extend(_event_specific_violations(event))
        if _contains_secret(event):
            violations.append(_violation(span_id, "unredacted_sensitive_value"))
        if span_id:
            seen_spans.add(span_id)

    if ends and ends[-1].get("status") == "ok":
        evaluations = [
            event for event in events if event.get("event_type") == "evaluation.result"
        ]
        if not any(
            event.get("verdict") == "pass"
            and event.get("status") == "ok"
            and event.get("evaluator") != event.get("producer")
            for event in evaluations
        ):
            violations.append(
                _violation(ends[-1].get("span_id"), "missing_passing_evaluation")
            )
        if any(event.get("verdict") != "pass" for event in evaluations):
            violations.append(
                _violation(ends[-1].get("span_id"), "successful_run_has_failed_evaluation")
            )
    if ends and ends[-1].get("status") == "error":
        if not any(event.get("event_type") == "agent.error" for event in events):
            violations.append(_violation(ends[-1].get("span_id"), "missing_error_event"))

    return violations


def _event_specific_violations(event: dict[str, Any]) -> list[dict[str, Any]]:
    event_type = event.get("event_type")
    span_id = event.get("span_id")
    required: dict[str, tuple[str, ...]] = {
        "agent.run.start": ("producer",),
        "model.call": (
            "model",
            "input_tokens",
            "output_tokens",
            "cost_usd",
            "duration_ms",
        ),
        "tool.call": ("tool_name", "duration_ms", "exit_code"),
        "agent.handoff": ("from_actor", "to_actor", "reason"),
        "evaluation.result": ("evaluator", "producer", "verdict", "score"),
        "agent.error": ("error_type", "error_message"),
        "agent.run.end": ("duration_ms",),
    }
    missing = [field for field in required.get(event_type, ()) if event.get(field) is None]
    violations = []
    if missing:
        violations.append(_violation(span_id, "missing_event_fields", missing))
    required_attributes: dict[str, tuple[str, ...]] = {
        "agent.run.start": ("goal", "repository", "base_commit"),
        "model.call": ("request_ref", "response_ref"),
        "tool.call": ("input_ref", "output_ref"),
        "agent.handoff": ("artifact_ref",),
        "evaluation.result": ("check_ref",),
        "agent.error": ("evidence_ref",),
        "agent.run.end": ("head_commit", "summary_ref"),
    }
    attributes = event.get("attributes")
    missing_attributes = [
        field
        for field in required_attributes.get(event_type, ())
        if not isinstance(attributes, dict) or attributes.get(field) is None
    ]
    if missing_attributes:
        violations.append(
            _violation(span_id, "missing_event_attributes", missing_attributes)
        )
    status = event.get("status")
    if status not in ALLOWED_STATUSES:
        violations.append(_violation(span_id, "unknown_status", status))
    expected_statuses = {
        "agent.run.start": {"running"},
        "agent.run.end": {"ok", "error", "cancelled"},
        "model.call": {"ok", "error"},
        "tool.call": {"ok", "error"},
        "agent.handoff": {"ok"},
        "evaluation.result": {"ok", "error"},
        "agent.error": {"error"},
    }
    if status in ALLOWED_STATUSES and status not in expected_statuses.get(event_type, set()):
        violations.append(_violation(span_id, "invalid_event_status", status))
    if event_type == "evaluation.result" and event.get("evaluator") == event.get("producer"):
        violations.append(_violation(span_id, "self_evaluation"))
    if event_type == "evaluation.result":
        score = event.get("score")
        if isinstance(score, (int, float)) and not 0 <= score <= 1:
            violations.append(_violation(span_id, "evaluation_score_out_of_range"))
        if event.get("verdict") not in {"pass", "fail"}:
            violations.append(_violation(span_id, "invalid_evaluation_verdict"))
    if event_type == "model.call":
        for field in ("input_tokens", "output_tokens", "cost_usd"):
            value = event.get(field)
            if isinstance(value, (int, float)) and value < 0:
                violations.append(_violation(span_id, f"negative_{field}"))
    if event_type in {"model.call", "tool.call", "agent.run.end"}:
        duration = event.get("duration_ms")
        if isinstance(duration, (int, float)) and duration < 0:
            violations.append(_violation(span_id, "negative_duration"))
    if event_type == "tool.call":
        exit_code = event.get("exit_code")
        if event.get("status") == "ok" and exit_code != 0:
            violations.append(_violation(span_id, "ok_tool_has_nonzero_exit"))
        if event.get("status") == "error" and exit_code == 0:
            violations.append(_violation(span_id, "failed_tool_has_zero_exit"))
    return violations


def _contains_secret(value: Any, key: str | None = None) -> bool:
    if key and _is_sensitive_key(key) and value != REDACTED:
        return True
    if isinstance(value, dict):
        return any(_contains_secret(child, str(child_key)) for child_key, child in value.items())
    if isinstance(value, list):
        return any(_contains_secret(child) for child in value)
    return isinstance(value, str) and value != REDACTED and bool(SECRET_PATTERN.search(value))


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return normalized in SENSITIVE_KEYS or any(
        normalized.endswith(f"_{marker}") for marker in SENSITIVE_KEYS
    )


def _violation(span_id: str | None, rule: str, detail: Any = None) -> dict[str, Any]:
    result = {"span_id": span_id, "rule": rule}
    if detail is not None:
        result["detail"] = detail
    return result
