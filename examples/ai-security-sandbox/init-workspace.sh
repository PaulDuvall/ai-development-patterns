#!/bin/bash
# AI Security Sandbox Workspace Initialization

echo "🔒 Initializing AI Security Sandbox..."
echo "Workspace: $(pwd)"
echo "User: $(whoami) ($(id))"
echo "Python: $(python --version)"

# Create workspace subdirectories
mkdir -p logs generated

# Set up environment
export AI_SANDBOX=true
export PYTHONPATH="/workspace/src:$PYTHONPATH"

# Display security status
echo ""
echo "🛡️ Security Status:"
echo "✅ Network isolation: $(if ping -c 1 -W 1 8.8.8.8 &>/dev/null; then echo 'DISABLED ⚠️'; else echo 'ENABLED'; fi)"
echo "✅ Non-root user: $(if [[ $(id -u) -eq 0 ]]; then echo 'DISABLED ⚠️'; else echo 'ENABLED'; fi)"
echo "✅ Read-only source: $(if [[ -w /workspace/src ]] 2>/dev/null; then echo 'DISABLED ⚠️'; else echo 'ENABLED'; fi)"

echo ""
echo "🚀 AI Security Sandbox ready for secure development!"
echo "   Use 'python /workspace/healthcheck.py' to run full health check"
echo ""
