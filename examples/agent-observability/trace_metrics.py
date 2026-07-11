"""Cost, latency, token, tool, and evaluation summaries for agent traces."""

from __future__ import annotations

from collections import Counter
from typing import Any


def summarize_trace(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate the operational signals needed to review one agent run."""
    model_events = [event for event in events if event.get("event_type") == "model.call"]
    tool_events = [event for event in events if event.get("event_type") == "tool.call"]
    evaluations = [
        event for event in events if event.get("event_type") == "evaluation.result"
    ]
    end = next(
        (event for event in reversed(events) if event.get("event_type") == "agent.run.end"),
        {},
    )

    return {
        "trace_id": events[0].get("trace_id") if events else None,
        "run_id": events[0].get("run_id") if events else None,
        "outcome": end.get("status", "incomplete"),
        "run_duration_ms": _number(end.get("duration_ms")),
        "model_latency_ms": sum(_number(event.get("duration_ms")) for event in model_events),
        "tool_latency_ms": sum(_number(event.get("duration_ms")) for event in tool_events),
        "input_tokens": sum(_integer(event.get("input_tokens")) for event in model_events),
        "output_tokens": sum(_integer(event.get("output_tokens")) for event in model_events),
        "cost_usd": round(sum(_number(event.get("cost_usd")) for event in model_events), 6),
        "models": dict(Counter(event.get("model", "unknown") for event in model_events)),
        "tools": dict(Counter(event.get("tool_name", "unknown") for event in tool_events)),
        "tool_failures": sum(event.get("status") != "ok" for event in tool_events),
        "handoffs": sum(event.get("event_type") == "agent.handoff" for event in events),
        "evaluations": [
            {
                "evaluator": event.get("evaluator"),
                "verdict": event.get("verdict"),
                "score": event.get("score"),
            }
            for event in evaluations
        ],
        "errors": sum(event.get("event_type") == "agent.error" for event in events),
    }


def budget_alerts(
    summary: dict[str, Any],
    *,
    max_cost_usd: float,
    max_duration_ms: float,
    max_output_tokens: int,
) -> list[str]:
    """Return deterministic budget violations for a summarized trace."""
    alerts = []
    if summary.get("cost_usd", 0) > max_cost_usd:
        alerts.append("cost_budget_exceeded")
    if summary.get("run_duration_ms", 0) > max_duration_ms:
        alerts.append("latency_budget_exceeded")
    if summary.get("output_tokens", 0) > max_output_tokens:
        alerts.append("output_token_budget_exceeded")
    return alerts


def _number(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) else 0.0


def _integer(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) else 0
