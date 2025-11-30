#!/bin/bash
set -euo pipefail

# Enforce Golden Test Permissions
# Sets all golden tests to read-only (444)

echo "🔒 Enforcing golden test permissions..."

# Find all Python test files in tests/golden/ and set to 444
count=0
while IFS= read -r -d '' file; do
    chmod 444 "$file"
    echo "   ✓ $file → 444 (read-only)"
    ((count++))
done < <(find tests/golden -type f -name "*.py" -print0)

echo ""
echo "✅ Protected $count golden test(s)"
echo "   AI cannot modify these files"
echo "   Human edits require promotion workflow"
