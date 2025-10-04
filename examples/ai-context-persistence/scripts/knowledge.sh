#!/bin/bash
# AI Context Persistence - Knowledge Management (Simplified)
#
# Capture successful patterns and failures for reuse

set -euo pipefail

KNOWLEDGE_DIR=".ai/knowledge"
PATTERNS_DIR="$KNOWLEDGE_DIR/patterns"
FAILURES_DIR="$KNOWLEDGE_DIR/failures"

show_usage() {
    cat << 'EOF'
Knowledge Management Tool - Capture and search AI patterns

Usage: ./knowledge.sh [OPTION]

Options:
    --init                          Initialize knowledge structure
    --success [OPTIONS]             Capture successful pattern
    --failure [OPTIONS]             Document failed attempt
    --search <keyword>              Search patterns and failures
    --help                          Show this help

Capture Success:
    --domain <name>                 Domain/category (e.g., "auth", "database")
    --pattern <name>                Pattern name (e.g., "JWT Auth")
    --prompt <text>                 Exact prompt that worked
    --success-rate <percent>        Success rate (e.g., "95%")
    --context <text>                When to use (optional)

Capture Failure:
    --domain <name>                 Domain/category
    --bad-prompt <text>             The prompt that failed
    --problem <text>                What went wrong
    --solution <text>               Better approach

Examples:
    # Initialize
    ./knowledge.sh --init

    # Capture success
    ./knowledge.sh --success \
      --domain "auth" \
      --pattern "JWT Auth" \
      --prompt "JWT with RS256, 15min access, httpOnly cookie" \
      --success-rate "95%"

    # Document failure
    ./knowledge.sh --failure \
      --domain "auth" \
      --bad-prompt "Make auth secure" \
      --problem "Too vague" \
      --solution "Specify exact requirements"

    # Search
    ./knowledge.sh --search "auth"
EOF
}

init_knowledge() {
    echo "Initializing knowledge structure..."
    mkdir -p "$PATTERNS_DIR" "$FAILURES_DIR"

    cat > "$PATTERNS_DIR/README.md" << 'EOF'
# Successful AI Patterns

Working prompts with success rates.

## Format
```markdown
### [Pattern Name] ([Success Rate]% success)
**Prompt**: "[Exact prompt that works]"
**Context**: [When to use]
**Last Used**: [Date]
**Success Rate**: [Percentage]
```
EOF

    cat > "$FAILURES_DIR/README.md" << 'EOF'
# Failed AI Attempts

Document failures to avoid repeating mistakes.

## Format
```markdown
### ❌ "[Failed prompt]"
**Problem**: [What went wrong]
**Time Wasted**: [Duration]
**Better Approach**: "[Improved prompt]"
**Date**: [When this occurred]
```
EOF

    echo "✓ Knowledge structure created at $KNOWLEDGE_DIR"
}

capture_success() {
    local domain="$1"
    local pattern="$2"
    local prompt="$3"
    local success_rate="${4:-Unknown}"
    local context="${5:-}"

    local file="$PATTERNS_DIR/${domain}.md"
    local date=$(date +%Y-%m-%d)

    # Create file if needed
    [[ ! -f "$file" ]] && echo "# $domain Patterns" > "$file" && echo "" >> "$file"

    # Add entry
    cat >> "$file" << EOF

### $pattern ($success_rate success)
**Prompt**: "$prompt"
**Context**: ${context:-General use}
**Last Used**: $date
**Success Rate**: $success_rate

EOF

    echo "✓ Pattern captured in $file"
}

capture_failure() {
    local domain="$1"
    local bad_prompt="$2"
    local problem="$3"
    local solution="$4"
    local time_wasted="${5:-Unknown}"

    local file="$FAILURES_DIR/${domain}.md"
    local date=$(date +%Y-%m-%d)

    # Create file if needed
    [[ ! -f "$file" ]] && echo "# $domain Failures" > "$file" && echo "" >> "$file"

    # Add entry
    cat >> "$file" << EOF

### ❌ "$bad_prompt"
**Problem**: $problem
**Time Wasted**: $time_wasted
**Better Approach**: "$solution"
**Date**: $date

EOF

    echo "✓ Failure captured in $file"
}

search_knowledge() {
    local keyword="$1"

    echo "Searching for: $keyword"
    echo ""

    # Search patterns
    if [[ -d "$PATTERNS_DIR" ]]; then
        echo "=== Successful Patterns ==="
        grep -r -i "$keyword" "$PATTERNS_DIR" 2>/dev/null | head -10 || echo "No patterns found"
        echo ""
    fi

    # Search failures
    if [[ -d "$FAILURES_DIR" ]]; then
        echo "=== Failed Attempts ==="
        grep -r -i "$keyword" "$FAILURES_DIR" 2>/dev/null | head -10 || echo "No failures found"
        echo ""
    fi
}

# Parse arguments
ACTION="${1:-}"
shift || true

case "$ACTION" in
    --init)
        init_knowledge
        ;;
    --success)
        DOMAIN=""
        PATTERN=""
        PROMPT=""
        SUCCESS_RATE=""
        CONTEXT=""

        while [[ $# -gt 0 ]]; do
            case "$1" in
                --domain) DOMAIN="$2"; shift 2 ;;
                --pattern) PATTERN="$2"; shift 2 ;;
                --prompt) PROMPT="$2"; shift 2 ;;
                --success-rate) SUCCESS_RATE="$2"; shift 2 ;;
                --context) CONTEXT="$2"; shift 2 ;;
                *) echo "Unknown option: $1"; exit 1 ;;
            esac
        done

        if [[ -z "$DOMAIN" || -z "$PATTERN" || -z "$PROMPT" ]]; then
            echo "Error: --domain, --pattern, and --prompt are required"
            exit 1
        fi

        capture_success "$DOMAIN" "$PATTERN" "$PROMPT" "$SUCCESS_RATE" "$CONTEXT"
        ;;
    --failure)
        DOMAIN=""
        BAD_PROMPT=""
        PROBLEM=""
        SOLUTION=""
        TIME_WASTED=""

        while [[ $# -gt 0 ]]; do
            case "$1" in
                --domain) DOMAIN="$2"; shift 2 ;;
                --bad-prompt) BAD_PROMPT="$2"; shift 2 ;;
                --problem) PROBLEM="$2"; shift 2 ;;
                --solution) SOLUTION="$2"; shift 2 ;;
                --time-wasted) TIME_WASTED="$2"; shift 2 ;;
                *) echo "Unknown option: $1"; exit 1 ;;
            esac
        done

        if [[ -z "$DOMAIN" || -z "$BAD_PROMPT" || -z "$PROBLEM" || -z "$SOLUTION" ]]; then
            echo "Error: --domain, --bad-prompt, --problem, and --solution are required"
            exit 1
        fi

        capture_failure "$DOMAIN" "$BAD_PROMPT" "$PROBLEM" "$SOLUTION" "$TIME_WASTED"
        ;;
    --search)
        if [[ -z "${1:-}" ]]; then
            echo "Error: Search keyword required"
            exit 1
        fi
        search_knowledge "$1"
        ;;
    --help|-h|"")
        show_usage
        ;;
    *)
        echo "Unknown action: $ACTION"
        echo ""
        show_usage
        exit 1
        ;;
esac
