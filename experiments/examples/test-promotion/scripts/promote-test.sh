#!/bin/bash
set -euo pipefail

# Test Promotion Script
# Proposes an AI-generated test as a protected golden contract for human review

GENERATED_TEST="${1:-}"

if [[ -z "$GENERATED_TEST" ]]; then
    echo "Usage: ./scripts/promote-test.sh <path-to-generated-test>"
    echo "Example: ./scripts/promote-test.sh tests/generated/test_payment.py"
    exit 1
fi

if [[ ! -f "$GENERATED_TEST" ]]; then
    echo "❌ Error: Test file not found: $GENERATED_TEST"
    exit 1
fi

if [[ ! "$GENERATED_TEST" =~ ^tests/generated/ ]]; then
    echo "❌ Error: Can only promote tests from tests/generated/"
    echo "   Got: $GENERATED_TEST"
    exit 1
fi

echo "🔍 Test Promotion Workflow"
echo "   Source: $GENERATED_TEST"
echo ""

# Step 1: Validate test passes
echo "Step 1: Validating test passes..."
if ! pytest "$GENERATED_TEST" -v; then
    echo "❌ Test must pass before promotion"
    exit 1
fi
echo "✅ Test passes"
echo ""

# Step 2: Human quality checklist
echo "Step 2: Quality Review Checklist"
echo "   Please review the test and answer the following:"
echo ""

read -r -p "   Does this test capture critical behavior? (y/n): " critical
if [[ "$critical" != "y" ]]; then
    echo "❌ Promotion cancelled - test not critical"
    exit 1
fi

read -r -p "   Is the test stable (not flaky)? (y/n): " stable
if [[ "$stable" != "y" ]]; then
    echo "❌ Promotion cancelled - test may be flaky"
    exit 1
fi

read -r -p "   Does it have clear, specific assertions? (y/n): " assertions
if [[ "$assertions" != "y" ]]; then
    echo "❌ Promotion cancelled - assertions not clear"
    exit 1
fi

read -r -p "   Is it properly documented? (y/n): " documented
if [[ "$documented" != "y" ]]; then
    echo "❌ Promotion cancelled - needs documentation"
    exit 1
fi

echo ""
echo "✅ Quality checks passed"
echo ""

# Step 3: Determine golden path
BASENAME=$(basename "$GENERATED_TEST")
GOLDEN_PATH="tests/golden/${BASENAME}"

# Check if golden test already exists
if [[ -f "$GOLDEN_PATH" ]]; then
    echo "❌ Error: Golden test already exists: $GOLDEN_PATH"
    echo "   This promotion path only adds new contracts; modify an existing"
    echo "   contract through a separately reviewed policy exception."
    exit 1
fi

# Step 4: Copy to golden with read-only permissions
echo "Step 3: Copying to golden tests..."
cp "$GENERATED_TEST" "$GOLDEN_PATH"
chmod 444 "$GOLDEN_PATH"
echo "✅ Test promoted to: $GOLDEN_PATH (444 permissions)"
echo ""

# Step 5: Git operations
echo "Step 4: Creating promotion commit..."
git add "$GOLDEN_PATH"

COMMIT_MSG="test-promotion: Promote ${BASENAME} to golden status

Source: $GENERATED_TEST
Target: $GOLDEN_PATH
Reviewer: $(git config user.name)

Checklist:
- [x] Test captures critical behavior
- [x] Test is stable (not flaky)
- [x] Clear, specific assertions
- [x] Properly documented"

git commit -m "$COMMIT_MSG"
echo "✅ Commit created"
echo ""

# Step 6: Summary
echo "📋 Promotion Summary"
echo "   ✓ Test validated and passing"
echo "   ✓ Quality checklist completed"
echo "   ✓ Promoted to: $GOLDEN_PATH"
echo "   ✓ Permissions set to 444 (read-only)"
echo "   ✓ Committed to git"
echo ""
echo "Next steps:"
echo "  1. Create PR: git push origin HEAD"
echo "  2. Request review from the configured CODEOWNERS"
echo "  3. Label PR with 'test-promotion'"
echo "  4. Merge after approval"
echo ""
echo "🎉 Test promotion complete!"
