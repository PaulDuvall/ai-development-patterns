#!/usr/bin/env python3
"""Build a source-linked diagnostic bundle from agent trace JSON Lines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from agent_tracing import redact
from trace_metrics import summarize_trace


def load_events(path: str | Path) -> list[dict[str, Any]]:
    """Load valid JSON objects from a trace JSONL file."""
    events = []
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"line {line_number} is not a JSON object")
            events.append(value)
    return events


def failure_timeline(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return model/tool/error/evaluation events in diagnostic order."""
    relevant = {
        "model.call",
        "tool.call",
        "agent.handoff",
        "evaluation.result",
        "agent.error",
        "agent.run.end",
    }
    return [
        redact(
            {
                key: event.get(key)
                for key in (
                    "timestamp",
                    "event_type",
                    "span_id",
                    "parent_span_id",
                    "status",
                    "model",
                    "tool_name",
                    "duration_ms",
                    "cost_usd",
                    "error_type",
                    "error_message",
                    "evaluator",
                    "verdict",
                    "attributes",
                )
                if event.get(key) is not None
            }
        )
        for event in events
        if event.get("event_type") in relevant
    ]


def diagnosis_bundle(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a redacted bundle a human or fresh diagnostic agent can inspect."""
    return redact({
        "summary": summarize_trace(events),
        "failed_spans": [
            event.get("span_id")
            for event in events
            if event.get("status") == "error"
        ],
        "timeline": failure_timeline(events),
        "artifact_references": sorted(
            {
                str(value)
                for event in events
                for key, value in event.get("attributes", {}).items()
                if key.endswith("_ref") and value
            }
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", help="Path to agent trace JSONL")
    parser.add_argument("--output", help="Optional diagnostic-bundle JSON path")
    args = parser.parse_args()

    bundle = diagnosis_bundle(load_events(args.trace))
    payload = json.dumps(bundle, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
