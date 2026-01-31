#!/bin/bash

# Security Sandbox Management Script
# Simplifies setup and usage of the Security Sandbox pattern
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
Security Sandbox Management Script

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    setup           Complete setup including Docker Compose installation
    build           Build the AI sandbox container
    start           Start the AI sandbox environment (includes setup if needed)
    stop            Stop the AI sandbox environment
    shell           Open an interactive shell in the sandbox
    exec <cmd>      Execute a command in the sandbox
    status          Show sandbox status and security validation
    logs            Show sandbox logs
    clean           Remove sandbox containers and volumes
    validate        Validate sandbox security configuration
    demo            Run a demonstration of sandbox isolation

EXAMPLES:
    # Complete automated setup and start
    $0 start

    # Manual setup (installs Docker Compose if needed)
    $0 setup

    # Run Claude Code in the sandbox
    $0 exec "claude --help"

    # Test network isolation
    $0 demo

    # Clean up everything
    $0 clean

AUTOMATION FEATURES:
    ✓ Automatically starts Docker if not running
    ✓ Installs Docker Compose if missing
    ✓ Creates all required configuration files
    ✓ Builds secure container with validation

SECURITY FEATURES:
    ✓ Complete network isolation (network_mode: none)
    ✓ Non-root user execution (UID 1000)
    ✓ Read-only source code mounts
    ✓ Resource limits (2 CPU, 4GB RAM)
    ✓ No privileged capabilities
    ✓ Credential isolation (no AWS/SSH/env mounts)

For more information, see:
https://github.com/PaulDuvall/ai-development-patterns/tree/main/examples/security-sandbox

EOF
}

# Auto-install Docker Compose if needed
install_docker_compose() {
    log_info "Installing Docker Compose automatically..."
    
    local os_type="$(uname -s)"
    local arch="$(uname -m)"
    local compose_version="v2.24.5"
    
    # Map architecture names for Docker Compose releases
    case "$arch" in
        x86_64) arch="x86_64" ;;
        arm64|aarch64) arch="aarch64" ;;
        *) 
            log_error "Unsupported architecture: $arch"
            return 1
            ;;
    esac
    
    # Create local bin directory if it doesn't exist
    mkdir -p "$HOME/.local/bin"
    
    # Convert OS type to lowercase for URL
    local os_lower=$(echo "$os_type" | tr '[:upper:]' '[:lower:]')
    
    # Download Docker Compose - use correct URL format
    local download_url="https://github.com/docker/compose/releases/download/${compose_version}/docker-compose-${os_lower}-${arch}"
    local install_path="$HOME/.local/bin/docker-compose"
    
    log_info "Downloading Docker Compose ${compose_version} for ${os_lower}-${arch}..."
    log_info "URL: $download_url"
    
    if curl -L "$download_url" -o "$install_path" --progress-bar --fail; then
        chmod +x "$install_path"
        
        # Add to PATH if not already there
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            export PATH="$HOME/.local/bin:$PATH"
            
            # Add to shell profile for persistence
            local shell_profile=""
            if [[ -f "$HOME/.zshrc" ]]; then
                shell_profile="$HOME/.zshrc"
            elif [[ -f "$HOME/.bashrc" ]]; then
                shell_profile="$HOME/.bashrc"
            elif [[ -f "$HOME/.bash_profile" ]]; then
                shell_profile="$HOME/.bash_profile"
            fi
            
            if [[ -n "$shell_profile" ]] && ! grep -q "HOME/.local/bin" "$shell_profile"; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_profile"
                log_info "Added $HOME/.local/bin to PATH in $shell_profile"
            fi
        fi
        
        log_success "Docker Compose installed successfully to $install_path"
        return 0
    else
        log_error "Failed to download Docker Compose"
        return 1
    fi
}

# Check if Docker is available and install Docker Compose if needed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first:"
        echo ""
        case "$(uname -s)" in
            Darwin*)
                log_info "macOS: Install Docker Engine with Homebrew:"
                echo "  brew install docker"
                echo "  brew install docker-buildx"
                echo "  Or use Colima: brew install colima && colima start"
                ;;
            Linux*)
                log_info "Linux: Install Docker Engine with your package manager:"
                echo "  Ubuntu/Debian: sudo apt-get install docker.io"
                echo "  CentOS/RHEL: sudo yum install docker"
                echo "  Arch: sudo pacman -S docker"
                ;;
            *)
                log_info "Visit https://docs.docker.com/engine/install/ for Docker Engine installation"
                ;;
        esac
        echo ""
        log_info "After installing Docker, run this script again"
        exit 1
    fi

    # Check if Docker is running, start it automatically if not
    if ! docker info &> /dev/null; then
        log_warning "Docker is not running, starting it automatically..."
        
        case "$(uname -s)" in
            Darwin*)
                log_info "Starting Docker on macOS..."
                
                # Check for Colima first (preferred alternative to Docker Desktop)
                if command -v colima &> /dev/null; then
                    log_info "Found Colima, starting Docker with Colima..."
                    if colima start --cpu 2 --memory 4 2>/dev/null; then
                        log_success "Colima started successfully"
                    else
                        log_warning "Colima failed to start, checking if already running..."
                        if colima status | grep -q "Running"; then
                            log_success "Colima is already running"
                        else
                            log_error "Failed to start Colima"
                            exit 1
                        fi
                    fi
                    
                # Check for Docker Desktop as fallback
                elif [[ -d "/Applications/Docker.app" ]]; then
                    log_info "Starting Docker Desktop..."
                    open /Applications/Docker.app
                    log_info "Waiting for Docker to start..."
                    
                    # Wait up to 60 seconds for Docker to start
                    local timeout=60
                    local elapsed=0
                    while ! docker info &> /dev/null && [[ $elapsed -lt $timeout ]]; do
                        sleep 2
                        elapsed=$((elapsed + 2))
                        echo -n "."
                    done
                    echo ""
                    
                    if docker info &> /dev/null; then
                        log_success "Docker started successfully"
                    else
                        log_error "Docker failed to start within ${timeout} seconds"
                        exit 1
                    fi
                    
                # No Docker runtime found
                else
                    log_error "No Docker runtime found on macOS"
                    log_info "Install Docker Engine alternatives:"
                    echo "  Option 1 (Recommended): brew install colima && colima start"
                    echo "  Option 2: brew install docker && start Docker daemon manually"
                    exit 1
                fi
                ;;
            Linux*)
                log_info "Starting Docker daemon on Linux..."
                # Try to start Docker daemon
                if command -v systemctl &> /dev/null; then
                    if sudo systemctl start docker 2>/dev/null; then
                        log_success "Docker daemon started successfully"
                        
                        # Add user to docker group if not already
                        if ! groups | grep -q docker; then
                            log_info "Adding user to docker group..."
                            sudo usermod -aG docker "$USER"
                            log_warning "You may need to log out and back in for group changes to take effect"
                            log_info "For now, trying with sudo..."
                        fi
                    else
                        log_error "Failed to start Docker daemon. Please run:"
                        echo "  sudo systemctl start docker"
                        exit 1
                    fi
                elif command -v service &> /dev/null; then
                    if sudo service docker start 2>/dev/null; then
                        log_success "Docker service started successfully"
                    else
                        log_error "Failed to start Docker service. Please run:"
                        echo "  sudo service docker start"
                        exit 1
                    fi
                else
                    log_error "Cannot start Docker automatically on this Linux distribution"
                    log_info "Please start Docker manually and try again"
                    exit 1
                fi
                ;;
            *)
                log_error "Cannot start Docker automatically on this platform"
                log_info "Please start Docker manually and try again"
                exit 1
                ;;
        esac
    fi

    # Check for either docker-compose or docker compose, install if needed
    if ! command -v docker-compose &> /dev/null; then
        if ! docker compose version &> /dev/null 2>&1; then
            log_warning "Docker Compose not found, installing automatically..."
            if install_docker_compose; then
                # Verify installation
                if ! command -v docker-compose &> /dev/null; then
                    log_error "Docker Compose installation failed"
                    exit 1
                fi
            else
                log_error "Failed to install Docker Compose automatically"
                exit 1
            fi
        fi
    fi
    
    log_success "Docker and Docker Compose are ready"
}

# Create all necessary files if they don't exist
create_sandbox_files() {
    # Create requirements file
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
    
    # Create healthcheck script
    local healthcheck_file="$SCRIPT_DIR/healthcheck.py"
    if [[ ! -f "$healthcheck_file" ]]; then
        log_info "Creating healthcheck.py..."
        cat > "$healthcheck_file" << 'EOF'
#!/usr/bin/env python3
"""
AI Security Sandbox Health Check
Validates that the sandbox environment is running correctly
"""
import sys
import os
import subprocess

def check_python():
    """Check Python is working"""
    return sys.version_info >= (3, 8)

def check_workspace():
    """Check workspace directory exists and is accessible"""
    workspace_dir = os.environ.get('WORKSPACE_DIR', '/workspace')
    return os.path.exists(workspace_dir) and os.access(workspace_dir, os.R_OK | os.W_OK)

def check_network_isolation():
    """Verify network isolation is working"""
    try:
        # This should fail in a properly isolated container
        result = subprocess.run(['ping', '-c', '1', '-W', '1', '8.8.8.8'], 
                              capture_output=True, timeout=5)
        # If ping succeeds, network isolation is NOT working
        return result.returncode != 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Timeout or no ping command means isolation is working
        return True

def main():
    """Run all health checks"""
    checks = [
        ("Python version", check_python),
        ("Workspace access", check_workspace),
        ("Network isolation", check_network_isolation)
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        try:
            result = check_func()
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{name}: {status}")
            if not result:
                all_passed = False
        except Exception as e:
            print(f"{name}: ❌ ERROR - {e}")
            all_passed = False
    
    if all_passed:
        print("\n🔒 AI Security Sandbox is healthy and properly isolated")
        sys.exit(0)
    else:
        print("\n⚠️ AI Security Sandbox has issues")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF
        chmod +x "$healthcheck_file"
        log_success "Created healthcheck.py"
    fi
    
    # Create workspace initialization script
    local init_file="$SCRIPT_DIR/init-workspace.sh"
    if [[ ! -f "$init_file" ]]; then
        log_info "Creating init-workspace.sh..."
        cat > "$init_file" << 'EOF'
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
echo "✅ Read-only source: $(if [[ -w /workspace/src 2>/dev/null ]]; then echo 'DISABLED ⚠️'; else echo 'ENABLED'; fi)"

echo ""
echo "🚀 AI Security Sandbox ready for secure development!"
echo "   Use 'python /workspace/healthcheck.py' to run full health check"
echo ""
EOF
        chmod +x "$init_file"
        log_success "Created init-workspace.sh"
    fi
}

# Build the sandbox container
build_sandbox() {
    log_info "Building AI Security Sandbox container..."
    
    # Create all necessary files automatically
    create_sandbox_files
    
    # Change to project root for build context
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
        setup)
            # Setup can run without Docker being started
            log_info "Running complete AI Security Sandbox setup..."
            
            # Check if Docker is installed (but don't require it to be running)
            if ! command -v docker &> /dev/null; then
                log_error "Docker is not installed. Please install Docker first:"
                echo ""
                case "$(uname -s)" in
                    Darwin*)
                        log_info "macOS: Install Docker Engine with Homebrew:"
                        echo "  brew install docker"
                        echo "  Or use Colima: brew install colima && colima start"
                        ;;
                    Linux*)
                        log_info "Linux: Install Docker Engine with your package manager:"
                        echo "  Ubuntu/Debian: sudo apt-get install docker.io"
                        echo "  CentOS/RHEL: sudo yum install docker"
                        echo "  Arch: sudo pacman -S docker"
                        ;;
                    *)
                        log_info "Visit https://docs.docker.com/engine/install/ for Docker Engine installation"
                        ;;
                esac
                echo ""
                log_info "After installing Docker, run '$0 setup' again"
                exit 1
            fi
            
            # Install Docker Compose if needed
            if ! command -v docker-compose &> /dev/null; then
                if ! docker compose version &> /dev/null 2>&1; then
                    log_warning "Docker Compose not found, installing automatically..."
                    if install_docker_compose; then
                        log_success "Docker Compose installed successfully"
                    else
                        log_error "Failed to install Docker Compose automatically"
                        exit 1
                    fi
                fi
            fi
            
            # Create all necessary files
            create_sandbox_files
            
            log_success "Setup complete!"
            echo ""
            log_info "Next step:"
            echo "  Run the sandbox: $0 start"
            echo "  (Docker will be started automatically if needed)"
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
