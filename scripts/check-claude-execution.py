#!/usr/bin/env python3
"""Fail closed when Claude Code reports an unsuccessful research execution.

The Claude Code Action can currently emit a result whose subtype is ``success``
while ``is_error`` is true.  The action treats that combination as successful,
so workflows must independently inspect its local execution file before using
any candidate output.  This checker deliberately prints only fixed diagnostic
categories; raw model output may contain secrets or untrusted web content.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any


MAX_EXECUTION_BYTES = 64 * 1024 * 1024


def _diagnostic_text(result: dict[str, Any]) -> str:
    """Return bounded text used only to choose a safe diagnostic category."""
    values: list[str] = []
    for key in ("result", "errors"):
        value = result.get(key)
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, list):
            values.extend(item for item in value if isinstance(item, str))
    return " ".join(values)[:65_536].casefold()


def _classify_failure(result: dict[str, Any]) -> str:
    text = _diagnostic_text(result)
    classifiers = (
        (
            "authentication_failed",
            (
                "authentication",
                "invalid x-api-key",
                "invalid api key",
                "unauthorized",
                "status 401",
                " 401",
            ),
        ),
        (
            "authorization_failed",
            ("forbidden", "permission denied", "status 403", " 403"),
        ),
        (
            "billing_or_credit_error",
            (
                "credit",
                "billing",
                "payment required",
                "usage limit",
                "status 402",
                " 402",
            ),
        ),
        ("rate_limited", ("rate_limit", "rate limit", "status 429", " 429")),
        ("service_overloaded", ("overloaded", "status 529", " 529")),
        ("request_timed_out", ("timed out", "timeout")),
        ("turn_limit_reached", ("max turns", "maximum turns", "error_max_turns")),
        ("invalid_request", ("invalid_request", "invalid request", "status 400", " 400")),
    )
    for category, markers in classifiers:
        if any(marker in text for marker in markers):
            return category

    model_markers = (
        "not found",
        "not_found",
        "does not exist",
        "not available",
        "access",
    )
    if "model" in text and any(marker in text for marker in model_markers):
        return "model_unavailable"

    subtype = result.get("subtype")
    if subtype == "error_max_turns":
        return "turn_limit_reached"
    if subtype == "error_max_budget_usd":
        return "budget_limit_reached"
    if subtype == "error_during_execution":
        return "execution_error"
    return "unspecified_execution_error"


def validate_execution_file(
    path: Path | None, *, runner_temp: Path | None = None
) -> str | None:
    """Return a safe failure category, or ``None`` for a genuine success."""
    if path is None:
        return "missing_execution_file"
    try:
        stat = path.lstat()
    except OSError:
        return "missing_execution_file"
    if path.is_symlink() or not path.is_file():
        return "invalid_execution_file"
    if runner_temp is not None:
        try:
            expected = (runner_temp / "claude-execution-output.json").resolve()
            actual = path.resolve(strict=True)
        except OSError:
            return "invalid_execution_file"
        if actual != expected:
            return "unexpected_execution_file_path"
    if stat.st_size > MAX_EXECUTION_BYTES:
        return "oversized_execution_file"

    try:
        events = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "invalid_execution_file"
    if not isinstance(events, list) or not events:
        return "invalid_execution_file"

    results = [
        event
        for event in events
        if isinstance(event, dict) and event.get("type") == "result"
    ]
    if len(results) != 1 or events[-1] is not results[0]:
        return "missing_final_result"
    result = results[0]
    if result.get("subtype") == "success" and result.get("is_error") is False:
        return None
    return _classify_failure(result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Require a genuine successful Claude Code execution result."
    )
    parser.add_argument(
        "execution_file",
        nargs="?",
        default=os.environ.get("CLAUDE_EXECUTION_FILE", ""),
    )
    args = parser.parse_args(argv)

    runner_temp_value = os.environ.get("RUNNER_TEMP", "")
    runner_temp = Path(runner_temp_value) if runner_temp_value else None
    execution_file = Path(args.execution_file) if args.execution_file else None
    failure = validate_execution_file(execution_file, runner_temp=runner_temp)
    if failure is not None:
        print(
            f"::error::Claude research did not complete successfully ({failure})",
            file=sys.stderr,
        )
        return 1
    print("Claude research execution result is successful")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
