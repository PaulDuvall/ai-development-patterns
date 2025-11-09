#!/bin/bash
# automated-review.sh - Complete parallel agent review and integration
# Part of AI Review Automation experimental pattern

set -euo pipefail

# Configuration
WORKSPACE_DIR="workspace"
MERGED_DIR="$WORKSPACE_DIR/merged"
CONFIG_FILE="review_config.yaml"
LOG_FILE="review_automation.log"

# Colors for output  
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    echo -e "${RED}❌ ERROR: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

# Success message
success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

# Warning message  
warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
    log "WARNING: $1"
}

# Info message
info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
    log "INFO: $1"
}

# Usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

AI Review Automation for Parallel Agent Outputs

OPTIONS:
    --workspace DIR     Agent workspace directory (default: workspace)
    --config FILE       Review configuration file (default: review_config.yaml)
    --dry-run          Analyze conflicts without merging
    --force-merge      Skip conflict resolution approval
    --quality-only     Run only quality gates, skip conflict detection
    --help             Show this help message

EXAMPLES:
    $0                                  # Run full automated review
    $0 --dry-run                       # Analyze without merging
    $0 --workspace custom/workspace    # Use custom workspace
    $0 --quality-only                  # Skip conflict detection

EOF
}

# Parse command line arguments
WORKSPACE_DIR="workspace"
DRY_RUN=false
FORCE_MERGE=false
QUALITY_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --workspace)
            WORKSPACE_DIR="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force-merge)
            FORCE_MERGE=true
            shift
            ;;
        --quality-only)
            QUALITY_ONLY=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            error_exit "Unknown option: $1"
            ;;
    esac
done

# Main execution
main() {
    log "=== AI Review Automation Started ==="
    
    # Validate environment
    validate_environment
    
    if [[ "$QUALITY_ONLY" == false ]]; then
        # Step 1: Detect conflicts between agent outputs
        info "Scanning for conflicts across agent workspaces..."
        detect_conflicts
    fi
    
    # Step 2: Run quality gates and validation
    info "Running quality gates on combined outputs..."
    run_quality_gates
    
    # Step 3: Auto-merge or request human review
    if [[ "$DRY_RUN" == false ]]; then
        info "Executing merge strategy..."
        execute_merge_strategy
    else
        info "Dry run complete - no changes made"
    fi
    
    log "=== AI Review Automation Complete ==="
}

# Validate environment and dependencies
validate_environment() {
    info "Validating environment..."
    
    # Check if workspace exists
    if [[ ! -d "$WORKSPACE_DIR" ]]; then
        error_exit "Workspace directory not found: $WORKSPACE_DIR"
    fi
    
    # Check for agent workspaces
    local agent_dirs=($(find "$WORKSPACE_DIR" -maxdepth 1 -name "agent-*" -type d 2>/dev/null))
    if [[ ${#agent_dirs[@]} -eq 0 ]]; then
        error_exit "No agent workspaces found in $WORKSPACE_DIR"
    fi
    
    info "Found ${#agent_dirs[@]} agent workspaces"
    
    # Check dependencies
    command -v python3 >/dev/null 2>&1 || error_exit "python3 is required but not installed"
    command -v git >/dev/null 2>&1 || error_exit "git is required but not installed"
    
    # Create log file
    touch "$LOG_FILE" || error_exit "Cannot create log file: $LOG_FILE"
    
    success "Environment validation complete"
}

# Detect conflicts between agent outputs
detect_conflicts() {
    info "Analyzing parallel agent outputs for integration issues..."
    
    # Use AI to analyze conflicts
    local conflict_analysis
    conflict_analysis=$(python3 << 'EOF'
import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict

def analyze_agent_outputs(workspace_dir):
    """Analyze agent outputs for potential conflicts."""
    
    conflicts = []
    file_map = defaultdict(list)
    
    # Scan all agent workspaces
    agent_dirs = [d for d in Path(workspace_dir).iterdir() 
                  if d.is_dir() and d.name.startswith('agent-')]
    
    print(f"Analyzing {len(agent_dirs)} agent workspaces...")
    
    # Build file mapping
    for agent_dir in agent_dirs:
        agent_name = agent_dir.name
        for file_path in agent_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = file_path.relative_to(agent_dir)
                file_info = {
                    'agent': agent_name,
                    'path': str(file_path),
                    'relative_path': str(relative_path),
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime
                }
                
                # Calculate file hash for content comparison
                try:
                    with open(file_path, 'rb') as f:
                        file_info['hash'] = hashlib.md5(f.read()).hexdigest()
                except:
                    file_info['hash'] = 'unreadable'
                    
                file_map[str(relative_path)].append(file_info)
    
    # Detect conflicts
    for rel_path, file_list in file_map.items():
        if len(file_list) > 1:
            # Multiple agents modified the same relative path
            hashes = set(f['hash'] for f in file_list)
            
            if len(hashes) > 1:  # Different content
                conflict = {
                    'type': 'file_conflict',
                    'path': rel_path,
                    'agents': [f['agent'] for f in file_list],
                    'severity': 'high' if rel_path.endswith(('.py', '.js', '.ts', '.java')) else 'medium',
                    'details': f"File {rel_path} modified by {len(file_list)} agents with different content"
                }
                conflicts.append(conflict)
    
    # Check for potential API contract mismatches
    api_files = []
    for rel_path, file_list in file_map.items():
        if any(keyword in rel_path.lower() for keyword in ['api', 'endpoint', 'route', 'service']):
            api_files.extend(file_list)
    
    if len(api_files) > 1:
        # Simple heuristic for API contract analysis
        agents_with_apis = set(f['agent'] for f in api_files)
        if len(agents_with_apis) > 1:
            conflict = {
                'type': 'api_contract_mismatch',
                'agents': list(agents_with_apis),
                'severity': 'critical',
                'details': f"Multiple agents ({', '.join(agents_with_apis)}) created API definitions - potential contract mismatch"
            }
            conflicts.append(conflict)
    
    # Output results
    result = {
        'conflicts_found': len(conflicts),
        'conflicts': conflicts,
        'agents_analyzed': len(agent_dirs),
        'total_files': sum(len(files) for files in file_map.values())
    }
    
    return result

# Run analysis
import sys
workspace = sys.argv[1] if len(sys.argv) > 1 else "workspace"
result = analyze_agent_outputs(workspace)
print(json.dumps(result, indent=2))
EOF
"$WORKSPACE_DIR")

    # Parse conflict analysis results
    local conflicts_found
    conflicts_found=$(echo "$conflict_analysis" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['conflicts_found'])")
    
    if [[ "$conflicts_found" -gt 0 ]]; then
        warning "Found $conflicts_found conflicts between agent outputs"
        echo "$conflict_analysis" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for conflict in data['conflicts']:
    severity = conflict['severity'].upper()
    print(f'  [{severity}] {conflict[\"type\"]}: {conflict[\"details\"]}')
    print(f'    Agents involved: {\"  \".join(conflict[\"agents\"])}')
    print()
"
        
        if [[ "$FORCE_MERGE" == false ]]; then
            echo -e "${YELLOW}Conflicts detected. Resolution required before merge.${NC}"
            # Store conflict details for later processing
            echo "$conflict_analysis" > "$WORKSPACE_DIR/conflict_analysis.json"
        fi
    else
        success "No conflicts detected between agent outputs"
    fi
}

# Run quality gates and validation
run_quality_gates() {
    info "Validating merged agent outputs against quality standards..."
    
    # Create temporary merged workspace for quality validation
    local temp_merged="$WORKSPACE_DIR/temp_merged"
    mkdir -p "$temp_merged"
    
    # Merge agent outputs (simple file copy for validation)
    for agent_dir in "$WORKSPACE_DIR"/agent-*; do
        if [[ -d "$agent_dir" ]]; then
            info "Merging outputs from $(basename "$agent_dir")"
            # Use rsync to merge, existing files kept (no overwrite for validation)
            rsync -av --ignore-existing "$agent_dir/" "$temp_merged/" || true
        fi
    done
    
    # Run quality validation
    local quality_results
    quality_results=$(python3 << 'EOF'
import os
import subprocess
import json
from pathlib import Path

def run_quality_checks(merged_dir):
    """Run comprehensive quality checks on merged outputs."""
    
    results = {
        'syntax_validation': {'passed': 0, 'failed': 0, 'errors': []},
        'security_scan': {'passed': True, 'issues': []},
        'test_coverage': {'percentage': 0, 'threshold_met': False},
        'integration_tests': {'passed': 0, 'failed': 0, 'errors': []},
        'overall_status': 'unknown'
    }
    
    merged_path = Path(merged_dir)
    
    # 1. Syntax validation
    print("Running syntax validation...")
    python_files = list(merged_path.rglob('*.py'))
    js_files = list(merged_path.rglob('*.js'))
    ts_files = list(merged_path.rglob('*.ts'))
    
    for py_file in python_files:
        try:
            result = subprocess.run(['python3', '-m', 'py_compile', str(py_file)], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                results['syntax_validation']['passed'] += 1
            else:
                results['syntax_validation']['failed'] += 1
                results['syntax_validation']['errors'].append({
                    'file': str(py_file),
                    'error': result.stderr.strip()
                })
        except Exception as e:
            results['syntax_validation']['errors'].append({
                'file': str(py_file),
                'error': f"Validation failed: {str(e)}"
            })
    
    # 2. Security scan (simplified - check for common issues)
    print("Running security scan...")
    security_issues = []
    
    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                content = f.read()
                # Check for common security issues
                if 'password' in content.lower() and ('=' in content or ':' in content):
                    if 'hardcoded' in content.lower() or '"' in content or "'" in content:
                        security_issues.append({
                            'file': str(py_file),
                            'issue': 'Potential hardcoded password',
                            'severity': 'high'
                        })
                
                if 'eval(' in content or 'exec(' in content:
                    security_issues.append({
                        'file': str(py_file),
                        'issue': 'Dynamic code execution detected',
                        'severity': 'high'
                    })
        except Exception:
            pass
    
    results['security_scan']['issues'] = security_issues
    results['security_scan']['passed'] = len(security_issues) == 0
    
    # 3. Test coverage (simplified)
    print("Checking test coverage...")
    test_files = list(merged_path.rglob('test_*.py')) + list(merged_path.rglob('*_test.py'))
    total_py_files = len(python_files)
    
    if total_py_files > 0:
        coverage_percentage = (len(test_files) / total_py_files) * 100
        results['test_coverage']['percentage'] = round(coverage_percentage, 1)
        results['test_coverage']['threshold_met'] = coverage_percentage >= 80
    
    # 4. Integration tests (check if tests can be imported)
    print("Validating integration tests...")
    integration_passed = 0
    integration_failed = 0
    
    for test_file in test_files:
        try:
            # Try to import the test file
            result = subprocess.run(['python3', '-c', f'import sys; sys.path.append("{merged_path}"); import {test_file.stem}'], 
                                  capture_output=True, text=True, cwd=str(merged_path))
            if result.returncode == 0:
                integration_passed += 1
            else:
                integration_failed += 1
                results['integration_tests']['errors'].append({
                    'file': str(test_file),
                    'error': result.stderr.strip()
                })
        except Exception as e:
            integration_failed += 1
            results['integration_tests']['errors'].append({
                'file': str(test_file),
                'error': str(e)
            })
    
    results['integration_tests']['passed'] = integration_passed
    results['integration_tests']['failed'] = integration_failed
    
    # Overall status determination
    quality_issues = (
        results['syntax_validation']['failed'] +
        len(results['security_scan']['issues']) +
        results['integration_tests']['failed'] +
        (0 if results['test_coverage']['threshold_met'] else 1)
    )
    
    if quality_issues == 0:
        results['overall_status'] = 'passed'
    elif quality_issues <= 2:
        results['overall_status'] = 'warning'
    else:
        results['overall_status'] = 'failed'
    
    return results

# Run quality checks
import sys
merged_dir = sys.argv[1] if len(sys.argv) > 1 else "workspace/temp_merged"
results = run_quality_checks(merged_dir)
print(json.dumps(results, indent=2))
EOF
"$temp_merged")

    # Parse quality results
    local overall_status
    overall_status=$(echo "$quality_results" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['overall_status'])")
    
    # Display quality results
    echo "$quality_results" | python3 -c "
import sys, json
data = json.load(sys.stdin)

print('Quality Gate Results:')
print('====================')

# Syntax validation
syntax = data['syntax_validation']
if syntax['failed'] == 0:
    print(f'✅ Syntax Validation: {syntax[\"passed\"]} files passed')
else:
    print(f'❌ Syntax Validation: {syntax[\"failed\"]} files failed, {syntax[\"passed\"]} passed')
    for error in syntax['errors'][:3]:  # Show first 3 errors
        print(f'   - {error[\"file\"]}: {error[\"error\"]}')
    if len(syntax['errors']) > 3:
        print(f'   ... and {len(syntax[\"errors\"]) - 3} more errors')

# Security scan
security = data['security_scan']
if security['passed']:
    print('✅ Security Scan: No issues found')
else:
    print(f'❌ Security Scan: {len(security[\"issues\"])} issues found')
    for issue in security['issues'][:3]:
        print(f'   - {issue[\"file\"]}: {issue[\"issue\"]} ({issue[\"severity\"]})')

# Test coverage
coverage = data['test_coverage']
if coverage['threshold_met']:
    print(f'✅ Test Coverage: {coverage[\"percentage\"]}% (meets 80% threshold)')
else:
    print(f'⚠️ Test Coverage: {coverage[\"percentage\"]}% (below 80% threshold)')

# Integration tests
integration = data['integration_tests']
if integration['failed'] == 0:
    print(f'✅ Integration Tests: {integration[\"passed\"]} tests validated')
else:
    print(f'❌ Integration Tests: {integration[\"failed\"]} failed, {integration[\"passed\"]} passed')

print(f'\\nOverall Status: {data[\"overall_status\"].upper()}')
"
    
    # Store quality results
    echo "$quality_results" > "$WORKSPACE_DIR/quality_results.json"
    
    # Clean up temporary directory
    rm -rf "$temp_merged"
    
    case "$overall_status" in
        "passed")
            success "All quality gates passed"
            return 0
            ;;
        "warning")
            warning "Quality gates passed with warnings"
            return 1
            ;;
        "failed")
            error_exit "Quality gates failed - manual review required"
            ;;
        *)
            error_exit "Unknown quality gate status: $overall_status"
            ;;
    esac
}

# Execute merge strategy based on quality results
execute_merge_strategy() {
    local quality_status=0
    local conflicts_exist=false
    
    # Check quality results
    if [[ -f "$WORKSPACE_DIR/quality_results.json" ]]; then
        local overall_status
        overall_status=$(python3 -c "import json; data=json.load(open('$WORKSPACE_DIR/quality_results.json')); print(data['overall_status'])")
        
        if [[ "$overall_status" == "failed" ]]; then
            quality_status=1
        fi
    fi
    
    # Check conflict results
    if [[ -f "$WORKSPACE_DIR/conflict_analysis.json" ]]; then
        local conflicts_found
        conflicts_found=$(python3 -c "import json; data=json.load(open('$WORKSPACE_DIR/conflict_analysis.json')); print(data['conflicts_found'])")
        
        if [[ "$conflicts_found" -gt 0 ]]; then
            conflicts_exist=true
        fi
    fi
    
    # Determine merge strategy
    if [[ $quality_status -eq 0 && "$conflicts_exist" == false ]]; then
        info "Proceeding with automatic merge - all checks passed"
        execute_automatic_merge
    elif [[ "$FORCE_MERGE" == true ]]; then
        warning "Force merge requested - bypassing quality/conflict checks"
        execute_automatic_merge
    else
        warning "Manual review required - generating review report"
        generate_review_report
        return 1
    fi
}

# Execute automatic merge of agent outputs
execute_automatic_merge() {
    info "Executing automatic merge of agent outputs..."
    
    # Create merged directory
    mkdir -p "$MERGED_DIR"
    
    # Merge agent outputs with conflict resolution
    for agent_dir in "$WORKSPACE_DIR"/agent-*; do
        if [[ -d "$agent_dir" ]]; then
            local agent_name
            agent_name=$(basename "$agent_dir")
            info "Merging outputs from $agent_name"
            
            # Use rsync with existing file preservation for safety
            rsync -av --ignore-existing "$agent_dir/" "$MERGED_DIR/" || {
                error_exit "Failed to merge outputs from $agent_name"
            }
        fi
    done
    
    # Run integration validation
    info "Running integration validation..."
    if validate_merged_integration; then
        success "Integration validation passed"
        
        # Copy merged results to source
        info "Copying merged results to source directory..."
        if [[ -d "src" ]]; then
            rsync -av "$MERGED_DIR/" src/ || error_exit "Failed to copy merged results"
        fi
        
        # Cleanup agent workspaces
        info "Cleaning up agent workspaces..."
        rm -rf "$WORKSPACE_DIR"/agent-*
        
        success "Automatic merge completed successfully"
        
        # Generate success report
        generate_success_report
        
    else
        error_exit "Integration validation failed - manual review required"
    fi
}

# Validate merged integration
validate_merged_integration() {
    info "Validating merged integration..."
    
    cd "$MERGED_DIR" || return 1
    
    # Run basic integration tests
    if [[ -f "requirements.txt" ]]; then
        info "Installing Python dependencies..."
        python3 -m pip install -r requirements.txt --quiet || return 1
    fi
    
    if [[ -f "package.json" ]]; then
        info "Installing Node.js dependencies..."
        npm install --silent || return 1
    fi
    
    # Run tests if they exist
    if find . -name "test_*.py" -o -name "*_test.py" | grep -q .; then
        info "Running Python tests..."
        python3 -m pytest -v --tb=short || return 1
    fi
    
    if [[ -f "package.json" ]] && grep -q '"test"' package.json; then
        info "Running Node.js tests..."
        npm test || return 1
    fi
    
    cd - > /dev/null
    
    return 0
}

# Generate review report for manual intervention
generate_review_report() {
    info "Generating human-readable review report..."
    
    local report_file="$WORKSPACE_DIR/review_report.md"
    
cat > "$report_file" << 'EOF'
# AI Review Automation Report

## Executive Summary

This report details the automated review of parallel agent outputs and identifies issues requiring human attention.

EOF

    # Add conflict information if exists
    if [[ -f "$WORKSPACE_DIR/conflict_analysis.json" ]]; then
        echo "## Conflict Analysis" >> "$report_file"
        echo "" >> "$report_file"
        python3 -c "
import json
data = json.load(open('$WORKSPACE_DIR/conflict_analysis.json'))
print(f'**Conflicts Found:** {data[\"conflicts_found\"]}')
print(f'**Agents Analyzed:** {data[\"agents_analyzed\"]}')
print(f'**Total Files:** {data[\"total_files\"]}')
print()

for conflict in data['conflicts']:
    print(f'### {conflict[\"type\"].replace(\"_\", \" \").title()}')
    print(f'- **Severity:** {conflict[\"severity\"].upper()}')
    print(f'- **Agents Involved:** {\" \".join(conflict[\"agents\"])}')
    print(f'- **Details:** {conflict[\"details\"]}')
    print()
" >> "$report_file"
    fi
    
    # Add quality results if exists
    if [[ -f "$WORKSPACE_DIR/quality_results.json" ]]; then
        echo "## Quality Gate Results" >> "$report_file"
        echo "" >> "$report_file"
        python3 -c "
import json
data = json.load(open('$WORKSPACE_DIR/quality_results.json'))

print(f'**Overall Status:** {data[\"overall_status\"].upper()}')
print()

syntax = data['syntax_validation']
print(f'**Syntax Validation:** {syntax[\"passed\"]} passed, {syntax[\"failed\"]} failed')

security = data['security_scan']
print(f'**Security Scan:** {\"PASSED\" if security[\"passed\"] else \"FAILED\"} ({len(security[\"issues\"])} issues)')

coverage = data['test_coverage']
print(f'**Test Coverage:** {coverage[\"percentage\"]}% ({\"meets\" if coverage[\"threshold_met\"] else \"below\"} 80% threshold)')

integration = data['integration_tests']
print(f'**Integration Tests:** {integration[\"passed\"]} passed, {integration[\"failed\"]} failed')
print()

if syntax['errors']:
    print('### Syntax Errors')
    for error in syntax['errors'][:5]:
        print(f'- `{error[\"file\"]}`: {error[\"error\"]}')
    print()

if security['issues']:
    print('### Security Issues')
    for issue in security['issues']:
        print(f'- `{issue[\"file\"]}`: {issue[\"issue\"]} ({issue[\"severity\"]})')
    print()
" >> "$report_file"
    fi
    
    # Add recommendations
cat >> "$report_file" << 'EOF'
## Recommended Actions

1. **Review Conflicts**: Manually resolve file conflicts between agents
2. **Address Quality Issues**: Fix syntax errors and security vulnerabilities
3. **Improve Test Coverage**: Add tests to meet 80% coverage threshold
4. **Validate Integration**: Ensure merged components work together properly

## Next Steps

1. Review this report with the development team
2. Assign conflict resolution tasks to appropriate developers
3. Address quality gate failures before attempting merge
4. Re-run automated review after manual fixes

---

*Report generated by AI Review Automation at $(date)*
EOF

    info "Review report generated: $report_file"
    
    # Display key recommendations
    echo -e "\n${YELLOW}📋 Manual Review Required${NC}"
    echo -e "${YELLOW}=========================${NC}"
    if [[ -f "$WORKSPACE_DIR/conflict_analysis.json" ]]; then
        local conflicts_found
        conflicts_found=$(python3 -c "import json; data=json.load(open('$WORKSPACE_DIR/conflict_analysis.json')); print(data['conflicts_found'])")
        echo -e "• Resolve $conflicts_found conflicts between agent outputs"
    fi
    
    if [[ -f "$WORKSPACE_DIR/quality_results.json" ]]; then
        echo -e "• Address quality gate failures identified in analysis"
    fi
    
    echo -e "• Review detailed report: $report_file"
    echo -e "• Re-run automation after manual fixes: $0"
}

# Generate success report
generate_success_report() {
    info "Generating success report..."
    
    local report_file="$WORKSPACE_DIR/success_report.md"
    
cat > "$report_file" << EOF
# AI Review Automation - Success Report

## Summary

✅ **Automated review and merge completed successfully**

- **Date:** $(date)
- **Agents Processed:** $(find "$WORKSPACE_DIR" -maxdepth 1 -name "agent-*" -type d 2>/dev/null | wc -l)
- **Quality Gates:** All passed
- **Conflicts:** None detected or successfully resolved
- **Integration Status:** Validated and working

## Merged Components

$(find "$MERGED_DIR" -type f -name "*.py" -o -name "*.js" -o -name "*.ts" 2>/dev/null | head -10 | sed 's/^/- /')

## Quality Metrics

EOF

    if [[ -f "$WORKSPACE_DIR/quality_results.json" ]]; then
        python3 -c "
import json
data = json.load(open('$WORKSPACE_DIR/quality_results.json'))

syntax = data['syntax_validation']
coverage = data['test_coverage']
security = data['security_scan']

print(f'- **Syntax Validation:** {syntax[\"passed\"]} files passed')
print(f'- **Test Coverage:** {coverage[\"percentage\"]}%')
print(f'- **Security Scan:** {\"Clean\" if security[\"passed\"] else \"Issues found\"}')
print(f'- **Integration Tests:** {data[\"integration_tests\"][\"passed\"]} passed')
" >> "$report_file"
    fi
    
cat >> "$report_file" << 'EOF'

## Next Steps

1. Review merged code in the source directory
2. Run full test suite to validate integration
3. Proceed with deployment pipeline
4. Monitor for any integration issues

---

*Report generated by AI Review Automation*
EOF

    success "Success report generated: $report_file"
}

# Execute main function
main "$@"