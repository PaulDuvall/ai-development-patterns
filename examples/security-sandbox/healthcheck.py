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
