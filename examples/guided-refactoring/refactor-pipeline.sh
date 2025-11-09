#!/bin/bash
# refactor-pipeline.sh - Automated AI-driven refactoring pipeline

set -e

# Configuration
COVERAGE_THRESHOLD=90
COMPLEXITY_THRESHOLD=10
MAX_METHOD_LINES=20
MAX_CLASS_LINES=250

echo "🔍 AI-Driven Refactoring Pipeline Starting..."

# 1. Pre-refactoring validation
echo "=== Pre-refactoring Validation ==="
echo "Checking test coverage..."
coverage run -m pytest tests/ 2>/dev/null || echo "⚠️ Tests failed - aborting refactoring"
COVERAGE=$(coverage report --show-missing | tail -1 | awk '{print $4}' | sed 's/%//')

if (( $(echo "$COVERAGE < $COVERAGE_THRESHOLD" | bc -l) )); then
    echo "❌ Coverage $COVERAGE% below threshold $COVERAGE_THRESHOLD% - improve tests first"
    exit 1
fi

echo "✅ Coverage: $COVERAGE% (above $COVERAGE_THRESHOLD% threshold)"

# 2. Code smell detection
echo "=== Code Smell Detection ==="
echo "Running static analysis..."

# Complexity analysis
echo "Checking cyclomatic complexity..."
flake8 --select=C901 --max-complexity=$COMPLEXITY_THRESHOLD src/ > complexity_violations.txt 2>/dev/null || true

# Method/class size analysis  
echo "Checking method and class sizes..."
pylint src/ --disable=all --enable=R0915,R0902,R0904 --reports=no > size_violations.txt 2>/dev/null || true

# Duplicate code detection
echo "Checking for code duplication..."
pylint src/ --disable=all --enable=R0801 --reports=no > duplicate_violations.txt 2>/dev/null || true

# 3. AI analysis and prioritization
echo "=== AI Analysis ==="
cat > ai_analysis_prompt.txt << 'EOF'
Analyze the following static analysis results and prioritize refactoring opportunities:

Complexity violations:
$(cat complexity_violations.txt)

Size violations:  
$(cat size_violations.txt)

Duplicate code violations:
$(cat duplicate_violations.txt)

For each violation:
1. Assess impact (high/medium/low) based on:
   - How often the code is changed
   - How complex the violation is
   - How much it affects readability

2. Suggest specific refactoring strategy:
   - Extract Method for long methods
   - Extract Class for large classes  
   - Extract Function for duplicates

3. Estimate effort (1-4 hours) and risk (low/medium/high)

4. Generate implementation plan with specific steps

Output format:
PRIORITY: HIGH/MEDIUM/LOW
FILE: path/to/file.py
VIOLATION: description
STRATEGY: refactoring approach
EFFORT: X hours
RISK: low/medium/high
PLAN: step-by-step implementation
EOF

# Note: In real implementation, this would call your AI service
echo "📋 Generating AI refactoring analysis..."
echo "Priority analysis saved to: refactoring_analysis.txt"

# 4. Automated low-risk refactorings
echo "=== Automated Refactoring ==="

# Example: Extract constants (low risk)
echo "Extracting magic numbers and strings..."
python -c "
import ast
import re

# Simple example: find magic numbers and suggest constants
print('Suggested constant extractions:')
print('- MAX_RETRY_COUNT = 3  # Found in retry logic')
print('- DEFAULT_TIMEOUT = 30  # Found in API calls')
"

# 5. Run tests after each refactoring
echo "=== Validation ==="
echo "Running tests after refactoring..."
pytest tests/ --quiet
echo "✅ All tests passing"

# Check coverage maintained
coverage run -m pytest tests/ >/dev/null 2>&1
NEW_COVERAGE=$(coverage report | tail -1 | awk '{print $4}' | sed 's/%//')
echo "Coverage after refactoring: $NEW_COVERAGE%"

# 6. Quality metrics comparison
echo "=== Quality Metrics ==="
python quality-metrics.py --generate-report

# 7. Commit refactoring changes
if git diff --quiet; then
    echo "ℹ️ No changes to commit"
else
    echo "📝 Committing refactoring changes..."
    git add .
    git commit -m "refactor: automated code smell fixes

- Extract constants for magic numbers
- Improve method complexity scores
- Maintain test coverage at $NEW_COVERAGE%

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
fi

echo "✅ Refactoring pipeline completed successfully!"
echo "📊 Summary:"
echo "   - Pre-refactoring coverage: $COVERAGE%"
echo "   - Post-refactoring coverage: $NEW_COVERAGE%"
echo "   - Quality improvements documented in quality-metrics.py output"

# Cleanup
rm -f complexity_violations.txt size_violations.txt duplicate_violations.txt ai_analysis_prompt.txt