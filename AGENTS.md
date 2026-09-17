# Agent Instructions

## Task Tracking

Tasks live in `.tasks/backlog.jsonl` — an append-only JSONL file, one task per line, git-tracked. There is no daemon and no database: the file is the record and git is the history.

Do NOT use TodoWrite, TaskCreate, markdown TODO lists, or `bd`/beads — this repo migrated off beads on 2026-08-17.

**A task's state is its LAST line.** The file is append-only, so `grep '"status": *"open"'` also matches tasks that were later closed, over-reporting the open set. Always fold last-line-wins:

```bash
python3 -c "import json;last={};[last.__setitem__(t['id'],t) for t in map(json.loads,filter(str.strip,open('.tasks/backlog.jsonl')))];print('\n'.join(f\"{i}  {t['title'][:68]}\" for i,t in last.items() if t['status']=='open'))"
```

Close a task by APPENDING a new line with `status` set to `closed`; never edit or delete an existing line. Work discovered while doing another task gets its own line with `discovered_from` set to the parent id.

**Schema:** `{id, title, status, blocks[], depends_on[], spec_ref, created, priority, description, discovered_from?}` — `status` is `open` or `closed`; `priority` is 1 (most urgent) to 4; a task is ready when every id in `depends_on` is closed. Issue ids keep their original beads form so existing commit messages still resolve.

The full beads history is archived verbatim at `.tasks/beads-archive.jsonl`.

## Pattern Adoption Evaluation

Run model-backed pattern-adoption research only through the repository-local
`$evaluate-pattern-adoption` skill in an interactive, signed-in local Codex client.
Never run it in GitHub Actions, expose evaluator API keys to the repository, or bypass either the
exact plan approval or the separate draft-PR publication approval. Use no more than three
read-only research subagents at once, keep the root task as the sole writer, and use a fresh
read-only verifier for every batch. GitHub Actions is limited to deterministic validation and
read-only link/content checks for this capability.

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File tasks for remaining work** - Append tasks to `.tasks/backlog.jsonl` for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update task status** - Append `status=closed` lines for finished work
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
