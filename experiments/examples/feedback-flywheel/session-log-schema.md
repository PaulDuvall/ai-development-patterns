# Session Log Schema

Use this template after each AI-assisted development session to capture structured outcomes for retrospective analysis.

## Template

```yaml
# .ai/session-logs/YYYY-MM-DD.yaml
session:
  date: "YYYY-MM-DD"
  developer: "name"
  task_type: "feature|bugfix|refactor|test|docs"
  duration_minutes: 0
  tools_used:
    - "claude-code"

outcomes:
  first_pass_accepted: 0      # Generations accepted without modification
  required_correction: 0       # Generations that needed manual fixes
  total_generations: 0         # Total AI generation requests
  acceptance_rate: 0.00        # first_pass_accepted / total_generations

corrections:
  - generation: "brief description of what was generated"
    issue: "what was wrong with the output"
    correction: "what the developer changed"
    root_cause: "why the AI got it wrong"
    proposed_rule: "rule that would prevent this in future"
    severity: "minor|moderate|major"

insights:
  worked_well:
    - "what produced good results on first pass"
  worked_poorly:
    - "what consistently required rework"
  pattern_detected: "higher-level observation about the session"
```

## Field Definitions

| Field | Required | Description |
|-------|----------|-------------|
| `session.date` | Yes | ISO date of the session |
| `session.developer` | Yes | Who ran the session |
| `session.task_type` | Yes | Category of work performed |
| `outcomes.first_pass_accepted` | Yes | Count of generations accepted as-is |
| `outcomes.total_generations` | Yes | Total generation requests made |
| `corrections[].root_cause` | Yes | Why the AI produced incorrect output |
| `corrections[].proposed_rule` | Yes | Concrete rule to prevent recurrence |
| `corrections[].severity` | No | Impact level of the correction |
| `insights.pattern_detected` | No | Cross-cutting observation |

## Guidelines

- Log immediately after the session while context is fresh
- Be specific in `root_cause` — "missing rule" is too vague; "no convention for HTTP status codes in .ai/rules" is actionable
- Write `proposed_rule` as you would write it in `.ai/rules/` — ready to copy-paste
- Only log corrections that represent systemic issues, not one-off typos
