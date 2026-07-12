# Security Sandbox Implementation

This directory contains a runnable example implementation of the **[Security Sandbox](../../README.md#security-sandbox)** pattern: running AI tools in an isolated container with **no network access** and **no access to host credentials**.

## Overview

The Security Sandbox example provides:
- Complete network isolation (`network_mode: none`)
- Non-root execution (UID 1000)
- Read-only source mounts
- Docker-managed writable test, output, and log volumes

## Files in This Implementation

- `Dockerfile.ai-sandbox` - Minimal container image for secure AI-assisted development
- `.dockerignore` - Default-deny build-context allowlist for the four required inputs
- `docker-compose.basic.yml` - Smallest sandbox with a writable test volume
- `docker-compose.ai-sandbox.yml` - Script-friendly sandbox with output/log volumes
- `docker-compose.parallel-agents.yml` - Multi-agent sandbox with per-agent output volumes
- `ai-sandbox.sh` - Convenience script to build/start/validate the sandbox
- `init-workspace.sh` - Container init script (creates runtime dirs and prints safety status)
- `healthcheck.py` - Basic sandbox health check
- `requirements-sandbox.txt` - Base Python dependencies installed in the image
- `resource-locking.sh` - Example resource locking helper for parallel agents
- `emergency-shutdown.sh` - Emergency shutdown helper

## Prerequisites

Install Docker Engine and either the Docker Compose plugin (`docker compose`) or
the packaged standalone command (`docker-compose`) before using this example:

<https://docs.docker.com/compose/install/>

The management script validates those prerequisites. It does not download
executables, install checksum-free binaries, or modify shell startup files.

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
docker compose -f docker-compose.basic.yml exec ai-development bash
```

The basic service overrides the image's interactive-shell default with a
long-lived foreground process and a minimal init process, so `up -d` remains
running until `docker compose down` while signals and child processes are
handled correctly. Initialization fails closed if network isolation cannot be
proven. The writable test area is a named volume, avoiding auto-created
root-owned host directories on Linux. All three Compose files share the local
image tag `ai-development-patterns/security-sandbox:local`, allowing CI or a
developer to build once and start any configuration with `--no-build`.

Start the parallel example similarly; every agent remains detached and gets a
separate named output volume:

```bash
docker compose -f docker-compose.parallel-agents.yml up -d
docker compose -f docker-compose.parallel-agents.yml exec ai-agent-backend bash
```

`./ai-sandbox.sh validate` checks the network mode, UID, dropped capabilities,
sensitive mounts, memory limit, source writability, and the complete in-container
health check. It reports every finding in one run and returns nonzero if any
check fails; it never prints a successful validation for a partially secure
container.

## Verify Network Isolation

The health check uses Python sockets rather than `ping`, `curl`, or DNS. Its
default probe is the numeric endpoint `1.1.1.1:443`. A successful connection
fails the check. Only an explicit local kernel or policy denial with no visible
non-loopback interface passes. Thus an internal bridge with `eth0` cannot be
mistaken for `network_mode: none`. Timeouts, refused connections, DNS names,
invalid settings, and unexpected errors are reported as **isolation not
proven** and also fail.

Verify the normal `network_mode: none` path after starting the service:

```bash
docker compose -f docker-compose.basic.yml exec -T ai-development \
  python3 /workspace/healthcheck.py --network-only
```

First verify that a Docker-internal bridge with no external egress still fails
because it exposes a non-loopback interface:

```bash
image="$(docker compose -f docker-compose.basic.yml images -q ai-development)"
docker network create --internal sandbox-internal-negative-control
probe_status=0
probe_output="$(docker run --rm \
  --network sandbox-internal-negative-control \
  "$image" python3 /workspace/healthcheck.py --network-only 2>&1)" || \
  probe_status=$?
printf '%s\n' "$probe_output"
test "$probe_status" -eq 1
grep -q 'non-loopback interface(s) are present' <<<"$probe_output"
docker network rm sandbox-internal-negative-control
```

For a reachable-peer negative control, run a local HTTP server and the probe
on the same temporary Docker network. The target is supplied as a numeric
address, so this test does not depend on public egress or DNS:

```bash
docker network create sandbox-egress-negative-control
docker run --detach --rm --name sandbox-egress-target \
  --network sandbox-egress-negative-control \
  "$image" python3 -m http.server 8080
target_ip="$(docker inspect --format \
  '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
  sandbox-egress-target)"

probe_status=0
probe_output="$(docker run --rm \
  --network sandbox-egress-negative-control \
  --env SANDBOX_NETWORK_PROBE_HOST="$target_ip" \
  --env SANDBOX_NETWORK_PROBE_PORT=8080 \
  "$image" python3 /workspace/healthcheck.py --network-only 2>&1)" || \
  probe_status=$?
printf '%s\n' "$probe_output"
test "$probe_status" -eq 1
grep -q 'TCP egress reached' <<<"$probe_output"

docker rm --force sandbox-egress-target
docker network rm sandbox-egress-negative-control
```

The configurable probe variables are `SANDBOX_NETWORK_PROBE_HOST` (a numeric
IPv4 or IPv6 address), `SANDBOX_NETWORK_PROBE_PORT`, and the optional bounded
`SANDBOX_NETWORK_PROBE_TIMEOUT`.

## Inspect and Export Writable Data

All writable work areas use Docker-managed named volumes. They initialize from
the image with UID 1000 ownership and persist across a normal `docker compose
down`. The full configuration keeps `/workspace/generated` and
`/workspace/logs` writable while the rest of its container filesystem is
read-only. Basic Compose uses `/workspace/tests`; parallel Compose uses an
isolated `/output` volume per agent. Source remains read-only, and no host
credential paths are mounted. The image's source directory and trusted health
and initialization scripts remain root-owned and non-writable to UID 1000.

Inspect the volumes through the non-root service:

```bash
docker compose -f docker-compose.ai-sandbox.yml exec -T ai-development \
  ls -la /workspace/generated /workspace/logs
docker compose -f docker-compose.basic.yml exec -T ai-development \
  ls -la /workspace/tests
docker compose -f docker-compose.parallel-agents.yml exec -T \
  ai-agent-backend ls -la /output
```

Copy generated artifacts to a new host directory when they are ready for
review:

```bash
mkdir -p exported-generated
docker compose -f docker-compose.ai-sandbox.yml cp \
  ai-development:/workspace/generated/. ./exported-generated/
mkdir -p exported-backend
docker compose -f docker-compose.parallel-agents.yml cp \
  ai-agent-backend:/output/. ./exported-backend/
```

To seed Basic Compose with existing tests, copy them into the running non-root
service instead of bind-mounting a potentially root-owned directory:

```bash
docker compose -f docker-compose.basic.yml cp \
  /path/to/tests/. ai-development:/workspace/tests/
```

`./ai-sandbox.sh clean` removes the full configuration's volumes. For any
Compose file, `docker compose -f <compose-file> down --volumes` deliberately
removes the volumes declared by that file and their contents.

## Notes

- `src/` is a small placeholder directory you can replace with your own code mount.
- Writable test data, generated output, and runtime logs live in named volumes and are not committed.
