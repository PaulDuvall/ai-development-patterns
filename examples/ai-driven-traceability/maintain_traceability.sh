#!/bin/bash
# AI-Driven Traceability - Complete maintenance automation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/traceability_config.json"

# Initialize traceability system
init_traceability() {
    echo "🔗 Initializing AI-Driven Traceability System..."
    
    # Create configuration file
    cat > "$CONFIG_FILE" << 'EOF'
{
  "requirement_patterns": [
    "\\[\\^req-[a-zA-Z0-9-]+\\]",
    "\\[\\^REQ[0-9]+\\]"
  ],
  "user_story_patterns": [
    "US-[0-9]+",
    "Story-[0-9]+",
    "#[0-9]+"
  ],
  "ignore_paths": [
    "node_modules/",
    ".git/",
    "build/",
    "dist/",
    ".venv/",
    "__pycache__/"
  ]
}
EOF
    
    # Create git hooks
    mkdir -p .git/hooks
    
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Validate traceability before commit
echo "🔍 Checking traceability links..."
if command -v ./maintain_traceability.sh >/dev/null; then
    ./maintain_traceability.sh --validate-staged
else
    examples/ai-driven-traceability/maintain_traceability.sh --validate-staged
fi
EOF
    
    chmod +x .git/hooks/pre-commit
    
    echo "✅ Traceability system initialized"
    echo "   - Configuration: $CONFIG_FILE"
    echo "   - Git hooks: .git/hooks/pre-commit"
}

# Scan new code for missing requirement links
scan_new_code() {
    echo "🔍 Scanning for traceability gaps..."
    
    # Get recently changed files
    changed_files=$(git diff --name-only HEAD~1 2>/dev/null || git ls-files "*.py" "*.js" "*.java" "*.go" | head -10)
    
    if [[ -z "$changed_files" ]]; then
        echo "No changed files found"
        return 0
    fi
    
    local gaps_found=0
    
    echo "$changed_files" | while read -r file; do
        if [[ ! -f "$file" ]]; then
            continue
        fi
        
        # Skip ignored paths
        if grep -q "node_modules\|\.git\|build\|dist" <<< "$file"; then
            continue
        fi
        
        # Check for implementation without traceability links
        if grep -q "class\|function\|def " "$file" && ! grep -q "# Implements:\|# Satisfies:" "$file"; then
            echo "⚠️  Missing traceability in: $file"
            
            # Use AI to suggest requirement links
            ai_suggestion=$(ai "Analyze $file and suggest requirement links:
            - What product requirement does this code satisfy?
            - Which user story does it implement?
            - Generate proper traceability annotations: # Implements: [^req_id]
            
            Focus on the main functionality and provide specific requirement IDs." 2>/dev/null || echo "AI analysis unavailable")
            
            if [[ "$ai_suggestion" != "AI analysis unavailable" ]]; then
                echo "💡 AI Suggestion for $file:"
                echo "$ai_suggestion"
                echo ""
            fi
            
            gaps_found=$((gaps_found + 1))
        fi
    done
    
    if [[ $gaps_found -eq 0 ]]; then
        echo "✅ No traceability gaps found"
    else
        echo "❌ Found $gaps_found files with missing traceability"
    fi
}

# Validate existing traceability links
validate_links() {
    echo "🔍 Validating existing traceability links..."
    
    local broken_links=0
    local total_links=0
    
    # Find all requirement references
    req_refs=$(grep -r "\\[\\^req-" . --include="*.py" --include="*.js" --include="*.java" --include="*.go" --include="*.md" 2>/dev/null || true)
    
    if [[ -z "$req_refs" ]]; then
        echo "ℹ️  No requirement links found"
        return 0
    fi
    
    echo "$req_refs" | while read -r line; do
        if [[ -z "$line" ]]; then continue; fi
        
        file=$(echo "$line" | cut -d: -f1)
        req_id=$(echo "$line" | grep -o "\\[\\^req-[a-zA-Z0-9-]*\\]")
        
        total_links=$((total_links + 1))
        
        echo "📋 Checking $req_id in $file"
        
        # Simple validation - in practice, you'd check against actual requirement database
        if [[ ${#req_id} -lt 8 ]]; then
            echo "⚠️  Potentially invalid requirement format: $req_id"
            broken_links=$((broken_links + 1))
        fi
    done
    
    echo ""
    echo "📊 Validation Summary:"
    echo "   Total links checked: $total_links"
    echo "   Potentially broken: $broken_links"
    
    if [[ $broken_links -eq 0 ]]; then
        echo "✅ All traceability links appear valid"
    else
        echo "❌ Some links may need attention"
    fi
}

# Generate coverage report
generate_coverage_report() {
    echo "📊 Generating traceability coverage report..."
    
    local output_file="${1:-traceability-report.md}"
    
    cat > "$output_file" << 'EOF'
# Traceability Coverage Report

Generated on: $(date)

## Summary

EOF
    
    # Count files with and without traceability
    total_files=$(find . -name "*.py" -o -name "*.js" -o -name "*.java" -o -name "*.go" | grep -v -E "(node_modules|\.git|build|dist|__pycache__|\.venv)" | wc -l)
    files_with_trace=$(grep -l "# Implements:\|# Satisfies:" $(find . -name "*.py" -o -name "*.js" -o -name "*.java" -o -name "*.go" | grep -v -E "(node_modules|\.git|build|dist|__pycache__|\.venv)") 2>/dev/null | wc -l)
    
    coverage_percent=$(( files_with_trace * 100 / total_files ))
    
    cat >> "$output_file" << EOF
- **Total Code Files**: $total_files
- **Files with Traceability**: $files_with_trace
- **Coverage**: $coverage_percent%

## Files Missing Traceability

EOF
    
    # List files without traceability
    find . -name "*.py" -o -name "*.js" -o -name "*.java" -o -name "*.go" | \
    grep -v -E "(node_modules|\.git|build|dist|__pycache__|\.venv)" | \
    while read -r file; do
        if ! grep -q "# Implements:\|# Satisfies:" "$file" 2>/dev/null; then
            echo "- \`$file\`" >> "$output_file"
        fi
    done
    
    cat >> "$output_file" << 'EOF'

## Requirement Links Found

EOF
    
    # List all requirement links
    grep -r "\\[\\^req-" . --include="*.py" --include="*.js" --include="*.java" --include="*.go" --include="*.md" 2>/dev/null | \
    while read -r line; do
        if [[ -n "$line" ]]; then
            file=$(echo "$line" | cut -d: -f1)
            req_id=$(echo "$line" | grep -o "\\[\\^req-[a-zA-Z0-9-]*\\]")
            echo "- \`$file\`: $req_id" >> "$output_file"
        fi
    done
    
    echo "✅ Coverage report generated: $output_file"
    
    # Display summary
    echo ""
    echo "📊 Coverage Summary:"
    echo "   Total files: $total_files"
    echo "   With traceability: $files_with_trace"
    echo "   Coverage: $coverage_percent%"
}

# Impact analysis for changes
impact_analysis() {
    local since_ref="${1:-HEAD~5}"
    echo "🔍 Analyzing impact of changes since $since_ref..."
    
    # Get changed files
    changed_files=$(git diff --name-only "$since_ref" 2>/dev/null || echo "")
    
    if [[ -z "$changed_files" ]]; then
        echo "No changes found since $since_ref"
        return 0
    fi
    
    echo "📁 Changed Files:"
    echo "$changed_files" | sed 's/^/   - /'
    echo ""
    
    # Extract requirements from changed files
    echo "🔗 Affected Requirements:"
    affected_reqs=()
    
    while read -r file; do
        if [[ -f "$file" ]]; then
            reqs=$(grep -o "\\[\\^req-[a-zA-Z0-9-]*\\]" "$file" 2>/dev/null || true)
            if [[ -n "$reqs" ]]; then
                echo "   $file:"
                echo "$reqs" | sed 's/^/     - /'
                affected_reqs+=($reqs)
            fi
        fi
    done <<< "$changed_files"
    
    if [[ ${#affected_reqs[@]} -eq 0 ]]; then
        echo "   No requirements found in changed files"
    fi
    
    echo ""
    echo "💡 AI Impact Analysis:"
    
    # Use AI for deeper impact analysis
    ai_analysis=$(ai "Analyze the impact of these file changes:

Files changed: $changed_files

Provide analysis on:
1. What requirements/features are affected
2. Which tests might need updates
3. What documentation should be reviewed
4. Risk assessment (low/medium/high)

Be specific and actionable." 2>/dev/null || echo "AI analysis unavailable")
    
    if [[ "$ai_analysis" != "AI analysis unavailable" ]]; then
        echo "$ai_analysis"
    else
        echo "   Manual review recommended for changed files"
    fi
}

# Validate staged files (for git hooks)
validate_staged() {
    echo "🔍 Validating traceability in staged files..."
    
    staged_files=$(git diff --cached --name-only --diff-filter=AM 2>/dev/null || echo "")
    
    if [[ -z "$staged_files" ]]; then
        echo "✅ No staged files to validate"
        return 0
    fi
    
    local issues_found=0
    
    while read -r file; do
        if [[ ! -f "$file" ]]; then
            continue
        fi
        
        # Skip non-code files
        if ! grep -q -E "\\.(py|js|java|go)$" <<< "$file"; then
            continue
        fi
        
        # Check for implementation without traceability
        if grep -q "class\|function\|def " "$file" && ! grep -q "# Implements:\|# Satisfies:" "$file"; then
            echo "❌ Missing traceability in staged file: $file"
            echo "   Add requirement links before committing"
            issues_found=$((issues_found + 1))
        fi
    done <<< "$staged_files"
    
    if [[ $issues_found -eq 0 ]]; then
        echo "✅ All staged files have proper traceability"
        return 0
    else
        echo "❌ Found $issues_found staged files with missing traceability"
        return 1
    fi
}

# Show usage
show_usage() {
    cat << 'EOF'
AI-Driven Traceability Maintenance Tool

USAGE:
    maintain_traceability.sh [COMMAND] [OPTIONS]

COMMANDS:
    --init                     Initialize traceability system
    --scan-new                 Scan for missing requirement links
    --validate                 Validate existing traceability links
    --coverage-report [FILE]   Generate coverage report (default: traceability-report.md)
    --impact-analysis [REF]    Analyze impact of changes (default: since HEAD~5)
    --validate-staged          Validate staged files (for git hooks)
    --help                     Show this help message

EXAMPLES:
    # Initialize system
    ./maintain_traceability.sh --init
    
    # Check for missing links in recent changes
    ./maintain_traceability.sh --scan-new
    
    # Validate all existing links
    ./maintain_traceability.sh --validate
    
    # Generate coverage report
    ./maintain_traceability.sh --coverage-report
    
    # Analyze impact of changes in last 10 commits
    ./maintain_traceability.sh --impact-analysis HEAD~10
    
    # Validate staged files (used by git hooks)
    ./maintain_traceability.sh --validate-staged
EOF
}

# Main command processing
case "${1:-}" in
    "--init")
        init_traceability
        ;;
    "--scan-new")
        scan_new_code
        ;;
    "--validate")
        validate_links
        ;;
    "--coverage-report")
        generate_coverage_report "${2:-}"
        ;;
    "--impact-analysis")
        impact_analysis "${2:-}"
        ;;
    "--validate-staged")
        validate_staged
        ;;
    "--help"|"-h"|"")
        show_usage
        ;;
    *)
        echo "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac