# Verification Decisions

The durable record connecting evidence to human judgment. Two things live here: the
**naming-decision ledger** (per pattern: what the industry calls the practice, what the
pipeline recommends, and what the maintainer decided) and the **rubric decision record**
(changes to how evidence is scored and verdicts computed).

Ownership: the **Decision column is written only by humans** — the pipeline never decides.
Verification runs refresh the data columns (Alignment, Industry terms, Recommendation) in
their single batched evidence PR when evidence changes. CI (`tests/test_evidence_files.py`) requires
a ledger row for every `verified` pattern whose `naming_alignment` is not `strong`, so a new
naming signal cannot land without appearing here.

**After editing this file** (recording a decision, adjusting a recommendation):
run `python3 scripts/generate-verification-status.py` — [STATUS.md](STATUS.md) embeds the
Recommendation and Decision columns and CI fails while it is stale. To gather fresh evidence
behind a recommendation, run the pipeline instead: see "Running a verification" in
[README.md](README.md) (`gh workflow run verify-patterns.yml` or `/verify-patterns`).

## Naming-decision ledger

Alignment values come from each pattern's `evidence/<slug>.yaml`; rules are defined in
[README.md](README.md). Rename mechanics, when a rename is accepted, follow
`PATTERN_MIGRATION_GUIDE.md`.

| Pattern | Alignment | Industry terms | Recommendation | Decision |
|---------|-----------|----------------|----------------|----------|
| Agent Readiness | strong | *agent readiness* (Factory.ai, Kodus); *agent-ready codebase* (Upsun); *AI readiness checklist* (independent practitioner); *AI maturity self-assessment* (Coder) | **Keep — accepted rename from Readiness Assessment** (most sources use the agent-readiness term; the former name collided with org-level AI readiness) | Accepted 2026-07-10 — canonical rename applied |
| Incremental Generation | aliased | no stable industry name; *progressive enhancement* collides with the established web-design term | **Keep — accepted rename from Progressive Enhancement** (the new catalog name describes the mechanism without retaining the collision) | Accepted 2026-07-10 — canonical rename applied |
| Agent Memory | strong | *memory* / *agent memory* (Anthropic, Cline, MemGPT) | **Keep — accepted rename from Context Persistence** (memory terminology is consistent across sources) | Accepted 2026-07-10 — canonical rename applied |
| Codified Rules | weak | `AGENTS.md` (open format), *Rules* (Cursor), `CLAUDE.md` (Anthropic), *repository custom instructions* (GitHub Copilot) | Keep + alias | Accepted 2026-07-04 — alias mentions merged (PR #29) |
| Tool Integration | aliased | *tool use* (Anthropic), *function calling* (OpenAI), *MCP* | Keep + alias | Accepted 2026-07-04 — alias mentions merged (PR #29) |
| Planned Implementation | aliased | *plan mode* (Cursor, Claude Code) | Keep + alias (a Plan Mode rename would strain the principle-not-vendor-feature rule) | Accepted 2026-07-04 — alias mention merged (PR #29) |
| Security Sandbox | strong | *sandboxing*, *devcontainer isolation*, *execution isolation*, *microVM sandbox* | Keep (most independently scoreable sources use our word; no spec-compliant candidate beats it) | Accepted 2026-07-04 |
| Issue Generation | weak | no dominant competing term | Keep | Accepted 2026-07-04 |
| Developer Lifecycle | aliased | *AI-DLC* (AWS), spec-driven workflow framings | Keep (note the scope overlap with Spec-Driven Development) | Accepted 2026-07-04 |

Nine of the eleven current assessments are schema-v2 legacy imports and therefore have `weak`
verdicts until a complete refresh supplies query, content-hash, and verifier provenance; Agent
Readiness and Event Automation have complete provenance. This ledger retains the earlier human
naming decisions during that refresh. Spec-Driven Development remains omitted because its naming
alignment is `strong`; Security Sandbox is retained to preserve its accepted decision history even
though its independently scoreable sources now recompute to `strong` alignment.

### 2026-07-10 — three accepted evidence-led renames

The maintainer accepted the three recommendations that were still pending and applied them across
the catalog as atomic migrations:

1. **Readiness Assessment → Agent Readiness** — aligns the catalog with codebase-focused industry
   terminology and avoids confusion with organization-level AI readiness assessments.
2. **Progressive Enhancement → Incremental Generation** — removes the collision with the established
   web-development term while retaining the small, deployable-generation mechanism.
3. **Context Persistence → Agent Memory** — adopts the memory terminology used consistently by agent
   products, documentation, implementations, and practitioner artifacts.

The source records remain explicit `legacy-import` evidence and still need a complete automated
refresh. Renaming changes only their canonical catalog mapping and the mechanically derived naming
alignment; it does not upgrade their adoption verdicts or provenance.

## Rubric decision record

### 2026-07-10 — schema v2 and legacy-evidence migration

The validator now requires a versioned schema and treats provenance as part of the verdict rather
than optional commentary.

1. **Complete provenance is required for `verified`** — all three search modes record exact queries
   and candidate counts; every entry records its organization, independence group, canonical URL,
   normalized-content hash, and verifier metadata.
2. **Adoption is multidimensional** — `verified` requires a runnable T1 implementation and
   independent T3/T4 adoption from another group. T5 never unlocks the verdict.
3. **Independence is enforced** — one entry per independence group per file and one canonical URL
   across the evidence set. Duplicate sources no longer inflate multiple claims.
4. **Legacy assertions were withdrawn** — the ten July 2 files were migrated honestly as
   `provenance_status: legacy-import`. Their immutable PRs record aggregate search coverage, but
   unavailable query strings, per-mode candidate counts, hashes, and verifier metadata remain
   explicitly unknown. They cannot be `verified` until refreshed.
5. **Status semantics changed** — assessed coverage, adoption verdict, staleness, and provenance
   refresh needs are separate signals in `STATUS.md`.

### 2026-07-04 — four decisions following the tooling review

Approved by the maintainer and originally generation-gated by `last_checked`. The July 10 schema-v2
migration supersedes that temporary split: legacy `verified:` fields are no longer accepted, and
provenance status now controls eligibility. Enforced in `scripts/validate-evidence.py`;
human-readable rules in [README.md](README.md).

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
