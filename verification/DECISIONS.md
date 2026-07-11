# Verification Decisions

The durable record connecting evidence to human judgment. Two things live here: the
**naming-decision ledger** (per pattern: what the industry calls the practice, what the
pipeline recommends, and what the maintainer decided) and the **rubric decision record**
(changes to how evidence is scored and verdicts computed).

Ownership: the **Decision column is written only by humans** — the pipeline never decides.
Verification runs synchronize evidence-derived Alignment values in their single run-level PR and
add a neutral `Review naming signal` placeholder when a newly verified, non-strong pattern has no
row. Humans refine Industry terms and Recommendation and exclusively own Decision. CI
(`tests/test_evidence_files.py`) requires a ledger row for every `verified` pattern whose
`naming_alignment` is not `strong`, so a new naming signal cannot land without appearing here.

**After editing this file** (recording a decision, adjusting a recommendation):
run `python3 scripts/generate-verification-status.py` — [STATUS.md](STATUS.md) embeds the
Recommendation and Decision columns and CI fails while it is stale. To gather fresh evidence
behind a recommendation, invoke `$evaluate-pattern-adoption` in a signed-in local Codex session;
see "Local evidence evaluation" in [README.md](README.md). GitHub Actions validates evidence but
never performs model-backed research.

## Naming-decision ledger

Alignment values come from each pattern's `evidence/<slug>.yaml`; rules are defined in
[README.md](README.md). Rename mechanics, when a rename is accepted, follow
`PATTERN_MIGRATION_GUIDE.md`.

| Pattern | Alignment | Industry terms | Recommendation | Decision |
|---------|-----------|----------------|----------------|----------|
| Agent Readiness | strong | *agent readiness* (Factory.ai, Kodus); *agent-ready codebase* (Upsun); *AI readiness checklist* (independent practitioner); *AI maturity self-assessment* (Coder) | **Keep — accepted rename from Readiness Assessment** (most sources use the agent-readiness term; the former name collided with org-level AI readiness) | Accepted 2026-07-10 — canonical rename applied |
| Incremental Generation | aliased | no stable industry name; *progressive enhancement* collides with the established web-design term | **Keep — accepted rename from Progressive Enhancement** (the new catalog name describes the mechanism without retaining the collision) | Accepted 2026-07-10 — canonical rename applied |
| Agent Memory | strong | *memory* / *agent memory* (Anthropic, Cline, MemGPT) | **Keep — accepted rename from Context Persistence** (memory terminology is consistent across sources) | Accepted 2026-07-10 — canonical rename applied |
| Codified Rules | aliased | `AGENTS.md` (open format), *Rules* (Cursor), `CLAUDE.md` (Anthropic), *repository custom instructions* (GitHub Copilot) | Keep + alias | Accepted 2026-07-04 — alias mentions merged (PR #29) |
| Tool Integration | aliased | *tool use* (Anthropic), *function calling* (OpenAI), *MCP* | Keep + alias | Accepted 2026-07-04 — alias mentions merged (PR #29) |
| Planned Implementation | aliased | *plan mode* (Cursor, Claude Code) | Keep + alias (a Plan Mode rename would strain the principle-not-vendor-feature rule) | Accepted 2026-07-04 — alias mention merged (PR #29) |
| Security Sandbox | strong | *sandboxing*, *devcontainer isolation*, *execution isolation*, *microVM sandbox* | Keep (most independently scoreable sources use our word; no spec-compliant candidate beats it) | Accepted 2026-07-04 |
| Issue Generation | aliased | no dominant competing term | Keep | Accepted 2026-07-04 |
| Developer Lifecycle | aliased | *AI-DLC* (AWS), spec-driven workflow framings | Keep (note the scope overlap with Spec-Driven Development) | Accepted 2026-07-04 |
| Code Research | weak | *code research*; async coding agents; cloud software-engineering agents | Keep — accepted rename from Asynchronous Research and promotion | Accepted 2026-07-11 |
| Atomic Decomposition | aliased | task splitting and ownership; sectioning; contract-first fan-out | Keep + alias | Accepted 2026-07-11 — canonical principle retained |
| Autonomous SOC | weak | Security Copilot agents; agentic SOC; AI SOC analyst; autonomous SOC | Keep — accepted rename from Autonomous Defense and SOC-specific narrowing | Accepted 2026-07-11 — remains experimental |
| Autonomous Remediation | aliased | Copilot Autofix; Autofix; automated program repair | Keep experimental — accepted demotion pending independent evidence for the complete detector-to-same-session-repair loop | Accepted 2026-07-11 |
| Bounded Autonomy | none | no stable industry term; implementations expose turn, cost, time, step, and termination caps | Keep — accepted promotion after making deterministic bounds the required core and advanced diagnostics optional | Accepted 2026-07-11 |
| Centralized Rules | aliased | AI rules; AI instructions; AGENTS.md single source of truth | Keep + alias (distinct from repository-local Codified Rules because it distributes rules across projects) | Accepted 2026-07-11 — canonical name retained |
| ChatOps Security | aliased | ChatOps solution; ChatOps for Security Operations | Keep + alias; retain as an experimental delivery interface | Accepted 2026-07-11 — canonical name retained |
| Model Routing | aliased | LLM routing; dynamic model routing; choosing the right model | Keep — accepted rename from Context Optimization and promotion | Accepted 2026-07-11 |
| Error Resolution | aliased | Repairing Programs; Fix with Copilot; AI Root Cause Analysis | Keep + alias; clarify the human review and validation boundary | Accepted 2026-07-11 — canonical name retained and scope narrowed |
| Agent Hooks | aliased | hooks; plugins; AI agent hooks | Keep — accepted rename from Event Automation; cross-vendor implementations expose lifecycle hooks | Accepted 2026-07-11 |
| Feedback Flywheel | weak | harness engineering; living context | Keep + alias; remain experimental until adoption is broader | Accepted 2026-07-11 — canonical name retained |
| Guided Architecture | aliased | domain-modeling pipelines; Well-Architected review; architectural decision generation | Keep experimental; require a tighter framework-specific boundary before promotion | Accepted 2026-07-11 — canonical umbrella retained for exploration |
| Guided Chaos | aliased | Smart Chaos; natural-language chaos engineering | Keep — accepted rename from Chaos Engineering and promotion | Accepted 2026-07-11 |
| Guided Refactoring | aliased | AI CodeFix; agentic refactoring; MCP-guided refactoring | Keep + alias | Accepted 2026-07-11 — canonical principle retained |
| On-Call Handoff | aliased | handoff summary; shift notifications; outage summary | Keep — accepted rename from Handoff Automation and narrowing to operational shift handoffs | Accepted 2026-07-11 — remains experimental |
| Handoff Protocols | aliased | coding agent; human-in-the-loop; agent-generated PR | Keep + alias; define it as the return and approval boundary | Accepted 2026-07-11 — canonical name retained |
| Image Spec | aliased | Screenshots and Files; design-to-code; screenshot-to-code | Keep + alias; narrow to screenshots and design mockups translated into UI code | Accepted 2026-07-11 — canonical name retained and scope narrowed |
| Incident Automation | aliased | AI-generated runbook; AI SRE; Vibe OnCall | Keep + alias; distinguish response execution from On-Call Handoff | Accepted 2026-07-11 — canonical name retained |
| Long-Running Orchestration | aliased | cloud tasks; autonomous software engineer; cloud agent; background agents | Keep + alias; define it by duration, persisted state, checkpoints, and recovery | Accepted 2026-07-11 — remains experimental |
| Agent Observability | weak | LLM engineering platform; AI observability; tracing; agent observability; Harness Engineering | Keep — accepted rename from Observable Development and reframe around agent runs, tool events, traces, and evaluations | Accepted 2026-07-11 — application logging moved to Error Resolution |
| Pipeline Synthesis | aliased | Agentic Workflows; AutoPipelineAI | Keep + alias; absorb deployment generation as a subtype | Accepted 2026-07-11 — Deployment Synthesis merged and retired |
| Policy Generation | weak | NL2Cedar; OPA AI assistant; Dynamic Kubernetes Policy Generator | Keep + alias; narrow to natural-language or runtime context transformed into validated policy-as-code | Accepted 2026-07-11 — canonical name retained and scope narrowed |
| Review Automation | aliased | automated PR reviews; automatic code review; AI code review | Keep + alias; narrow to automated pull-request and code review | Accepted 2026-07-11 — canonical two-word name retained |
| Flake Management | aliased | flaky test management; flaky test detection; automated detection and suppression | Keep — accepted rename from Suite Health and narrowing to detection, quarantine, suppression, and tracked remediation | Accepted 2026-07-11 — remains experimental |
| Testing Orchestration | aliased | automated unit-test generation; writing tests with coding agents; automated test improvement | Keep + alias; retain the test-generation and verification boundary | Accepted 2026-07-11 — remains experimental |
| Workflow Orchestration | weak | orchestration framework; workflow orchestration agents; human-in-the-loop agents | Keep + alias; distinguish runtime coordination from pipeline-definition generation | Accepted 2026-07-11 — remains experimental |
| Security Orchestration | none | no stable industry term recorded | Keep experimental — accepted demotion until exact evidence demonstrates multi-tool aggregation plus AI summarization | Accepted 2026-07-11 |
| Autonomous Acceptance | aliased | Software Factory; executable acceptance gates; signed attestations | Keep experimental; do not promote without a shipped end-to-end implementation | Accepted 2026-07-11 — canonical name retained |
| Test Promotion | aliased | golden tests; protected test baselines | Keep experimental; require evidence for the complete candidate-to-approved-baseline workflow | Accepted 2026-07-11 — canonical name retained |

This ledger retains earlier human naming decisions while evidence is refreshed independently.
Current coverage, provenance, verdicts, and freshness are generated in `STATUS.md`. A pattern may
remain here after its alignment becomes `strong` when the row preserves accepted decision history.

### 2026-07-11 — two-word taxonomy consolidation

The maintainer accepted the evidence-led catalog review subject to `pattern-spec.md`'s exact
two-word rule. Adoption evidence was accepted separately in PR #70; this decision changes catalog
boundaries and names without claiming that a taxonomy edit is new research.

Canonical renames:

1. **Event Automation → Agent Hooks**
2. **Observable Development → Agent Observability**
3. **Context Optimization → Model Routing**
4. **Asynchronous Research → Code Research**
5. **Chaos Engineering → Guided Chaos**
6. **Suite Health → Flake Management**
7. **Handoff Automation → On-Call Handoff**
8. **Autonomous Defense → Autonomous SOC**

Maturity and boundary decisions:

- Promote Bounded Autonomy, Model Routing, Code Research, Drift Remediation, Guided Chaos,
  Evidence Automation, and Debt Forecasting to the main catalog.
- Demote Security Orchestration and Autonomous Remediation to experiments until their complete
  catalog mechanisms have exact independent evidence.
- Merge Deployment Synthesis into Pipeline Synthesis and retire the former slug.
- Retire Release Synthesis as a standalone AI pattern; retain deterministic release-note
  automation only as supporting lifecycle/pipeline guidance.
- Replace Upgrade Advisor with the materially different Dependency Migration experiment. Its old
  dependency-update evidence is not reassigned; the new slug remains pending local evaluation.
- Narrow Image Spec, Policy Generation, Review Automation, and Flake Management to the mechanisms
  actually supported by their evidence. Clarify Error Resolution as human-gated.
- Keep Autonomous Acceptance and Test Promotion experimental and weak; verification does not imply
  promotion.

Historical search queries, source titles, quotes, and provider provenance may retain retired names.
Active registry IDs, evidence filenames, examples, links, generated data, and evaluator scopes use
only the new canonical taxonomy.

### 2026-07-10 — three accepted evidence-led renames

The maintainer accepted the three recommendations that were still pending and applied them across
the catalog as atomic migrations:

1. **Readiness Assessment → Agent Readiness** — aligns the catalog with codebase-focused industry
   terminology and avoids confusion with organization-level AI readiness assessments.
2. **Progressive Enhancement → Incremental Generation** — removes the collision with the established
   web-development term while retaining the small, deployable-generation mechanism.
3. **Context Persistence → Agent Memory** — adopts the memory terminology used consistently by agent
   products, documentation, implementations, and practitioner artifacts.

At rename time, the source records remained explicit `legacy-import` evidence; the rename changed
only their canonical catalog mapping and mechanically derived naming alignment. Subsequent evidence
refreshes, if any, are reflected in `STATUS.md` and do not alter that historical rationale.

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
