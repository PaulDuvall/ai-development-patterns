#!/bin/bash
# Script to rename example directories to match new pattern names using git mv

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "Renaming example directories..."

# Main examples
echo "Renaming main example directories..."

cd "$REPO_ROOT"

# Use git mv for proper tracking
git mv examples/ai-context-persistence examples/context-persistence
git mv examples/ai-development-lifecycle examples/developer-lifecycle
git mv examples/ai-driven-refactoring examples/guided-refactoring
git mv examples/ai-driven-traceability examples/automated-traceability
git mv examples/ai-issue-generation examples/issue-generation
git mv examples/ai-plan-first-development examples/planned-implementation
git mv examples/ai-security-sandbox examples/security-sandbox
git mv examples/ai-tool-integration examples/tool-integration
git mv examples/atomic-task-decomposition examples/atomic-decomposition
git mv examples/observable-ai-development examples/observable-development
git mv examples/parallelized-ai-agents examples/parallel-agents
git mv examples/performance-baseline-management examples/baseline-management
git mv examples/policy-as-code-generation examples/policy-generation
git mv examples/rules-as-code examples/codified-rules
git mv examples/security-scanning-orchestration examples/security-orchestration
git mv examples/specification-driven-development examples/spec-driven-development

echo "  ✅ Renamed 16 main example directories"

# Experimental examples
echo "Renaming experimental example directories..."

git mv experiments/examples/ai-event-automation experiments/examples/event-automation
git mv experiments/examples/ai-guided-blue-green-deployment experiments/examples/deployment-synthesis
git mv experiments/examples/ai-review-automation experiments/examples/review-automation
git mv experiments/examples/ai-workflow-orchestration experiments/examples/workflow-orchestration
git mv experiments/examples/comprehensive-ai-testing-strategy experiments/examples/testing-orchestration
git mv experiments/examples/custom-ai-commands experiments/examples/custom-commands
git mv experiments/examples/dependency-upgrade-advisor experiments/examples/upgrade-advisor
git mv experiments/examples/drift-detection-remediation experiments/examples/drift-remediation
git mv experiments/examples/human-ai-handoff experiments/examples/handoff-protocols
git mv experiments/examples/incident-response-automation experiments/examples/incident-automation
git mv experiments/examples/technical-debt-forecasting experiments/examples/debt-forecasting

echo "  ✅ Renamed 11 experimental example directories"

echo ""
echo "✅ Example directory rename script completed successfully!"
echo "  Total directories renamed: 27"
