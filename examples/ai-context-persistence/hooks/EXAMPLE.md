# Hooks in Action - Example Workflow

This demonstrates how Claude Code hooks automate AI Context Persistence.

## Initial Setup

```bash
# Clone/setup your project
cd my-project

# Install AI Context Persistence
cp -r examples/ai-context-persistence/hooks .ai/
./ai-context-persistence/hooks/setup-hooks.sh

# Start Claude Code
claude

# Approve hooks
/hooks
# Review each hook, approve trusted ones
# Restart Claude Code
```

## Day 1 - First Session

### Starting Claude Code

When you run `claude`, the **SessionStart** hook automatically runs:

```
=== 📚 Context Resume ===

📝 Recent Session Notes:
No notes yet

📋 Current TODOs:
No active TODOs

💭 Recent Decisions:
No decisions logged

=== Ready to Continue ===

Claude Code is ready.
```

### Working on a Feature

You ask Claude to implement JWT authentication:

```
You: Implement JWT authentication with RS256 signing
```

Claude generates the code. After the **Edit** tool runs, **PostToolUse** hook triggers:

```
💡 Tip: If this worked well, capture the pattern:
   .ai/knowledge/patterns/[domain].md
```

### Capturing Success

You decide to capture this pattern:

```bash
./scripts/knowledge.sh --success \
  --domain "auth" \
  --pattern "JWT Auth" \
  --prompt "JWT with RS256, 15min access, httpOnly cookie" \
  --success-rate "100%"
```

### Recording Decisions

You update DECISIONS.log:

```bash
cat >> .ai/memory/DECISIONS.log << EOF
[$(date '+%Y-%m-%d %H:%M')] Use RS256 for JWT signing
Rationale: Asymmetric keys enable better key rotation
Alternatives: HS256 (simpler but less flexible)
Impact: auth-service, api-gateway
EOF
```

### Ending Session

When you stop Claude Code (`Ctrl+D` or `/exit`), **SessionEnd** hook runs:

```
💾 Session context saved
```

Your scratchpad is automatically archived.

## Day 2 - Resuming Work

### Starting Fresh Session

Run `claude` again. **SessionStart** hook automatically loads context:

```
=== 📚 Context Resume ===

📝 Recent Session Notes:
<!-- Session ended: 2024-01-15 17:30 -->

📋 Current TODOs:
No active TODOs

💭 Recent Decisions:
[2024-01-15 15:45] Use RS256 for JWT signing

💡 Available Knowledge Patterns:
auth

=== Ready to Continue ===
```

You're immediately back in context without manually loading anything!

### Continuing Development

You continue work, adding password hashing:

```
You: Add bcrypt password hashing with salt rounds=12
```

Claude implements it. **PostToolUse** reminds you:

```
💡 Tip: If this worked well, capture the pattern:
   .ai/knowledge/patterns/[domain].md
```

You capture another pattern:

```bash
./scripts/knowledge.sh --success \
  --domain "auth" \
  --pattern "Password Hashing" \
  --prompt "bcrypt with salt rounds=12, async/await, compare for validation" \
  --success-rate "100%"
```

## Day 3 - Context Getting Large

### Context Warning

After extensive development, context window fills up. **PreCompact** hook triggers:

```
⚠️  Context window approaching limit

💡 Consider creating a 'Previously On...' recap:
   ./scripts/context-compact.sh --summarize

Or ask Claude: 'Create a recap in .ai/memory/NOTES.md summarizing our recent work'
```

### Creating Recap

You ask Claude:

```
You: Create a 'Previously On...' recap in .ai/memory/NOTES.md summarizing our JWT auth work
```

Claude creates:

```markdown
## Previously On...

As of 2024-01-16, we're implementing JWT-based authentication for the API.

**Key Decisions:**
- Use RS256 for JWT signing (better key rotation)
- bcrypt with salt rounds=12 for password hashing

**Current State:**
- JWT middleware: ✅ Complete
- Password hashing: ✅ Complete
- Rate limiting: ⏳ In progress

**Next Steps:**
- Implement rate limiting middleware
- Add refresh token rotation
- Write integration tests
```

## Day 4 - Team Member Joins

### New Developer Setup

Your teammate clones the repo:

```bash
git clone repo
cd repo

# Hooks are already configured in .claude/settings.json
claude
/hooks  # Approve hooks
# Restart
```

### Automatic Onboarding

When they start Claude Code, **SessionStart** hook loads all context:

```
=== 📚 Context Resume ===

📝 Recent Session Notes:
## Previously On...
As of 2024-01-16, we're implementing JWT-based authentication...

📋 Current TODOs:
- [ ] Implement rate limiting middleware
- [ ] Add refresh token rotation

💭 Recent Decisions:
[2024-01-15 15:45] Use RS256 for JWT signing
[2024-01-16 09:22] bcrypt salt rounds=12

💡 Available Knowledge Patterns:
auth

=== Ready to Continue ===
```

They're immediately productive without asking "what's the context?"

## Day 5 - Knowledge Reuse

### Searching Patterns

Your teammate works on a different service needing auth:

```bash
./scripts/knowledge.sh --search "auth"
```

Output:
```
Searching for: auth

=== Successful Patterns ===
.ai/knowledge/patterns/auth.md:### JWT Auth (100% success)
.ai/knowledge/patterns/auth.md:**Prompt**: "JWT with RS256, 15min access, httpOnly cookie"
.ai/knowledge/patterns/auth.md:### Password Hashing (100% success)
.ai/knowledge/patterns/auth.md:**Prompt**: "bcrypt with salt rounds=12, async/await"
```

They reuse the exact prompt that worked before:

```
You: Implement JWT with RS256, 15min access, httpOnly cookie for the payment service
```

Instant success because of captured knowledge!

## Hook Benefits Demonstrated

### Automation
- ✅ Context loads automatically (no manual script running)
- ✅ Session state saved automatically
- ✅ Reminders at the right time

### Team Efficiency
- ✅ New members onboard instantly
- ✅ Knowledge shared automatically via git
- ✅ Consistent workflow across team

### Zero Overhead
- ✅ Hooks run in background (<1 second each)
- ✅ No manual memory management
- ✅ Focus on coding, not context management

## Customizing for Your Workflow

### Add Custom Reminders

Edit `.ai/hooks/session-resume.sh`:

```bash
# Add after existing content
echo "🌿 Current branch: $(git branch --show-current)"
echo "🔥 Uncommitted changes: $(git status --short | wc -l)"
```

### Project-Specific Context

Add project checks:

```bash
# In session-resume.sh
if [[ -f "package.json" ]]; then
    echo "📦 Node version: $(node --version)"
fi

if [[ -f "requirements.txt" ]]; then
    echo "🐍 Python version: $(python --version)"
fi
```

### Conditional Hooks

Only run hooks in certain branches:

```bash
# In session-resume.sh
current_branch=$(git branch --show-current)

if [[ "$current_branch" == "main" ]]; then
    echo "⚠️  Working on main branch - be careful!"
fi
```

## Troubleshooting

### Hook Not Running

```bash
# Test manually
bash .ai/hooks/session-resume.sh

# Check permissions
ls -la .ai/hooks/

# Verify hook approval
claude
/hooks
```

### Wrong Path in Output

Hooks use `$CLAUDE_PROJECT_DIR`. Verify:

```bash
# In hook script, add debug:
echo "Project dir: $CLAUDE_PROJECT_DIR"
```

### Too Much Output

Reduce verbosity:

```bash
# Simplify session-resume.sh
echo "📚 Context loaded. Recent work: $(head -1 .ai/memory/NOTES.md)"
```

## Real-World Impact

### Before Hooks (Manual)
```bash
# Every session
cd project
./scripts/session-resume.sh  # Manual
cat .ai/memory/TODO.md       # Manual
cat .ai/memory/DECISIONS.log # Manual
# Finally start coding... lost 2-3 minutes
```

### With Hooks (Automatic)
```bash
claude
# Context already loaded, start coding immediately
# Saved 2-3 minutes × 5 sessions/day = 10-15 min/day
```

**Time saved per developer:** ~1 hour per week

**For a team of 5:** ~5 hours per week = 260 hours per year

This is the power of automation!
