#!/bin/bash
# AI Context Persistence - Session Resume
#
# Display context summary for resuming work across sessions

set -euo pipefail

MEMORY_DIR=".ai/memory"
TODO_FILE="$MEMORY_DIR/TODO.md"
DECISIONS_FILE="$MEMORY_DIR/DECISIONS.log"
NOTES_FILE="$MEMORY_DIR/NOTES.md"
SCRATCHPAD_FILE="$MEMORY_DIR/scratchpad.md"

show_usage() {
    cat << 'EOF'
Session Resume - Quickly resume AI development sessions

Usage: ./session-resume.sh [OPTION]

Options:
    --quick             Quick summary (default)
    --full              Show all memory files
    --todos             Show only TODOs
    --decisions         Show only decisions
    --notes             Show only notes
    --help              Show this help

Examples:
    ./session-resume.sh              # Quick summary
    ./session-resume.sh --full       # Everything
    ./session-resume.sh --todos      # Just TODOs
EOF
}

show_todos() {
    echo "=== Current Tasks ==="
    echo ""

    if [[ ! -f "$TODO_FILE" ]]; then
        echo "No TODO.md found"
        return
    fi

    # Active tasks
    local active=$(grep '^\- \[ \]' "$TODO_FILE" 2>/dev/null | head -5 || true)
    if [[ -n "$active" ]]; then
        echo "Active:"
        echo "$active"
        echo ""
    fi

    # Blocked tasks
    local blocked=$(grep -B1 'blocked' "$TODO_FILE" 2>/dev/null | grep '^\- \[ \]' | head -3 || true)
    if [[ -n "$blocked" ]]; then
        echo "Blocked:"
        echo "$blocked"
        echo ""
    fi

    # Recently completed
    local completed=$(grep '^\- \[x\]' "$TODO_FILE" 2>/dev/null | tail -3 || true)
    if [[ -n "$completed" ]]; then
        echo "Recently Completed:"
        echo "$completed"
        echo ""
    fi
}

show_decisions() {
    echo "=== Recent Decisions ==="
    echo ""

    if [[ ! -f "$DECISIONS_FILE" ]]; then
        echo "No DECISIONS.log found"
        return
    fi

    # Last 3 decisions
    grep -A4 '^\[20' "$DECISIONS_FILE" 2>/dev/null | tail -15 || echo "No decisions recorded"
    echo ""
}

show_notes() {
    echo "=== Session Notes ==="
    echo ""

    if [[ ! -f "$NOTES_FILE" ]]; then
        echo "No NOTES.md found"
        return
    fi

    # Show "Previously on..." if it exists
    if grep -q "^## Previously" "$NOTES_FILE" 2>/dev/null; then
        echo "Previously On:"
        sed -n '/^## Previously/,/^##/p' "$NOTES_FILE" | grep -v '^##' | head -10
        echo ""
    fi

    # Most recent session
    if grep -q "^## Session" "$NOTES_FILE" 2>/dev/null; then
        echo "Most Recent Session:"
        grep "^## Session" "$NOTES_FILE" | tail -1
        sed -n "/^## Session/,/^##/p" "$NOTES_FILE" | grep '^\*\*' | head -8
        echo ""
    fi
}

show_scratchpad() {
    if [[ ! -f "$SCRATCHPAD_FILE" ]]; then
        return
    fi

    local size=$(wc -l < "$SCRATCHPAD_FILE" 2>/dev/null || echo "0")
    if [[ $size -lt 5 ]]; then
        return
    fi

    echo "=== Active Exploration ==="
    echo ""
    head -15 "$SCRATCHPAD_FILE"
    if [[ $size -gt 15 ]]; then
        echo "... ($(($size - 15)) more lines)"
    fi
    echo ""
}

quick_resume() {
    echo ""
    echo "=== Session Resume ==="
    echo ""
    show_todos
    show_decisions
    show_notes
    [[ -f "$SCRATCHPAD_FILE" ]] && show_scratchpad
    echo "Ready to continue work."
    echo ""
}

full_resume() {
    echo ""
    echo "=== Full Context ==="
    echo ""
    for file in "$TODO_FILE" "$DECISIONS_FILE" "$NOTES_FILE" "$SCRATCHPAD_FILE"; do
        if [[ -f "$file" ]]; then
            echo "=== $(basename "$file") ==="
            echo ""
            cat "$file"
            echo ""
        fi
    done
}

# Main
MODE="${1:---quick}"

case "$MODE" in
    --quick)
        quick_resume
        ;;
    --full)
        full_resume
        ;;
    --todos)
        show_todos
        ;;
    --decisions)
        show_decisions
        ;;
    --notes)
        show_notes
        ;;
    --help|-h)
        show_usage
        ;;
    *)
        echo "Unknown option: $MODE"
        echo ""
        show_usage
        exit 1
        ;;
esac
