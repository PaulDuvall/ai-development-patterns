# Loop Engineering Checklist

*Safe autonomous loops — three principles, each check named with the primitive that enforces it.*

This is the field companion to the [Loop Engineering Lens](../README.md#loop-engineering-lens). Each check pairs a generic principle (vendor-neutral) with the Claude Code primitive (in backticks) that enforces it. The runnable wrapper is [the wrapper-script example](../examples/bounded-autonomy/), and the bounding discipline is the [Bounded Autonomy](../README.md#bounded-autonomy) pattern.

## Principle 1 — No executable done-check, no loop

Gate the loop before you start it. Run the Intake Gate as a GO/NO-GO: if any row fails, you do not have a loop yet.

| Check | Pass if | If not |
|-------|---------|--------|
| State-driven iteration | Next step depends on tool output | Otherwise a slash command or script |
| Executable done-check | One command exits 0 or 1 | No exit code, no loop |
| Reversible failure | Worktree or branch, revert is cheap | Human-only recovery means stop |
| Tools + context wired | MCP, CLAUDE.md, allowed tools set | Wire these first |
| Worth repeating | Recurring, not one-off | One-off, run it interactively |

### Convergence Contract

- [ ] Observable goal, not a verb. Returns 200 on `/health` — a state the run can check. `CLAUDE.md`
- [ ] Acceptance criteria written first. Spec or plan before code. `plan mode`
- [ ] Intent, code, test kept separate. The test arbitrates. `spec / code / test`

## Principle 2 — The test arbitrates, not the model

One task, deterministic verification, no self-certification.

### Scope each loop tightly

- [ ] One task per loop. One subagent per concern. `.claude/agents/`
- [ ] Split large work into gates. Plan, then execute step by step. `TodoWrite`
- [ ] Separate discovery from execution. Read-only plan first. `--permission-mode plan`
- [ ] Freeze characterization tests before refactors. Pin behavior, then change. `git commit`
- [ ] Never write the test and the change in one pass. A verifier subagent did not author the code. `SubagentStop`

### Verify with hooks

- [ ] Sync trunk before verify. Pull or rebase, then check. `SessionStart`
- [ ] Lint, types, tests, security on every edit. `PostToolUse`
- [ ] Block premature completion. Hold the agent until checks pass. `Stop (exit 2)`
- [ ] Emit a signed evidence bundle. Spec + commit SHA + executed test. `--output-format json`

## Principle 3 — Your verification reach sets the autonomy ceiling

Bound the loop. Humans own the edges.

### Bound the loop

- [ ] Cap agentic turns. 5 pre-commit, 40 CI, 120 overnight. `--max-turns`
- [ ] Cap spend. Hard dollar limit, run aborts. `--max-budget-usd`
- [ ] Stall + divergence detector. Stop when stuck or drifting. `Stop`
- [ ] Retry only recoverable errors. In the wrapper script.

### State and observability

- [ ] State in git and files. The working tree is the state. `git`
- [ ] Commit at phase boundaries. One commit per milestone. `git commit`
- [ ] Isolated worktree per agent. No cross-agent collisions. `--worktree`
- [ ] Capture cost, turns, session. Machine-readable result. `--output-format json`
- [ ] Diagnosable failure trail. Transcript plus hook logs. `transcript_path`

### Humans own the edges

- [ ] Upstream: humans author versioned policy. Deny wins over allow. `.claude/settings.json`
- [ ] Mid-loop: human escape hatch. Permission prompts, Esc to interrupt. `--permission-mode`
- [ ] Downstream: CI gate clears, human approves the merge. `--allowedTools`

> Principles drive the checks. If a check does not serve a principle above it, cut it.

## Related

- [Loop Engineering Lens](../README.md#loop-engineering-lens)
- [Bounded Autonomy](../README.md#bounded-autonomy)
- [the wrapper-script example](../examples/bounded-autonomy/)
