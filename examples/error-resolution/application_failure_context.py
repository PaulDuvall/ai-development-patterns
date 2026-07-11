"""Structured application failure context for human-gated Error Resolution.

This is application telemetry, not an agent-run trace. It captures the business
operation, correlation ID, exact failure, safe reproduction inputs, and source
revision that a diagnostic agent needs to propose a fix.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REDACTED = "[REDACTED]"
SENSITIVE_KEYS = frozenset(
    {
        "api_key",
        "authorization",
        "cookie",
        "credential",
        "password",
        "secret",
        "token",
        "access_token",
        "refresh_token",
    }
)
SECRET_VALUE = re.compile(
    r"(?i)(bearer\s+[A-Za-z0-9._~+/=-]+|\bsk-[A-Za-z0-9_-]{12,}\b|"
    r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{12,}\b)"
)


def capture_failure(
    *,
    operation: str,
    error: Exception,
    safe_inputs: dict[str, Any],
    source_commit: str,
    evidence_refs: list[str],
    correlation_id: str | None = None,
    agent_trace_id: str | None = None,
) -> dict[str, Any]:
    """Return redacted, source-linked context for one application failure."""
    return _redact(
        {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "correlation_id": correlation_id or f"req_{uuid.uuid4().hex[:16]}",
            "agent_trace_id": agent_trace_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "safe_inputs": safe_inputs,
            "source_commit": source_commit,
            "evidence_refs": evidence_refs,
        }
    )


def write_failure(path: str | Path, failure: dict[str, Any]) -> None:
    """Write one reviewed failure-context artifact as JSON."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(_redact(failure), indent=2, sort_keys=True) + "\n")


def _redact(value: Any, key: str | None = None) -> Any:
    if key and _is_sensitive_key(key):
        return REDACTED
    if isinstance(value, dict):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value]
    if isinstance(value, str):
        return SECRET_VALUE.sub(REDACTED, value)
    return value


def _is_sensitive_key(key: str) -> bool:
    """Match exact or provider-prefixed secret keys after normalization."""
    normalized = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
    return normalized in SENSITIVE_KEYS or any(
        normalized.endswith(f"_{marker}") for marker in SENSITIVE_KEYS
    )
