# Event Automation Example

Simple security automation that blocks sensitive file edits and scans for hardcoded secrets.

For complete pattern documentation, see: [Event Automation](../../README.md#event-automation)

## Quick Start

```bash
# 1. Install gitleaks (optional, for secret detection)
brew install gitleaks  # macOS
# or: https://github.com/gitleaks/gitleaks#installing

# 2. Create hooks directory in your project
mkdir -p .ai/hooks

# 3. Copy security hook
cp security-hook.sh .ai/hooks/
chmod +x .ai/hooks/security-hook.sh

# 4. Configure Claude Code
# Copy claude-settings.json to .claude/settings.json in your project root
mkdir -p .claude
cp claude-settings.json .claude/settings.json
```

## What It Does

**security-hook.sh** runs automatically on file edits and writes:

1. **Blocks sensitive files**: Prevents editing `.env`, `secrets.json`, credentials files
2. **Detects secrets**: Scans for API keys, tokens, passwords using gitleaks
3. **Provides guidance**: Shows remediation steps when issues found

## Example Workflow

```bash
# Developer tries to edit .env file
# AI attempts to execute Edit tool
# → PreToolUse hook runs security-hook.sh
# → Exit code 2 returned (BLOCK)
# → AI shows: "❌ Blocked: Cannot edit sensitive file"

# Developer edits src/api.js
# → PreToolUse hook: File allowed (exit 0)
# → AI executes file edit
# → PostToolUse hook: Scans for secrets
# → Warning if hardcoded API key found
```

## Exit Codes

- `0` - Allow operation
- `2` - Block operation (PreToolUse only)
- `1` - Warning (operation continues)

## Customization

Edit `security-hook.sh` to change blocked file patterns:

```bash
# Current patterns
if echo "$FILE" | grep -E "(\.env|secrets\.json|credentials|\.aws/|\.ssh/id_)" > /dev/null; then
  exit 2
fi

# Add your patterns
if echo "$FILE" | grep -E "(your-pattern|another-pattern)" > /dev/null; then
  exit 2
fi
```

## Testing

```bash
# Test blocking sensitive files
TOOL_INPUT_FILE_PATH=".env" ./security-hook.sh
# Should output: ❌ Blocked...
# Exit code: 2

# Test allowing normal files
TOOL_INPUT_FILE_PATH="src/app.js" ./security-hook.sh
# No output
# Exit code: 0
```

## Security Note

This hook runs with your full system credentials. Review the script before enabling. Test in a safe environment first.
