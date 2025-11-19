### Centralized Rules

**Maturity**: Advanced
**Description**: Enforce organization-wide AI rules through a central gateway service or shared SDK library rather than distributing configuration files to each repository.

**Related Patterns**: [Codified Rules](#codified-rules), [Policy Generation](#policy-generation), [Security Orchestration](#security-orchestration)

#### Core Implementation

Centralize AI rules in a three-layer architecture:

1. **Gateway service** - Internal service that owns all org rules, calls AI providers
2. **Wrapper library** - Shared SDK package that embeds org rules in system prompts
3. **CLI/editor layer** - Developer tools that call gateway or wrapper, never AI providers directly

**Gateway pattern**:
```
Developer tool → Internal gateway → AI provider
                      ↓
              Org rules applied
              Input/output filtered
              Usage logged
```

**Wrapper library pattern**:
```
Developer tool → @yourorg/ai-client → AI provider
                        ↓
                Org rules in system prompt
                Consistent across all repos
```

**Governance capabilities**:
- Input filters (block secrets, enforce read-only paths)
- Output filters (scan for banned APIs, license violations)
- Policy-as-code integration (OPA rules before/after AI calls)
- Centralized audit logging (repo, task type, tokens, files touched)

**Benefits over distributed config**:
- Change rules once, all tools updated
- Enforceable guardrails (not just suggestions)
- Aggregate metrics across teams
- Model switching without repo changes

Complete Example: See [experiments/examples/centralized-rules/](experiments/examples/centralized-rules/) for working gateway, wrapper library, and CLI implementations.

#### Anti-pattern: Scattered Configuration

Copying AI rule files into every repository:

```
repo-a/.cursorrules    # v1.2 of org rules
repo-b/CLAUDE.md       # v1.1 (outdated)
repo-c/.ai/rules/      # Custom fork, diverged
```

**Problems**:
- Rules drift across repositories
- No enforcement (developers can ignore or modify)
- No visibility into AI usage patterns
- Model/rule changes require updating every repo
