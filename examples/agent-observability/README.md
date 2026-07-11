# Agent Observability Example

This directory implements [Agent Observability](../../README.md#agent-observability) for agent runs—not application business operations. It records model calls, tool calls, handoffs, evaluations, cost, latency, tokens, and failures as redacted, correlated trace events.

## Files

- `agent_tracing.py` — provider-neutral JSONL trace recorder with pre-write redaction.
- `trace_metrics.py` — deterministic cost, token, latency, tool, handoff, and outcome summaries.
- `trace_diagnostics.py` — failure timeline and source-linked diagnostic bundle builder.
- `trace_fitness.py` — schema, span relationship, independence, completeness, and secret checks.
- `trace_quality_judge.py` — pluggable diagnostic-usefulness review with a deterministic fallback.
- `sample_agent_runs.py` — complete, failed, and incomplete example runs.
- `.ai/rules/agent-observability.md` — the trace contract agents and orchestrators must follow.
- `tests/` — executable examples for trace validity, redaction, metrics, evaluation, and diagnosis.

## Trace Shape

Every event carries `trace_id`, `span_id`, `parent_span_id`, `run_id`, and `session_id`. Event-specific fields make the run reconstructable:

```json
{
  "schema_version": 1,
  "trace_id": "trace_...",
  "span_id": "span_...",
  "parent_span_id": "span_root",
  "run_id": "run_...",
  "session_id": "session_demo",
  "event_type": "model.call",
  "status": "ok",
  "model": "reasoning-model",
  "input_tokens": 1800,
  "output_tokens": 420,
  "cost_usd": 0.024,
  "duration_ms": 870,
  "attributes": {
    "request_ref": "sha256:request-1",
    "response_ref": "sha256:response-1"
  }
}
```

Raw prompts, model responses, tool payloads, source files, and environment values are deliberately absent. Store them in access-controlled artifacts when required and reference them by hash, commit, or path.

## Record a Run

Run the examples from this directory so the provider-neutral modules resolve consistently:

```bash
cd examples/agent-observability
mkdir -p artifacts
```

```python
from agent_tracing import TraceRecorder

trace = TraceRecorder(session_id="session_42", output_path="artifacts/failed-trace.jsonl")
root = trace.start_run(
    goal="Fix the failing retry test",
    producer="implementation-agent",
    repository="acme/payments",
    base_commit="9a17d2c",
)

trace.model_call(
    parent_span_id=root,
    model="reasoning-model",
    input_tokens=1200,
    output_tokens=280,
    cost_usd=0.018,
    duration_ms=610,
    request_ref="sha256:request",
    response_ref="sha256:response",
)
test_span = trace.tool_call(
    parent_span_id=root,
    tool_name="pytest",
    duration_ms=430,
    status="error",
    input_ref="tests/test_retry.py",
    output_ref="artifacts/pytest.txt",
    exit_code=1,
)
trace.error(
    parent_span_id=test_span,
    error_type="AssertionError",
    error_message="expected 3 retries, observed 4",
    evidence_ref="artifacts/pytest.txt",
)
trace.finish_run(
    status="error",
    head_commit="9a17d2c",
    duration_ms=1100,
    summary_ref="artifacts/run-summary.json",
)
```

## Validate and Summarize

```python
from sample_agent_runs import successful_agent_run
from trace_fitness import validate_trace
from trace_metrics import budget_alerts, summarize_trace
from trace_quality_judge import rate_trace_quality

events = successful_agent_run("artifacts/success-trace.jsonl")
assert validate_trace(events) == []

summary = summarize_trace(events)
assert budget_alerts(
    summary,
    max_cost_usd=0.10,
    max_duration_ms=5000,
    max_output_tokens=1000,
) == []
assert rate_trace_quality(events).is_useful
```

The deterministic validator checks what can be proven from structure. A fresh reviewer can use the pluggable quality interface for semantic assessment; the producer identity and evaluator identity remain distinct in the trace.

## Diagnose a Failure

```bash
python trace_diagnostics.py artifacts/failed-trace.jsonl \
  --output artifacts/diagnostic-bundle.json
```

The bundle contains a cost/latency summary, failed span IDs, ordered model/tool/error/evaluation events, and immutable artifact references. Feed that redacted bundle into human-gated [Error Resolution](../error-resolution/) rather than sending raw credentials or an entire repository to a diagnostic model.

## Run the Example Tests

```bash
python -m pytest tests -q
```

## Anti-pattern: Opaque Runs

A transcript alone is not an operational trace. Without span relationships, model and tool metadata, costs, handoffs, evaluation identity, and source-linked failures, reviewers cannot reconstruct what acted, what it touched, why it stopped, or whether the producer certified itself.
