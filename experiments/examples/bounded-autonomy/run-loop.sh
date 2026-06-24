#!/usr/bin/env bash
set -euo pipefail

# Bounded Autonomy wrapper: a bounded loop around an agent command.
# Every iteration runs the agent, then the executable done-check. The loop
# exits 0 the moment the done-check passes, or aborts when a bound trips.

# --- Caps (read from env, sane defaults) ---
MAX_TURNS="${MAX_TURNS:-40}"            # hard cap on agent iterations
MAX_BUDGET_USD="${MAX_BUDGET_USD:-5.00}" # hard spend cap; run aborts when exceeded
MAX_WALL_SECS="${MAX_WALL_SECS:-1800}"  # wall-clock cap (default 30 min)
STALL_WINDOW="${STALL_WINDOW:-3}"       # abort after N iterations with no new commit
AGENT_CMD="${AGENT_CMD:-./agent-once.sh}"          # one agent turn; prints a per-turn COST line
DONE_CHECK="${DONE_CHECK:-./done-check.sh}"        # executable done-check (exit 0 = goal met)
RECOVERABLE_EXIT_CODES="${RECOVERABLE_EXIT_CODES:-1 75}" # retry only these; anything else aborts

# Example (Claude Code): point AGENT_CMD at a wrapper that invokes claude with
# matching caps and a machine-readable summary, e.g.:
#   AGENT_CMD='claude -p "continue the task" \
#     --max-turns 5 --max-budget-usd 1.00 --output-format json > turn.json'
# Then parse turn.json for total_cost_usd and emit it as the COST line below.

# --- State ---
turns=0
cost="0"
start_ts=$(date +%s)
stall_count=0
last_sha="$(git rev-parse HEAD 2>/dev/null || echo none)"
outcome="unknown"

is_recoverable() {
  local code="$1"
  for ok in $RECOVERABLE_EXIT_CODES; do
    [ "$code" = "$ok" ] && return 0
  done
  return 1
}

write_evidence() {
  local wall=$(( $(date +%s) - start_ts ))
  cat > evidence.json <<EOF
{
  "turns": ${turns},
  "cost": ${cost},
  "wall_secs": ${wall},
  "last_sha": "${last_sha}",
  "outcome": "${outcome}"
}
EOF
  echo "evidence.json written: outcome=${outcome} turns=${turns} cost=${cost}"
}
trap write_evidence EXIT

while : ; do
  # Bound: turn cap
  if [ "$turns" -ge "$MAX_TURNS" ]; then outcome="max_turns"; exit 2; fi
  # Bound: wall-clock cap
  if [ "$(( $(date +%s) - start_ts ))" -ge "$MAX_WALL_SECS" ]; then outcome="max_wall"; exit 2; fi
  # Bound: spend cap
  if awk "BEGIN{exit !(${cost} >= ${MAX_BUDGET_USD})}"; then outcome="max_budget"; exit 2; fi

  turns=$(( turns + 1 ))
  echo "--- iteration ${turns} (cost=${cost}) ---"

  # Run one agent turn; capture its exit code without tripping set -e
  set +e
  iter_cost="$("$AGENT_CMD" 2>/dev/null | awk -F= '/^COST=/{print $2}')"
  rc=$?
  set -e
  [ -n "${iter_cost:-}" ] && cost="$(awk "BEGIN{printf \"%.4f\", ${cost} + ${iter_cost}}")"

  # Retry only recoverable errors; non-recoverable aborts.
  if [ "$rc" -ne 0 ]; then
    if is_recoverable "$rc"; then
      echo "recoverable error (exit ${rc}); retrying"
      continue
    fi
    outcome="agent_error_${rc}"; exit "$rc"
  fi

  # Commit at phase boundary if the agent left any change (tracked or new file).
  if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -q -m "chore(loop): phase boundary at iteration ${turns}"
  fi

  # Stall detector: abort if HEAD has not advanced for STALL_WINDOW iterations.
  head_sha="$(git rev-parse HEAD 2>/dev/null || echo none)"
  if [ "$head_sha" = "$last_sha" ]; then
    stall_count=$(( stall_count + 1 ))
    [ "$stall_count" -ge "$STALL_WINDOW" ] && { outcome="stalled"; exit 2; }
  else
    stall_count=0
    last_sha="$head_sha"
  fi

  # The test arbitrates: exit 0 the moment the observable goal is met.
  if "$DONE_CHECK"; then outcome="done"; exit 0; fi
done
