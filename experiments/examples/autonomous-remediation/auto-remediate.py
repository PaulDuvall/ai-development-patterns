#!/usr/bin/env python3
"""PostToolUse hook: detect code-quality violations and ask the LLM to fix them.

Reads the Claude Code event JSON on stdin. On clean files, exits 0. On
violations, emits a JSON block-decision with a structured report the LLM
can act on in the same session.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detectors import run_all_detectors
from detectors.fixes import FIX_HINTS, format_report

STATE_FILE = Path("/tmp/.auto-remediate-state.json")
RETRY_BUDGET = 3


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return {}


def save_state(state: dict) -> None:
    try:
        STATE_FILE.write_text(json.dumps(state))
    except OSError as exc:
        print(f"auto-remediate: could not persist state ({exc})", file=sys.stderr)


def record_block(file_path: str) -> int:
    state = load_state()
    entry = state.get(file_path, {"count": 0, "last": 0})
    if time.time() - entry["last"] > 600:
        entry["count"] = 0
    entry["count"] += 1
    entry["last"] = time.time()
    state[file_path] = entry
    save_state(state)
    return entry["count"]


def clear_block(file_path: str) -> None:
    state = load_state()
    state.pop(file_path, None)
    save_state(state)


def read_event() -> dict:
    try:
        return json.load(sys.stdin)
    except ValueError:
        return {}


def safe_detect(file_path: str) -> list | None:
    try:
        return run_all_detectors(file_path)
    except Exception as exc:
        print(f"auto-remediate: detector crashed ({exc}) — failing open", file=sys.stderr)
        return None


def emit_exhaustion_notice(file_path: str, blocks: int) -> None:
    message = (
        f"auto-remediate: {file_path} has been blocked {blocks} times. "
        "Suggested actions: raise the rule threshold in thresholds.yml, "
        "add the file to skip_directories, or add an inline '# rule: ignore' marker."
    )
    print(message, file=sys.stderr)
    clear_block(file_path)


def emit_block(file_path: str, violations: list) -> None:
    print(json.dumps({
        "decision": "block",
        "reason": format_report(file_path, violations, FIX_HINTS),
    }))


def main() -> int:
    event = read_event()
    file_path = event.get("tool_input", {}).get("file_path", "")
    if not file_path or not os.path.isfile(file_path):
        return 0

    violations = safe_detect(file_path)
    if violations is None:
        return 0
    if not violations:
        clear_block(file_path)
        return 0

    blocks = record_block(file_path)
    if blocks > RETRY_BUDGET:
        emit_exhaustion_notice(file_path, blocks)
        return 0

    emit_block(file_path, violations)
    return 0


if __name__ == "__main__":
    sys.exit(main())
