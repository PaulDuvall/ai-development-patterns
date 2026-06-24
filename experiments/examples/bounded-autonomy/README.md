# Bounded Autonomy — Wrapper-Script Example

A runnable, tool-agnostic example of [Bounded Autonomy](../../README.md#bounded-autonomy): a thin wrapper that runs an agent in a loop, lets the agent work freely *inside* hard bounds, and lets a deterministic done-check — never the model — decide when the loop is finished.

This is the "wrapper script" that the [Loop Engineering Checklist](../../../docs/loop-engineering-checklist.md) refers to, and a concrete instance of the [Loop Engineering Lens](../../../README.md#loop-engineering-lens). The lens has three principles; this directory maps each one to an artifact you can run.

## The three principles, mapped to files

| Principle | What it means | Where it lives here |
|-----------|---------------|---------------------|
| **01 — No executable done-check, no loop.** Gate the loop before you start it. | The goal is an observable *state* a command can check, not a verb. | `done-check.sh` exits 0 only when the goal state holds. The loop refuses to declare success any other way. |
| **02 — The test arbitrates, not the model.** Deterministic verification, no self-certification. | The agent proposes; a separate check disposes. | `run-loop.sh` runs `done-check.sh` every iteration and only exits 0 when it passes. `stop-hook.sh` blocks the agent from quitting early. |
| **03 — Your verification reach sets the autonomy ceiling.** Bound the loop; humans own the edges. | Caps on turns, spend, wall-clock, and stall. State in git. Policy authored by humans. | `run-loop.sh` enforces four caps + a stall detector and writes `evidence.json`. `settings.example.json` holds the human-authored allow/deny policy. |

## Files

- **`run-loop.sh`** — the bounded wrapper. Runs the agent in a loop under four caps (turns, spend, wall-clock, stall), retries only recoverable errors, commits at phase boundaries, runs the done-check each iteration, and writes a machine-readable `evidence.json`.
- **`done-check.sh`** — the executable done-check. Runs lint, types, and tests, then verifies the observable goal. Exit 0 = done, exit 1 = keep going.
- **`stop-hook.sh`** — a stop hook that blocks premature completion: runs the done-check and exits 2 (blocking) if the goal is not yet met.
- **`settings.example.json`** — a human-authored allow/deny policy that wires the stop hook and constrains what the agent may do.
- **`evidence.json`** — *(generated)* the run summary: turns, accumulated cost, wall seconds, last commit SHA, and outcome.

## How to run

Provide your own one-turn agent as `agent-once.sh` (or set `AGENT_CMD`). It does one unit of work and prints a single `COST=<usd>` line so the wrapper can accumulate spend. A trivial stand-in:

```bash
cat > agent-once.sh <<'EOF'
#!/usr/bin/env bash
# do one increment of work, then signal cost
echo "work $(date +%s)" >> log.txt
touch .goal-met            # in a real run, the agent reaches the goal over many turns
echo "COST=0.05"
EOF
chmod +x agent-once.sh *.sh

git init -q && git commit -q --allow-empty -m init

MAX_TURNS=40 MAX_BUDGET_USD=5.00 MAX_WALL_SECS=1800 STALL_WINDOW=3 ./run-loop.sh
cat evidence.json
```

The loop exits **0** with `outcome: "done"` once `done-check.sh` passes, or non-zero when a bound trips (`max_turns`, `max_budget`, `max_wall`, `stalled`) or the agent hits a non-recoverable error. Either way, `evidence.json` is written on exit.

### Caps (environment variables)

| Var | Default | Bound |
|-----|---------|-------|
| `MAX_TURNS` | `40` | hard cap on agent iterations |
| `MAX_BUDGET_USD` | `5.00` | accumulated spend; run aborts when exceeded |
| `MAX_WALL_SECS` | `1800` | wall-clock ceiling |
| `STALL_WINDOW` | `3` | abort after N iterations with no new commit |
| `RECOVERABLE_EXIT_CODES` | `1 75` | agent exit codes worth retrying; anything else aborts |
| `AGENT_CMD` | `./agent-once.sh` | one agent turn |
| `DONE_CHECK` | `./done-check.sh` | the arbitrating check |

## Mapping the generic mechanisms to Claude Code

This example leads with the generic mechanism; here is how each one binds to a specific Claude Code flag or hook. The principles are the same with any agent runner — only the flag names change.

| Generic mechanism (in this example) | Claude Code instance |
|-------------------------------------|----------------------|
| Agent-turn cap (`MAX_TURNS`) | `--max-turns` |
| Spend/budget cap (`MAX_BUDGET_USD`) | `--max-budget-usd` |
| Machine-readable run summary (`evidence.json`) | `--output-format json` (parse `total_cost_usd`, `num_turns`, `session_id`) |
| A stop hook that blocks completion (`stop-hook.sh`, exit 2) | `Stop` hook in `.claude/settings.json` |
| Versioned allow/deny policy (`settings.example.json`) | `permissions.allow` / `permissions.deny` in `.claude/settings.json` |
| Isolated git worktree per agent | `--worktree` (or `git worktree add`) |
| Interactive escape hatch | `--permission-mode` + permission prompts (Esc to interrupt) |
| State in git / commit at phase boundaries | plain `git commit` between milestones |

The `AGENT_CMD` block at the top of `run-loop.sh` shows how you would point the wrapper at `claude` with `--max-turns`, `--max-budget-usd`, and `--output-format json`, then feed the reported cost back into the spend cap.

## See also

- Pattern: [Bounded Autonomy](../../README.md#bounded-autonomy)
- Lens: [Loop Engineering Lens](../../../README.md#loop-engineering-lens)
- Checklist: [Loop Engineering Checklist](../../../docs/loop-engineering-checklist.md)
