#!/usr/bin/env python3
"""Summarize deterministic parallel-agent simulator progress."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time
from typing import Any


def load_shared_memory(path: Path) -> dict[str, Any]:
    """Read only simulated fixture state, treating an absent file as empty."""
    if not path.exists():
        return {"agents": {}, "version": 1}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("agents", {}), dict):
        raise ValueError("shared memory must be a JSON object with an agents object")
    if data.get("version") != 1:
        raise ValueError("shared-memory version must be 1")
    unknown_keys = sorted(set(data) - {"agents", "version"})
    if unknown_keys:
        raise ValueError(f"shared memory contains unsupported keys: {unknown_keys}")
    for agent_id, result in data.get("agents", {}).items():
        if not isinstance(agent_id, str) or not isinstance(result, dict):
            raise ValueError("every shared-memory agent result must be an object")
        if result.get("status") != "fixture_generated":
            raise ValueError(
                f"agent {agent_id!r} status must be 'fixture_generated'"
            )
        if result.get("execution") != "simulated":
            raise ValueError(f"agent {agent_id!r} execution must be 'simulated'")
    return data


def collect_artifacts(watch_dir: Path) -> list[str]:
    """Return stable, relative paths for regular workspace artifacts."""
    if not watch_dir.exists():
        return []
    artifacts = []
    for path in watch_dir.rglob("*"):
        if path.is_symlink():
            continue
        if path.is_file():
            artifacts.append(path.relative_to(watch_dir).as_posix())
    return sorted(artifacts)


def build_report(watch_dir: Path, memory_path: Path) -> dict[str, Any]:
    memory = load_shared_memory(memory_path)
    agents = memory.get("agents", {})
    artifacts = collect_artifacts(watch_dir)
    return {
        "agent_count": len(agents),
        "agents": agents,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "execution": "simulated",
        "mode": "deterministic-local-simulator",
        "model_calls": 0,
        "provider_api_calls": 0,
        "status": "fixture_generated" if agents else "awaiting_fixtures",
    }


def write_report(report_dir: Path, report: dict[str, Any]) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    destination = report_dir / "parallel-agent-status.json"
    serialized = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if not destination.exists() or destination.read_text(encoding="utf-8") != serialized:
        temporary = report_dir / f".{destination.name}.{os.getpid()}.tmp"
        temporary.write_text(serialized, encoding="utf-8")
        os.replace(temporary, destination)
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch-dir", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument(
        "--shared-memory",
        type=Path,
        default=Path(
            os.environ.get("SHARED_MEMORY_PATH", "/shared/agent_memory.json")
        ),
    )
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.interval <= 0:
        raise ValueError("--interval must be greater than zero")

    while True:
        report = build_report(args.watch_dir, args.shared_memory)
        destination = write_report(args.report_dir, report)
        print(
            f"wrote {destination}: "
            f"{report['agent_count']} agents, {report['artifact_count']} artifacts",
            flush=True,
        )
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
