#!/bin/bash
# AI-powered policy generation from compliance requirements

set -euo pipefail

REQUIREMENTS_FILE="$1"
POLICY_TYPE="${2:-cedar}"  # cedar or opa
OUTPUT_FILE="${3:-/dev/stdout}"

if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
    echo "Error: Requirements file $REQUIREMENTS_FILE not found" >&2
    exit 1
fi

# Generate Cedar policies
generate_cedar_policy() {
    local req_file="$1"
    
    ai "Convert the compliance requirements in $req_file into Cedar policy code:

Requirements: $(cat "$req_file")

Generate Cedar policy that:
1. Follows Cedar syntax exactly
2. Implements the security requirements
3. Uses appropriate actions and resources
4. Includes permit/forbid decisions
5. Adds descriptive comments

Output only valid Cedar policy code."
}

# Generate OPA/Rego policies
generate_opa_policy() {
    local req_file="$1"
    
    ai "Convert the compliance requirements in $req_file into OPA Rego policy code:

Requirements: $(cat "$req_file")

Generate Rego policy that:
1. Follows OPA Rego syntax exactly
2. Implements the security requirements
3. Uses appropriate input structure
4. Includes allow/deny rules
5. Adds descriptive comments

Output only valid Rego policy code."
}

# Main execution
case "$POLICY_TYPE" in
    "cedar")
        echo "# Generated Cedar policy from $REQUIREMENTS_FILE"
        echo "# Generated on: $(date)"
        echo ""
        generate_cedar_policy "$REQUIREMENTS_FILE"
        ;;
    "opa"|"rego")
        echo "# Generated OPA policy from $REQUIREMENTS_FILE"
        echo "# Generated on: $(date)"
        echo ""
        generate_opa_policy "$REQUIREMENTS_FILE"
        ;;
    *)
        echo "Error: Unsupported policy type: $POLICY_TYPE" >&2
        echo "Supported types: cedar, opa" >&2
        exit 1
        ;;
esac