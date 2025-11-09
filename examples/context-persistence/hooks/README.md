# Claude Code Hooks for AI Context Persistence

Automate context loading and knowledge capture using Claude Code hooks.

## Quick Setup

1. **Copy hooks to your project:**
   ```bash
   mkdir -p .ai/hooks
   cp hooks/*.sh .ai/hooks/
   chmod +x .ai/hooks/*.sh
   ```

2. **Configure hooks:**
   ```bash
   mkdir -p .claude
   cp hooks/settings.json .claude/settings.json
   ```

3. **Approve hooks in Claude Code:**
   ```bash
   claude
   /hooks  # Review and approve
   # Restart Claude Code to activate
   ```

## Available Hooks

### SessionStart - Automatic Context Loading

**File:** `session-resume.sh`

Automatically displays context when starting a session:
- Recent session notes
- Current TODOs
- Recent decisions
- Active scratchpad
- Available knowledge patterns

**Configuration:**
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "bash \"$CLAUDE_PROJECT_DIR\"/.ai/hooks/session-resume.sh"
      }]
    }]
  }
}
```

**Example Output:**
```
=== 📚 Context Resume ===

📝 Recent Session Notes:
Session 2024-01-15: Working on JWT auth...

📋 Current TODOs:
- [ ] Implement JWT middleware
- [ ] Add bcrypt hashing

💭 Recent Decisions:
[2024-01-15] Use RS256 for JWT signing

=== Ready to Continue ===
```

### SessionEnd - Auto-save Session State

**File:** `session-end.sh`

Saves session state when ending:
- Timestamps session end in NOTES.md
- Archives scratchpad if it has content
- Preserves investigation history

**Configuration:**
```json
{
  "hooks": {
    "SessionEnd": [{
      "hooks": [{
        "type": "command",
        "command": "bash \"$CLAUDE_PROJECT_DIR\"/.ai/hooks/session-end.sh"
      }]
    }]
  }
}
```

### PostToolUse - Knowledge Capture Reminder

**File:** `post-edit-reminder.sh`

Reminds you to capture successful patterns after edits.

**Configuration:**
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "bash \"$CLAUDE_PROJECT_DIR\"/.ai/hooks/post-edit-reminder.sh"
      }]
    }]
  }
}
```

**Example Output:**
```
💡 Tip: If this worked well, capture the pattern:
   .ai/knowledge/patterns/[domain].md
```

### PreCompact - Context Summarization Reminder

**File:** `pre-compact.sh`

Reminds you to create a recap before context compaction.

**Configuration:**
```json
{
  "hooks": {
    "PreCompact": [{
      "hooks": [{
        "type": "command",
        "command": "bash \"$CLAUDE_PROJECT_DIR\"/.ai/hooks/pre-compact.sh"
      }]
    }]
  }
}
```

**Example Output:**
```
⚠️  Context window approaching limit

💡 Consider creating a 'Previously On...' recap:
   ./scripts/context-compact.sh --summarize
```

### Stop - Final Reminder

Simple echo reminder when stopping Claude Code.

**Configuration:**
```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "echo '\n💾 Remember to update TODO.md and capture successful patterns'"
      }]
    }]
  }
}
```

## Hook Security

Claude Code hooks require approval for security:

1. Hooks are defined in `.claude/settings.json`
2. First run, use `/hooks` to review
3. Approve trusted hooks
4. Restart Claude Code

**Important:** Only approve hooks you understand and trust.

## Customization

### Modify Hook Behavior

Edit hook scripts to customize behavior:

```bash
# Example: Add context size check to session-resume.sh
if [[ -d ".ai/memory" ]]; then
    total_size=$(du -sh .ai/memory | cut -f1)
    echo "📊 Context Size: $total_size"
fi
```

### Add Project-Specific Context

Extend session-resume.sh with project-specific info:

```bash
# Show current git branch
echo "🌿 Branch: $(git branch --show-current)"

# Show recent commits
echo "📝 Recent commits:"
git log --oneline -3
```

### Add Custom Hooks

Create new hooks for your workflow:

```bash
# .ai/hooks/pre-commit-check.sh
#!/bin/bash
# Remind to update DECISIONS.log before commits

if git diff --cached --quiet; then
    echo "💡 Large commit detected"
    echo "Did you update .ai/memory/DECISIONS.log?"
fi
```

Add to settings.json:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash.*git commit",
      "hooks": [{
        "type": "command",
        "command": "bash \"$CLAUDE_PROJECT_DIR\"/.ai/hooks/pre-commit-check.sh"
      }]
    }]
  }
}
```

## Integration with Scripts

Hooks work seamlessly with the context management scripts:

### Session Resume Hook + Script
```bash
# Hook runs automatically on SessionStart
# Manually run for detailed view:
./scripts/session-resume.sh --full
```

### Context Compact Hook + Script
```bash
# Hook reminds when context is large
# Run script to actually compact:
./scripts/context-compact.sh --summarize
```

## Troubleshooting

### Hook Not Running

1. Check hook approval: `/hooks` in Claude Code
2. Verify script permissions: `chmod +x .ai/hooks/*.sh`
3. Check script path in settings.json
4. Restart Claude Code

### Hook Errors

View hook output in Claude Code:
```bash
# Test hook manually
bash .ai/hooks/session-resume.sh

# Check for errors
echo $?
```

### Disable Hooks Temporarily

Remove from `.claude/settings.json` or use `/hooks` to disable.

## Best Practices

### DO
- ✅ Keep hooks fast (<5 seconds)
- ✅ Use timeouts in settings.json
- ✅ Test hooks manually before adding
- ✅ Commit .claude/settings.json for team sharing

### DON'T
- ❌ Don't run expensive operations in hooks
- ❌ Don't modify files in PreCompact (read-only)
- ❌ Don't add hooks that require user input
- ❌ Don't use hooks for critical operations

## Advanced Examples

### Parse Hook Input JSON

Some hooks receive JSON input:

```bash
#!/bin/bash
# Parse SessionStart input
input=$(cat)
session_id=$(echo "$input" | jq -r '.session_id')
transcript_path=$(echo "$input" | jq -r '.transcript_path')

echo "Session ID: $session_id"
```

### Conditional Hook Execution

Run hooks only in certain conditions:

```bash
#!/bin/bash
# Only show context if memory directory exists
if [[ ! -d ".ai/memory" ]]; then
    exit 0
fi

# Show context...
```

### Multi-Project Context

Share knowledge across projects:

```bash
#!/bin/bash
# Load patterns from team knowledge base
if [[ -d "../team-knowledge/patterns" ]]; then
    echo "📚 Team Knowledge Available:"
    ls ../team-knowledge/patterns/*.md
fi
```

## See Also

- [Claude Code Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks)
- [Main README](../README.md) - Core context persistence concepts
- [Scripts README](../scripts/) - Manual context management tools
