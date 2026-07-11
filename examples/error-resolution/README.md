# Error Resolution Pattern - Examples

This directory contains working examples and templates for the Error Resolution pattern.

## Directory Structure

```
examples/error-resolution/
├── application_failure_context.py   # Redacted, source-linked application failures
├── templates/                      # Reusable templates
│   ├── error-context-template.md  # Generic error context collection
│   └── ai-prompt-template.md      # Structured AI prompts for diagnosis
└── tests/
    └── test_application_failure_context.py  # Redaction and persistence checks
```

## Quick Start

### Capture Application Failure Context

Application logging belongs here when its purpose is reproducing and resolving a failure. Capture structured operation context and, when an agent was involved, correlate it to the separate [Agent Observability](../agent-observability/) trace:

```python
from application_failure_context import capture_failure, write_failure

try:
    process_payment(order_id="order_42")
except PaymentError as error:
    failure = capture_failure(
        operation="process_payment",
        error=error,
        safe_inputs={"order_id": "order_42"},
        source_commit="9a17d2c",
        evidence_refs=["logs/payment-order_42.jsonl", "traces/request-order_42.json"],
        correlation_id="req_42",
        agent_trace_id="trace_4c2d",
    )
    write_failure("artifacts/payment-failure.json", failure)
    raise
```

Record operation name, correlation ID, error type/message, safe reproduction inputs, source commit, and immutable log/trace references. Redact credentials before persistence. This artifact enters the human review workflow; it does not authorize automatic patch application.

### Using Templates

```bash
# 1. Copy error context template
cp templates/error-context-template.md .error-context.md

# 2. Fill in your error details
vim .error-context.md

# 3. Use AI prompt template
cat templates/ai-prompt-template.md | sed "s/ERROR_CONTEXT/$(cat .error-context.md)/" | ai
```

### Run the Example Tests

```bash
python -m pytest examples/error-resolution/tests -q
```

## Pattern Documentation

For complete pattern documentation, see the [Error Resolution](../../README.md#error-resolution) pattern in the main README.
