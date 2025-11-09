#!/bin/bash
# security-hook.sh
# Simple security automation for AI coding assistants
#
# Usage: Attach to PreToolUse and PostToolUse events
# Exit codes: 0=allow, 2=block, 1=warn

FILE="$TOOL_INPUT_FILE_PATH"

# Skip if no file path provided
[ -z "$FILE" ] && exit 0

# Block sensitive files (.env, credentials, secrets)
if echo "$FILE" | grep -E "(\.env|secrets\.json|credentials|\.aws/|\.ssh/id_)" > /dev/null; then
  echo "❌ Blocked: Cannot edit sensitive file: $FILE"
  echo ""
  echo "Sensitive files are protected to prevent accidental exposure."
  echo "If you need to modify configuration, use a template file."
  exit 2
fi

# Scan for hardcoded secrets using gitleaks (if available)
if command -v gitleaks > /dev/null 2>&1; then
  if [ -f "$FILE" ]; then
    if gitleaks detect --no-git --source="$FILE" 2>&1 | grep -q "leaks found"; then
      echo "⚠️  Warning: Potential secret detected in $FILE"
      echo ""
      echo "Common secrets to avoid:"
      echo "  - API keys (sk-*, api_key=)"
      echo "  - Passwords (password=, pwd=)"
      echo "  - Tokens (token=, auth_token=)"
      echo ""
      echo "Use environment variables instead: process.env.API_KEY"
      exit 1
    fi
  fi
fi

# All checks passed
exit 0
