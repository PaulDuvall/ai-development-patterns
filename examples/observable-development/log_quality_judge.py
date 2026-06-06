"""Log-quality judge (inferential sensor).

The probabilistic half of the Observable Development feedback loop. Where
`observability_fitness.py` answers "is it logged?", this answers "is it useful for
diagnosis?" by sampling structured log entries and rating them.

The judge is pluggable. The default `heuristic_judge` is deterministic and runs
with no external dependencies, so it is safe in CI. `anthropic_judge` wires the
same interface to an LLM-as-judge for richer, semantic verdicts in environments
where that is available.
"""

from typing import Callable

# A judge takes the parsed log entries for one operation and returns a verdict.
Judge = Callable[[list[dict]], "LogQualityVerdict"]

# Fields that make an error log diagnosable in a single pass.
REQUIRED_ERROR_FIELDS = frozenset({"error_type", "error_message"})

# Prompt used by the reflection loop and by `anthropic_judge`.
REFLECTION_PROMPT = """You are auditing the logs emitted for a single operation.
Rate, from 0.0 to 1.0, how useful these logs are for diagnosing a failure in one
pass. List any missing context (inputs to reproduce, error type/message, timing,
correlation id). Respond as JSON: {"score": float, "missing": [str], "reason": str}.

Logs:
{logs}
"""


class LogQualityVerdict:
    """A judge's rating of one operation's logs."""

    def __init__(self, score: float, missing: list[str], reason: str):
        self.score = score
        self.missing = missing
        self.reason = reason

    @property
    def is_useful(self) -> bool:
        """True if the logs clear the usefulness bar (score >= 0.7)."""
        return self.score >= 0.7

    def __repr__(self) -> str:
        return f"LogQualityVerdict(score={self.score}, missing={self.missing})"


def rate_log_quality(entries: list[dict], judge: Judge | None = None) -> LogQualityVerdict:
    """Rate one operation's log entries for diagnosability.

    Args:
        entries: Parsed structured log entries (dicts) for one operation.
        judge: Strategy to use; defaults to the deterministic `heuristic_judge`.

    Returns:
        A `LogQualityVerdict`.
    """
    return (judge or heuristic_judge)(entries)


def heuristic_judge(entries: list[dict]) -> LogQualityVerdict:
    """Deterministic judge: score logs by the diagnostic signals present."""
    if not entries:
        return LogQualityVerdict(0.0, ["no logs emitted"], "operation is a black box")
    missing = _missing_signals(entries)
    score = max(0.0, 1.0 - 0.25 * len(missing))
    reason = "all key diagnostic signals present" if not missing else "missing signals"
    return LogQualityVerdict(round(score, 2), missing, reason)


def _missing_signals(entries: list[dict]) -> list[str]:
    """Return the diagnostic signals absent from a set of log entries."""
    missing = []
    if not any(entry.get("correlation_id") for entry in entries):
        missing.append("correlation_id")
    error_entries = [e for e in entries if str(e.get("operation", "")).endswith("_error")]
    for field in sorted(REQUIRED_ERROR_FIELDS):
        if error_entries and not any(_context_has(e, field) for e in error_entries):
            missing.append(field)
    return missing


def _context_has(entry: dict, field: str) -> bool:
    """True if a log entry carries `field` at top level or inside context."""
    return field in entry or field in entry.get("context", {})


def anthropic_judge(model: str = "claude-haiku-4-5-20251001") -> Judge:
    """Build an LLM-as-judge backed by the Claude API.

    The API key is read from the ANTHROPIC_API_KEY environment variable by the SDK;
    no secret is passed or logged here. Returns a `Judge` callable so it is a drop-in
    replacement for `heuristic_judge`.
    """
    import json

    from anthropic import Anthropic  # Imported lazily so CI need not install it.

    client = Anthropic()

    def _judge(entries: list[dict]) -> LogQualityVerdict:
        prompt = REFLECTION_PROMPT.format(logs=json.dumps(entries, indent=2))
        message = client.messages.create(
            model=model, max_tokens=512, messages=[{"role": "user", "content": prompt}]
        )
        payload = json.loads(message.content[0].text)
        return LogQualityVerdict(payload["score"], payload["missing"], payload["reason"])

    return _judge
