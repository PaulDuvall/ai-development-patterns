#!/bin/bash
# AI Context Persistence - PostToolUse Hook
#
# Reminds you to capture successful patterns after file edits
# Configure in .claude/settings.json:
#
# {
#   "hooks": {
#     "PostToolUse": [{
#       "matcher": "Write|Edit",
#       "hooks": [{
#         "type": "command",
#         "command": "bash \"$CLAUDE_PROJECT_DIR\"/.ai/hooks/post-edit-reminder.sh"
#       }]
#     }]
#   }
# }

set -euo pipefail

echo ""
echo "💡 Tip: If this worked well, capture the pattern:"
echo "   .ai/knowledge/patterns/[domain].md"
echo ""
