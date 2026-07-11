# Agent Observability Standard

This feedforward guide implements [Agent Observability](../../../../README.md#agent-observability).
The deterministic feedback gate in `trace_fitness.py` enforces the schema; an
independent reviewer may use `trace_quality_judge.py` to assess whether a valid
trace is diagnostically useful.

## Required Events

1. **Root run span** — emit `agent.run.start` and `agent.run.end` with run,
   session, repository, base commit, final commit, status, and duration.
2. **Model calls** — record model identifier, input/output token counts, cost,
   latency, and status. Store hashes or artifact references, not raw prompts or
   responses.
3. **Tool calls** — record tool name, parent span, status, duration, exit code,
   and input/output references. Never put unrestricted tool payloads in a trace.
4. **Handoffs** — record source actor, target actor, reason, and artifact ref so
   responsibility changes are explicit.
5. **Evaluations** — bind evaluator and producer identities, verdict, score, and
   check artifact. A producer cannot certify its own successful run.
6. **Failures** — emit an `agent.error` event with the error type, redacted
   message, failed parent span, and immutable evidence reference.

## Correlation

- One `trace_id` joins the whole run.
- One `run_id` identifies the agent invocation.
- Every event has a unique `span_id`.
- Every non-root event has a valid `parent_span_id`.
- Preserve upstream trace IDs when an orchestrator delegates work; start a new
  run ID for the delegated agent.

## Privacy and Redaction

- Redact passwords, credentials, authorization headers, cookies, API keys, and
  tokens before writing an event.
- Prefer commit SHAs, content hashes, and artifact paths to raw source, prompts,
  responses, command arguments, or environment values.
- Apply repository retention and access policies to trace artifacts.
- A missing field stays missing; never ask a model to reconstruct telemetry.

## Operational Budgets

Capture cost, token, and latency fields for every model call and durations for
tool calls and the whole run. Evaluate budgets deterministically with
`trace_metrics.budget_alerts`; the agent does not raise its own limits.
