#!/bin/bash
# Resource locking for parallel AI agents

# Resource locking prevents conflicts between parallel agents
acquire_lock() {
    local resource="$1" agent="$2"
    (set -C; echo "$agent" > "$resource.lock") 2>/dev/null
}

release_lock() {
    local resource="$1"
    rm -f "$resource.lock"
}

# Example usage for package.json modification
if acquire_lock "package.json" "$AGENT_ID"; then
    echo "Agent $AGENT_ID acquired lock for package.json"
    modify_package_json && release_lock "package.json"
    echo "Agent $AGENT_ID released lock for package.json"
else
    echo "Agent $AGENT_ID failed to acquire lock for package.json"
    exit 1
fi

# Monitor function for observing lock usage
monitor_locks() {
    echo "=== Lock Monitoring Started ==="
    while true; do
        echo "$(date): Active locks:"
        find . -name "*.lock" -exec basename {} .lock \; | sed 's/^/  - /'
        sleep 5
    done
}

# Check if monitor mode is requested
if [[ "$1" == "monitor" ]]; then
    monitor_locks
fi