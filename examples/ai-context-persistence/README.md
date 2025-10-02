# AI Context Persistence Implementation

This directory contains a complete implementation of the AI Context Persistence pattern, managing AI context as a finite resource through structured memory schemas, prompt pattern capture, and session continuity protocols.

## Overview

AI Context Persistence enables teams to:
- **Structure memory** using standardized schemas (TODO, DECISIONS, NOTES, scratchpad)
- **Manage context** as a finite resource with just-in-time retrieval and compaction
- **Resume sessions** seamlessly with continuity protocols across AI interactions
- **Capture patterns** - working prompts and failures with success rates

## Core Concept

Treat AI context like working memory with diminishing returns. Effective context persistence requires:
- **Minimal high-signal tokens**: Find smallest set of information that maximizes outcomes
- **Progressive disclosure**: Load context dynamically rather than pre-loading everything
- **Structured persistence**: Externalize information to memory schemas outside context window

## Files in this Implementation

### Memory Schema Templates (`templates/`)
- `TODO.md` - Task tracking across AI sessions
- `DECISIONS.log` - Architectural decisions with timestamp and rationale
- `decisions.json` - Machine-readable decision format
- `NOTES.md` - Session continuity and discoveries
- `scratchpad.md` - Working memory for active exploration

### Context Management Scripts (`scripts/`)
- `context-compact.sh` - Context compaction and summarization
- `session-resume.sh` - Quick session context loading
- `knowledge-capture.sh` - Capture prompt patterns and failures
- `knowledge-maintenance.sh` - Knowledge cleanup and analysis

### Working Examples (`examples/`)
- `.ai/memory/` - Realistic memory files in use (TODO, DECISIONS, NOTES, scratchpad)
- `.ai/knowledge/` - Prompt pattern library (patterns/, failures/)

## Quick Start

### 1. Session Resume - Load Context

```bash
# Resume previous work session
./scripts/session-resume.sh

# Shows: Current TODOs, recent decisions, session notes, active explorations
# Use at start of every AI session for continuity
```

### 2. Memory Schemas - Structure Information

```bash
# Copy templates to your project
cp -r templates/.ai .

# Use memory schemas to persist context:
# - TODO.md: Track tasks and blockers across sessions
# - DECISIONS.log: Record architectural choices with rationale
# - NOTES.md: Session discoveries and "Previously on..." recaps
# - scratchpad.md: Working memory for active debugging/exploration
```

### 3. Context Management - Compact When Full

```bash
# Check context size
./scripts/context-compact.sh --status

# Create "Previously on..." recap when context is full
./scripts/context-compact.sh --summarize

# Archive old session notes (>30 days)
./scripts/context-compact.sh --archive-notes
```

### 4. Prompt Patterns - Capture Knowledge

```bash
# Initialize prompt pattern library
./scripts/knowledge-capture.sh --init

# Capture successful pattern
./scripts/knowledge-capture.sh --success \
  --domain "auth" \
  --pattern "JWT with RS256" \
  --prompt "JWT with RS256, 15min access, httpOnly cookie" \
  --success-rate "95%"

# Document failure to avoid repeating
./scripts/knowledge-capture.sh --failure \
  --domain "auth" \
  --bad-prompt "Make auth secure" \
  --problem "Too vague → AI over-engineers" \
  --solution "Specify exact JWT requirements"

# Search patterns
./scripts/knowledge-maintenance.sh --search "auth"

# Find stale knowledge for review
./knowledge-maintenance.sh --stale-review
```

## Knowledge Organization

### Patterns Structure
```markdown
# .ai/knowledge/patterns/auth.md

### JWT Auth (95% success)
**Prompt**: "JWT with RS256, 15min access, 7day refresh in httpOnly cookie"
**Context**: Node.js APIs
**Gotcha**: AI defaults to insecure HS256 - always specify RS256
**Last Used**: 2024-01-15
**Success Rate**: 95% (19/20 attempts)

### Password Hash (90% success)
**Prompt**: "bcrypt with salt rounds=12, async/await, bcrypt.compare for validation"
**Context**: Any Node.js backend
**Gotcha**: AI uses deprecated hashSync - specify async
**Last Used**: 2024-01-12
**Success Rate**: 90% (18/20 attempts)
```

### Failures Structure
```markdown
# .ai/knowledge/failures/auth.md

### ❌ "Make auth secure"
**Problem**: Too vague → AI adds OAuth + sessions + JWT complexity
**Time Wasted**: 2 hours debugging over-engineered solution
**Better Approach**: "Implement JWT auth with RS256, 15min expiry, secure httpOnly cookies"
**Date**: 2024-01-10

### ❌ "Add authentication"
**Problem**: No constraints → 500 lines of unnecessary middleware
**Time Wasted**: 45 minutes simplifying generated code
**Better Approach**: "Simple JWT middleware: verify token, attach user to req, 401 on invalid"
**Date**: 2024-01-08
```

### Gotchas Structure
```markdown
# .ai/knowledge/gotchas/general.md

### AI Over-Engineering Tendency
**Behavior**: AI adds complexity when constraints are missing
**Fix**: Always specify exact requirements and limitations
**Examples**: "Simple X, not enterprise-grade" or "Maximum 50 lines"

### Default to Insecure Patterns
**Behavior**: AI chooses convenient over secure (HS256 vs RS256)
**Fix**: Explicitly specify security requirements
**Examples**: "Use RS256", "async/await not sync", "parameterized queries"
```

## Advanced Features

### Success Rate Tracking
```bash
# Update success rate after using a pattern
./knowledge-capture.sh --update-success \
  --domain "auth" \
  --pattern "JWT Auth" \
  --result "success"  # or "failure"

# View success rate trends
./knowledge-maintenance.sh --success-trends
```

### Knowledge Versioning
```bash
# Create versioned knowledge backup
./knowledge-maintenance.sh --backup --version "v1.2"

# Compare knowledge versions
./knowledge-maintenance.sh --diff "v1.1" "v1.2"
```

### Team Knowledge Sharing
```bash
# Export knowledge for team sharing
./knowledge-maintenance.sh --export --format json > team-knowledge.json

# Import knowledge from team member
./knowledge-maintenance.sh --import team-knowledge.json
```

## Templates and Examples

### Pattern Template
```markdown
### [Pattern Name] ([Success Rate]% success)
**Prompt**: "[Exact prompt that works]"
**Context**: [When to use this pattern]
**Gotcha**: [Common AI behavior to watch out for]
**Last Used**: [Date]
**Success Rate**: [Percentage] ([successful attempts]/[total attempts])
**Notes**: [Additional context or variations]
```

### Failure Template
```markdown
### ❌ "[Failed prompt or approach]"
**Problem**: [What went wrong and why]
**Time Wasted**: [How much time was lost]
**Better Approach**: "[Improved prompt or strategy]"
**Date**: [When this failure occurred]
**Root Cause**: [Why this approach failed]
```

## Integration Examples

### Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
# Remind to capture knowledge for significant changes

if [[ $(git diff --cached --name-only | wc -l) -gt 5 ]]; then
    echo "Large changeset detected. Consider capturing knowledge:"
    echo "  ./knowledge-capture.sh --success --domain [domain] --pattern [pattern]"
fi
```

### IDE Integration
```bash
# VS Code snippet for quick knowledge capture
# Add to .vscode/snippets/knowledge.json
{
  "capture-success": {
    "prefix": "kc-success",
    "body": [
      "./knowledge-capture.sh --success \\",
      "  --domain \"$1\" \\",
      "  --pattern \"$2\" \\", 
      "  --prompt \"$3\" \\",
      "  --success-rate \"$4%\""
    ]
  }
}
```

### CI/CD Knowledge Updates
```yaml
# .github/workflows/knowledge-maintenance.yml
name: Knowledge Maintenance
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
jobs:
  maintain:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Review Stale Knowledge
        run: ./knowledge-maintenance.sh --stale-review --auto-cleanup
      - name: Generate Knowledge Report
        run: ./knowledge-maintenance.sh --report > knowledge-report.md
```

## Maintenance and Best Practices

### Regular Maintenance Tasks
```bash
# Weekly maintenance routine
./knowledge-maintenance.sh --weekly-maintenance

# This performs:
# - Identify stale knowledge (>90 days unused)
# - Update success rates based on recent usage
# - Consolidate similar patterns
# - Generate usage statistics
```

### Knowledge Quality Guidelines

#### High-Impact Knowledge (Capture These)
- Patterns with >80% success rate
- Failures that wasted >30 minutes
- Gotchas that were non-obvious
- Domain-specific prompt formulations

#### Low-Impact Knowledge (Avoid These)
- Obvious or well-documented patterns
- Single-use, context-specific solutions
- Exhaustive documentation that won't be referenced
- Patterns with <50% success rate (unless educational)

### Anti-Pattern Prevention
```bash
# Detect knowledge hoarding patterns
./knowledge-maintenance.sh --anti-pattern-check

# Reports:
# - Unused knowledge files (>3 months)
# - Overly detailed entries (>200 words)
# - Low-success patterns (<60%)
# - Duplicate or overlapping entries
```

## Troubleshooting

### Common Issues
- **Knowledge Not Used**: Check if entries are too detailed or too generic
- **Outdated Patterns**: Run regular maintenance to identify stale knowledge
- **Low Success Rates**: Review and improve prompt formulations
- **Knowledge Silos**: Ensure team sharing and regular export/import

### Debug Commands
```bash
# Find unused knowledge
find .ai/knowledge -name "*.md" -mtime +90

# Check knowledge access patterns
./knowledge-maintenance.sh --usage-stats

# Validate knowledge format
./knowledge-maintenance.sh --validate-format
```

## Contributing

When adding knowledge patterns:
1. Use consistent templates and formatting
2. Include realistic success rates and usage context
3. Focus on actionable, reusable patterns
4. Document failures that wasted significant time
5. Regular review and pruning of knowledge base

## Security Considerations

⚠️ **Important Security Notes**
- Never capture sensitive data in knowledge files
- Review knowledge entries before committing to version control
- Use generic examples rather than real credentials or secrets
- Regular audit of knowledge content for data leaks