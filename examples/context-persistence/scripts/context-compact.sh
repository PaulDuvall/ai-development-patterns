#!/bin/bash
# AI Context Persistence - Context Compaction
#
# Manage context size and create session summaries

set -euo pipefail

MEMORY_DIR=".ai/memory"
TODO_FILE="$MEMORY_DIR/TODO.md"
DECISIONS_FILE="$MEMORY_DIR/DECISIONS.log"
NOTES_FILE="$MEMORY_DIR/NOTES.md"
SCRATCHPAD_FILE="$MEMORY_DIR/scratchpad.md"

show_usage() {
    cat << 'EOF'
Context Compaction - Manage AI context size

Usage: ./context-compact.sh [OPTION]

Options:
    --status            Show current context size estimate
    --summarize         Create "Previously on..." recap
    --help              Show this help

Examples:
    ./context-compact.sh --status      # Check size
    ./context-compact.sh --summarize   # Create recap
EOF
}

estimate_size() {
    echo "=== Context Size ==="
    echo ""

    local total_chars=0
    local total_tokens=0

    for file in "$TODO_FILE" "$DECISIONS_FILE" "$NOTES_FILE" "$SCRATCHPAD_FILE"; do
        if [[ -f "$file" ]]; then
            local chars=$(wc -c < "$file" 2>/dev/null || echo "0")
            local tokens=$((chars / 4))  # ~4 chars per token
            total_chars=$((total_chars + chars))
            total_tokens=$((total_tokens + tokens))
            printf "%-20s %8s chars  ~%6s tokens\n" "$(basename "$file")" "$chars" "$tokens"
        fi
    done

    echo ""
    echo "Total: $total_chars chars  ~$total_tokens tokens"
    echo ""

    if [[ $total_tokens -gt 8000 ]]; then
        echo "⚠️  Context is large. Consider --summarize"
    elif [[ $total_tokens -gt 4000 ]]; then
        echo "ℹ️  Context is moderate. Monitor growth."
    else
        echo "✓ Context is manageable"
    fi
}

create_summary() {
    echo "Creating recap..."
    echo ""

    if [[ ! -f "$NOTES_FILE" ]]; then
        mkdir -p "$MEMORY_DIR"
        cat > "$NOTES_FILE" << 'EOF'
# Session Notes

## Previously On...

[Recap will appear here]

EOF
    fi

    # Extract key info
    local active_tasks=$(grep -E '^\-\s+\[ \]' "$TODO_FILE" 2>/dev/null | head -3 | sed 's/^- \[ \] //' || echo "No active tasks")
    local recent_decision=$(grep -E '^\[20' "$DECISIONS_FILE" 2>/dev/null | tail -1 | cut -d']' -f2- | cut -d':' -f2 || echo "No recent decisions")
    local blocked_tasks=$(grep -B1 'blocked' "$TODO_FILE" 2>/dev/null | grep '^\-\s+\[ \]' | head -1 | sed 's/^- \[ \] //' || echo "No blockers")

    local date=$(date +%Y-%m-%d)

    # Create recap
    cat > "${NOTES_FILE}.tmp" << EOF
# Session Notes

## Previously On... (Updated: $date)

**Current Focus**: ${active_tasks}

**Recent Decision**: ${recent_decision}

**Blockers**: ${blocked_tasks}

**Next Milestone**: [Update manually with next major goal]

---

EOF

    # Append existing notes
    if grep -q "^## Session" "$NOTES_FILE" 2>/dev/null; then
        grep -A1000 "^## Session" "$NOTES_FILE" >> "${NOTES_FILE}.tmp"
    fi

    mv "${NOTES_FILE}.tmp" "$NOTES_FILE"

    echo "✓ Recap created in NOTES.md"
    echo ""
    echo "Review and refine the 'Previously on...' section:"
    echo "  1. Summarize overall objective"
    echo "  2. List key decisions"
    echo "  3. Highlight current focus"
    echo "  4. Note blockers"
    echo "  5. State next milestone"
}

# Main
case "${1:-}" in
    --status)
        estimate_size
        ;;
    --summarize)
        create_summary
        ;;
    --help|-h|"")
        show_usage
        ;;
    *)
        echo "Unknown option: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
