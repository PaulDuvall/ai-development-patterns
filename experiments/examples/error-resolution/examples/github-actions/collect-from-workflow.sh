#!/bin/bash
# collect-from-workflow.sh
# Collect comprehensive error context from GitHub Actions workflow run
#
# Usage: ./collect-from-workflow.sh <run-id>
# Example: ./collect-from-workflow.sh 18578261366

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <run-id>"
    echo "Example: $0 18578261366"
    exit 1
fi

RUN_ID=$1

echo "🔍 Collecting error context from workflow run $RUN_ID..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Fetch error logs
echo "  📋 Fetching error logs..."
gh run view "$RUN_ID" --log-failed > ci-error.log 2>&1 || {
    echo "❌ Failed to fetch workflow run logs"
    echo "Make sure you have access to the repository and run ID is correct"
    exit 1
}

# Get workflow info
echo "  📊 Fetching workflow info..."
gh run view "$RUN_ID" --json headBranch,headSha,event,status,conclusion,workflowName > workflow-info.json

# Extract failed jobs
echo "  💥 Extracting failed jobs..."
gh run view "$RUN_ID" --json jobs --jq '.jobs[] | select(.conclusion == "failure")' > failed-jobs.json

# Get recent commits
echo "  📝 Getting recent commits..."
BRANCH=$(jq -r '.headBranch' workflow-info.json)
git log --oneline -5 "$BRANCH" > recent-commits.txt 2>/dev/null || echo "[Unable to fetch git history]" > recent-commits.txt

# Get changed files
echo "  📁 Getting changed files..."
SHA=$(jq -r '.headSha' workflow-info.json)
git diff --name-only "$SHA~1" "$SHA" > changed-files.txt 2>/dev/null || echo "[Unable to fetch changed files]" > changed-files.txt

# Get workflow file
echo "  ⚙️  Getting workflow configuration..."
WORKFLOW_NAME=$(jq -r '.workflowName' workflow-info.json)
gh run view "$RUN_ID" --json workflowDatabaseId --jq '.workflowDatabaseId' | \
  xargs -I {} gh api repos/{owner}/{repo}/actions/workflows/{} --jq '.path' > workflow-path.txt 2>/dev/null || echo "[Unable to fetch workflow path]" > workflow-path.txt

# Compile comprehensive context
echo "  📄 Compiling context document..."
cat > .error-context.md << EOF
# GitHub Actions Failure Analysis

## Workflow Run Information

- **Run ID**: $RUN_ID
- **Workflow**: $(jq -r '.workflowName' workflow-info.json)
- **Branch**: $(jq -r '.headBranch' workflow-info.json)
- **Commit**: $(jq -r '.headSha' workflow-info.json)
- **Event**: $(jq -r '.event' workflow-info.json)
- **Status**: $(jq -r '.status' workflow-info.json)
- **Conclusion**: $(jq -r '.conclusion' workflow-info.json)

## Error Logs

\`\`\`
$(cat ci-error.log)
\`\`\`

## Failed Jobs

\`\`\`json
$(cat failed-jobs.json)
\`\`\`

## Recent Commits

\`\`\`
$(cat recent-commits.txt)
\`\`\`

## Changed Files

\`\`\`
$(cat changed-files.txt)
\`\`\`

## File Contents

$(while IFS= read -r file; do
    if [ -f "$file" ]; then
        echo "### $file"
        echo "\`\`\`"
        cat "$file"
        echo "\`\`\`"
        echo ""
    fi
done < changed-files.txt)

## Workflow Configuration

Workflow file: \`$(cat workflow-path.txt)\`

## Environment

- **Repository**: $(gh repo view --json nameWithOwner --jq '.nameWithOwner')
- **Run URL**: https://github.com/$(gh repo view --json nameWithOwner --jq '.nameWithOwner')/actions/runs/$RUN_ID

## Next Steps

Use AI to analyze this context:

\`\`\`bash
ai "Diagnose this GitHub Actions failure:

\$(cat .error-context.md)

Provide:
1. Root cause analysis
2. Specific fix commands
3. Prevention strategy (pre-commit hooks, local validation)"
\`\`\`

EOF

# Cleanup temporary files
rm -f ci-error.log workflow-info.json failed-jobs.json recent-commits.txt changed-files.txt workflow-path.txt

echo ""
echo "✅ Context collected successfully!"
echo "📄 Saved to: .error-context.md"
echo ""
echo "Next steps:"
echo "  1. Review: cat .error-context.md"
echo "  2. Analyze with AI: ai \"\$(cat .error-context.md)\""
echo "  3. Or use prompt template: cat ../../templates/ai-prompt-template.md"
