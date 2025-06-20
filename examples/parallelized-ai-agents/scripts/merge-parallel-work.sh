#!/bin/bash
# merge-parallel-work.sh - Automated conflict detection and resolution for parallel AI agents
# This script manages the integration of work from multiple parallel agents

set -euo pipefail

# Configuration
MAIN_BRANCH="${MAIN_BRANCH:-main}"
AGENT_BRANCH_PREFIX="${AGENT_BRANCH_PREFIX:-agent/}"
WORKSPACE_DIR="${WORKSPACE_DIR:-./workspace}"
REPORTS_DIR="${REPORTS_DIR:-./reports}"
SHARED_MEMORY="${SHARED_MEMORY:-./shared-memory/agent_memory.json}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create report directory
mkdir -p "$REPORTS_DIR"

# Function to check if a branch exists
branch_exists() {
    git show-ref --verify --quiet "refs/heads/$1"
}

# Function to analyze shared memory for agent insights
analyze_shared_memory() {
    if [ -f "$SHARED_MEMORY" ]; then
        log_info "Analyzing shared memory for agent insights..."
        python3 - <<EOF
import json
import sys

try:
    with open('$SHARED_MEMORY', 'r') as f:
        memory = json.load(f)
    
    print("\n=== Agent Activity Summary ===")
    for agent_id, discoveries in memory.get('discoveries', {}).items():
        print(f"\n{agent_id}:")
        print(f"  - Discoveries: {len(discoveries)}")
        for key, value in list(discoveries.items())[:3]:  # Show first 3
            print(f"    • {key}: {value.get('value', 'N/A')[:50]}...")
    
    if memory.get('conflicts'):
        print("\n=== Detected Conflicts ===")
        for conflict in memory['conflicts']:
            print(f"  - {conflict['key']} between {', '.join(conflict['agents'])}")
    
except Exception as e:
    print(f"Error reading shared memory: {e}", file=sys.stderr)
    sys.exit(1)
EOF
    fi
}

# Function to create merge report
create_merge_report() {
    local branch=$1
    local status=$2
    local details=$3
    local report_file="$REPORTS_DIR/merge_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" <<EOF
{
    "branch": "$branch",
    "status": "$status",
    "details": "$details",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "main_branch": "$MAIN_BRANCH"
}
EOF
}

# Function to attempt automated conflict resolution
resolve_conflicts() {
    local conflicted_files=$(git diff --name-only --diff-filter=U)
    
    if [ -z "$conflicted_files" ]; then
        return 0
    fi
    
    log_warning "Attempting automated conflict resolution..."
    
    echo "$conflicted_files" | while read -r file; do
        log_info "Analyzing conflict in: $file"
        
        # Try different resolution strategies
        case "$file" in
            *.json)
                # For JSON files, try to merge objects
                python3 - "$file" <<'EOF'
import sys
import json
import re

file_path = sys.argv[1]
try:
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract the conflicted sections
    ours_match = re.search(r'<<<<<<< HEAD\n(.*?)\n=======', content, re.DOTALL)
    theirs_match = re.search(r'=======\n(.*?)\n>>>>>>> ', content, re.DOTALL)
    
    if ours_match and theirs_match:
        try:
            ours = json.loads(ours_match.group(1))
            theirs = json.loads(theirs_match.group(1))
            
            # Simple merge strategy - combine both
            if isinstance(ours, dict) and isinstance(theirs, dict):
                merged = {**ours, **theirs}
                # Remove conflict markers and replace with merged content
                clean_content = re.sub(r'<<<<<<< HEAD.*?>>>>>>> .*?\n', 
                                      json.dumps(merged, indent=2), 
                                      content, flags=re.DOTALL)
                with open(file_path, 'w') as f:
                    f.write(clean_content)
                print(f"Automatically resolved JSON conflict in {file_path}")
            else:
                print(f"Cannot auto-merge non-dict JSON in {file_path}")
        except json.JSONDecodeError:
            print(f"Invalid JSON in conflict sections of {file_path}")
except Exception as e:
    print(f"Error processing {file_path}: {e}")
EOF
                ;;
            *.md)
                # For markdown, keep both versions with headers
                log_info "Keeping both versions for markdown file: $file"
                ;;
            *)
                # For other files, we'll need manual resolution
                log_warning "Cannot auto-resolve: $file"
                ;;
        esac
    done
    
    # Check if all conflicts were resolved
    if [ -z "$(git diff --name-only --diff-filter=U)" ]; then
        log_success "All conflicts resolved automatically!"
        return 0
    else:
        return 1
    fi
}

# Function to analyze and merge a single branch
merge_agent_branch() {
    local branch=$1
    local branch_name=$(echo "$branch" | sed 's|origin/||')
    
    log_info "Processing branch: $branch_name"
    
    # Create a temporary merge branch
    local temp_branch="temp-merge-$(date +%s)"
    git checkout -b "$temp_branch" "$MAIN_BRANCH" 2>/dev/null
    
    # Attempt merge
    if git merge --no-commit --no-ff "$branch" 2>/dev/null; then
        # Check for any changes
        if [ -n "$(git status --porcelain)" ]; then
            log_success "Clean merge possible for $branch_name"
            
            # Commit the merge
            git commit -m "Merge $branch_name - Automated parallel agent integration"
            
            # Fast-forward main branch
            git checkout "$MAIN_BRANCH"
            git merge --ff-only "$temp_branch"
            
            create_merge_report "$branch_name" "success" "Clean merge completed"
        else:
            log_info "No changes in $branch_name"
            create_merge_report "$branch_name" "no_changes" "Branch contains no new changes"
        fi
    else
        log_warning "Conflicts detected in $branch_name"
        
        # Try automated resolution
        if resolve_conflicts; then
            git add -A
            git commit -m "Merge $branch_name with automated conflict resolution"
            
            # Fast-forward main branch
            git checkout "$MAIN_BRANCH"
            git merge --ff-only "$temp_branch"
            
            create_merge_report "$branch_name" "success" "Merged with automated conflict resolution"
        else:
            log_error "Manual intervention required for $branch_name"
            
            # Save conflict information
            local conflicts=$(git diff --name-only --diff-filter=U | tr '\n' ',')
            create_merge_report "$branch_name" "conflict" "Manual resolution required for: $conflicts"
            
            # Abort the merge
            git merge --abort
        fi
    fi
    
    # Cleanup
    git checkout "$MAIN_BRANCH" 2>/dev/null
    git branch -D "$temp_branch" 2>/dev/null || true
}

# Main execution
main() {
    log_info "Starting parallel agent work integration..."
    
    # Ensure we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository!"
        exit 1
    fi
    
    # Fetch latest changes
    log_info "Fetching latest changes..."
    git fetch --all --prune
    
    # Store current branch
    CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "HEAD")
    
    # Switch to main branch
    git checkout "$MAIN_BRANCH"
    git pull origin "$MAIN_BRANCH"
    
    # Analyze shared memory
    analyze_shared_memory
    
    # Find all agent branches
    AGENT_BRANCHES=$(git branch -r | grep "${AGENT_BRANCH_PREFIX}" | grep -v HEAD || true)
    
    if [ -z "$AGENT_BRANCHES" ]; then
        log_warning "No agent branches found with prefix: ${AGENT_BRANCH_PREFIX}"
        exit 0
    fi
    
    log_info "Found agent branches:"
    echo "$AGENT_BRANCHES" | sed 's/^/  - /'
    
    # Process each branch
    echo "$AGENT_BRANCHES" | while read -r branch; do
        merge_agent_branch "$branch"
    done
    
    # Generate summary report
    log_info "Generating summary report..."
    
    cat > "$REPORTS_DIR/merge_summary_$(date +%Y%m%d_%H%M%S).txt" <<EOF
Parallel Agent Merge Summary
===========================
Date: $(date)
Main Branch: $MAIN_BRANCH

Processed Branches:
$AGENT_BRANCHES

Reports Generated:
$(ls -1 "$REPORTS_DIR"/merge_*.json 2>/dev/null | tail -10)

Current Status:
$(git status --short)
EOF
    
    # Return to original branch
    if [ "$CURRENT_BRANCH" != "$MAIN_BRANCH" ]; then
        git checkout "$CURRENT_BRANCH" 2>/dev/null || true
    fi
    
    log_success "Parallel agent work integration completed!"
    log_info "Check $REPORTS_DIR for detailed merge reports"
}

# Run main function
main "$@"