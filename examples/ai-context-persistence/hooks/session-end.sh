#!/bin/bash
# AI Context Persistence - SessionEnd Hook
#
# Automatically saves session state when ending a Claude Code session
# Configure in .claude/settings.json:
#
# {
#   "hooks": {
#     "SessionEnd": [{
#       "hooks": [{
#         "type": "command",
#         "command": "bash \"$CLAUDE_PROJECT_DIR\"/.ai/hooks/session-end.sh"
#       }]
#     }]
#   }
# }

set -euo pipefail

MEMORY_DIR=".ai/memory"
ARCHIVE_DIR=".ai/archive"

timestamp=$(date '+%Y-%m-%d %H:%M')

# Append session end marker to notes
if [[ -f "$MEMORY_DIR/NOTES.md" ]]; then
    echo "" >> "$MEMORY_DIR/NOTES.md"
    echo "<!-- Session ended: $timestamp -->" >> "$MEMORY_DIR/NOTES.md"
fi

# Archive scratchpad if it has content
if [[ -f "$MEMORY_DIR/scratchpad.md" ]] && [[ $(wc -l < "$MEMORY_DIR/scratchpad.md") -gt 10 ]]; then
    mkdir -p "$ARCHIVE_DIR/scratchpads"
    cp "$MEMORY_DIR/scratchpad.md" "$ARCHIVE_DIR/scratchpads/scratchpad-$(date +%Y%m%d-%H%M).md"
fi

echo "💾 Session context saved"
