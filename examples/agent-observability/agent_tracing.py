"""Structured tracing primitives for agent runs.

The recorder captures the control-plane events needed to reconstruct an agent
run without persisting raw prompts, model output, tool payloads, or secrets.
It has no provider dependency and writes optional JSON Lines for later review.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


SCHEMA_VERSION = 1
REDACTED = "[REDACTED]"
ALLOWED_STATUSES = frozenset({"running", "ok", "error", "cancelled"})
SENSITIVE_KEYS = frozenset(
    {
        "api_key",
        "authorization",
        "cookie",
        "credential",
        "password",
        "secret",
        "token",
    }
)
SECRET_PATTERNS = (
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{12,}\b"),
)


def utc_now() -> str:
    """Return an RFC 3339 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    """Return a compact opaque identifier suitable for trace joins."""
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def redact(value: Any, key: str | None = None) -> Any:
    """Recursively redact sensitive keys and recognizable credential strings."""
    if key and _is_sensitive_key(key):
        return REDACTED
    if isinstance(value, dict):
        return {str(k): redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        result = value
        for pattern in SECRET_PATTERNS:
            result = pattern.sub(REDACTED, result)
        return result
    return value


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return normalized in SENSITIVE_KEYS or any(
        normalized.endswith(f"_{marker}") for marker in SENSITIVE_KEYS
    )


class TraceRecorder:
    """Collect one agent run as structured, redacted trace events."""

    def __init__(
        self,
        *,
        session_id: str,
        output_path: str | Path | None = None,
        clock: Callable[[], str] = utc_now,
    ) -> None:
        self.session_id = session_id
        self.trace_id = new_id("trace")
        self.run_id = new_id("run")
        self.output_path = Path(output_path) if output_path else None
        if self.output_path and self.output_path.exists() and self.output_path.stat().st_size:
            raise FileExistsError(
                f"refusing to append a new run to existing trace: {self.output_path}"
            )
        self.clock = clock
        self.events: list[dict[str, Any]] = []
        self.root_span_id: str | None = None

    def start_run(
        self,
        *,
        goal: str,
        producer: str,
        repository: str,
        base_commit: str,
    ) -> str:
        """Start the root agent-run span and return its span ID."""
        if self.root_span_id:
            raise RuntimeError("run already started")
        self.root_span_id = new_id("span")
        self._emit(
            "agent.run.start",
            span_id=self.root_span_id,
            status="running",
            producer=producer,
            attributes={
                "goal": goal,
                "repository": repository,
                "base_commit": base_commit,
            },
        )
        return self.root_span_id

    def model_call(
        self,
        *,
        parent_span_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        duration_ms: float,
        request_ref: str,
        response_ref: str,
        status: str = "ok",
    ) -> str:
        """Record model metadata without storing raw prompts or responses."""
        return self._emit(
            "model.call",
            parent_span_id=parent_span_id,
            status=status,
            duration_ms=duration_ms,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            attributes={"request_ref": request_ref, "response_ref": response_ref},
        )

    def tool_call(
        self,
        *,
        parent_span_id: str,
        tool_name: str,
        duration_ms: float,
        status: str,
        input_ref: str,
        output_ref: str,
        exit_code: int,
    ) -> str:
        """Record a tool invocation using references instead of raw payloads."""
        return self._emit(
            "tool.call",
            parent_span_id=parent_span_id,
            status=status,
            duration_ms=duration_ms,
            tool_name=tool_name,
            exit_code=exit_code,
            attributes={"input_ref": input_ref, "output_ref": output_ref},
        )

    def handoff(
        self,
        *,
        parent_span_id: str,
        from_actor: str,
        to_actor: str,
        reason: str,
        artifact_ref: str,
    ) -> str:
        """Record an explicit producer-to-reviewer or agent-to-agent handoff."""
        return self._emit(
            "agent.handoff",
            parent_span_id=parent_span_id,
            status="ok",
            from_actor=from_actor,
            to_actor=to_actor,
            reason=reason,
            attributes={"artifact_ref": artifact_ref},
        )

    def evaluation(
        self,
        *,
        parent_span_id: str,
        evaluator: str,
        producer: str,
        verdict: str,
        score: float,
        check_ref: str,
    ) -> str:
        """Record an evaluation and the identities needed to check independence."""
        return self._emit(
            "evaluation.result",
            parent_span_id=parent_span_id,
            status="ok" if verdict == "pass" else "error",
            evaluator=evaluator,
            producer=producer,
            verdict=verdict,
            score=score,
            attributes={"check_ref": check_ref},
        )

    def error(
        self,
        *,
        parent_span_id: str,
        error_type: str,
        error_message: str,
        evidence_ref: str,
    ) -> str:
        """Record a failure with a source reference for diagnosis."""
        return self._emit(
            "agent.error",
            parent_span_id=parent_span_id,
            status="error",
            error_type=error_type,
            error_message=error_message,
            attributes={"evidence_ref": evidence_ref},
        )

    def finish_run(
        self,
        *,
        status: str,
        head_commit: str,
        duration_ms: float,
        summary_ref: str,
    ) -> str:
        """Close the run with its exact output commit and summary reference."""
        if status not in {"ok", "error", "cancelled"}:
            raise ValueError("run status must be ok, error, or cancelled")
        return self._emit(
            "agent.run.end",
            parent_span_id=self._root(),
            status=status,
            duration_ms=duration_ms,
            attributes={"head_commit": head_commit, "summary_ref": summary_ref},
        )

    def _root(self) -> str:
        if not self.root_span_id:
            raise RuntimeError("start_run must be called first")
        return self.root_span_id

    def _emit(
        self,
        event_type: str,
        *,
        span_id: str | None = None,
        parent_span_id: str | None = None,
        status: str,
        duration_ms: float | None = None,
        attributes: dict[str, Any] | None = None,
        **fields: Any,
    ) -> str:
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"unsupported trace status: {status}")
        if event_type != "agent.run.start":
            self._root()
        event_span_id = span_id or new_id("span")
        event = redact(
            {
                "schema_version": SCHEMA_VERSION,
                "timestamp": self.clock(),
                "trace_id": self.trace_id,
                "span_id": event_span_id,
                "parent_span_id": parent_span_id,
                "run_id": self.run_id,
                "session_id": self.session_id,
                "event_type": event_type,
                "status": status,
                "duration_ms": duration_ms,
                "attributes": attributes or {},
                **fields,
            }
        )
        self.events.append(event)
        if self.output_path:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with self.output_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event, sort_keys=True) + "\n")
        return event_span_id
