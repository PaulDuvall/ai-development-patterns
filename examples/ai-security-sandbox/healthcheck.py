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
