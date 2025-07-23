#!/bin/bash
# AI Knowledge Maintenance - Analysis and cleanup tools

set -euo pipefail

KNOWLEDGE_DIR=".ai/knowledge"
PATTERNS_DIR="$KNOWLEDGE_DIR/patterns"
FAILURES_DIR="$KNOWLEDGE_DIR/failures"
GOTCHAS_DIR="$KNOWLEDGE_DIR/gotchas"

# Find stale knowledge (>90 days old)
find_stale_knowledge() {
    echo "=== Stale Knowledge Review ==="
    echo "Files not modified in 90+ days:"
    echo ""
    
    if command -v find >/dev/null; then
        find "$KNOWLEDGE_DIR" -name "*.md" -mtime +90 2>/dev/null | while read -r file; do
            echo "  📅 $(stat -f "%Sm" -t "%Y-%m-%d" "$file" 2>/dev/null || stat -c "%y" "$file" 2>/dev/null | cut -d' ' -f1): $file"
        done
    else
        echo "  find command not available"
    fi
    
    echo ""
    echo "Consider reviewing these files for relevance and accuracy."
}

# Show most-used patterns
show_top_patterns() {
    echo "=== Most Referenced Patterns ==="
    echo ""
    
    if [[ -d "$PATTERNS_DIR" ]]; then
        grep -r "### " "$PATTERNS_DIR/" 2>/dev/null | \
        cut -d: -f2 | \
        sort | \
        uniq -c | \
        sort -nr | \
        head -10 | \
        while read -r count pattern; do
            echo "  $count references: $pattern"
        done
    else
        echo "  No patterns directory found"
    fi
    echo ""
}

# Search knowledge base
search_knowledge() {
    local query="$1"
    echo "=== Knowledge Search: '$query' ==="
    echo ""
    
    if command -v grep >/dev/null; then
        grep -r -i "$query" "$KNOWLEDGE_DIR/" 2>/dev/null | while read -r line; do
            file=$(echo "$line" | cut -d: -f1)
            content=$(echo "$line" | cut -d: -f2-)
            echo "📄 $(basename "$file"): $content"
        done
    else
        echo "  grep command not available"
    fi
    echo ""
}

# Generate usage statistics
generate_usage_stats() {
    echo "=== Knowledge Base Statistics ==="
    echo ""
    
    # Count files and entries
    local pattern_files=$(find "$PATTERNS_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local failure_files=$(find "$FAILURES_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local gotcha_files=$(find "$GOTCHAS_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    
    local pattern_entries=$(grep -r "^### " "$PATTERNS_DIR/" 2>/dev/null | wc -l | tr -d ' ')
    local failure_entries=$(grep -r "^### " "$FAILURES_DIR/" 2>/dev/null | wc -l | tr -d ' ')
    local gotcha_entries=$(grep -r "^### " "$GOTCHAS_DIR/" 2>/dev/null | wc -l | tr -d ' ')
    
    echo "  📊 Files:"
    echo "    Patterns: $pattern_files files"
    echo "    Failures: $failure_files files"
    echo "    Gotchas: $gotcha_files files"
    echo ""
    echo "  📈 Entries:"
    echo "    Successful patterns: $pattern_entries"
    echo "    Documented failures: $failure_entries"
    echo "    Behavior gotchas: $gotcha_entries"
    echo ""
    
    # Show domains covered
    echo "  🏷️  Domains covered:"
    find "$PATTERNS_DIR" -name "*.md" 2>/dev/null | while read -r file; do
        domain=$(basename "$file" .md)
        entry_count=$(grep -c "^### " "$file" 2>/dev/null || echo "0")
        echo "    $domain: $entry_count patterns"
    done
    echo ""
}

# Check for anti-patterns in knowledge base
check_anti_patterns() {
    echo "=== Anti-Pattern Detection ==="
    echo ""
    
    # Check for unused knowledge (files not accessed recently)
    echo "🔍 Checking for unused knowledge..."
    find "$KNOWLEDGE_DIR" -name "*.md" -atime +90 2>/dev/null | while read -r file; do
        echo "  ⚠️  Not accessed in 90+ days: $file"
    done
    
    # Check for overly detailed entries (>200 words)
    echo ""
    echo "🔍 Checking for overly detailed entries..."
    find "$KNOWLEDGE_DIR" -name "*.md" 2>/dev/null | while read -r file; do
        word_count=$(wc -w < "$file" 2>/dev/null || echo "0")
        if [[ $word_count -gt 200 ]]; then
            echo "  📝 Very detailed file ($word_count words): $(basename "$file")"
        fi
    done
    
    # Check for low success patterns
    echo ""
    echo "🔍 Checking for low-success patterns..."
    grep -r "Success Rate.*[0-4][0-9]%" "$PATTERNS_DIR/" 2>/dev/null | while read -r line; do
        file=$(echo "$line" | cut -d: -f1)
        pattern=$(echo "$line" | cut -d: -f2-)
        echo "  📉 Low success rate: $(basename "$file") - $pattern"
    done
    
    echo ""
    echo "💡 Consider reviewing highlighted items for potential cleanup."
}

# Weekly maintenance routine
weekly_maintenance() {
    echo "=== Weekly Knowledge Maintenance ==="
    echo ""
    
    # Run all checks
    find_stale_knowledge
    echo ""
    check_anti_patterns
    echo ""
    generate_usage_stats
    echo ""
    
    # Generate action items
    echo "=== Recommended Actions ==="
    echo ""
    echo "  1. Review stale knowledge files for accuracy"
    echo "  2. Update success rates based on recent usage" 
    echo "  3. Consolidate similar patterns if found"
    echo "  4. Remove or archive unused knowledge"
    echo "  5. Add new patterns discovered this week"
    echo ""
}

# Export knowledge in different formats
export_knowledge() {
    local format="${1:-json}"
    local output_file="${2:-knowledge-export.$format}"
    
    echo "Exporting knowledge to $output_file (format: $format)"
    
    case "$format" in
        "json")
            cat > "$output_file" << 'EOF'
{
  "export_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "patterns": {
EOF
            
            # Export patterns
            find "$PATTERNS_DIR" -name "*.md" 2>/dev/null | while read -r file; do
                domain=$(basename "$file" .md)
                echo "    \"$domain\": {"
                echo "      \"file\": \"$file\","
                echo "      \"content\": $(cat "$file" | jq -Rs .)"
                echo "    },"
            done | sed '$ s/,$//'
            
            echo "  },"
            echo "  \"failures\": {"
            
            # Export failures  
            find "$FAILURES_DIR" -name "*.md" 2>/dev/null | while read -r file; do
                domain=$(basename "$file" .md)
                echo "    \"$domain\": {"
                echo "      \"file\": \"$file\","
                echo "      \"content\": $(cat "$file" | jq -Rs .)"
                echo "    },"
            done | sed '$ s/,$//'
            
            echo "  }"
            echo "}"
            ;;
        "markdown")
            cat > "$output_file" << 'EOF'
# AI Knowledge Export
Generated on: $(date)

## Successful Patterns
EOF
            find "$PATTERNS_DIR" -name "*.md" 2>/dev/null | while read -r file; do
                echo "### $(basename "$file" .md | tr '[:lower:]' '[:upper:]') Domain"
                echo ""
                cat "$file"
                echo ""
            done >> "$output_file"
            
            echo "## Failed Attempts" >> "$output_file"
            find "$FAILURES_DIR" -name "*.md" 2>/dev/null | while read -r file; do
                echo "### $(basename "$file" .md | tr '[:lower:]' '[:upper:]') Domain" >> "$output_file"
                echo "" >> "$output_file"
                cat "$file" >> "$output_file"
                echo "" >> "$output_file"
            done
            ;;
        *)
            echo "Unsupported format: $format"
            echo "Supported formats: json, markdown"
            exit 1
            ;;
    esac
    
    echo "✓ Knowledge exported to $output_file"
}

# Validate knowledge format
validate_format() {
    echo "=== Knowledge Format Validation ==="
    echo ""
    
    local issues_found=0
    
    # Check patterns format
    find "$PATTERNS_DIR" -name "*.md" 2>/dev/null | while read -r file; do
        echo "Validating $file..."
        
        # Check for required fields in patterns
        if ! grep -q "^### .* (.* success)" "$file" 2>/dev/null; then
            echo "  ⚠️  Missing success rate format in pattern headers"
            issues_found=$((issues_found + 1))
        fi
        
        if ! grep -q "\*\*Prompt\*\*:" "$file" 2>/dev/null; then
            echo "  ⚠️  Missing **Prompt**: field"
            issues_found=$((issues_found + 1))
        fi
    done
    
    # Check failures format
    find "$FAILURES_DIR" -name "*.md" 2>/dev/null | while read -r file; do
        echo "Validating $file..."
        
        if ! grep -q "^### ❌" "$file" 2>/dev/null; then
            echo "  ⚠️  Missing ❌ prefix in failure headers"
            issues_found=$((issues_found + 1))
        fi
        
        if ! grep -q "\*\*Problem\*\*:" "$file" 2>/dev/null; then
            echo "  ⚠️  Missing **Problem**: field"
            issues_found=$((issues_found + 1))
        fi
    done
    
    if [[ $issues_found -eq 0 ]]; then
        echo "✅ All knowledge files follow proper format"
    else
        echo "❌ Found $issues_found format issues"
    fi
}

# Show usage
show_usage() {
    cat << 'EOF'
AI Knowledge Maintenance Tool

USAGE:
    knowledge-maintenance.sh [COMMAND] [OPTIONS]

COMMANDS:
    --stale-review             Find knowledge files not updated in 90+ days
    --top-patterns             Show most referenced patterns
    --search QUERY             Search knowledge base for term
    --usage-stats              Generate knowledge base statistics
    --anti-pattern-check       Check for knowledge anti-patterns
    --weekly-maintenance       Run weekly maintenance routine
    --export FORMAT [FILE]     Export knowledge (formats: json, markdown)
    --validate-format          Validate knowledge file formatting
    --help                     Show this help message

EXAMPLES:
    # Find stale knowledge
    ./knowledge-maintenance.sh --stale-review
    
    # Search for authentication patterns
    ./knowledge-maintenance.sh --search "auth"
    
    # Run weekly maintenance
    ./knowledge-maintenance.sh --weekly-maintenance
    
    # Export knowledge for sharing
    ./knowledge-maintenance.sh --export json team-knowledge.json
    
    # Validate format compliance
    ./knowledge-maintenance.sh --validate-format
EOF
}

# Main command processing
case "${1:-}" in
    "--stale-review")
        find_stale_knowledge
        ;;
    "--top-patterns")
        show_top_patterns
        ;;
    "--search")
        if [[ -z "${2:-}" ]]; then
            echo "Error: Search query required"
            exit 1
        fi
        search_knowledge "$2"
        ;;
    "--usage-stats")
        generate_usage_stats
        ;;
    "--anti-pattern-check")
        check_anti_patterns
        ;;
    "--weekly-maintenance")
        weekly_maintenance
        ;;
    "--export")
        format="${2:-json}"
        output_file="${3:-knowledge-export.$format}"
        export_knowledge "$format" "$output_file"
        ;;
    "--validate-format")
        validate_format
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