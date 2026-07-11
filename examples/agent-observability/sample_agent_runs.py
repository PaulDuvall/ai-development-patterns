"""Sample successful, failed, and incomplete agent-run traces."""

from __future__ import annotations

from pathlib import Path

from agent_tracing import TraceRecorder


def successful_agent_run(output_path: str | Path | None = None) -> list[dict]:
    recorder = TraceRecorder(session_id="session_demo", output_path=output_path)
    root = recorder.start_run(
        goal="Add a validated retry policy",
        producer="implementation-agent",
        repository="example/service",
        base_commit="a1b2c3d",
    )
    recorder.model_call(
        parent_span_id=root,
        model="reasoning-model",
        input_tokens=1800,
        output_tokens=420,
        cost_usd=0.024,
        duration_ms=870,
        request_ref="sha256:request-1",
        response_ref="sha256:response-1",
    )
    recorder.tool_call(
        parent_span_id=root,
        tool_name="apply_patch",
        duration_ms=38,
        status="ok",
        input_ref="sha256:patch-plan",
        output_ref="git-diff:working-tree",
        exit_code=0,
    )
    recorder.tool_call(
        parent_span_id=root,
        tool_name="pytest",
        duration_ms=410,
        status="ok",
        input_ref="tests/test_retry.py",
        output_ref="artifacts/pytest.txt",
        exit_code=0,
    )
    recorder.handoff(
        parent_span_id=root,
        from_actor="implementation-agent",
        to_actor="verification-agent",
        reason="independent review after deterministic checks",
        artifact_ref="git:head:d4e5f6a",
    )
    recorder.evaluation(
        parent_span_id=root,
        evaluator="verification-agent",
        producer="implementation-agent",
        verdict="pass",
        score=0.96,
        check_ref="artifacts/verification.json",
    )
    recorder.finish_run(
        status="ok",
        head_commit="d4e5f6a",
        duration_ms=1560,
        summary_ref="artifacts/run-summary.json",
    )
    return recorder.events


def failed_agent_run(output_path: str | Path | None = None) -> list[dict]:
    recorder = TraceRecorder(session_id="session_failure", output_path=output_path)
    root = recorder.start_run(
        goal="Migrate a configuration schema",
        producer="implementation-agent",
        repository="example/service",
        base_commit="112233a",
    )
    recorder.model_call(
        parent_span_id=root,
        model="reasoning-model",
        input_tokens=950,
        output_tokens=210,
        cost_usd=0.012,
        duration_ms=440,
        request_ref="sha256:request-failure",
        response_ref="sha256:response-failure",
    )
    tool_span = recorder.tool_call(
        parent_span_id=root,
        tool_name="pytest",
        duration_ms=205,
        status="error",
        input_ref="tests/test_config.py",
        output_ref="artifacts/pytest-failure.txt",
        exit_code=1,
    )
    recorder.error(
        parent_span_id=tool_span,
        error_type="AssertionError",
        error_message="expected schema version 3, received 2",
        evidence_ref="artifacts/pytest-failure.txt",
    )
    recorder.finish_run(
        status="error",
        head_commit="112233a",
        duration_ms=720,
        summary_ref="artifacts/failed-run-summary.json",
    )
    return recorder.events


def incomplete_agent_run() -> list[dict]:
    """Anti-example: no closing event, tool evidence, or evaluation."""
    recorder = TraceRecorder(session_id="session_incomplete")
    root = recorder.start_run(
        goal="Unbounded task",
        producer="implementation-agent",
        repository="example/service",
        base_commit="abcdef0",
    )
    recorder.model_call(
        parent_span_id=root,
        model="reasoning-model",
        input_tokens=100,
        output_tokens=50,
        cost_usd=0.001,
        duration_ms=100,
        request_ref="sha256:incomplete-request",
        response_ref="sha256:incomplete-response",
    )
    return recorder.events
