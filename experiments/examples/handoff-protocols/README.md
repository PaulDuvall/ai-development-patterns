# Handoff Protocols Example

This example accompanies the experimental [Handoff Protocols](../../README.md#handoff-protocols) pattern. It provides a task complexity assessor that scores a task description across security, creativity, integration, domain, time, and business-impact factors, then recommends a delegation strategy (`ai_first`, `ai_with_review`, `collaborative`, `human_first`, or `human_only`) with a confidence level, effort estimate, and risk rating.

## Current Status

`handoff_assessor.py` is a runnable, self-contained reference implementation of pre-task capability assessment: it decides how work should be delegated before it starts. The catalog entry for [Handoff Protocols](../../README.md#handoff-protocols) owns the return and approval boundary — the Return Contract that governs how delegated work comes back for review, approval, correction, or human takeover. This example does not implement that contract; alignment to the Return Contract is pending. Until then, read this example as a complement to the pattern: it demonstrates how work is routed to an executor, not how results return for approval.

## Files

- [`handoff_assessor.py`](handoff_assessor.py) — keyword- and heuristic-based task complexity scorer with a CLI. Requires Python 3.10+ and PyYAML (`pip install pyyaml`).

## Quick Start

```bash
# Assess a task with the built-in default weights and thresholds
python3 handoff_assessor.py --task "Implement JWT authentication for API"

# Machine-readable output with task context
python3 handoff_assessor.py --task "Migrate the orders database schema" \
  --priority high --output json

# Show per-factor scores behind a recommendation
python3 handoff_assessor.py --task "Redesign onboarding user experience" --debug
```

Verified output for the first command:

```text
Task Complexity Assessment
========================
Strategy: Ai First
Confidence: 89%
Complexity Score: 0.18
Estimated Effort: 1-2 hours
Risk Level: Low
Reasoning: Low complexity task suitable for AI automation with quality gates
```

## Configuration

The assessor looks for `handoff_config.yaml` (override with `--config`) and falls back to built-in defaults when the file is absent. A supplied file must define both blocks in full — partial files raise `KeyError`:

```yaml
complexity_thresholds:
  ai_first: 0.3
  ai_with_review: 0.7
  human_first: 0.9
  human_only: 1.0
assessment_criteria:
  security_weight: 0.25
  creativity_weight: 0.20
  integration_weight: 0.20
  domain_weight: 0.15
  time_weight: 0.10
  business_weight: 0.10
```

Two overrides bypass the thresholds: a task scoring high on both security and business criticality routes to `human_only`, and a task scoring very high on creativity routes to `collaborative`.

## Known Limitations

- Keyword scoring under-weights risk: the JWT example above routes to `ai_first` even though it is security-sensitive, because a short description matches too few keywords to cross the security override.
- The `--deadline-days` flag is accepted but has no effect through the CLI; the scoring code only reads it when a separate `deadline` context key is present, and the CLI never sets one.
- Scores are static heuristics with no feedback loop; the assessor never learns from actual delegation outcomes.
- The example stops at the recommendation. It does not execute a handoff, enforce quality gates, or produce the Return Contract defined by the catalog pattern.

## Integration with Other Patterns

### [Agent Observability](../../../README.md#agent-observability)

The `--output json` mode produces a machine-readable record of each routing decision (strategy, confidence, score, reasoning), suitable for logging alongside agent telemetry so routing accuracy can be audited against outcomes.

## Promotion Path

Promotion requires implementing the Return Contract from the catalog entry (typed return states, approval boundary, human takeover), replacing static keyword heuristics with outcome-calibrated scoring, and evidence from practitioner use that assessed routing outperforms unassisted delegation decisions.

## Anti-pattern: Scores as Gates

Wiring keyword-derived complexity scores directly into automated routing — with no human calibration and no outcome tracking — sends security-sensitive work to unsupervised automation whenever the task description happens to be terse. Treat the recommendation as decision support for a human, not as an authoritative gate.
