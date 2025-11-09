#!/bin/bash
# AI Context Persistence - PreCompact Hook
#
# Reminds you to create a recap before context compaction
# Configure in .claude/settings.json:
#
# {
#   "hooks": {
#     "PreCompact": [{
#       "hooks": [{
#         "type": "command",
#         "command": "bash \"$CLAUDE_PROJECT_DIR\"/.ai/hooks/pre-compact.sh"
#       }]
#     }]
#   }
# }

set -euo pipefail

echo ""
echo "⚠️  Context window approaching limit"
echo ""
echo "💡 Consider creating a 'Previously On...' recap:"
echo "   ./scripts/context-compact.sh --summarize"
echo ""
echo "Or ask Claude: 'Create a recap in .ai/memory/NOTES.md summarizing our recent work'"
echo ""
