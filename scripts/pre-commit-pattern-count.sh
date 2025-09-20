#!/bin/bash
#
# Pre-commit hook to automatically update pattern count badge
#
# To install this hook:
# cp scripts/pre-commit-pattern-count.sh .git/hooks/pre-commit
# chmod +x .git/hooks/pre-commit
#
# To make it optional (just warn instead of blocking commits):
# Set PATTERN_COUNT_WARN_ONLY=1 environment variable

set -e

echo "🔍 Checking pattern count badge..."

# Run the pattern count update script
python scripts/update-pattern-count.py

# Check if README.md was modified
if git diff --quiet README.md; then
    echo "✅ Pattern count badge is up to date"
    exit 0
else
    echo "📝 Pattern count badge was updated"

    if [ "${PATTERN_COUNT_WARN_ONLY:-0}" = "1" ]; then
        echo "⚠️  WARNING: Pattern count badge was out of date and has been updated"
        echo "    The updated README.md is staged automatically"
        # Stage the updated README.md
        git add README.md
        exit 0
    else
        echo "❌ Pattern count badge was out of date"
        echo "   The badge has been automatically updated"
        echo "   Please review the changes and re-run your commit"
        echo ""
        echo "   Changes made:"
        git diff README.md
        echo ""
        echo "   To automatically stage the update and continue, set:"
        echo "   export PATTERN_COUNT_WARN_ONLY=1"

        # Stage the updated README.md for convenience
        git add README.md
        exit 1
    fi
fi