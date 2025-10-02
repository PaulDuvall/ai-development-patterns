#!/bin/bash
# AI Context & Knowledge Engineering - Context Compaction
#
# Summarizes context when approaching token limits to maintain efficiency
# Creates "Previously on..." recaps for session continuity

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
NC='\033[0m' # No Color

show_usage() {
    cat << EOF
Context Compaction Tool - Manage AI context as a finite resource

Usage: $0 [OPTION]

Options:
    --summarize         Create "Previously on..." recap from current context
    --status            Show current context usage estimate
    --extract-decisions Extract architectural decisions from scratchpad/notes
    --archive-notes     Archive old session notes (>30 days)
    --help              Show this help message

Examples:
    # Create session recap when context is full
    $0 --summarize

    # Check current context usage
    $0 --status

    # Extract decisions from exploration notes
    $0 --extract-decisions

    # Archive old notes to reduce context size
    $0 --archive-notes

Description:
    Context compaction helps manage token limits by summarizing and structuring
    information outside the context window. Use this when:
    - Context window is approaching limits
    - Starting a new session after a break
    - Handing off work to another developer/AI
    - Long exploration sessions need summarization

EOF
}

estimate_context_size() {
    local total_chars=0
    local total_tokens_est=0

    echo -e "${BLUE}📊 Context Size Estimation${NC}"
    echo ""

    for file in "$TODO_FILE" "$DECISIONS_FILE" "$NOTES_FILE" "$SCRATCHPAD_FILE"; do
        if [[ -f "$file" ]]; then
            local chars=$(wc -c < "$file" 2>/dev/null || echo "0")
            local tokens_est=$((chars / 4))  # Rough estimate: ~4 chars per token
            total_chars=$((total_chars + chars))
            total_tokens_est=$((total_tokens_est + tokens_est))

            printf "  %-20s %8s chars  ~%6s tokens\n" "$(basename "$file")" "$chars" "$tokens_est"
        fi
    done

    echo ""
    echo "  Total: $total_chars chars  ~$total_tokens_est tokens"
    echo ""

    if [[ $total_tokens_est -gt 8000 ]]; then
        echo -e "${YELLOW}⚠️  Context is large. Consider --summarize or --archive-notes${NC}"
    elif [[ $total_tokens_est -gt 4000 ]]; then
        echo -e "${YELLOW}ℹ️  Context is moderate. Monitor growth.${NC}"
    else
        echo -e "${GREEN}✓ Context is manageable${NC}"
    fi
}

create_summary() {
    echo -e "${BLUE}📝 Creating 'Previously on...' Recap${NC}"
    echo ""

    if [[ ! -f "$NOTES_FILE" ]]; then
        echo "NOTES.md not found. Creating minimal recap from TODO.md..."
        mkdir -p "$MEMORY_DIR"
        cat > "$NOTES_FILE" << 'EOF'
# Session Notes

## Previously On...

[Generated recap will appear here]

EOF
    fi

    # Extract key information
    local active_tasks=$(grep -E '^\-\s+\[ \]' "$TODO_FILE" 2>/dev/null | head -3 | sed 's/^- \[ \] //' || echo "No active tasks")
    local recent_decision=$(grep -E '^\[20' "$DECISIONS_FILE" 2>/dev/null | tail -1 | cut -d']' -f2- | cut -d':' -f2 || echo "No recent decisions")
    local blocked_tasks=$(grep -B1 'Status.*blocked' "$TODO_FILE" 2>/dev/null | grep '^\-\s+\[ \]' | head -1 | sed 's/^- \[ \] //' || echo "No blockers")

    local recap_date=$(date +%Y-%m-%d)

    # Create compact recap
    cat > "${NOTES_FILE}.tmp" << EOF
# Session Notes

## Previously On... (Updated: $recap_date)

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

    echo -e "${GREEN}✓ Recap created in NOTES.md${NC}"
    echo ""
    echo "Review and refine the 'Previously on...' section to:"
    echo "  1. Summarize overall objective"
    echo "  2. List key decisions"
    echo "  3. Highlight current focus"
    echo "  4. Note blockers"
    echo "  5. State next milestone"
}

extract_decisions() {
    echo -e "${BLUE}🔍 Extracting Decisions from Notes/Scratchpad${NC}"
    echo ""

    local findings=0

    # Look for decision-like patterns in scratchpad
    if [[ -f "$SCRATCHPAD_FILE" ]]; then
        if grep -qi "decision\|chose\|selected\|using.*instead" "$SCRATCHPAD_FILE"; then
            echo "Potential decisions found in scratchpad.md:"
            grep -i "decision\|chose\|selected\|using.*instead" "$SCRATCHPAD_FILE" | head -5
            echo ""
            echo "Consider moving these to DECISIONS.log with full rationale."
            findings=$((findings + 1))
        fi
    fi

    # Look for architectural choices in notes
    if [[ -f "$NOTES_FILE" ]]; then
        if grep -qi "decided\|chose\|selected\|architecture\|approach" "$NOTES_FILE"; then
            echo "Potential decisions found in NOTES.md:"
            grep -i "decided\|chose\|selected" "$NOTES_FILE" | head -5
            echo ""
            echo "Consider formalizing these in DECISIONS.log."
            findings=$((findings + 1))
        fi
    fi

    if [[ $findings -eq 0 ]]; then
        echo -e "${GREEN}✓ No unrecorded decisions detected${NC}"
    fi
}

archive_old_notes() {
    echo -e "${BLUE}📦 Archiving Old Session Notes${NC}"
    echo ""

    if [[ ! -f "$NOTES_FILE" ]]; then
        echo "No NOTES.md found to archive."
        return
    fi

    local archive_dir="$MEMORY_DIR/archive"
    mkdir -p "$archive_dir"

    local archive_date=$(date +%Y-%m-%d)
    local archive_file="$archive_dir/notes-archive-$archive_date.md"

    # Extract sessions older than 30 days
    local cutoff_date=$(date -v-30d +%Y-%m-%d 2>/dev/null || date -d "30 days ago" +%Y-%m-%d 2>/dev/null)

    echo "Archiving sessions older than $cutoff_date..."

    # This is a simplified approach - in production, parse dates from session headers
    if grep -q "^## Session 2024" "$NOTES_FILE"; then
        grep -B1 "^## Session" "$NOTES_FILE" | head -20 > "$archive_file"
        echo ""
        echo -e "${GREEN}✓ Old sessions archived to:${NC}"
        echo "  $archive_file"
        echo ""
        echo "Manually remove archived sessions from NOTES.md to reduce size."
    else
        echo "No sessions found to archive."
    fi
}

# Main script logic
case "${1:-}" in
    --summarize)
        create_summary
        ;;
    --status)
        estimate_context_size
        ;;
    --extract-decisions)
        extract_decisions
        ;;
    --archive-notes)
        archive_old_notes
        ;;
    --help|-h)
        show_usage
        ;;
    *)
        if [[ -n "${1:-}" ]]; then
            echo "Unknown option: $1"
            echo ""
        fi
        show_usage
        exit 1
        ;;
esac
