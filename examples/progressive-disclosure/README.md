# Progressive Disclosure Example

This example provides a tool-agnostic starter layout for implementing the [Progressive Disclosure](../../README.md#progressive-disclosure) pattern in a real repository.

## Goal

Keep a small, universal rules file that applies to every task, and load specialized rules only when the work context requires them (security, API design, testing, CI/CD, etc.).

## Starter Layout

```text
.ai/
├── CLAUDE.md                  # Universal rules + routing hints (<60 lines)
├── rules/
│   ├── security/              # secrets, auth, dependencies
│   ├── development/           # api-design, database, testing
│   ├── operations/            # deployment, monitoring, cicd
│   └── architecture/          # patterns, performance
└── prompts/                   # reusable task templates
```

## Suggested Workflow

1. Keep `.ai/CLAUDE.md` minimal and explicit about **when** to load specialized rules.
2. Add small, focused rule files under `.ai/rules/` (aim for <100 lines each).
3. Optionally combine with [Event Automation](../../README.md#event-automation) to auto-load the relevant rules before edits, writes, or test runs.

