# Claude Code Configuration (Asynchronous Research)

Use this checklist to set up Claude Code for "fire-and-forget" research investigations.

## Recommended Setup

1. Create a dedicated research repository (no production secrets).
2. Add an `AGENTS.md` that defines:
   - folder naming conventions
   - deliverables (`prompt.md`, findings `README.md`, scripts/data)
   - preferred tooling (pytest, Node, etc.)
3. Prefer PR-based workflows:
   - one PR per research task
   - clear titles: `research: <topic>`
4. Keep tasks narrowly scoped and testable:
   - "prove X", "measure Y", "compare A vs B"
   - require runnable code + reproducible results

## Prompt Template (Copy/Paste)

```text
Work in new folder: <task-name>/

Goal:
- <one sentence>

Do:
1) Create a minimal reproduction / benchmark harness.
2) Run it and capture results.
3) Summarize findings in README.md.

Deliverables:
- prompt.md (this prompt)
- README.md (findings + how to reproduce)
- code + data + charts (if applicable)
```

