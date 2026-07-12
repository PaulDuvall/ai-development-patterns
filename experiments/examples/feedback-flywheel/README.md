# Feedback Flywheel Implementation

This example implements the experimental [Feedback Flywheel](../../README.md#feedback-flywheel) pattern: teams improve AI-assisted development through structured retrospectives that feed corrections back into codified rules and custom commands.

## Current Status

The session log schema, analysis script, and worked example are a functional reference implementation. The script runs standalone with Python 3.9+ and PyYAML. Session logging itself is a manual discipline — nothing here captures outcomes automatically, and adopters supply their own rules directory and command tooling.

## Overview

Feedback Flywheel enables teams to:
- Analyze AI-assisted session logs for repeated correction cycles
- Extract patterns from what worked vs. what required rework
- Propose updates to codified rules, custom commands, and progressive disclosure routing
- Track first-pass acceptance rate as a leading indicator of AI collaboration maturity

## Files in this Example

- `README.md` - Usage documentation (this file)
- [`session-log-schema.md`](session-log-schema.md) - Structured format for capturing session outcomes
- [`retro-analysis.py`](retro-analysis.py) - Script to extract correction patterns from session logs
- [`example-retro/sample-session.yaml`](example-retro/sample-session.yaml) - Example session log
- [`example-retro/retro-output.md`](example-retro/retro-output.md) - Annotated worked report based on the sample log; its no-repeat note and Analysis section are human additions beyond the analyzer's output

## Pattern Definition

For the pattern definition, maturity, related patterns, and source, see [Feedback Flywheel](../../README.md#feedback-flywheel) in the experiments catalog.

## Core Implementation

### Session Log Schema

Capture structured outcomes after each AI-assisted session:

```yaml
# .ai/session-logs/2026-04-08.yaml
session:
  date: "2026-04-08"
  developer: "alice"
  task_type: "feature"
  duration_minutes: 45

outcomes:
  first_pass_accepted: 3
  required_correction: 2
  total_generations: 5
  acceptance_rate: 0.60

corrections:
  - generation: "database migration"
    issue: "used raw SQL instead of ORM migration"
    correction: "regenerated with Django migration framework"
    root_cause: "missing framework preference in rules"
    proposed_rule: "Always use Django ORM migrations, never raw SQL"

  - generation: "API endpoint"
    issue: "returned 200 for creation instead of 201"
    correction: "manually changed status code"
    root_cause: "no HTTP status code convention in rules"
    proposed_rule: "Use 201 for resource creation, 204 for deletion"

insights:
  worked_well:
    - "test generation with existing fixtures"
    - "error handling followed project conventions"
  pattern_detected: "framework-specific conventions missing from rules"
```

### Retrospective Analysis

Run periodic retrospectives to extract actionable improvements:

```bash
# Weekly retro: analyze last 7 days of session logs
python retro-analysis.py --period 7d --output retro-report.md

# Monthly trend: track acceptance rate over time
python retro-analysis.py --period 30d --trend --output monthly-trend.md
```

[`retro-analysis.py`](retro-analysis.py) loads session logs from `--log-dir` (default: `.ai/session-logs`), computes the aggregate first-pass acceptance rate, ranks root causes by frequency, flags corrections whose proposed rule recurs across sessions, and writes a markdown report to `--output` (default: stdout). It requires Python 3.9+ and PyYAML (`pip install pyyaml`). See [`example-retro/retro-output.md`](example-retro/retro-output.md) for an annotated worked report; the analyzer does not generate its explicit no-repeat note or Analysis section.

### Feeding Back Into Rules

The retrospective output drives concrete updates:

```bash
# 1. Review the proposed-rule section from the retro
sed -n '/^## Proposed Rule Updates/,/^## /p' retro-report.md

# 2. Add validated rules to project configuration
ai "Review these proposed rules from our retrospective:
$(cat retro-report.md)

For each proposed rule:
1. Check if it conflicts with existing rules in .ai/rules/
2. Draft the rule in our standard format
3. Add to the appropriate rules file"

```

In a later session, exercise the rule by asking your own configured AI assistant to generate a
database migration that adds a `status` column to `orders`. Inspect and validate the generated
migration; this example assumes no particular result.

### Metrics Dashboard

Track the flywheel's effectiveness over time:

```markdown
## Team Metrics (Rolling 30 Days)

| Metric                    | Current | Previous | Trend |
|---------------------------|---------|----------|-------|
| First-pass acceptance rate| 78%     | 65%      | +13%  |
| Corrections per session   | 1.2     | 2.4      | -50%  |
| Rules added from retro    | 4       | 6        | -     |
| Repeated corrections      | 0       | 3        | -100% |
```

**First-pass acceptance rate** is the primary leading indicator. It measures how often AI-generated code is accepted without modification on the first attempt. Rising acceptance rate signals that rules and context are improving.

### Custom Command: `/retro`

Automate the retrospective with a custom command:

```yaml
# .ai/commands/retro.yaml
name: retro
description: "Run a feedback retrospective on recent AI sessions"
steps:
  - analyze: "Review session logs from the past {{period | default: '7d'}}"
  - extract: "Identify repeated corrections and root causes"
  - propose: "Draft rule updates for top 3 root causes"
  - report: "Generate retro summary with acceptance rate trend"
```

## Anti-pattern: Blind Iteration

**What it looks like**: Running AI-assisted sessions repeatedly without analyzing what went wrong or feeding corrections back into rules. Each session starts from scratch, repeating the same mistakes.

**Why it fails**:
- Same corrections applied manually session after session
- No institutional memory of what prompts or rules work
- Acceptance rate stays flat or declines as codebase grows
- Developer frustration increases as AI "never learns"

**Example**:

```yaml
# Week 1: Developer corrects AI output for missing error handling
# Week 2: Same developer corrects same error handling pattern
# Week 3: Different developer hits the same issue
# Week 4: Team concludes "AI doesn't understand our codebase"
#
# Root cause: No one added an error handling rule after Week 1
```

**Fix**: After the first correction, capture it in a session log. At the weekly retro, extract the root cause and add a rule. The second occurrence should never happen.

## Integration

The Feedback Flywheel connects the pattern ecosystem into a continuous improvement cycle:

```
Session Outcomes → Session Logs → Retrospective Analysis
       ↓                                    ↓
  Agent Memory              Proposed Rule Updates
                                           ↓
                                    Codified Rules
                                           ↓
                                  Improved AI Sessions
                                           ↓
                                   Higher Acceptance Rate
                                           ↓
                                    Session Outcomes → ...
```

## Quick Start

```bash
# 1. Create session log directory
mkdir -p .ai/session-logs

# 2. Start from the real sample YAML, then replace every sample value
cp example-retro/sample-session.yaml .ai/session-logs/$(date +%Y-%m-%d).yaml
# Set session.date to the filename date and record the actual session outcomes.

# 3. Run weekly retrospective
python retro-analysis.py --period 7d

# 4. Apply proposed rules
# Review and add validated rules to .ai/rules/
```

This directory provides a runnable file-based analyzer, a session schema, and a worked example. It
does not capture sessions or apply proposed rules automatically.

## Known Limitations

- Session capture is manual, so missing or selectively recorded outcomes can bias the retrospective.
- The analyzer summarizes file-based logs and does not integrate with assistant telemetry or issue
  trackers.
- Acceptance-rate movement does not by itself prove improved correctness; teams must pair it with
  deterministic quality and outcome measures.
- The worked metrics and proposed rules are illustrative and must not be treated as adoption
  evidence or universal targets.

## Promotion Path

Promotion requires privacy-aware automated capture, validation across multiple teams and toolchains,
and evidence that reviewed rule changes reduce repeated corrections while preserving correctness,
security, and human ownership of policy changes.
