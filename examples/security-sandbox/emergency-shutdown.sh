#!/bin/bash
# Emergency safety monitoring and shutdown for AI agents

VIOLATIONS_FILE="safety-violations.json"
MAX_VIOLATIONS=5

# Monitor for violations and emergency shutdown
monitor_safety() {
    while true; do
        if [[ -f "$VIOLATIONS_FILE" ]]; then
            violations_count=$(jq '.violations | length' "$VIOLATIONS_FILE" 2>/dev/null || echo 0)
            
            if [[ $violations_count -gt $MAX_VIOLATIONS ]]; then
                echo "EMERGENCY: $violations_count violations detected (max: $MAX_VIOLATIONS)"
                echo "Initiating emergency shutdown..."
                
                # Emergency stop all containers
                docker-compose down --timeout 10
                
                # Kill any runaway AI agent processes
                pkill -f "ai-agent" || true
                
                # Clear all agent workspaces
                rm -rf /workspace/agent-*/ || true
                
                # Log the emergency shutdown
                echo "$(date): Emergency shutdown triggered due to $violations_count violations" >> emergency.log
                
                exit 1
            fi
        fi
        
        sleep 10
    done
}

# Manual emergency shutdown
emergency_stop() {
    echo "Manual emergency shutdown initiated..."
    docker-compose down --timeout 10
    pkill -f "ai-agent" || true
    rm -rf /workspace/agent-*/ || true
    echo "Emergency shutdown complete"
}

# Initialize violations file if it doesn't exist
initialize_monitoring() {
    if [[ ! -f "$VIOLATIONS_FILE" ]]; then
        echo '{"violations": []}' > "$VIOLATIONS_FILE"
    fi
}

# Main execution
case "$1" in
    "monitor")
        initialize_monitoring
        monitor_safety
        ;;
    "stop")
        emergency_stop
        ;;
    *)
        echo "Usage: $0 {monitor|stop}"
        echo "  monitor - Start continuous safety monitoring"
        echo "  stop    - Perform immediate emergency shutdown"
        exit 1
        ;;
esac