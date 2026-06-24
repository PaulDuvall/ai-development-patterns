#!/usr/bin/env bash
set -euo pipefail

# Executable done-check: the single command that arbitrates the loop.
# Exit 0 when the observable goal is met; exit 1 otherwise. The agent never
# self-certifies — this script does.
#
# Each gate runs only if its tool is present, so the script parses and runs
# cleanly in any checkout. Replace the placeholders with your real commands.

have() { command -v "$1" >/dev/null 2>&1; }

# Gate 1: lint (computational guard)
if have ruff; then
  ruff check . || { echo "done-check: lint failed" >&2; exit 1; }
fi

# Gate 2: types
if have mypy; then
  mypy . || { echo "done-check: type check failed" >&2; exit 1; }
fi

# Gate 3: tests. Exit code 5 means "no tests collected" — not a failure here.
if have pytest; then
  rc=0; pytest -q || rc=$?
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 5 ]; then
    echo "done-check: tests failed" >&2; exit 1
  fi
fi

# Gate 4: the observable goal. Replace with a real state check, e.g. a health
# probe that returns 200. Here we treat the presence of a marker file as the goal.
if [ ! -f .goal-met ]; then
  echo "done-check: observable goal not yet met (.goal-met missing)" >&2
  exit 1
fi

echo "done-check: all gates pass — goal met"
exit 0
