#!/bin/bash
# AI Context Persistence - Prompt Pattern Capture and Management
#
# Part of the AI Context Persistence pattern
# Captures successful prompts and failures with success rates for reuse

set -euo pipefail

KNOWLEDGE_DIR=".ai/knowledge"
PATTERNS_DIR="$KNOWLEDGE_DIR/patterns"
FAILURES_DIR="$KNOWLEDGE_DIR/failures"
GOTCHAS_DIR="$KNOWLEDGE_DIR/gotchas"

# Initialize knowledge structure
init_knowledge_structure() {
    echo "Initializing AI knowledge structure..."
    mkdir -p "$PATTERNS_DIR" "$FAILURES_DIR" "$GOTCHAS_DIR"
    
    # Create README for each directory
    cat > "$PATTERNS_DIR/README.md" << 'EOF'
# Successful AI Patterns

This directory contains working AI prompts and patterns with success rates.

## Format
```markdown
### [Pattern Name] ([Success Rate]% success)
**Prompt**: "[Exact prompt that works]"
**Context**: [When to use this pattern]
**Gotcha**: [Common AI behavior to watch out for]
**Last Used**: [Date]
**Success Rate**: [Percentage] ([attempts passed]/[total attempts])
```
EOF

    cat > "$FAILURES_DIR/README.md" << 'EOF'
# Failed AI Attempts

This directory documents failed prompts and approaches to avoid repeating mistakes.

## Format
```markdown
### ❌ "[Failed prompt or approach]"
**Problem**: [What went wrong and why]
**Time Wasted**: [How much time was lost]
**Better Approach**: "[Improved prompt or strategy]"
**Date**: [When this failure occurred]
```
EOF

    cat > "$GOTCHAS_DIR/README.md" << 'EOF'
# AI Behavior Gotchas

This directory contains common AI behaviors and workarounds.

## Format
```markdown
### [Gotcha Name]
**Behavior**: [What the AI tends to do]
**Fix**: [How to work around this behavior]
**Examples**: [Specific examples or prompts]
```
EOF

    echo "Knowledge structure initialized at $KNOWLEDGE_DIR"
}

# Capture successful pattern
capture_success() {
    local domain="$1"
    local pattern="$2"
    local prompt="$3"
    local context="${4:-}"
    local success_rate="${5:-Unknown}"
    local gotcha="${6:-}"
    
    local file="$PATTERNS_DIR/${domain}.md"
    local date=$(date +%Y-%m-%d)
    
    echo "Capturing successful pattern: $pattern"
    
    # Create file if it doesn't exist
    if [[ ! -f "$file" ]]; then
        echo "# $domain Patterns" > "$file"
        echo "" >> "$file"
    fi
    
    # Add pattern entry
    cat >> "$file" << EOF

### $pattern ($success_rate success)
**Prompt**: "$prompt"
**Context**: $context
**Last Used**: $date
**Success Rate**: $success_rate
$([ -n "$gotcha" ] && echo "**Gotcha**: $gotcha")

EOF
    
    echo "✓ Success pattern captured in $file"
}

# Capture failure
capture_failure() {
    local domain="$1"
    local bad_prompt="$2"
    local problem="$3"
    local solution="$4"
    local time_wasted="${5:-Unknown}"
    
    local file="$FAILURES_DIR/${domain}.md"
    local date=$(date +%Y-%m-%d)
    
    echo "Capturing failure: $bad_prompt"
    
    # Create file if it doesn't exist
    if [[ ! -f "$file" ]]; then
        echo "# $domain Failures" > "$file"
        echo "" >> "$file"
    fi
    
    # Add failure entry
    cat >> "$file" << EOF

### ❌ "$bad_prompt"
**Problem**: $problem
**Time Wasted**: $time_wasted
**Better Approach**: "$solution"
**Date**: $date

EOF
    
    echo "✓ Failure captured in $file"
}

# Update success rate for existing pattern
update_success_rate() {
    local domain="$1"
    local pattern="$2"
    local result="$3"  # "success" or "failure"
    
    local file="$PATTERNS_DIR/${domain}.md"
    
    if [[ ! -f "$file" ]]; then
        echo "Error: Pattern file $file not found"
        return 1
    fi
    
    echo "Updating success rate for: $pattern ($result)"
    
    # Extract current success rate and calculate new one
    # This is a simplified version - in practice, you'd want more robust parsing
    local current_line=$(grep -n "### $pattern" "$file" || echo "")
    
    if [[ -n "$current_line" ]]; then
        echo "✓ Pattern found, updating success rate"
        # Update last used date
        sed -i "s/\*\*Last Used\*\*:.*/\*\*Last Used\*\*: $(date +%Y-%m-%d)/" "$file"
        echo "✓ Updated last used date"
    else
        echo "Warning: Pattern '$pattern' not found in $file"
    fi
}

# Capture gotcha/behavior pattern
capture_gotcha() {
    local name="$1"
    local behavior="$2"
    local fix="$3"
    local examples="${4:-}"
    
    local file="$GOTCHAS_DIR/general.md"
    
    echo "Capturing gotcha: $name"
    
    # Create file if it doesn't exist
    if [[ ! -f "$file" ]]; then
        echo "# General AI Gotchas" > "$file"
        echo "" >> "$file"
    fi
    
    # Add gotcha entry
    cat >> "$file" << EOF

### $name
**Behavior**: $behavior
**Fix**: $fix
$([ -n "$examples" ] && echo "**Examples**: $examples")

EOF
    
    echo "✓ Gotcha captured in $file"
}

# Quick knowledge capture from command line
quick_capture() {
    echo "=== Quick Knowledge Capture ==="
    echo "This will guide you through capturing AI knowledge."
    echo ""
    
    read -p "Type (success/failure/gotcha): " type
    read -p "Domain (auth/api/database/etc): " domain
    
    case "$type" in
        "success")
            read -p "Pattern name: " pattern
            read -p "Working prompt: " prompt
            read -p "Context/when to use: " context
            read -p "Success rate (e.g., 95%): " success_rate
            read -p "Gotcha/warning (optional): " gotcha
            
            capture_success "$domain" "$pattern" "$prompt" "$context" "$success_rate" "$gotcha"
            ;;
        "failure")
            read -p "Failed prompt: " bad_prompt
            read -p "What went wrong: " problem
            read -p "Better approach: " solution
            read -p "Time wasted: " time_wasted
            
            capture_failure "$domain" "$bad_prompt" "$problem" "$solution" "$time_wasted"
            ;;
        "gotcha")
            read -p "Gotcha name: " name
            read -p "AI behavior: " behavior
            read -p "How to fix: " fix
            read -p "Examples (optional): " examples
            
            capture_gotcha "$name" "$behavior" "$fix" "$examples"
            ;;
        *)
            echo "Invalid type. Use: success, failure, or gotcha"
            exit 1
            ;;
    esac
}

# Show usage
show_usage() {
    cat << 'EOF'
AI Knowledge Capture Tool

USAGE:
    knowledge-capture.sh [COMMAND] [OPTIONS]

COMMANDS:
    --init                     Initialize knowledge directory structure
    --quick                    Interactive knowledge capture
    
    --success                  Capture successful pattern
      --domain DOMAIN          Domain (auth, api, database, etc.)
      --pattern NAME           Pattern name
      --prompt TEXT            Working prompt
      --context TEXT           When to use context
      --success-rate RATE      Success rate (e.g., 95%)
      --gotcha TEXT            Optional gotcha/warning
    
    --failure                  Capture failed attempt
      --domain DOMAIN          Domain
      --bad-prompt TEXT        Failed prompt
      --problem TEXT           What went wrong
      --solution TEXT          Better approach
      --time-wasted TIME       Time wasted
    
    --gotcha                   Capture AI behavior gotcha
      --name TEXT              Gotcha name
      --behavior TEXT          AI behavior description
      --fix TEXT               How to work around it
      --examples TEXT          Optional examples
    
    --update-success           Update success rate for existing pattern
      --domain DOMAIN          Domain
      --pattern NAME           Pattern name
      --result RESULT          "success" or "failure"

EXAMPLES:
    # Initialize structure
    ./knowledge-capture.sh --init
    
    # Capture successful auth pattern
    ./knowledge-capture.sh --success \
      --domain "auth" \
      --pattern "JWT Auth" \
      --prompt "JWT with RS256, 15min access, httpOnly cookie" \
      --context "Node.js APIs" \
      --success-rate "95%" \
      --gotcha "AI defaults to HS256 - specify RS256"
    
    # Capture failure
    ./knowledge-capture.sh --failure \
      --domain "auth" \
      --bad-prompt "Make auth secure" \
      --problem "Too vague - AI over-engineers" \
      --solution "Specify exact JWT requirements" \
      --time-wasted "2 hours"
    
    # Interactive capture
    ./knowledge-capture.sh --quick
EOF
}

# Parse command line arguments
if [[ $# -eq 0 ]]; then
    show_usage
    exit 1
fi

case "$1" in
    "--init")
        init_knowledge_structure
        ;;
    "--quick")
        quick_capture
        ;;
    "--success")
        shift
        domain="" pattern="" prompt="" context="" success_rate="" gotcha=""
        
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --domain) domain="$2"; shift 2 ;;
                --pattern) pattern="$2"; shift 2 ;;
                --prompt) prompt="$2"; shift 2 ;;
                --context) context="$2"; shift 2 ;;
                --success-rate) success_rate="$2"; shift 2 ;;
                --gotcha) gotcha="$2"; shift 2 ;;
                *) echo "Unknown option: $1"; exit 1 ;;
            esac
        done
        
        if [[ -z "$domain" || -z "$pattern" || -z "$prompt" ]]; then
            echo "Error: --domain, --pattern, and --prompt are required"
            exit 1
        fi
        
        capture_success "$domain" "$pattern" "$prompt" "$context" "$success_rate" "$gotcha"
        ;;
    "--failure")
        shift
        domain="" bad_prompt="" problem="" solution="" time_wasted=""
        
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --domain) domain="$2"; shift 2 ;;
                --bad-prompt) bad_prompt="$2"; shift 2 ;;
                --problem) problem="$2"; shift 2 ;;
                --solution) solution="$2"; shift 2 ;;
                --time-wasted) time_wasted="$2"; shift 2 ;;
                *) echo "Unknown option: $1"; exit 1 ;;
            esac
        done
        
        if [[ -z "$domain" || -z "$bad_prompt" || -z "$problem" || -z "$solution" ]]; then
            echo "Error: --domain, --bad-prompt, --problem, and --solution are required"
            exit 1
        fi
        
        capture_failure "$domain" "$bad_prompt" "$problem" "$solution" "$time_wasted"
        ;;
    "--update-success")
        shift
        domain="" pattern="" result=""
        
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --domain) domain="$2"; shift 2 ;;
                --pattern) pattern="$2"; shift 2 ;;
                --result) result="$2"; shift 2 ;;
                *) echo "Unknown option: $1"; exit 1 ;;
            esac
        done
        
        if [[ -z "$domain" || -z "$pattern" || -z "$result" ]]; then
            echo "Error: --domain, --pattern, and --result are required"
            exit 1
        fi
        
        update_success_rate "$domain" "$pattern" "$result"
        ;;
    "--help"|"-h")
        show_usage
        ;;
    *)
        echo "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac