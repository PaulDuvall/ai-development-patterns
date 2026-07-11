"""Pluggable quality assessment for the diagnostic usefulness of an agent trace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from trace_fitness import validate_trace


@dataclass(frozen=True)
class TraceQualityVerdict:
    score: float
    missing: tuple[str, ...]
    reason: str

    @property
    def is_useful(self) -> bool:
        return self.score >= 0.8


Judge = Callable[[list[dict]], TraceQualityVerdict]


REVIEW_PROMPT = """Review this redacted agent-run trace for diagnostic usefulness.
Check whether a reviewer can reconstruct the model calls, tool calls, handoffs,
evaluation, costs, latency, and failure path. Do not infer missing events. Return
JSON with score, missing, and reason. The evaluator must be independent of the
agent recorded as producer.

Trace:
{trace}
"""


def rate_trace_quality(
    events: list[dict], judge: Judge | None = None
) -> TraceQualityVerdict:
    """Rate the trace with a supplied independent judge or deterministic fallback."""
    return (judge or heuristic_judge)(events)


def heuristic_judge(events: list[dict]) -> TraceQualityVerdict:
    """Score schema validity and coverage without making a model call."""
    if not events:
        return TraceQualityVerdict(0.0, ("trace",), "no trace events")

    event_types = {event.get("event_type") for event in events}
    expected = {
        "agent.run.start",
        "agent.run.end",
        "model.call",
        "tool.call",
        "evaluation.result",
    }
    missing = sorted(expected - event_types)
    end = next(
        (event for event in reversed(events) if event.get("event_type") == "agent.run.end"),
        {},
    )
    if end.get("status") == "error" and "agent.error" not in event_types:
        missing.append("agent.error")

    violations = validate_trace(events)
    violation_rules = sorted({item["rule"] for item in violations})
    missing.extend(f"rule:{rule}" for rule in violation_rules)
    missing = sorted(set(missing))
    score = max(0.0, 1.0 - 0.12 * len(missing))
    reason = "complete diagnostic trace" if not missing else "trace has diagnostic gaps"
    return TraceQualityVerdict(round(score, 2), tuple(missing), reason)
