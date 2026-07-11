"""Executable checks for redacted application failure artifacts."""

import json
import sys
from pathlib import Path


EXAMPLE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXAMPLE_DIR))

from application_failure_context import REDACTED, capture_failure, write_failure  # noqa: E402


class PaymentError(RuntimeError):
    """Example application failure."""


def test_capture_failure_keeps_diagnostic_fields_and_redacts_secrets():
    failure = capture_failure(
        operation="process_payment",
        error=PaymentError("provider rejected Bearer secret-token-value"),
        safe_inputs={
            "order_id": "order_42",
            "password": "do-not-store",
            "token": "plain-secret-token",
            "x-api-key": "plain-secret-api-key",
            "nested": ("Bearer tuple-secret-value",),
        },
        source_commit="9a17d2c",
        evidence_refs=["logs/order_42.jsonl", "sk-abcdefghijklmnop"],
        correlation_id="req_42",
        agent_trace_id="trace_4c2d",
    )

    assert failure["operation"] == "process_payment"
    assert failure["correlation_id"] == "req_42"
    assert failure["agent_trace_id"] == "trace_4c2d"
    assert failure["safe_inputs"]["order_id"] == "order_42"
    assert failure["safe_inputs"]["password"] == REDACTED
    assert failure["safe_inputs"]["token"] == REDACTED
    assert failure["safe_inputs"]["x-api-key"] == REDACTED
    assert failure["safe_inputs"]["nested"] == [REDACTED]
    assert REDACTED in failure["error_message"]
    assert failure["evidence_refs"][1] == REDACTED


def test_capture_failure_generates_a_correlation_id_when_absent():
    failure = capture_failure(
        operation="refresh_cache",
        error=RuntimeError("timeout"),
        safe_inputs={},
        source_commit="9a17d2c",
        evidence_refs=[],
    )

    assert failure["correlation_id"].startswith("req_")
    assert failure["agent_trace_id"] is None


def test_write_failure_redacts_a_mutated_artifact_before_persistence(tmp_path):
    path = tmp_path / "failure.json"
    write_failure(path, {
        "operation": "process_payment",
        "authorization": "Bearer secret-token-value",
        "error_message": "API key sk-abcdefghijklmnop",
    })

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["authorization"] == REDACTED
    assert REDACTED in written["error_message"]
    assert "secret-token-value" not in path.read_text(encoding="utf-8")
