# GitHub Actions Error Resolution Example

This example demonstrates how to use the Error Resolution pattern with GitHub Actions CI/CD failures.

## Overview

GitHub Actions provides rich error context through:
- Workflow run logs via `gh` CLI
- Job outputs and step failures
- Integration with git history and file changes

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Access to repository workflow runs
- Basic bash/shell scripting knowledge

## Quick Start

### 1. Fetch Error from GitHub Actions

```bash
# Get error from specific workflow run
gh run view RUN_ID --log-failed > ci-error.log

# Or get latest failed run
gh run list --status failure --limit 1 --json databaseId --jq '.[0].databaseId' | \
  xargs gh run view --log-failed > ci-error.log
```

### 2. Collect Context

```bash
# Use the collection script
./collect-from-workflow.sh RUN_ID
# Creates .error-context.md with full context
```

### 3. AI Diagnosis

```bash
ai "Diagnose this GitHub Actions failure:

$(cat .error-context.md)

Provide:
1. Root cause
2. Fix commands
3. How to test locally before pushing"
```

## Example: Real CI Failure

See [ci-failure-example.md](ci-failure-example.md) for a complete example of diagnosing and fixing:
- Terraform formatting issues
- Shellcheck warnings
- Validation failures

This example shows the actual error from workflow run 18578261366.

## Integration Script

The `collect-from-workflow.sh` script automates context collection:

```bash
#!/bin/bash
# Usage: ./collect-from-workflow.sh <run-id>

RUN_ID=$1

# Fetch error logs
gh run view $RUN_ID --log-failed > ci-error.log

# Get workflow info
gh run view $RUN_ID --json headBranch,headSha,event > workflow-info.json

# Extract failed jobs
gh run view $RUN_ID --json jobs --jq '.jobs[] | select(.conclusion == "failure")' > failed-jobs.json

# Get recent commits
BRANCH=$(jq -r '.headBranch' workflow-info.json)
git log --oneline -5 $BRANCH > recent-commits.txt

# Get changed files
SHA=$(jq -r '.headSha' workflow-info.json)
git diff --name-only $SHA~1 $SHA > changed-files.txt

# Compile context
cat > .error-context.md << EOF
# GitHub Actions Failure Analysis

## Workflow Run
- Run ID: $RUN_ID
- Branch: $(jq -r '.headBranch' workflow-info.json)
- Commit: $(jq -r '.headSha' workflow-info.json)
- Event: $(jq -r '.event' workflow-info.json)

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
$(cat changed-files.txt)

## File Contents
$(for file in $(cat changed-files.txt); do
    echo "### $file"
    echo "\`\`\`"
    cat $file 2>/dev/null || echo "[File not in working directory]"
    echo "\`\`\`"
done)
EOF

echo "✅ Context collected in .error-context.md"
echo "Next: Use AI to analyze the error"
```

## Common GitHub Actions Error Patterns

### Build Tool Failures
- Linting errors (eslint, flake8, shellcheck)
- Formatting issues (prettier, black, terraform fmt)
- Type checking failures (mypy, tsc)

### Test Failures
- Unit test failures
- Integration test failures
- End-to-end test timeouts

### Deployment Issues
- Permission errors
- Resource conflicts
- Configuration mismatches

### Workflow Configuration
- Invalid YAML syntax
- Missing secrets
- Incorrect job dependencies

## Tips for GitHub Actions Debugging

1. **Use workflow_dispatch**: Add manual trigger for testing fixes
```yaml
on:
  workflow_dispatch:
  push:
    branches: [main]
```

2. **Add debug logging**: Enable step debugging
```yaml
- name: Debug info
  run: |
    echo "::debug::Variable value: $MY_VAR"
```

3. **Run locally**: Use `act` to test workflows locally
```bash
act -j job-name
```

4. **Check runner environment**: Verify OS, tool versions
```yaml
- name: Environment info
  run: |
    uname -a
    node --version
    python --version
```

## Automated Issue Creation

Create GitHub issues automatically from failures:

```bash
# After AI diagnosis
gh issue create \
  --title "CI Failure: Run $RUN_ID" \
  --body-file ai-diagnosis.md \
  --label "ci-failure,automated" \
  --assignee @me
```

## Prevention Strategies

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    hooks:
      - id: terraform_fmt
  - repo: https://github.com/shellcheck-py/shellcheck-py
    hooks:
      - id: shellcheck
```

### Local Validation Script
```bash
#!/bin/bash
# run-validations.sh - Run same checks as CI

echo "Running terraform fmt..."
terraform fmt -check -recursive

echo "Running shellcheck..."
shellcheck scripts/*.sh

echo "Running tests..."
pytest tests/

echo "✅ All validations passed"
```

### Matrix Testing Locally
Test across multiple environments before pushing:

```bash
# Test with different versions
docker run --rm -v $(pwd):/workspace python:3.9 pytest
docker run --rm -v $(pwd):/workspace python:3.10 pytest
docker run --rm -v $(pwd):/workspace python:3.11 pytest
```

## See Also

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub Actions Debugging Guide](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/enabling-debug-logging)
- [Act - Run GitHub Actions Locally](https://github.com/nektos/act)
