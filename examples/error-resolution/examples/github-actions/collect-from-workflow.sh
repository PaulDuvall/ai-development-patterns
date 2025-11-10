#!/bin/bash
# collect-from-workflow.sh
# Collect error context from GitHub Actions workflow run
#
# Usage: ./collect-from-workflow.sh <run-id>

set -e

[ -z "$1" ] && { echo "Usage: $0 <run-id>"; exit 1; }

RUN_ID=$1

command -v gh &> /dev/null || { echo "❌ Install GitHub CLI: https://cli.github.com/"; exit 1; }

echo "🔍 Collecting error context from workflow run $RUN_ID..."

# Fetch error logs and workflow info
gh run view "$RUN_ID" --log-failed > ci-error.log
gh run view "$RUN_ID" --json headBranch,headSha,workflowName > workflow.json

# Create context document
cat > .error-context.md << EOF
## Error Logs
\`\`\`
$(cat ci-error.log)
\`\`\`

## Recent Commits
\`\`\`
$(git log --oneline -5 $(jq -r '.headBranch' workflow.json))
\`\`\`

## Changed Files
\`\`\`
$(git diff --name-only $(jq -r '.headSha' workflow.json)~1 $(jq -r '.headSha' workflow.json))
\`\`\`
EOF

rm -f ci-error.log workflow.json

echo "✅ Context saved to .error-context.md"
echo "Next: ai \"\$(cat .error-context.md)\""
