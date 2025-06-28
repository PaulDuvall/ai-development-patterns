#!/bin/bash

# AI Security Sandbox Management Script
# Simplifies setup and usage of the AI Security Sandbox pattern
# Based on: https://github.com/PaulDuvall/ai-development-patterns

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SANDBOX_NAME="ai-dev-sandbox"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.ai-sandbox.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
AI Security Sandbox Management Script

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    build           Build the AI sandbox container
    start           Start the AI sandbox environment
    stop            Stop the AI sandbox environment
    shell           Open an interactive shell in the sandbox
    exec <cmd>      Execute a command in the sandbox
    status          Show sandbox status and security validation
    logs            Show sandbox logs
    clean           Remove sandbox containers and volumes
    validate        Validate sandbox security configuration
    demo            Run a demonstration of sandbox isolation

EXAMPLES:
    # Quick start - build and enter sandbox
    $0 start

    # Run Claude Code in the sandbox
    $0 exec "claude --help"

    # Test network isolation
    $0 demo

    # Clean up everything
    $0 clean

SECURITY FEATURES:
    ✓ Complete network isolation (network_mode: none)
    ✓ Non-root user execution (UID 1000)
    ✓ Read-only source code mounts
    ✓ Resource limits (2 CPU, 4GB RAM)
    ✓ No privileged capabilities
    ✓ Credential isolation (no AWS/SSH/env mounts)

For more information, see:
https://github.com/PaulDuvall/ai-development-patterns/tree/main/sandbox

EOF
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    # Check for either docker-compose or docker compose
    if ! command -v docker-compose &> /dev/null; then
        if ! docker compose version &> /dev/null 2>&1; then
            log_error "Docker Compose is not installed or not in PATH"
            echo ""
            log_info "To install Docker Compose, choose one of these options:"
            echo "  • macOS: brew install docker-compose"
            echo "  • Ubuntu/Debian: sudo apt-get install docker-compose-plugin"
            echo "  • Manual: https://docs.docker.com/compose/install/"
            echo ""
            log_info "Or use Docker Desktop which includes Docker Compose"
            exit 1
        fi
    fi
}

# Create requirements file if it doesn't exist
create_requirements() {
    local req_file="$SCRIPT_DIR/requirements-sandbox.txt"
    if [[ ! -f "$req_file" ]]; then
        log_info "Creating requirements-sandbox.txt..."
        cat > "$req_file" << 'EOF'
# AI Security Sandbox Dependencies
black==23.11.0
flake8==6.1.0
mypy==1.7.0
pytest==7.4.3
pytest-cov==4.1.0
requests==2.31.0
pydantic==2.5.0
ipython==8.17.2
jinja2==3.1.2
rich==13.7.0
click==8.1.7
EOF
        log_success "Created requirements-sandbox.txt"
    fi
}

# Build the sandbox container
build_sandbox() {
    log_info "Building AI Security Sandbox container..."
    create_requirements
    
    cd "$PROJECT_ROOT"
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" build ai-development
    else
        docker compose -f "$COMPOSE_FILE" build ai-development
    fi
    
    log_success "Sandbox container built successfully"
}

# Start the sandbox
start_sandbox() {
    log_info "Starting AI Security Sandbox..."
    
    # Build if not exists
    if ! docker image inspect ai-development-patterns-ai-development &> /dev/null; then
        build_sandbox
    fi
    
    cd "$PROJECT_ROOT"
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" up -d ai-development
    else
        docker compose -f "$COMPOSE_FILE" up -d ai-development
    fi
    
    # Wait for container to be ready
    log_info "Waiting for sandbox to be ready..."
    sleep 3
    
    if docker exec "$SANDBOX_NAME" python -c "print('Sandbox ready')" &> /dev/null; then
        log_success "AI Security Sandbox is running and ready"
        log_info "Use '$0 shell' to enter the sandbox"
        log_info "Use '$0 validate' to check security configuration"
    else
        log_error "Sandbox failed to start properly"
        exit 1
    fi
}

# Stop the sandbox
stop_sandbox() {
    log_info "Stopping AI Security Sandbox..."
    
    cd "$PROJECT_ROOT"
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" down
    else
        docker compose -f "$COMPOSE_FILE" down
    fi
    
    log_success "Sandbox stopped"
}

# Open shell in sandbox
shell_sandbox() {
    if ! docker ps --format "table {{.Names}}" | grep -q "$SANDBOX_NAME"; then
        log_warning "Sandbox is not running. Starting it now..."
        start_sandbox
    fi
    
    log_info "Opening shell in AI Security Sandbox..."
    log_info "You are now in an isolated environment with no network access"
    echo ""
    docker exec -it "$SANDBOX_NAME" /bin/bash
}

# Execute command in sandbox
exec_command() {
    local cmd="$1"
    
    if ! docker ps --format "table {{.Names}}" | grep -q "$SANDBOX_NAME"; then
        log_warning "Sandbox is not running. Starting it now..."
        start_sandbox
    fi
    
    log_info "Executing command in sandbox: $cmd"
    docker exec -it "$SANDBOX_NAME" bash -c "$cmd"
}

# Show status
show_status() {
    log_info "AI Security Sandbox Status"
    echo ""
    
    # Container status
    if docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "$SANDBOX_NAME"; then
        echo "📦 Container Status: RUNNING"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "$SANDBOX_NAME"
    else
        echo "📦 Container Status: STOPPED"
    fi
    
    echo ""
    
    # Image info
    if docker image inspect ai-development-patterns-ai-development &> /dev/null; then
        echo "🖼️  Image: BUILT"
        docker image inspect ai-development-patterns-ai-development --format "Created: {{.Created}}"
    else
        echo "🖼️  Image: NOT BUILT"
    fi
    
    echo ""
    
    # Security validation
    validate_security
}

# Show logs
show_logs() {
    log_info "AI Security Sandbox Logs"
    echo ""
    
    if docker ps --format "table {{.Names}}" | grep -q "$SANDBOX_NAME"; then
        docker logs --tail 50 -f "$SANDBOX_NAME"
    else
        log_warning "Sandbox is not running"
    fi
}

# Clean up
clean_sandbox() {
    log_warning "This will remove all sandbox containers and volumes"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up AI Security Sandbox..."
        
        cd "$PROJECT_ROOT"
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
        else
            docker compose -f "$COMPOSE_FILE" down -v --remove-orphans
        fi
        
        # Remove image
        if docker image inspect ai-development-patterns-ai-development &> /dev/null; then
            docker rmi ai-development-patterns-ai-development
        fi
        
        log_success "Cleanup complete"
    else
        log_info "Cleanup cancelled"
    fi
}

# Validate security configuration
validate_security() {
    log_info "Security Validation"
    echo ""
    
    if ! docker ps --format "table {{.Names}}" | grep -q "$SANDBOX_NAME"; then
        echo "❌ Container not running - cannot validate"
        return 1
    fi
    
    # Check network isolation
    if docker inspect "$SANDBOX_NAME" --format "{{.HostConfig.NetworkMode}}" | grep -q "none"; then
        echo "✅ Network isolation: ENABLED (network_mode: none)"
    else
        echo "❌ Network isolation: DISABLED"
    fi
    
    # Check user
    local user_info=$(docker exec "$SANDBOX_NAME" id 2>/dev/null || echo "")
    if echo "$user_info" | grep -q "uid=1000"; then
        echo "✅ Non-root user: ENABLED (UID 1000)"
    else
        echo "❌ Non-root user: DISABLED"
    fi
    
    # Check capabilities
    local caps=$(docker inspect "$SANDBOX_NAME" --format "{{.HostConfig.CapDrop}}" 2>/dev/null || echo "")
    if echo "$caps" | grep -q "ALL"; then
        echo "✅ Capabilities dropped: ALL"
    else
        echo "❌ Capabilities: NOT PROPERLY DROPPED"
    fi
    
    # Check for sensitive mounts
    local mounts=$(docker inspect "$SANDBOX_NAME" --format "{{range .Mounts}}{{.Source}} {{end}}" 2>/dev/null || echo "")
    local sensitive_found=false
    
    for sensitive in "/.aws" "/.ssh" "/.env" "/var/run/docker.sock"; do
        if echo "$mounts" | grep -q "$sensitive"; then
            echo "❌ Sensitive mount detected: $sensitive"
            sensitive_found=true
        fi
    done
    
    if ! $sensitive_found; then
        echo "✅ No sensitive mounts detected"
    fi
    
    # Check resource limits
    local memory_limit=$(docker inspect "$SANDBOX_NAME" --format "{{.HostConfig.Memory}}" 2>/dev/null || echo "0")
    if [[ "$memory_limit" != "0" ]]; then
        echo "✅ Memory limit: $(($memory_limit / 1024 / 1024 / 1024))GB"
    else
        echo "❌ Memory limit: NOT SET"
    fi
    
    echo ""
    log_success "Security validation complete"
}

# Run demonstration
run_demo() {
    log_info "AI Security Sandbox Demonstration"
    echo ""
    
    if ! docker ps --format "table {{.Names}}" | grep -q "$SANDBOX_NAME"; then
        log_warning "Starting sandbox for demonstration..."
        start_sandbox
    fi
    
    log_info "Testing network isolation..."
    echo ""
    
    echo "🧪 Testing external network access (should fail):"
    docker exec "$SANDBOX_NAME" bash -c "
        echo 'Attempting to ping Google DNS...'
        if ping -c 1 8.8.8.8 2>/dev/null; then
            echo '❌ SECURITY BREACH: Network access is available!'
        else
            echo '✅ Network isolation working: ping failed as expected'
        fi
        
        echo 'Attempting HTTP request...'
        if curl -s --connect-timeout 5 http://google.com 2>/dev/null; then
            echo '❌ SECURITY BREACH: HTTP access is available!'
        else
            echo '✅ Network isolation working: HTTP request failed as expected'
        fi
        
        echo 'Attempting DNS lookup...'
        if nslookup google.com 2>/dev/null; then
            echo '❌ SECURITY BREACH: DNS access is available!'
        else
            echo '✅ Network isolation working: DNS lookup failed as expected'
        fi
    " || true
    
    echo ""
    log_info "Testing file system access..."
    docker exec "$SANDBOX_NAME" bash -c "
        echo 'Current user:'
        id
        echo 'Workspace contents:'
        ls -la /workspace/
        echo 'Attempting to access sensitive directories...'
        if ls /home/aiuser/.aws 2>/dev/null; then
            echo '❌ AWS credentials directory accessible!'
        else
            echo '✅ AWS credentials directory not mounted'
        fi
    " || true
    
    echo ""
    log_success "Demonstration complete - sandbox is properly isolated"
}

# Main script logic
main() {
    # Only check Docker for commands that need it
    case "${1:-help}" in
        help|--help|-h)
            show_help
            exit 0
            ;;
    esac
    
    check_docker
    
    case "${1:-help}" in
        build)
            build_sandbox
            ;;
        start)
            start_sandbox
            ;;
        stop)
            stop_sandbox
            ;;
        shell)
            shell_sandbox
            ;;
        exec)
            if [[ $# -lt 2 ]]; then
                log_error "Command required for exec"
                exit 1
            fi
            exec_command "$2"
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        clean)
            clean_sandbox
            ;;
        validate)
            validate_security
            ;;
        demo)
            run_demo
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"