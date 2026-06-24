#!/usr/bin/env bash
set -euo pipefail

# Example (Claude Code): a Stop hook. Claude Code runs this when the agent
# tries to finish a turn. Exit 2 blocks completion and feeds the reason back to
# the agent; exit 0 lets it stop. This is the generic "block premature
# completion" mechanism — hold the agent until the done-check passes.

DONE_CHECK="${DONE_CHECK:-./done-check.sh}"

if "$DONE_CHECK"; then
  exit 0
fi

echo "Stop blocked: done-check has not passed. Keep working until ${DONE_CHECK} exits 0." >&2
exit 2
