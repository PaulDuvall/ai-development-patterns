"""Tests for agent-trace schema, relationships, redaction, and completeness."""

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tracing import REDACTED, TraceRecorder  # noqa: E402
from sample_agent_runs import (  # noqa: E402
    failed_agent_run,
    incomplete_agent_run,
    successful_agent_run,
)
from trace_fitness import validate_trace  # noqa: E402


def _rules(events):
    return {item["rule"] for item in validate_trace(events)}


def test_complete_agent_trace_passes():
    assert validate_trace(successful_agent_run()) == []


def test_trace_is_written_as_jsonl(tmp_path):
    output = tmp_path / "trace.jsonl"
    events = successful_agent_run(output)
    assert len(output.read_text().splitlines()) == len(events)


def test_recorder_refuses_to_mix_runs_in_existing_trace(tmp_path):
    output = tmp_path / "trace.jsonl"
    successful_agent_run(output)
    import pytest

    with pytest.raises(FileExistsError):
        TraceRecorder(session_id="second-run", output_path=output)


def test_incomplete_trace_fails_closed():
    rules = _rules(incomplete_agent_run())
    assert "expected_one_run_end" in rules


def test_unknown_parent_is_reported():
    events = successful_agent_run()
    events[1] = {**events[1], "parent_span_id": "span_missing"}
    assert "unknown_parent_span" in _rules(events)


def test_parent_must_precede_child_and_run_end_must_be_last():
    events = successful_agent_run()
    model = next(event for event in events if event["event_type"] == "model.call")
    tool = next(event for event in events if event["event_type"] == "tool.call")
    tool["parent_span_id"] = model["span_id"]
    events.remove(tool)
    events.insert(events.index(model), tool)
    rules = _rules(events)
    assert "parent_span_not_yet_emitted" in rules

    reordered = successful_agent_run()
    end = reordered.pop()
    reordered.insert(1, end)
    rules = _rules(reordered)
    assert "run_end_not_last" in rules


def test_self_evaluation_is_reported():
    events = successful_agent_run()
    evaluation = next(event for event in events if event["event_type"] == "evaluation.result")
    evaluation["evaluator"] = evaluation["producer"]
    assert "self_evaluation" in _rules(events)


def test_recorder_redacts_credentials_and_keeps_token_counts():
    recorder = TraceRecorder(session_id="redaction")
    root = recorder.start_run(
        goal="Inspect Authorization: Bearer abcdefghijklmnop",
        producer="agent",
        repository="example/repo",
        base_commit="1234567",
    )
    recorder.model_call(
        parent_span_id=root,
        model="model",
        input_tokens=123,
        output_tokens=45,
        cost_usd=0.1,
        duration_ms=5,
        request_ref="sk-abcdefghijklmnop",
        response_ref="sha256:redacted-response",
    )
    start, model = recorder.events
    assert REDACTED in start["attributes"]["goal"]
    assert model["attributes"]["request_ref"] == REDACTED
    assert model["input_tokens"] == 123


def test_raw_sensitive_value_is_reported():
    events = successful_agent_run()
    poisoned = copy.deepcopy(events)
    poisoned[1]["attributes"]["api_key"] = "sk-abcdefghijklmnop"
    assert "unredacted_sensitive_value" in _rules(poisoned)


def test_hyphenated_provider_keys_are_redacted():
    recorder = TraceRecorder(session_id="provider-keys")
    recorder.start_run(
        goal="Never persist sk-proj-abcdefghijklmnop or sk-ant-api03-abcdefghijklmnop",
        producer="agent",
        repository="example/repo",
        base_commit="1234567",
    )
    serialized = str(recorder.events)
    assert "sk-proj-" not in serialized
    assert "sk-ant-api03-" not in serialized
    assert REDACTED in serialized


def test_negative_usage_and_out_of_range_evaluation_are_reported():
    events = successful_agent_run()
    model = next(event for event in events if event["event_type"] == "model.call")
    evaluation = next(event for event in events if event["event_type"] == "evaluation.result")
    model["input_tokens"] = -1
    model["cost_usd"] = -0.1
    evaluation["score"] = 1.1
    rules = _rules(events)
    assert "negative_input_tokens" in rules
    assert "negative_cost_usd" in rules
    assert "evaluation_score_out_of_range" in rules


def test_required_diagnostic_attributes_are_enforced():
    events = successful_agent_run()
    start = next(event for event in events if event["event_type"] == "agent.run.start")
    model = next(event for event in events if event["event_type"] == "model.call")
    tool = next(event for event in events if event["event_type"] == "tool.call")
    evaluation = next(event for event in events if event["event_type"] == "evaluation.result")
    end = next(event for event in events if event["event_type"] == "agent.run.end")
    del start["attributes"]["repository"]
    del model["attributes"]["request_ref"]
    del tool["exit_code"]
    del evaluation["attributes"]["check_ref"]
    del end["attributes"]["head_commit"]
    rules = _rules(events)
    assert "missing_event_fields" in rules
    assert "missing_event_attributes" in rules


def test_unknown_terminal_status_is_rejected_by_api_and_validator():
    recorder = TraceRecorder(session_id="status")
    recorder.start_run(
        goal="status check",
        producer="agent",
        repository="example/repo",
        base_commit="1234567",
    )
    import pytest

    with pytest.raises(ValueError):
        recorder.finish_run(
            status="complete",
            head_commit="7654321",
            duration_ms=1,
            summary_ref="summary.json",
        )

    events = successful_agent_run()
    events[-1]["status"] = "complete"
    rules = _rules(events)
    assert "unknown_status" in rules


def test_schema_version_is_enforced():
    events = successful_agent_run()
    events[1]["schema_version"] = 999
    assert "unsupported_schema_version" in _rules(events)


def test_success_requires_an_independent_passing_evaluation():
    events = successful_agent_run()
    evaluation = next(event for event in events if event["event_type"] == "evaluation.result")
    evaluation["verdict"] = "fail"
    evaluation["status"] = "error"
    rules = _rules(events)
    assert "missing_passing_evaluation" in rules
    assert "successful_run_has_failed_evaluation" in rules


def test_error_outcome_requires_source_linked_error_event():
    events = [event for event in failed_agent_run() if event["event_type"] != "agent.error"]
    assert "missing_error_event" in _rules(events)


def test_tool_status_and_exit_code_must_agree():
    events = successful_agent_run()
    tool = next(event for event in events if event["event_type"] == "tool.call")
    tool["exit_code"] = 1
    assert "ok_tool_has_nonzero_exit" in _rules(events)

    failed = failed_agent_run()
    failed_tool = next(event for event in failed if event["event_type"] == "tool.call")
    failed_tool["exit_code"] = 0
    assert "failed_tool_has_zero_exit" in _rules(failed)
