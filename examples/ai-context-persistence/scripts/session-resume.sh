#!/bin/bash
# AI Context & Knowledge Engineering - Session Resume
#
# Display context summary for resuming work across sessions
# Provides quick overview of TODO, decisions, and notes

set -euo pipefail

MEMORY_DIR=".ai/memory"
TODO_FILE="$MEMORY_DIR/TODO.md"
DECISIONS_FILE="$MEMORY_DIR/DECISIONS.log"
NOTES_FILE="$MEMORY_DIR/NOTES.md"
SCRATCHPAD_FILE="$MEMORY_DIR/scratchpad.md"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

show_usage() {
    cat << EOF
Session Resume Tool - Quickly resume AI development sessions

Usage: $0 [OPTION]

Options:
    --full              Show full context (all files)
    --quick             Show minimal context (default)
    --todos             Show only TODO items
    --decisions         Show only recent decisions
    --notes             Show only session notes recap
    --help              Show this help message

Examples:
    # Quick resume (default) - shows summary of all context
    $0

    # Full context dump
    $0 --full

    # Just show current TODOs
    $0 --todos

    # See recent architectural decisions
    $0 --decisions

Description:
    Session resume helps you quickly get back into context by displaying:
    - Current tasks and blockers from TODO.md
    - Recent architectural decisions from DECISIONS.log
    - Session recap and discoveries from NOTES.md
    - Active explorations from scratchpad.md

    Use this when:
    - Starting a new development session
    - Returning after a break
    - Context-switching between tasks
    - Onboarding to existing work

EOF
}

show_section_header() {
    echo ""
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}  $1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

show_todos() {
    show_section_header "📋 Current Tasks"

    if [[ ! -f "$TODO_FILE" ]]; then
        echo -e "${YELLOW}No TODO.md found${NC}"
        return
    fi

    # Active tasks
    local active_count=$(grep -c '^\- \[ \]' "$TODO_FILE" 2>/dev/null || echo "0")
    if [[ $active_count -gt 0 ]]; then
        echo -e "${BOLD}Active Tasks:${NC}"
        grep '^\- \[ \]' "$TODO_FILE" | head -5 | sed 's/^/  /'
        if [[ $active_count -gt 5 ]]; then
            echo -e "  ${YELLOW}... and $((active_count - 5)) more${NC}"
        fi
        echo ""
    fi

    # Blocked tasks
    local blocked=$(grep -B1 -A2 'Status.*blocked' "$TODO_FILE" 2>/dev/null | grep '^\- \[ \]' | head -3 || true)
    if [[ -n "$blocked" ]]; then
        echo -e "${RED}Blocked Tasks:${NC}"
        echo "$blocked" | sed 's/^/  /'
        echo ""
    fi

    # Recently completed
    local completed_count=$(grep -c '^\- \[x\]' "$TODO_FILE" 2>/dev/null || echo "0")
    if [[ $completed_count -gt 0 ]]; then
        echo -e "${GREEN}Recently Completed:${NC}"
        grep '^\- \[x\]' "$TODO_FILE" | tail -3 | sed 's/^/  /'
        echo ""
    fi
}

show_decisions() {
    show_section_header "🏗️  Recent Architectural Decisions"

    if [[ ! -f "$DECISIONS_FILE" ]]; then
        echo -e "${YELLOW}No DECISIONS.log found${NC}"
        return
    fi

    # Show last 3 decisions
    local decision_count=$(grep -c '^\[20' "$DECISIONS_FILE" 2>/dev/null || echo "0")

    if [[ $decision_count -eq 0 ]]; then
        echo -e "${YELLOW}No decisions recorded yet${NC}"
        return
    fi

    echo -e "${BOLD}Last 3 Decisions:${NC}"
    echo ""

    # Extract last 3 decision blocks
    grep -A5 '^\[20' "$DECISIONS_FILE" | tail -24 | sed 's/^/  /'
}

show_notes() {
    show_section_header "📝 Session Context"

    if [[ ! -f "$NOTES_FILE" ]]; then
        echo -e "${YELLOW}No NOTES.md found${NC}"
        return
    fi

    # Show "Previously on..." if it exists
    if grep -q "^## Previously On" "$NOTES_FILE" 2>/dev/null; then
        echo -e "${BOLD}Previously On...:${NC}"
        echo ""
        sed -n '/^## Previously On/,/^##/p' "$NOTES_FILE" | sed '/^## Session/d' | sed '/^---/d' | sed 's/^/  /'
        echo ""
    fi

    # Show most recent session
    if grep -q "^## Session" "$NOTES_FILE" 2>/dev/null; then
        local recent_session=$(grep "^## Session" "$NOTES_FILE" | tail -1)
        echo -e "${BOLD}Most Recent Session:${NC}"
        echo ""
        echo "  $recent_session"

        # Extract key parts of recent session
        sed -n "/^## Session.*$(echo "$recent_session" | cut -d' ' -f3)/,/^## /p" "$NOTES_FILE" | \
            grep -E '^\*\*' | head -8 | sed 's/^/  /'
        echo ""
    fi
}

show_scratchpad() {
    show_section_header "🔬 Active Exploration"

    if [[ ! -f "$SCRATCHPAD_FILE" ]]; then
        echo -e "${YELLOW}No active scratchpad${NC}"
        return
    fi

    local scratchpad_size=$(wc -l < "$SCRATCHPAD_FILE" 2>/dev/null || echo "0")

    if [[ $scratchpad_size -lt 5 ]]; then
        echo -e "${YELLOW}Scratchpad is empty${NC}"
        return
    fi

    echo -e "${BOLD}Current Exploration:${NC}"
    echo ""

    # Show first 15 lines of scratchpad
    head -15 "$SCRATCHPAD_FILE" | sed 's/^/  /'

    if [[ $scratchpad_size -gt 15 ]]; then
        echo ""
        echo -e "  ${YELLOW}... ($((scratchpad_size - 15)) more lines in scratchpad.md)${NC}"
    fi

    echo ""
}

quick_resume() {
    echo ""
    echo -e "${BOLD}${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║  AI Context & Knowledge Engineering - Session Resume     ║${NC}"
    echo -e "${BOLD}${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"

    show_todos
    show_decisions
    show_notes

    # Check if scratchpad has content
    if [[ -f "$SCRATCHPAD_FILE" ]] && [[ $(wc -l < "$SCRATCHPAD_FILE") -gt 5 ]]; then
        show_scratchpad
    fi

    echo ""
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ Session context loaded. Ready to continue work.${NC}"
    echo ""
}

full_resume() {
    echo ""
    echo -e "${BOLD}${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║  Full Context Dump - All Memory Files                    ║${NC}"
    echo -e "${BOLD}${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"

    for file in "$TODO_FILE" "$DECISIONS_FILE" "$NOTES_FILE" "$SCRATCHPAD_FILE"; do
        if [[ -f "$file" ]]; then
            show_section_header "$(basename "$file")"
            cat "$file"
            echo ""
        fi
    done

    echo -e "${GREEN}✓ Full context displayed${NC}"
    echo ""
}

# Main script logic
MODE="${1:---quick}"

case "$MODE" in
    --full)
        full_resume
        ;;
    --quick)
        quick_resume
        ;;
    --todos)
        show_todos
        echo ""
        ;;
    --decisions)
        show_decisions
        echo ""
        ;;
    --notes)
        show_notes
        echo ""
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
