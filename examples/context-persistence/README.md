# Context Persistence Implementation

Manage AI context as a finite resource through structured memory schemas and session continuity.

## Quick Start

### Automated Setup (Recommended)

Use Claude Code hooks for automatic context loading:

```bash
./hooks/setup-hooks.sh
# Then: claude → /hooks → approve → restart
```

This configures automatic context loading on every Claude Code session.

### Manual Setup

Copy templates to your project:

```bash
cp -r templates/.ai .
```

This creates 4 memory files:
- **TODO.md** - Track tasks across sessions
- **DECISIONS.log** - Record architectural choices
- **NOTES.md** - Session discoveries and continuity
- **scratchpad.md** - Working memory (cleared after tasks)

### Resume Previous Session

**With Hooks (Automatic):**
Context loads automatically when starting Claude Code.

**Manual:**
```bash
./scripts/session-resume.sh

# Shows: Current TODOs, recent decisions, session notes
```

### 3. Manage Context Size

```bash
# Check context size
./scripts/context-compact.sh --status

# Create recap when context is full
./scripts/context-compact.sh --summarize
```

### 4. Capture Knowledge

```bash
# Initialize knowledge library
./scripts/knowledge.sh --init

# Capture successful pattern
./scripts/knowledge.sh --success \
  --domain "auth" \
  --pattern "JWT Auth" \
  --prompt "JWT with RS256, 15min access, httpOnly cookie" \
  --success-rate "95%"

# Document failure to avoid repeating
./scripts/knowledge.sh --failure \
  --domain "auth" \
  --bad-prompt "Make auth secure" \
  --problem "Too vague" \
  --solution "Specify exact requirements"

# Search patterns
./scripts/knowledge.sh --search "auth"
```

## Memory Schemas

### TODO.md - Task Tracking
```markdown
- [ ] Implement JWT middleware
  - **Status**: blocked
  - **Blocked By**: Key rotation design needed
  - **Dependencies**: none

- [x] Add bcrypt password hashing (2024-01-15)
  - **Outcome**: Implemented with salt rounds=12
```

### DECISIONS.log - Architectural Decisions
```
[2024-01-15 10:30] Use RS256 for JWT (not HS256)
Rationale: Asymmetric keys enable better key rotation
Alternatives: HS256 (simpler but less flexible)
Impact: auth-service, api-gateway
```

### NOTES.md - Session Continuity
```markdown
## Session 2024-01-15

**Context**: Implementing authentication system

**Discoveries**:
- bcrypt has performance issues >100 req/s
- RS256 only 2ms slower than HS256 at p99

**Blockers**:
- Need to decide on refresh token storage

**Next Actions**:
- Benchmark argon2 as bcrypt alternative

## Previously On...
As of 2024-01-15, implementing JWT auth with RS256.
Decided on RS256 for key rotation flexibility.
Current focus: password hashing performance.
Blocker: refresh token strategy needed.
Next: complete auth middleware with <50ms p99.
```

### scratchpad.md - Working Memory
```markdown
## Current Exploration
Investigating JWT verification failures (5% of requests)

### Hypothesis
Clock skew between auth server and gateway

### Evidence
- Failures only on api-gateway-2
- Clock is 47 seconds behind
- 60s tolerance → failures dropped to 0.1%

### Next Steps
- Enable NTP sync
- Add clock drift monitoring

[Clear after moving insights to NOTES.md]
```

## Available Scripts

### session-resume.sh
Resume work across sessions:
```bash
./scripts/session-resume.sh          # Quick summary
./scripts/session-resume.sh --full   # All memory files
./scripts/session-resume.sh --todos  # Just TODOs
```

### context-compact.sh
Manage context size:
```bash
./scripts/context-compact.sh --status     # Check size
./scripts/context-compact.sh --summarize  # Create recap
```

### knowledge.sh
Capture and search patterns:
```bash
./scripts/knowledge.sh --init                    # Setup
./scripts/knowledge.sh --success [OPTIONS]       # Capture success
./scripts/knowledge.sh --failure [OPTIONS]       # Document failure
./scripts/knowledge.sh --search "keyword"        # Find patterns
```

## Knowledge Patterns

Successful patterns stored in `.ai/knowledge/patterns/`:

```markdown
### JWT Auth (95% success)
**Prompt**: "JWT with RS256, 15min access, httpOnly cookie"
**Context**: Node.js APIs
**Gotcha**: AI defaults to insecure HS256 - always specify RS256
**Last Used**: 2024-01-15
**Success Rate**: 95% (19/20 attempts)
```

Failed attempts in `.ai/knowledge/failures/`:

```markdown
### ❌ "Make auth secure"
**Problem**: Too vague → AI over-engineers
**Time Wasted**: 2 hours
**Better Approach**: "JWT with RS256, 15min expiry, httpOnly cookies"
**Date**: 2024-01-10
```

## Workflow

### Starting a Session
1. Run `./scripts/session-resume.sh` to load context
2. Check TODO.md for current tasks
3. Review NOTES.md "Previously on..." section
4. Use scratchpad.md for active exploration

### During Development
1. Track tasks in TODO.md
2. Record decisions in DECISIONS.log
3. Note discoveries in scratchpad.md
4. Capture successful prompts with `knowledge.sh --success`

### Ending a Session
1. Move scratchpad insights to NOTES.md
2. Update TODO.md with progress
3. Check context size with `context-compact.sh --status`
4. If context is large, create recap with `--summarize`

### When Context is Full
1. Create "Previously on..." recap in NOTES.md
2. Archive old session notes (>30 days)
3. Consolidate TODO.md completed items
4. Clear scratchpad.md after extracting insights

## Best Practices

### DO
- ✅ Write session notes immediately after work
- ✅ Capture high-success patterns (>80%)
- ✅ Document failures that wasted >30 minutes
- ✅ Update TODO.md status in real-time
- ✅ Create recaps when context exceeds 8000 tokens

### DON'T
- ❌ Don't duplicate info across memory files
- ❌ Don't let scratchpad accumulate indefinitely
- ❌ Don't capture obvious or one-off patterns
- ❌ Don't let NOTES.md grow beyond 500 lines

## Claude Code Hooks

Automate context management with hooks. See [hooks/README.md](hooks/README.md) for details.

**Available Hooks:**
- **SessionStart** - Auto-load context when starting Claude Code
- **SessionEnd** - Auto-save session state when ending
- **PostToolUse** - Remind to capture successful patterns
- **PreCompact** - Suggest recap before context compaction

**Setup:**
```bash
./hooks/setup-hooks.sh
# Then approve hooks with /hooks in Claude Code
```

## Advanced Features

For enterprise features, see [ADVANCED.md](ADVANCED.md):
- Success rate tracking and trends
- Knowledge versioning and team sharing
- CI/CD integration
- IDE integration
- Anti-pattern detection
- Multi-project context sync

## Files in this Implementation

```
examples/context-persistence/
├── README.md              # This file
├── ADVANCED.md           # Advanced features
├── templates/            # Memory schema templates
│   ├── TODO.md
│   ├── DECISIONS.log
│   ├── decisions.json
│   ├── NOTES.md
│   └── scratchpad.md
├── scripts/              # Context management scripts
│   ├── session-resume.sh
│   ├── context-compact.sh
│   └── knowledge.sh
├── hooks/                # Claude Code hooks (NEW)
│   ├── README.md
│   ├── setup-hooks.sh
│   ├── session-resume.sh
│   ├── session-end.sh
│   ├── post-edit-reminder.sh
│   ├── pre-compact.sh
│   └── settings.json
└── examples/             # Working examples
    └── .ai/
        ├── memory/       # Example memory files
        └── knowledge/    # Example pattern library
```

## Security

⚠️ **Important**:
- Never capture sensitive data in knowledge files
- Review entries before committing to version control
- Use generic examples rather than real credentials
- Regularly audit knowledge content for data leaks
