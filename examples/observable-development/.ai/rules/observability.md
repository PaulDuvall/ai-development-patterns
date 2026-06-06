# Observability Standard (Feedforward Guide)

This is the **feedforward** half of [Observable Development](../../README.md): the
standard the AI agent writes against *before* any failure occurs. It is enforced by
the **feedback** half — `observability_fitness.py` (computational) and
`log_quality_judge.py` (inferential) — and is updated by the agent's reflection
loop each time the logs prove insufficient to diagnose a failure in one pass.

## Rules

1. **Every public operation emits a structured log.** Use the `log_operation`,
   `log_error`, or `log_performance` helpers from `observable_logging.py`. Never use
   bare `logging.info("...")` or `print(...)` for operational events.
2. **Correlation IDs propagate.** Structured helpers embed `correlation_id`
   automatically. Do not bypass them with raw logger calls, which drop the ID and
   break request tracing.
3. **Errors carry context.** Log the `error_type`, `error_message`, and the inputs
   needed to reproduce — not "something went wrong".
4. **Log start and outcome.** Each operation logs its start and its success or
   failure, so timing and state transitions are reconstructable.

## Reflection loop (how this file changes)

After the agent diagnoses a failure, run:

> Rate the logs you actually had to work with. What context was missing that would
> have made the root cause obvious in one pass? Emit the structured-logging changes
> that close that gap, and propose the update to this file so the next operation is
> logged the same way.

Apply the agent's accepted suggestion here. The harness improves each cycle instead
of repeating the same blind spots.
