# CI Integration Examples for AI Issue Generation

This document provides detailed examples for integrating AI-generated issues with CI workflows, including file tracking, traceability, and automated reporting.

## Issue CI Requirements Template

### AI Prompt for CI Integration
```bash
ai "For each generated work item, include CI integration requirements:

Issue Requirements:
- Define files to be added, updated, or removed
- Specify test coverage requirements (unit, integration, e2e)
- Include CI pipeline validation steps
- Link implementation to verification criteria

CI Report Integration:
- Include issue references in commit messages
- Generate CI reports that link back to originating issues
- Track file changes against issue scope
- Validate test coverage meets issue requirements

File Tracking Format:
Files Added: [list new files with purpose]
Files Updated: [list modified files with changes]
Files Removed: [list deleted files with reason]
Test Coverage: [minimum coverage % and test types]
CI Validation: [pipeline steps that must pass]"
```

## Issue-to-Implementation Traceability

### Complete Traceability Structure
```json
{
  "issue_id": "AUTH-002",
  "title": "Password validation service",
  "epic_id": "AUTH-001",
  "files": {
    "added": [
      {
        "path": "src/auth/validators.py",
        "purpose": "Core password validation logic with complexity rules"
      },
      {
        "path": "tests/test_validators.py",
        "purpose": "Unit tests for password validation functions"
      },
      {
        "path": "tests/integration/test_auth_flow.py",
        "purpose": "Integration tests for complete authentication flow"
      }
    ],
    "updated": [
      {
        "path": "src/auth/__init__.py",
        "changes": "Export new validator functions"
      },
      {
        "path": "requirements.txt",
        "changes": "Add passlib dependency for password hashing"
      },
      {
        "path": "src/auth/models.py",
        "changes": "Add password_last_changed field to User model"
      }
    ],
    "removed": []
  },
  "ci_requirements": {
    "test_coverage": {
      "minimum": "95%",
      "types": ["unit", "integration"],
      "critical_paths": ["password_validation", "security_checks"]
    },
    "pipeline_steps": [
      "lint",
      "unit-tests",
      "integration-tests",
      "security-scan",
      "coverage-check"
    ],
    "quality_gates": [
      "sonarqube-analysis",
      "security-scan-pass",
      "no-high-vulnerabilities"
    ],
    "performance_requirements": {
      "password_validation": "<100ms per validation",
      "memory_usage": "<50MB during test suite"
    }
  },
  "verification": {
    "commit_pattern": "AUTH-002: implement password validation service",
    "ci_report_links": [
      "build-{build_id}",
      "coverage-{build_id}",
      "security-{build_id}"
    ],
    "acceptance_validation": [
      "All unit tests pass",
      "Coverage >95%",
      "Security scan clean",
      "Integration tests pass",
      "Performance benchmarks met"
    ]
  }
}
```

## CI Report Linking Strategy

### Commit Message Format
```bash
# Standard commit format for AI-generated issues
git commit -m "AUTH-002: implement password validation service

Implement core password validation with complexity rules:
- Add password strength validation (8+ chars, mixed case, numbers, symbols)
- Implement rate limiting for failed validation attempts
- Add integration with authentication middleware
- Include comprehensive test coverage

Files changed per issue AUTH-002:
- Added: src/auth/validators.py, tests/test_validators.py, tests/integration/test_auth_flow.py
- Updated: src/auth/__init__.py, requirements.txt, src/auth/models.py

Test Coverage: 97% (target: 95%)
CI Pipeline: All checks passed
Security Scan: Clean

Closes: AUTH-002
Epic: AUTH-001
CI-Report: Available at https://ci.example.com/builds/AUTH-002-{build_id}
Coverage-Report: https://coverage.example.com/AUTH-002-{build_id}"
```

### Automated CI Report Generation
```yaml
# GitHub Actions example for linking issues to CI reports
name: CI with Issue Tracking

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-and-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Extract Issue ID from commit
        id: issue
        run: |
          ISSUE_ID=$(git log -1 --pretty=%B | grep -oP '(?<=^)[A-Z]+-\d+(?=:)' || echo "")
          echo "issue_id=$ISSUE_ID" >> $GITHUB_OUTPUT

      - name: Run Tests with Coverage
        run: |
          pytest --cov=src --cov-report=html --cov-report=json

      - name: Security Scan
        run: |
          bandit -r src/ -f json -o security-report.json

      - name: Update Issue with CI Results
        if: steps.issue.outputs.issue_id != ''
        env:
          ISSUE_ID: ${{ steps.issue.outputs.issue_id }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Post CI results as comment on the issue
          gh issue comment $ISSUE_ID --body "
          ## CI Results for Build #${{ github.run_number }}

          **Test Coverage**: $(jq -r '.totals.percent_covered' coverage.json)%
          **Security Scan**: $([ -s security-report.json ] && echo 'Issues Found' || echo 'Clean')
          **Build Status**: ✅ Passed

          **Reports**:
          - [Coverage Report](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
          - [Security Report](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})

          **Files Changed** (per issue scope):
          $(git diff --name-only HEAD~1)
          "
```

## File Change Validation

### Scope Validation Script
```python
#!/usr/bin/env python3
"""
Validate that file changes match issue scope requirements
"""
import json
import subprocess
import sys

def validate_file_changes(issue_id):
    # Load issue requirements from tracking file
    with open(f'issues/{issue_id}.json', 'r') as f:
        issue_data = json.load(f)

    # Get actual changed files from git
    result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'],
                          capture_output=True, text=True)
    actual_files = set(result.stdout.strip().split('\n'))

    # Expected files from issue requirements
    expected_added = set(f['path'] for f in issue_data['files']['added'])
    expected_updated = set(f['path'] for f in issue_data['files']['updated'])
    expected_files = expected_added | expected_updated

    # Validate scope
    unexpected_files = actual_files - expected_files
    missing_files = expected_files - actual_files

    if unexpected_files:
        print(f"❌ Unexpected files changed: {unexpected_files}")
        return False

    if missing_files:
        print(f"⚠️ Expected files not changed: {missing_files}")

    print(f"✅ File changes match issue {issue_id} scope")
    return True

if __name__ == "__main__":
    issue_id = sys.argv[1] if len(sys.argv) > 1 else "AUTH-002"
    valid = validate_file_changes(issue_id)
    sys.exit(0 if valid else 1)
```

## Coverage Validation

### Test Coverage Enforcement
```bash
#!/bin/bash
# Validate test coverage meets issue requirements

ISSUE_ID="$1"
ISSUE_FILE="issues/${ISSUE_ID}.json"

if [ ! -f "$ISSUE_FILE" ]; then
    echo "❌ Issue file not found: $ISSUE_FILE"
    exit 1
fi

# Extract required coverage from issue
REQUIRED_COVERAGE=$(jq -r '.ci_requirements.test_coverage.minimum' "$ISSUE_FILE" | sed 's/%//')

# Get actual coverage
ACTUAL_COVERAGE=$(pytest --cov=src --cov-report=json --quiet | jq -r '.totals.percent_covered')

# Validate coverage
if (( $(echo "$ACTUAL_COVERAGE >= $REQUIRED_COVERAGE" | bc -l) )); then
    echo "✅ Coverage $ACTUAL_COVERAGE% meets requirement $REQUIRED_COVERAGE%"
    exit 0
else
    echo "❌ Coverage $ACTUAL_COVERAGE% below requirement $REQUIRED_COVERAGE%"
    exit 1
fi
```

## Integration with Issue Trackers

### GitHub Issues Integration
```python
# Update GitHub issue with CI results
import requests
import json
import os

def update_issue_with_ci_results(issue_number, ci_results):
    github_token = os.environ['GITHUB_TOKEN']
    repo = os.environ['GITHUB_REPOSITORY']

    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    comment_body = f"""
## CI Results - Build #{ci_results['build_id']}

**Status**: {'✅ Passed' if ci_results['success'] else '❌ Failed'}
**Test Coverage**: {ci_results['coverage']}%
**Security Scan**: {ci_results['security_status']}

**Files Changed**:
{chr(10).join(f"- {f}" for f in ci_results['files_changed'])}

**Reports**:
- [Build Log]({ci_results['build_url']})
- [Coverage Report]({ci_results['coverage_url']})
- [Security Report]({ci_results['security_url']})
"""

    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    response = requests.post(url, headers=headers, json={'body': comment_body})

    return response.status_code == 201
```

This comprehensive CI integration ensures that AI-generated issues maintain full traceability from requirements through implementation to deployment.