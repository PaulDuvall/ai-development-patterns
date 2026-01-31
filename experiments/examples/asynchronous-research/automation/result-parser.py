#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


def find_tasks(repo_root: Path) -> list[Path]:
    tasks: list[Path] = []
    for candidate in repo_root.iterdir():
        if not candidate.is_dir():
            continue
        if candidate.name.startswith("."):
            continue
        if (candidate / "prompt.md").exists() or (candidate / "README.md").exists():
            tasks.append(candidate)
    return sorted(tasks)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize research task folders.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root to scan")
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    tasks = find_tasks(repo_root)

    print(f"Found {len(tasks)} candidate task folder(s) in {repo_root}")
    for task in tasks:
        prompt = "prompt.md" if (task / "prompt.md").exists() else "-"
        readme = "README.md" if (task / "README.md").exists() else "-"
        print(f"- {task.name}/ ({prompt}, {readme})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

