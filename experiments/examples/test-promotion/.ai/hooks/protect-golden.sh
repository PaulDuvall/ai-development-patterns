#!/bin/bash
# AI Protection Hook for Golden Tests
# Advisory hook template for blocking ordinary tool edits to protected golden tests

# This hook executes before Edit/Write tool use
# Exit code 0 = ALLOW
# Exit code 2 = BLOCK

FILE="$TOOL_INPUT_FILE_PATH"
TOOL="$TOOL_NAME"

# Block any Edit or Write operations on tests/golden/**
if [[ "$FILE" =~ ^tests/golden/ ]] && [[ "$TOOL" =~ (Edit|Write) ]]; then
    echo "❌ BLOCKED: Golden tests are protected from this tool"
    echo ""
    echo "   File: $FILE"
    echo "   Tool: $TOOL"
    echo ""
    echo "This configured hook reserves golden edits for the human-owned promotion path."
    echo "Shell access can bypass the hook, so required CI and CODEOWNERS remain authoritative."
    echo ""
    echo "Instead:"
    echo "  1. Create test in tests/generated/$( basename "$FILE")"
    echo "  2. Run and validate the test"
    echo "  3. Ask human to promote: ./scripts/promote-test.sh tests/generated/$(basename "$FILE")"
    echo ""
    exit 2  # BLOCK
fi

# Allow all other operations
exit 0  # ALLOW
