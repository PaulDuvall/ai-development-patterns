#!/bin/bash
# AI Context Persistence - SessionStart Hook
#
# Automatically loads context when starting a Claude Code session
# Configure in .claude/settings.json:
#
# {
#   "hooks": {
#     "SessionStart": [{
#       "hooks": [{
#         "type": "command",
#         "command": "bash \"$CLAUDE_PROJECT_DIR\"/.ai/hooks/session-resume.sh"
#       }]
#     }]
#   }
# }

set -euo pipefail

MEMORY_DIR=".ai/memory"

echo "=== 📚 Context Resume ==="
echo ""

# Show recent notes
if [[ -f "$MEMORY_DIR/NOTES.md" ]]; then
    echo "📝 Recent Session Notes:"
    tail -30 "$MEMORY_DIR/NOTES.md" 2>/dev/null || echo "No notes yet"
    echo ""
fi

# Show current TODOs
if [[ -f "$MEMORY_DIR/TODO.md" ]]; then
    echo "📋 Current TODOs:"
    grep '^\- \[ \]' "$MEMORY_DIR/TODO.md" 2>/dev/null | head -5 || echo "No active TODOs"
    echo ""
fi

# Show recent decisions
if [[ -f "$MEMORY_DIR/DECISIONS.log" ]]; then
    echo "💭 Recent Decisions:"
    grep '^\[20' "$MEMORY_DIR/DECISIONS.log" 2>/dev/null | tail -3 || echo "No decisions logged"
    echo ""
fi

# Show active scratchpad
if [[ -f "$MEMORY_DIR/scratchpad.md" ]] && [[ $(wc -l < "$MEMORY_DIR/scratchpad.md") -gt 5 ]]; then
    echo "🔍 Active Investigation:"
    head -15 "$MEMORY_DIR/scratchpad.md"
    echo ""
fi

# Show available knowledge patterns
if [[ -d ".ai/knowledge/patterns" ]]; then
    local pattern_count=$(find .ai/knowledge/patterns -name "*.md" -not -name "README.md" | wc -l)
    if [[ $pattern_count -gt 0 ]]; then
        echo "💡 Available Knowledge Patterns:"
        find .ai/knowledge/patterns -name "*.md" -not -name "README.md" -exec basename {} .md \; | head -5
        echo ""
    fi
fi

echo "=== Ready to Continue ==="
echo ""
