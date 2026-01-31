# Security Sandbox Implementation

This directory contains a runnable example implementation of the **[Security Sandbox](../../README.md#security-sandbox)** pattern: running AI tools in an isolated container with **no network access** and **no access to host credentials**.

## Overview

The Security Sandbox example provides:
- Complete network isolation (`network_mode: none`)
- Non-root execution (UID 1000)
- Read-only source mounts
- Separate writable output and log mounts

## Files in This Implementation

- `Dockerfile.ai-sandbox` - Minimal container image for secure AI-assisted development
- `docker-compose.basic.yml` - Smallest, single-container sandbox
- `docker-compose.ai-sandbox.yml` - Script-friendly sandbox configuration
- `docker-compose.parallel-agents.yml` - Example multi-agent sandbox with isolated outputs
- `ai-sandbox.sh` - Convenience script to build/start/validate the sandbox
- `init-workspace.sh` - Container init script (creates runtime dirs and prints safety status)
- `healthcheck.py` - Basic sandbox health check
- `requirements-sandbox.txt` - Base Python dependencies installed in the image
- `resource-locking.sh` - Example resource locking helper for parallel agents
- `emergency-shutdown.sh` - Emergency shutdown helper

## Quick Start

From the repository root:

```bash
./examples/security-sandbox/ai-sandbox.sh start
./examples/security-sandbox/ai-sandbox.sh shell
```

Or run the minimal Compose file directly:

```bash
cd examples/security-sandbox
docker compose -f docker-compose.basic.yml up -d
docker compose exec ai-development bash
```

## Notes

- `src/` is a small placeholder directory you can replace with your own code mount.
- `generated/` and `logs/` are created at runtime and are intentionally not committed.
