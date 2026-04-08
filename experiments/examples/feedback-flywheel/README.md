# Feedback Flywheel Implementation

This directory contains a complete implementation of the Feedback Flywheel pattern, enabling teams to systematically improve AI-assisted development through structured retrospectives that feed corrections back into codified rules and custom commands.

## Overview

Feedback Flywheel enables teams to:
- Analyze AI-assisted session logs for repeated correction cycles
- Extract patterns from what worked vs. what required rework
- Propose updates to codified rules, custom commands, and progressive disclosure routing
- Track first-pass acceptance rate as a leading indicator of AI collaboration maturity

## Files in this Implementation

- `README.md` - Complete pattern documentation (this file)
- `session-log-schema.md` - Structured format for capturing session outcomes
- `retro-analysis.py` - Script to extract correction patterns from session logs
- `example-retro/` - Worked example showing a full retrospective cycle

## Pattern Definition

### Feedback Flywheel

**Maturity**: Intermediate
**Description**: Systematically improve AI collaboration effectiveness by analyzing session outcomes and feeding corrections back into team rules and commands.

**Related Patterns**: [Codified Rules](../../../README.md#codified-rules), [Context Persistence](../../../README.md#context-persistence), [Progressive Disclosure](../../../README.md#progressive-disclosure)

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

```python
# retro-analysis.py (core logic)
import yaml
from pathlib import Path
from collections import Counter

def analyze_sessions(log_dir: Path, period_days: int) -> dict:
    """Analyze session logs and extract improvement opportunities."""
    corrections = []
    total_accepted = 0
    total_generations = 0

    for log_file in log_dir.glob("*.yaml"):
        session = yaml.safe_load(log_file.read_text())
        total_accepted += session["outcomes"]["first_pass_accepted"]
        total_generations += session["outcomes"]["total_generations"]
        corrections.extend(session.get("corrections", []))

    root_causes = Counter(c["root_cause"] for c in corrections)

    return {
        "acceptance_rate": total_accepted / max(total_generations, 1),
        "top_root_causes": root_causes.most_common(5),
        "proposed_rules": [c["proposed_rule"] for c in corrections],
        "total_corrections": len(corrections),
    }
```

### Feeding Back Into Rules

The retrospective output drives concrete updates:

```bash
# 1. Review proposed rules from retro
cat retro-report.md | grep "proposed_rule"

# 2. Add validated rules to project configuration
ai "Review these proposed rules from our retrospective:
$(cat retro-report.md)

For each proposed rule:
1. Check if it conflicts with existing rules in .ai/rules/
2. Draft the rule in our standard format
3. Add to the appropriate rules file"

# 3. Verify rules are applied in next session
ai "Generate a database migration for adding a 'status' column to orders"
# Expected: uses ORM migration (new rule applied), not raw SQL
```

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
  Context Persistence              Proposed Rule Updates
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

# 2. After each AI session, log outcomes
cp session-log-schema.md .ai/session-logs/$(date +%Y-%m-%d).yaml
# Edit with actual session data

# 3. Run weekly retrospective
python retro-analysis.py --period 7d

# 4. Apply proposed rules
# Review and add validated rules to .ai/rules/
```

**Complete Implementation**: This directory contains the full feedback flywheel system with session log schema, analysis scripts, and a worked example showing how retrospective analysis drives rule improvements.
