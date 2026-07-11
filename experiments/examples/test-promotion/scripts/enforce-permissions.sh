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
    count=$((count + 1))
done < <(find tests/golden -type f -name "*.py" -print0)

echo ""
echo "✅ Protected $count golden test(s)"
echo "   This advisory mode prevents accidental edits in this checkout"
echo "   CI and required CODEOWNERS review remain the binding controls"
