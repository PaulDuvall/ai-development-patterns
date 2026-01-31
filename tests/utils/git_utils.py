from __future__ import annotations

import subprocess
from pathlib import Path


def git_ls_files(repo_root: Path, path: str | None = None) -> list[str]:
    """
    Return git-tracked file paths (relative to repo_root).

    If `path` is provided, it is passed to `git ls-files` to scope results.
    """
    repo_root = Path(repo_root)
    cmd = ["git", "-C", str(repo_root), "ls-files"]
    if path:
        cmd.append(path)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def git_tracked_child_dirs(repo_root: Path, base_dir: str) -> list[Path]:
    """
    Return git-tracked immediate child directories under `base_dir`.

    Example:
      base_dir="examples" yields:
        [repo_root/examples/codified-rules, repo_root/examples/security-sandbox, ...]
    """
    base_dir = base_dir.strip("/").replace("\\", "/")
    prefix = f"{base_dir}/" if base_dir else ""

    tracked_files = git_ls_files(repo_root, base_dir if base_dir else None)
    child_names: set[str] = set()

    for path in tracked_files:
        if prefix and not path.startswith(prefix):
            continue
        remainder = path[len(prefix) :] if prefix else path
        if "/" not in remainder:
            continue
        child_names.add(remainder.split("/", 1)[0])

    repo_root = Path(repo_root)
    return [repo_root / base_dir / name for name in sorted(child_names)]

