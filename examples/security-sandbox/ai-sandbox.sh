#!/bin/bash

# Security Sandbox Management Script
# Simplifies setup and usage of the Security Sandbox pattern
# Based on: https://github.com/PaulDuvall/ai-development-patterns

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SANDBOX_NAME="ai-dev-sandbox"
SANDBOX_IMAGE="ai-development-patterns/security-sandbox:local"
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
    setup           Validate prerequisites and create local configuration
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

    # Validate prerequisites and create local configuration
    $0 setup

    # Inspect an installed deterministic tool in the sandbox
    $0 exec "pytest --version"

    # Test network isolation
    $0 demo

    # Clean up everything
    $0 clean

AUTOMATION FEATURES:
    ✓ Verifies Docker without starting services or changing system groups
    ✓ Validates an already installed Docker Compose command
    ✓ Creates all required configuration files
    ✓ Builds secure container with validation

SECURITY FEATURES:
    ✓ Complete network isolation (network_mode: none)
    ✓ Non-root user execution (UID 1000)
    ✓ Read-only source code mounts
    ✓ Docker-managed writable output and log volumes
    ✓ Resource limits (2 CPU, 4GB RAM)
    ✓ No privileged capabilities
    ✓ Credential isolation (no AWS/SSH/env mounts)

For more information, see:
https://github.com/PaulDuvall/ai-development-patterns/tree/main/examples/security-sandbox

EOF
}

# Require a package-managed Docker Compose installation. This script never
# downloads executables or mutates shell startup files.
require_docker_compose() {
    if command -v docker-compose &> /dev/null || \
        docker compose version &> /dev/null 2>&1; then
        return 0
    fi
    log_error "Docker Compose is required but was not found."
    echo "Install the Docker Compose plugin or docker-compose package first:"
    echo "  https://docs.docker.com/compose/install/"
    return 1
}

# Check whether Docker and Docker Compose are available.
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

    # Do not start privileged services, launch desktop applications, or change
    # group membership on the user's behalf. A sandbox helper should fail with
    # actionable instructions instead of mutating host security state.
    if ! docker info &> /dev/null; then
        log_error "The Docker daemon is not available."

        case "$(uname -s)" in
            Darwin*)
                log_info "Start Docker Desktop, or start Colima yourself with:"
                echo "  colima start"
                ;;
            Linux*)
                log_info "Start Docker with your system's service manager. For example:"
                echo "  sudo systemctl start docker"
                ;;
            *)
                log_info "Start the Docker daemon for this platform."
                ;;
        esac
        log_info "After Docker is running, run this script again."
        exit 1
    fi

    if ! require_docker_compose; then
        exit 1
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
# Floors set to versions with known CVE fixes; bump as advisories land.
black>=24.3.0
flake8>=7.0.0
mypy>=1.11.0
pytest>=9.0.3
pytest-cov>=5.0.0
requests>=2.33.0
pydantic>=2.7.4
ipython>=8.26.0
jinja2>=3.1.6
rich>=13.7.1
click>=8.1.7
EOF
        log_success "Created requirements-sandbox.txt"
    fi
    
    # Create healthcheck script
    local healthcheck_file="$SCRIPT_DIR/healthcheck.py"
    if [[ ! -f "$healthcheck_file" ]]; then
        log_info "Creating healthcheck.py..."
        cat > "$healthcheck_file" << 'EOF'
#!/usr/bin/env python3
"""Fail-closed health checks for the AI security sandbox."""

import argparse
import errno
import ipaddress
import os
import socket
import stat
import sys
import tempfile


DEFAULT_EGRESS_PROBE_HOST = "1.1.1.1"
DEFAULT_EGRESS_PROBE_PORT = 443
DEFAULT_EGRESS_PROBE_TIMEOUT = 2.0
BLOCKED_EGRESS_ERRNOS = frozenset(
    code
    for code in (
        getattr(errno, "EACCES", None),
        getattr(errno, "ENETDOWN", None),
        getattr(errno, "ENETUNREACH", None),
        getattr(errno, "EPERM", None),
    )
    if code is not None
)


def check_python():
    """Return whether the supported Python runtime is available."""
    return sys.version_info >= (3, 11)


def workspace_access_status():
    """Verify the read-only workspace and dedicated writable volumes."""
    workspace_dir = os.environ.get("WORKSPACE_DIR", "/workspace")
    if not os.path.isdir(workspace_dir) or not os.access(
            workspace_dir, os.R_OK):
        return False, f"workspace is not readable: {workspace_dir}"

    for name in ("generated", "logs"):
        path = os.path.join(workspace_dir, name)
        if os.path.islink(path) or not os.path.isdir(path):
            return False, f"writable workspace directory is unsafe: {path}"
        try:
            with tempfile.NamedTemporaryFile(
                    dir=path, prefix=".sandbox-health-") as probe:
                probe.write(b"healthcheck")
                probe.flush()
        except OSError as exc:
            return False, f"writable workspace probe failed for {path}: {exc}"
    return True, (
        f"{workspace_dir} is readable; generated/ and logs/ are writable")


def check_workspace():
    """Return whether the workspace mount contract is satisfied."""
    accessible, _ = workspace_access_status()
    return accessible


def immutable_runtime_status():
    """Verify trusted scripts are root-owned and source is non-writable."""
    workspace_dir = os.environ.get("WORKSPACE_DIR", "/workspace")
    for path in (
            os.path.join(workspace_dir, "healthcheck.py"),
            os.path.join(workspace_dir, "init-workspace.sh")):
        try:
            metadata = os.lstat(path)
        except OSError as exc:
            return False, f"cannot inspect trusted runtime file {path}: {exc}"
        if (not stat.S_ISREG(metadata.st_mode)
                or stat.S_ISLNK(metadata.st_mode)):
            return False, f"trusted runtime path is not a regular file: {path}"
        if metadata.st_uid != 0:
            return False, f"trusted runtime file is not root-owned: {path}"
        writable_bits = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
        if metadata.st_mode & writable_bits:
            return False, (
                f"trusted runtime file has writable mode bits: {path}")
        if os.access(path, os.W_OK):
            return False, f"trusted runtime file is writable: {path}"

    source = os.path.join(workspace_dir, "src")
    if os.path.islink(source) or not os.path.isdir(source):
        return False, f"source path is unsafe: {source}"
    if os.access(source, os.W_OK):
        return False, f"source path is writable: {source}"
    return True, (
        "trusted scripts are root-owned; source and scripts are read-only")


def _probe_configuration():
    """Return one validated numeric endpoint without performing DNS."""
    host = os.environ.get(
        "SANDBOX_NETWORK_PROBE_HOST", DEFAULT_EGRESS_PROBE_HOST)
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ValueError(
            "SANDBOX_NETWORK_PROBE_HOST must be a numeric IP address; "
            "DNS names cannot prove network isolation"
        ) from exc

    try:
        port = int(os.environ.get(
            "SANDBOX_NETWORK_PROBE_PORT", DEFAULT_EGRESS_PROBE_PORT))
    except ValueError as exc:
        raise ValueError(
            "SANDBOX_NETWORK_PROBE_PORT must be an integer") from exc
    if not 1 <= port <= 65535:
        raise ValueError(
            "SANDBOX_NETWORK_PROBE_PORT must be between 1 and 65535")

    try:
        timeout = float(os.environ.get(
            "SANDBOX_NETWORK_PROBE_TIMEOUT",
            DEFAULT_EGRESS_PROBE_TIMEOUT,
        ))
    except ValueError as exc:
        raise ValueError(
            "SANDBOX_NETWORK_PROBE_TIMEOUT must be a number") from exc
    if not 0.1 <= timeout <= 10.0:
        raise ValueError(
            "SANDBOX_NETWORK_PROBE_TIMEOUT must be between 0.1 and 10 seconds")

    return address, port, timeout


def _non_loopback_interfaces():
    """Return visible non-loopback interface names, failing on ambiguity."""
    interfaces = socket.if_nameindex()
    return sorted({name for _, name in interfaces if name != "lo"})


def probe_network_isolation():
    """Return ``(isolated, detail)`` from a Python-native TCP egress probe.

    A successful connection proves egress is available. Only an explicit
    local kernel or policy denial proves isolation. Timeouts, refused
    connections, malformed configuration, and other ambiguous failures remain
    failures so missing tools, DNS, or an unavailable remote service can never
    be mistaken for a secure sandbox.
    """
    try:
        address, port, timeout = _probe_configuration()
    except ValueError as exc:
        return False, f"configuration error: {exc}"

    family = socket.AF_INET6 if address.version == 6 else socket.AF_INET
    endpoint = (str(address), port, 0, 0) if address.version == 6 else (
        str(address), port)
    try:
        with socket.socket(family, socket.SOCK_STREAM) as connection:
            connection.settimeout(timeout)
            connection.connect(endpoint)
    except OSError as exc:
        error_name = errno.errorcode.get(exc.errno, "UNKNOWN")
        if exc.errno in BLOCKED_EGRESS_ERRNOS:
            try:
                interfaces = _non_loopback_interfaces()
            except OSError as interface_error:
                return False, (
                    "isolation not proven: cannot inspect network interfaces "
                    f"after {error_name}: {interface_error}"
                )
            if interfaces:
                return False, (
                    f"isolation not proven: {error_name} occurred but "
                    "non-loopback interface(s) are present: "
                    f"{', '.join(interfaces)}"
                )
            return True, (
                f"kernel blocked TCP egress to {address}:{port} "
                f"({error_name}); only loopback is present"
            )
        return False, (
            f"isolation not proven: TCP probe to {address}:{port} failed "
            f"ambiguously ({error_name}: {exc})"
        )
    return False, f"TCP egress reached {address}:{port}"


def check_network_isolation():
    """Return whether the Python-native probe proves network isolation."""
    isolated, _ = probe_network_isolation()
    return isolated


def _run_checks(network_only=False):
    """Run checks and return whether all checks passed."""
    runtime_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    checks = []
    if not network_only:
        checks.extend((
            (
                "Python version",
                lambda: (
                    check_python(),
                    f"running {runtime_version}",
                ),
            ),
            ("Workspace access", workspace_access_status),
            ("Runtime guards", immutable_runtime_status),
        ))
    checks.append(("Network isolation", probe_network_isolation))

    all_passed = True
    for name, check_func in checks:
        try:
            passed, detail = check_func()
        # Fail closed on unexpected probe or runtime errors.
        except Exception as exc:
            passed = False
            detail = f"unexpected error: {exc}"
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status} - {detail}")
        all_passed = all_passed and passed
    return all_passed


def main(argv=None):
    """Run all health checks, or only the isolation probe."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--network-only",
        action="store_true",
        help="run only the fail-closed Python TCP egress probe",
    )
    args = parser.parse_args(argv)

    all_passed = _run_checks(network_only=args.network_only)
    if all_passed:
        if not args.network_only:
            print("\nAI Security Sandbox is healthy and properly isolated")
        return 0
    if not args.network_only:
        print("\nAI Security Sandbox has issues")
    return 1


if __name__ == "__main__":
    sys.exit(main())
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
    if ! docker image inspect "$SANDBOX_IMAGE" &> /dev/null; then
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
    
    if docker exec "$SANDBOX_NAME" \
        python3 /workspace/healthcheck.py; then
        log_success "AI Security Sandbox is running and ready"
        log_info "Use '$0 shell' to enter the sandbox"
        log_info "Use '$0 validate' to check security configuration"
    else
        log_error "Sandbox failed its fail-closed health check"
        docker logs --tail 50 "$SANDBOX_NAME" || true
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
    if docker image inspect "$SANDBOX_IMAGE" &> /dev/null; then
        echo "🖼️  Image: BUILT"
        docker image inspect "$SANDBOX_IMAGE" --format "Created: {{.Created}}"
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
        if docker image inspect "$SANDBOX_IMAGE" &> /dev/null; then
            docker rmi "$SANDBOX_IMAGE"
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

    if ! docker ps --format "{{.Names}}" | grep -Fxq "$SANDBOX_NAME"; then
        echo "❌ Container not running - cannot validate"
        return 1
    fi

    local validation_failed=false
    local network_mode=""
    if network_mode=$(docker inspect "$SANDBOX_NAME" \
        --format "{{.HostConfig.NetworkMode}}" 2>/dev/null) && \
        [[ "$network_mode" == "none" ]]; then
        echo "✅ Network isolation: ENABLED (network_mode: none)"
    else
        echo "❌ Network isolation: DISABLED (${network_mode:-unknown})"
        validation_failed=true
    fi

    local user_id=""
    if user_id=$(docker exec "$SANDBOX_NAME" id -u 2>/dev/null) && \
        [[ "$user_id" == "1000" ]]; then
        echo "✅ Non-root user: ENABLED (UID 1000)"
    else
        echo "❌ Non-root user: DISABLED (${user_id:-unknown})"
        validation_failed=true
    fi

    local caps=""
    if caps=$(docker inspect "$SANDBOX_NAME" \
        --format "{{.HostConfig.CapDrop}}" 2>/dev/null) && \
        [[ "$caps" == *"ALL"* ]]; then
        echo "✅ Capabilities dropped: ALL"
    else
        echo "❌ Capabilities: NOT PROPERLY DROPPED"
        validation_failed=true
    fi

    local mounts=""
    local sensitive_found=false
    if mounts=$(docker inspect "$SANDBOX_NAME" --format \
        '{{range .Mounts}}{{.Source}}|{{.Destination}}{{println}}{{end}}' \
        2>/dev/null); then
        local source=""
        local destination=""
        local path=""
        while IFS='|' read -r source destination; do
            [[ -n "$source$destination" ]] || continue
            for path in "$source" "$destination"; do
                case "$path" in
                    */.aws|*/.aws/*|*/.ssh|*/.ssh/*|*/.env|*/.env/*|/var/run/docker.sock)
                        echo "❌ Sensitive mount detected: $source -> $destination"
                        sensitive_found=true
                        validation_failed=true
                        break
                        ;;
                esac
            done
        done <<< "$mounts"
    else
        echo "❌ Sensitive mounts: INSPECTION FAILED"
        sensitive_found=true
        validation_failed=true
    fi
    if [[ "$sensitive_found" == false ]]; then
        echo "✅ No sensitive mounts detected"
    fi

    local memory_limit=""
    if memory_limit=$(docker inspect "$SANDBOX_NAME" \
        --format "{{.HostConfig.Memory}}" 2>/dev/null) && \
        [[ "$memory_limit" =~ ^[1-9][0-9]*$ ]]; then
        echo "✅ Memory limit: $((memory_limit / 1024 / 1024))MiB"
    else
        echo "❌ Memory limit: NOT SET"
        validation_failed=true
    fi

    if docker exec "$SANDBOX_NAME" test ! -w /workspace/src; then
        echo "✅ Source directory: READ-ONLY to the sandbox user"
    else
        echo "❌ Source directory: WRITABLE to the sandbox user"
        validation_failed=true
    fi

    local health_output=""
    if health_output=$(docker exec "$SANDBOX_NAME" \
        python3 /workspace/healthcheck.py 2>&1); then
        printf '%s\n' "$health_output"
        echo "✅ Fail-closed container health check: PASSED"
    else
        printf '%s\n' "$health_output"
        echo "❌ Fail-closed container health check: FAILED"
        validation_failed=true
    fi

    echo ""
    if [[ "$validation_failed" == true ]]; then
        log_error "Security validation failed"
        return 1
    fi
    log_success "Security validation complete"
    return 0
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
    
    echo "🧪 Running the fail-closed Python TCP egress probe:"
    if ! docker exec "$SANDBOX_NAME" \
        python3 /workspace/healthcheck.py --network-only; then
        log_error "Network isolation is not proven; stopping the demonstration"
        return 1
    fi
    
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
            
            if ! require_docker_compose; then
                exit 1
            fi
            
            # Create all necessary files
            create_sandbox_files
            
            log_success "Setup complete!"
            echo ""
            log_info "Next step:"
            echo "  Run the sandbox: $0 start"
            echo "  (Start Docker yourself first if it is not already running.)"
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

# Run main only when executed, allowing focused tests to source the functions.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main "$@"
fi
