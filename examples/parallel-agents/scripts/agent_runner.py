#!/usr/bin/env python3
"""Run one deterministic, provider-free parallel-agent simulation task."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


TASK_ARTIFACTS = {
    "frontend-components": {
        "components/TaskList.tsx": """\
export type Task = {
  id: string;
  title: string;
  status: "todo" | "in-progress" | "done";
};

export function TaskList({ tasks }: { tasks: Task[] }) {
  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.id}>{task.title} ({task.status})</li>
      ))}
    </ul>
  );
}
""",
    },
    "backend-api": {
        "server.js": """\
const http = require("node:http");

const tasks = [];
const server = http.createServer((request, response) => {
  response.setHeader("content-type", "application/json");
  if (request.method === "GET" && request.url === "/api/tasks") {
    response.end(JSON.stringify({ tasks }));
    return;
  }
  response.statusCode = 404;
  response.end(JSON.stringify({ error: "not found" }));
});

server.listen(3000, "127.0.0.1");
""",
    },
    "database-schema": {
        "schema.prisma": """\
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Task {
  id          String @id @default(cuid())
  title       String
  description String?
  status      String @default("todo")
}
""",
    },
    "test-suite": {
        "test-plan.md": """\
# Deterministic test plan

- Verify `GET /api/tasks` returns a JSON task collection.
- Verify unknown routes return HTTP 404.
- Verify the task list renders each task exactly once.
- Verify the database task status defaults to `todo`.
""",
    },
}


def validate_fixture_catalog(data: Any) -> dict[str, dict[str, Any]]:
    """Validate the complete config-to-fixture contract before execution."""
    if not isinstance(data, dict):
        raise ValueError("task configuration must be a YAML object")
    expected_header = {
        "contract_version": 1,
        "execution": "simulated",
        "mode": "deterministic-local-simulator",
        "model_calls": 0,
        "provider_api_calls": 0,
    }
    for key, expected in expected_header.items():
        if data.get(key) != expected:
            raise ValueError(
                f"task configuration {key!r} must be {expected!r}"
            )

    raw_tasks = data.get("tasks")
    if not isinstance(raw_tasks, list):
        raise ValueError("task configuration must define a tasks list")

    catalog = {}
    for task in raw_tasks:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str):
            raise ValueError("every task must be an object with a string id")
        task_id = task["id"]
        if task_id in catalog:
            raise ValueError(f"duplicate task id: {task_id}")
        catalog[task_id] = task

    expected_ids = set(TASK_ARTIFACTS)
    actual_ids = set(catalog)
    if actual_ids != expected_ids:
        missing = sorted(expected_ids - actual_ids)
        extra = sorted(actual_ids - expected_ids)
        raise ValueError(
            f"task ids do not match simulator fixtures; missing={missing}, extra={extra}"
        )

    dependency_graph = {}
    for task_id, task in catalog.items():
        dependencies = task.get("dependencies")
        if not isinstance(dependencies, list) or not all(
            isinstance(item, str) for item in dependencies
        ):
            raise ValueError(f"task {task_id!r} dependencies must be a string list")
        if len(dependencies) != len(set(dependencies)):
            raise ValueError(f"task {task_id!r} contains duplicate dependencies")
        unknown = sorted(set(dependencies) - actual_ids)
        if unknown:
            raise ValueError(f"task {task_id!r} has unknown dependencies: {unknown}")
        if task_id in dependencies:
            raise ValueError(f"task {task_id!r} cannot depend on itself")
        dependency_graph[task_id] = dependencies

        contract = task.get("fixture_contract")
        if not isinstance(contract, dict):
            raise ValueError(f"task {task_id!r} must define fixture_contract")
        if contract.get("status") != "fixture_generated":
            raise ValueError(
                f"task {task_id!r} status must be 'fixture_generated'"
            )
        if contract.get("execution") != "simulated":
            raise ValueError(f"task {task_id!r} execution must be 'simulated'")

        raw_artifacts = contract.get("artifacts")
        if not isinstance(raw_artifacts, list) or not raw_artifacts:
            raise ValueError(f"task {task_id!r} must declare fixture artifacts")
        declared = {}
        for artifact in raw_artifacts:
            if not isinstance(artifact, dict):
                raise ValueError(f"task {task_id!r} artifact must be an object")
            relative = artifact.get("path")
            digest = artifact.get("sha256")
            media_type = artifact.get("media_type")
            if not isinstance(relative, str):
                raise ValueError(f"task {task_id!r} artifact path must be a string")
            normalized = PurePosixPath(relative)
            if (
                normalized.is_absolute()
                or ".." in normalized.parts
                or normalized.as_posix() != relative
            ):
                raise ValueError(
                    f"task {task_id!r} has unsafe artifact path: {relative!r}"
                )
            if relative in declared:
                raise ValueError(
                    f"task {task_id!r} declares artifact twice: {relative}"
                )
            if not isinstance(digest, str) or len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError(
                    f"task {task_id!r} artifact {relative!r} has invalid SHA-256"
                )
            if not isinstance(media_type, str) or not media_type:
                raise ValueError(
                    f"task {task_id!r} artifact {relative!r} needs a media type"
                )
            declared[relative] = digest

        expected_artifacts = TASK_ARTIFACTS[task_id]
        if set(declared) != set(expected_artifacts):
            raise ValueError(
                f"task {task_id!r} artifact paths do not match its simulator fixture"
            )
        for relative, content in expected_artifacts.items():
            actual_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            if declared[relative] != actual_digest:
                raise ValueError(
                    f"task {task_id!r} artifact {relative!r} SHA-256 does not "
                    "match the simulator fixture"
                )

    visiting = set()
    visited = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise ValueError(f"task dependency cycle includes {task_id!r}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in dependency_graph[task_id]:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in sorted(catalog):
        visit(task_id)
    return catalog


def load_task(task_file: Path, task_id: str) -> dict[str, Any]:
    """Load and validate one task from the committed task configuration."""
    data = yaml.safe_load(task_file.read_text(encoding="utf-8"))
    catalog = validate_fixture_catalog(data)
    if task_id in catalog:
        return catalog[task_id]
    choices = sorted(catalog)
    raise ValueError(
        f"unknown task {task_id!r}; available tasks: {', '.join(choices)}"
    )


def write_artifacts(workspace: Path, task_id: str) -> list[str]:
    """Write the stable artifact set for a supported simulation task."""
    try:
        artifacts = TASK_ARTIFACTS[task_id]
    except KeyError as exc:
        raise ValueError(f"task {task_id!r} has no deterministic simulator") from exc

    written = []
    for relative, content in sorted(artifacts.items()):
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        written.append(relative)
    return written


def update_shared_memory(
    memory_path: Path,
    *,
    agent_id: str,
    task_id: str,
    artifacts: list[str],
    dependencies: list[str],
    execution: str,
    status: str,
) -> None:
    """Atomically record a stable simulated result under an advisory lock."""
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = memory_path.with_suffix(f"{memory_path.suffix}.lock")
    if memory_path.is_symlink() or lock_path.is_symlink():
        raise ValueError("shared-memory files must not be symbolic links")

    with lock_path.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            if memory_path.exists():
                data = json.loads(memory_path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("shared memory must contain a JSON object")
                if data.get("version") != 1:
                    raise ValueError("shared-memory version must be 1")
                unknown_keys = sorted(set(data) - {"agents", "version"})
                if unknown_keys:
                    raise ValueError(
                        f"shared memory contains unsupported keys: {unknown_keys}"
                    )
            else:
                data = {"version": 1}

            agents = data.setdefault("agents", {})
            if not isinstance(agents, dict):
                raise ValueError("shared-memory agents entry must be an object")
            for existing_agent, result in agents.items():
                if not isinstance(existing_agent, str) or not isinstance(result, dict):
                    raise ValueError(
                        "every shared-memory agent result must be an object"
                    )
                if (
                    result.get("status") != "fixture_generated"
                    or result.get("execution") != "simulated"
                ):
                    raise ValueError(
                        f"shared-memory agent {existing_agent!r} is not a "
                        "simulated fixture result"
                    )
            agents[agent_id] = {
                "artifacts": artifacts,
                "dependencies": dependencies,
                "execution": execution,
                "status": status,
                "task_id": task_id,
            }

            serialized = json.dumps(data, indent=2, sort_keys=True) + "\n"
            temporary = memory_path.with_name(
                f".{memory_path.name}.{os.getpid()}.tmp"
            )
            temporary.write_text(serialized, encoding="utf-8")
            os.replace(temporary, memory_path)
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-file", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(os.environ.get("WORKSPACE_PATH", "/workspace")),
    )
    parser.add_argument(
        "--shared-memory",
        type=Path,
        default=Path(
            os.environ.get("SHARED_MEMORY_PATH", "/shared/agent_memory.json")
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    agent_id = os.environ.get("AGENT_ID", args.task_id)
    task = load_task(args.task_file, args.task_id)
    contract = task["fixture_contract"]
    artifacts = write_artifacts(args.workspace, args.task_id)
    update_shared_memory(
        args.shared_memory,
        agent_id=agent_id,
        task_id=args.task_id,
        artifacts=artifacts,
        dependencies=task["dependencies"],
        execution=contract["execution"],
        status=contract["status"],
    )
    print(
        json.dumps(
            {
                "agent_id": agent_id,
                "artifacts": artifacts,
                "dependencies": task["dependencies"],
                "execution": contract["execution"],
                "mode": "deterministic-local-simulator",
                "model_calls": 0,
                "provider_api_calls": 0,
                "status": contract["status"],
                "task_id": args.task_id,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
