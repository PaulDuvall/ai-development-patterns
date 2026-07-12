#!/bin/bash
# Security Sandbox Workspace Initialization

set -euo pipefail

echo "🔒 Initializing Security Sandbox..."
echo "Workspace: $(pwd)"
echo "User: $(whoami) ($(id))"
echo "Python: $(python --version)"

# Ensure writable-volume mount points exist
mkdir -p logs generated

# Set up environment
export AI_SANDBOX=true
export PYTHONPATH="/workspace/src:${PYTHONPATH:-}"

# Display security status
echo ""
echo "🛡️ Security Status:"
if ! python3 /workspace/healthcheck.py --network-only; then
    echo "❌ Network isolation is not proven; refusing to initialize." >&2
    exit 1
fi
echo "✅ Non-root user: $(if [[ $(id -u) -eq 0 ]]; then echo 'DISABLED ⚠️'; else echo 'ENABLED'; fi)"
echo "✅ Read-only source: $(if [[ -w /workspace/src ]] 2>/dev/null; then echo 'DISABLED ⚠️'; else echo 'ENABLED'; fi)"

echo ""
echo "🚀 Security Sandbox ready for secure development!"
echo "   Use 'python /workspace/healthcheck.py' to run full health check"
echo ""
