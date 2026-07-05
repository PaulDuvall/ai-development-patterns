# Verification Decisions

The durable record connecting evidence to human judgment. Two things live here: the
**naming-decision ledger** (per pattern: what the industry calls the practice, what the
pipeline recommends, and what the maintainer decided) and the **rubric decision record**
(changes to how evidence is scored and verdicts computed).

Ownership: the **Decision column is written only by humans** — the pipeline never decides.
Verification runs refresh the data columns (Alignment, Industry terms, Recommendation) in
their batched sources PR when evidence changes. CI (`tests/test_evidence_files.py`) requires
a ledger row for every `verified` pattern whose `naming_alignment` is not `strong`, so a new
naming signal cannot land without appearing here.

## Naming-decision ledger

Alignment values come from each pattern's `evidence/<slug>.yaml`; rules are defined in
[README.md](README.md). Rename mechanics, when a rename is accepted, follow
`PATTERN_MIGRATION_GUIDE.md`.

| Pattern | Alignment | Industry terms | Recommendation | Decision |
|---------|-----------|----------------|----------------|----------|
| Readiness Assessment | weak | *agent readiness* (Factory.ai, Kodus); *AI readiness assessment* (Microsoft — org-level, a name collision) | **Rename → Agent Readiness** (strong case: most sources use the term; current name collides with org-level AI readiness) | Pending |
| Progressive Enhancement | weak | no stable industry name; documented collision with the web-design term | **Rename → Incremental Generation** (strong case: naming vacuum plus collision) | Pending |
| Context Persistence | weak | *memory* / *agent memory* (Anthropic, Cline, MemGPT) | **Rename → Agent Memory** (moderate case: "memory" unanimous across sources; cost: breaks the Context family pairing) | Pending |
| Codified Rules | weak | `AGENTS.md` (open format), *Rules* (Cursor), `CLAUDE.md` (Anthropic), *repository custom instructions* (GitHub Copilot) | Keep + alias | Accepted 2026-07-04 — alias mentions merged (PR #29) |
| Tool Integration | weak | *tool use* (Anthropic), *function calling* (OpenAI), *MCP* | Keep + alias | Accepted 2026-07-04 — alias mentions merged (PR #29) |
| Planned Implementation | weak | *plan mode* (Cursor, Claude Code) | Keep + alias (a Plan Mode rename would strain the principle-not-vendor-feature rule) | Accepted 2026-07-04 — alias mention merged (PR #29) |
| Security Sandbox | weak | *sandboxing*, *devcontainer isolation*, *execution isolation*, *microVM sandbox*, *action-sandboxing* | Keep (half the sources use our word; no spec-compliant candidate beats it) | Accepted 2026-07-04 |
| Issue Generation | weak | no dominant competing term | Keep | Accepted 2026-07-04 |
| Developer Lifecycle | weak | *AI-DLC* (AWS), spec-driven workflow framings | Keep (note the scope overlap with Spec-Driven Development) | Accepted 2026-07-04 |

Spec-Driven Development is the only verified pattern with `strong` alignment and therefore
needs no row. Tool Integration, Planned Implementation, and Developer Lifecycle have zero
`named` sources, so their alignment recomputes to `aliased` (the strongest rename signal)
when the pipeline next regenerates their evidence — revisit their Keep decisions then.

## Rubric decision record

### 2026-07-04 — four decisions following the tooling review

Approved by the maintainer; all four are **generation-gated**: they apply to evidence files
carrying `last_checked` (everything the pipeline writes going forward), while legacy
`verified:` files keep the original rules until regenerated. Enforced in
`scripts/validate-evidence.py`; human-readable rules in [README.md](README.md).

1. **`naming_alignment` gains `aliased`** — zero `named` entries while stable industry names
   exist. Separates "nobody uses our name" (rename signal) from "half use our name" (both
   previously labeled `weak`).
2. **`verified` requires a practitioner-side source** — at least one T3–T5 entry alongside
   the strong tier. A single vendor's own documentation can no longer verify a pattern.
3. **Keep the 0–45 weighted score, add `tier_counts`** — the score remains the verdict input
   for continuity, but files and reports carry a per-tier breakdown so readers never
   reverse-engineer the arithmetic. Rejected alternative: replacing the score with
   "≥1 T1–T3 entry AND ≥3 total entries" (reproduces all verdicts to date but changes the
   documented semantics of every file).
4. **Admission rigor** — `mechanism_quote` required on `named` T1/T2 entries (a name
   collision alone must not earn top weights); one entry per organization per file; a
   non-fatal validator NOTE whenever one URL is scored across multiple patterns.

Context: the full review and rationale are in PR #33 and the evidence PRs #19–#28.
