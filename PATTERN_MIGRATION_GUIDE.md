# Pattern Migration Guide

## Overview

This guide documents the comprehensive renaming of patterns and antipatterns in the AI Development Patterns repository to comply with a strict two-word naming convention, including later evidence-led refinements to canonical names.

**Migration Dates:** November 2025; July 2026 evidence-led refinements and taxonomy consolidation
**Impact:** All 42 patterns and 56 antipatterns in the initial migration; 12 later canonical refinements; 47 active patterns after consolidation
**Compliance:** 8% → 100% (98 naming changes)

---

## Why This Change?

### Rationale

The two-word naming convention provides:

1. **Consistency**: All patterns follow the same Noun+Noun or Adjective+Noun structure
2. **Clarity**: Shorter names are easier to remember and reference
3. **Professionalism**: Aligns with industry pattern naming best practices (e.g., Gang of Four patterns)
4. **Discoverability**: Consistent naming improves search and navigation
5. **Internationalization**: Simpler names translate better across languages

### Pattern Language Alignment

This change aligns with established pattern naming conventions:
- **Gang of Four**: "Factory Method", "Abstract Factory", "Singleton" (all 2 words or less)
- **Enterprise Patterns**: "Service Locator", "Data Mapper", "Active Record"
- **Cloud Patterns**: "Circuit Breaker", "Event Sourcing", "CQRS"

---

## Complete Name Mapping

### Main Patterns (22 patterns)

| Old Name | New Name | Change Type | Notes |
|----------|----------|-------------|-------|
| AI Readiness Assessment | Agent Readiness | Removed "AI" prefix, then evidence-led refinement | Industry practice uses *agent readiness* for codebase-focused assessment; the intermediate name was `Readiness Assessment` |
| Rules as Code | Codified Rules | Removed preposition | More concise, maintains meaning |
| AI Security Sandbox | Security Sandbox | Removed "AI" prefix | Context is already AI development |
| AI Developer Lifecycle | Developer Lifecycle | Removed "AI" prefix | Lifecycle applies to AI development by default |
| AI Tool Integration | Tool Integration | Removed "AI" prefix | Tools are AI tools in this context |
| AI Issue Generation | Issue Generation | Removed "AI" prefix | Generation implies AI automation |
| Specification Driven Development | Spec-Driven Development | Hyphenated compound + clarified | Aligns with the repository's current canonical naming |
| AI Plan-First Development | Planned Implementation | Removed "AI", clarified | Describes planned approach to implementation |
| Progressive AI Enhancement | Incremental Generation | Removed "AI" prefix, then evidence-led refinement | Avoids collision with the established web-design term; the intermediate name was `Progressive Enhancement` |
| AI Choice Generation | Choice Generation | Removed "AI" prefix | Generation implies AI automation |
| Choice Generation | Cross-Model Validation | Reframed | Original pattern reduced to "ask one model for N options" — table stakes in 2026. Reframed around running the same prompt across multiple frontier models, where disagreement is signal. |
| Cross-Model Validation | Adversarial Evaluator | Renamed + expanded | Broadened to the GAN-style principle of separating the generating agent from an independent judging agent. Cross-model fan-out becomes one of two topologies (the other: an adversarial judge that attacks a single candidate). Old `#cross-model-validation` anchor preserved as an alias on the new section. |
| Question Generation | (merged) | Folded into Planned Implementation | The interview phase belongs as the opening of Planned Implementation rather than a separate pattern. |
| Constrained Generation | (merged) | Folded into Planned Implementation | Constraint examples now appear as the "Constrain" phase between interview and plan; standalone pattern was a 25-line stub. |
| Automated Traceability | (merged) | Folded into Spec-Driven Development | Traceability is the link layer implied by Spec-Driven's anchor/footnote system; the standalone 35-line entry duplicated coverage. |
| Guided Architecture | (demoted) | Moved to `experiments/README.md` | Pattern is broad enough that its concrete value depends heavily on the specific framework; remains in experiments pending tighter framing. |
| Baseline Management | (archived) | Removed | 20-line stub on AI-set CloudWatch thresholds; orphan with no incoming dependents and no plan to develop further. |
| Atomic Task Decomposition | Atomic Decomposition | Simplified | "Atomic" already implies task-level |
| Parallelized AI Coding Agents | Parallel Agents | Simplified, removed "AI" | Agents are AI agents in this context |
| AI Context Persistence | Agent Memory | Removed "AI" prefix, then evidence-led refinement | Aligns with industry memory terminology; the intermediate name was `Context Persistence` |
| Constraint-Based AI Development | Constrained Generation | Simplified, focused | Emphasizes the generation constraint |
| Observable AI Development | Agent Observability | Removed "AI" prefix, then evidence-led refinement | Aligns with agent tracing and evaluation evidence |
| AI-Driven Refactoring | Guided Refactoring | Changed "AI-Driven" to "Guided" | More concise, maintains meaning |
| AI-Driven Architecture Design | Guided Architecture | Changed "AI-Driven" to "Guided" | Parallel structure with Guided Refactoring |
| AI-Driven Traceability | Automated Traceability | Changed "AI-Driven" to "Automated" | Emphasizes automation benefit |
| Policy-as-Code Generation | Policy Generation | Simplified | "Generation" implies automation |
| Security Scanning Orchestration | Security Orchestration | Simplified | Orchestration implies scanning/automation |
| Performance Baseline Management | Baseline Management | Simplified | Context makes "Performance" implicit |
| Error Resolution | Error Resolution | No change | Already compliant (stable core pattern) |

### Main Antipatterns (31 antipatterns)

| Old Name | New Name | Change Type | Rationale |
|----------|----------|-------------|-----------|
| Rushing Into AI | Premature Adoption | Added negative prefix | "Premature" clearly indicates timing failure |
| Context Drift | Broken Context | Added negative prefix | "Broken" indicates failure state |
| Unrestricted Access | Unrestricted Access | No change | Already compliant |
| Shared Agent Workspaces | Conflicting Workspaces | Changed to negative implication | "Conflicting" clearly indicates problem |
| Ad-Hoc AI Development | Unplanned Development | Added negative prefix | "Unplanned" clearly negative |
| Prompt-Only AI Development | Disconnected Prompting | Simplified, negative implication | "Disconnected" clearly indicates isolation from tools |
| Vague Issue Generation | Under-Specified Issues | Added negative prefix | "Under-Specified" indicates insufficiency |
| Missing CI Integration | Broken Integration | Added negative prefix | "Broken" indicates failure |
| Implementation-First AI | Spec-Ignored | Symmetrical with "Spec-Driven Development" | Opposite of the pattern |
| Prompt Hoarding | Over-Prompting | Changed to "Over-" prefix | Indicates excess prompting |
| Blind Code Generation | Blind Generation | Simplified | "Blind" already negative |
| Analysis Paralysis | Over-Analysis | Changed to "Over-" prefix | More technical than "Paralysis" |
| Big Bang Generation | Monolithic Generation | Changed to technical term | "Monolithic" is standard negative term |
| Uncoordinated Parallel Execution | Uncoordinated Agents | Simplified | Parallel agents context is clear |
| Knowledge Hoarding | Over-Documentation | Changed to "Over-" prefix | More technical description |
| Context Bloat | Bloated Context | Adjusted word order | "Bloated" is negative adjective |
| Unconstrained Generation | Unconstrained Generation | No change | Already compliant |
| Constraint Overload | Over-Constrained | Changed to negative prefix | "Over-" prefix indicates excess |
| Pseudo-Atomic Tasks | False Atomicity | Changed to "False" | More precise negative indicator |
| Over-Decomposition | Over-Decomposition | No change | Already compliant |
| Black Box Development | Blind Development | Changed "Black Box" to "Blind" | Simpler, maintains meaning |
| Shotgun Surgery | Scattered Refactoring | Changed to domain term | "Scattered" more descriptive |
| Speculative Refactoring | Premature Refactoring | Changed to "Premature" | More standard negative term |
| Architecture Astronaut AI | Over-Architecting | Simplified | "Over-" prefix indicates excess |
| Manual Traceability Management | Broken Traceability | Simplified with negative | "Broken" indicates failure |
| Manual Policy Translation | Untested Policies | Changed focus | Untested is the key problem |
| Alert Fatigue | Over-Alerting | Changed to "Over-" prefix | Indicates root cause (too many alerts) |
| One-Off Alerts | Static Thresholds | Changed to technical term | "Static" indicates inflexibility |

### Experimental Patterns (20 patterns)

| Old Name | New Name | Change Type | Notes |
|----------|----------|-------------|-------|
| Human-AI Handoff Protocol | Handoff Protocols | Removed "Human-AI" | Context is clear |
| Comprehensive AI Testing Strategy | Testing Orchestration | Simplified | "Orchestration" implies comprehensive coordination |
| AI Workflow Orchestration | Workflow Orchestration | Removed "AI" prefix | Workflows are AI workflows in context |
| AI Review Automation | Review Automation | Removed "AI" prefix | Automation implies AI |
| Technical Debt Forecasting | Debt Forecasting | Simplified | "Technical" is implicit |
| Pipeline Synthesis | Pipeline Synthesis | No change | Already compliant |
| AI-Guided Blue-Green Deployment | (merged) | Folded into Pipeline Synthesis | Deployment generation is a pipeline subtype |
| Drift Detection & Remediation | Drift Remediation | Focused on key action | Remediation is the primary value |
| Release Note Synthesis | (retired) | Removed as standalone | Deterministic release-note automation is supporting lifecycle guidance |
| Incident Response Automation | Incident Automation | Simplified | "Automation" implies response |
| Test Suite Health Management | Flake Management | Narrowed | Matches flaky-test detection, quarantine, and suppression evidence |
| Dependency Upgrade Advisor | Dependency Migration | Reframed | Requires agentic compatibility analysis and code migration |
| On-Call Handoff Automation | On-Call Handoff | Simplified | Retains the operational shift boundary |
| Chaos Engineering Scenarios | Guided Chaos | Narrowed | Distinguishes agent-guided experiments from ordinary chaos engineering |
| ChatOps Security Integration | ChatOps Security | Simplified | "Integration" is implicit |
| Compliance Evidence Automation | Evidence Automation | Simplified | "Compliance" is implicit in evidence context |
| Context Window Optimization | Model Routing | Reframed | Matches cost/quality-aware model-selection evidence |
| Visual Context Scaffolding | Image Spec | Simplified | More concise, "Image" specifies visual type |
| AI Event Automation | Agent Hooks | Evidence-led refinement | Cross-vendor implementations use lifecycle hooks |
| Custom AI Commands | Custom Commands | Removed "AI" prefix | Commands are AI commands in context |

### Experimental Antipatterns (25 antipatterns)

| Old Name | New Name | Change Type | Rationale |
|----------|----------|-------------|-----------|
| Unclear Boundaries | Broken Boundaries | Changed to "Broken" prefix | More clearly negative |
| Test Generation Without Strategy | Scattered Testing | Simplified with negative | "Scattered" indicates lack of strategy |
| Uncoordinated Multi-Tool Usage | Chaotic Orchestration | Simplified | "Chaotic" opposite of good orchestration |
| Unsafe Parallel Execution | Unsafe Parallelism | Simplified | "Parallelism" encompasses execution |
| Manual-Only Review | Manual Reviews | Simplified | "Manual" is negative in automation context |
| Reactive Debt Management | Reactive Debt | Simplified | "Reactive" is negative (vs. proactive) |
| Manual Pipeline Maintenance | Manual Pipelines | Simplified | "Manual" indicates the antipattern |
| Blue-Green-Canary Confusion | Confused Deployment | Simplified | "Confused" is the negative state |
| Manual Drift Checking | Manual Drift | Simplified | "Manual" is the antipattern |
| Manual Release Notes | Manual Releases | Simplified | "Manual" is negative in automation context |
| Static Runbooks | Static Runbooks | No change | Already compliant |
| Ignoring Flaky Tests | Ignored Flakiness | Simplified | "Ignored" is the negative action |
| Batch Upgrades | Reckless Upgrades | Added negative prefix | "Reckless" indicates risk |
| Verbal-Only Handoffs | Undocumented Handoffs | Changed to negative prefix | "Undocumented" is clearer problem |
| Random Chaos | Random Chaos | No change | Already compliant |
| Delayed Security Feedback | Delayed Security | Simplified | "Delayed" is negative in DevSecOps |
| Manual Evidence Collection | Manual Evidence | Simplified | "Manual" is the antipattern |
| One-Size-Fits-All | Wasteful Context | Changed to technical negative | "Wasteful" indicates inefficiency |
| Kitchen Sink Upload | Overwhelming Visuals | Changed to technical term | "Overwhelming" indicates the problem |
| Unchecked Event Commands | Unchecked Events | Simplified | "Unchecked" is the negative state |
| Ignoring Built-in Commands | Redundant Commands | Changed to technical term | "Redundant" indicates duplication |
| Shallow Commands | Shallow Commands | No change | Already compliant |
| Hardcoded Context | Hardcoded Context | No change | Already compliant |
| Context-Free Error Messages | Contextless Errors | Simplified | "Contextless" is more concise |
| Blind Fix Application | Blind Fixes | Simplified | "Blind" is the negative indicator |
| Missing Rollback Strategy | Unprotected Fixes | Changed focus | "Unprotected" indicates lack of safety |

---

## July 2026 Evidence-Led Refinements

Machine-collected naming evidence led to three additional canonical changes accepted by the
maintainer on July 10, 2026:

| Retired Intermediate Name | Current Canonical Name | Retired Anchor | Current Anchor |
|---------------------------|------------------------|----------------|----------------|
| Readiness Assessment | Agent Readiness | `#readiness-assessment` | `#agent-readiness` |
| Progressive Enhancement | Incremental Generation | `#progressive-enhancement` | `#incremental-generation` |
| Context Persistence | Agent Memory | `#context-persistence` | `#agent-memory` |

These are full canonical migrations. Registry IDs, internal links, example paths, evidence
filenames, tests, and generated artifacts use the current names. The README preserves one explicit
legacy anchor for each immediately retired name so inbound links continue to resolve; decision
history and evidence source text also retain retired terminology where necessary for auditability.

## July 2026 Taxonomy Consolidation

On July 11, 2026, the maintainer accepted the full-catalog evidence baseline and applied a second
evidence-led migration under `pattern-spec.md`'s exact two-word rule. The active collection now has
29 main patterns and 18 experimental patterns (47 total).

### Canonical renames

| Retired Name | Current Canonical Name | Retired Anchor | Current Anchor |
|--------------|------------------------|----------------|----------------|
| Event Automation | Agent Hooks | `#event-automation` | `#agent-hooks` |
| Observable Development | Agent Observability | `#observable-development` | `#agent-observability` |
| Context Optimization | Model Routing | `#context-optimization` | `#model-routing` |
| Asynchronous Research | Code Research | `#asynchronous-research` | `#code-research` |
| Chaos Engineering | Guided Chaos | `#chaos-engineering` | `#guided-chaos` |
| Suite Health | Flake Management | `#suite-health` | `#flake-management` |
| Handoff Automation | On-Call Handoff | `#handoff-automation` | `#on-call-handoff` |
| Autonomous Defense | Autonomous SOC | `#autonomous-defense` | `#autonomous-soc` |

These names supersede the corresponding current-name cells in the historical November 2025 table.
Historical source titles, search queries, quotes, and issue records retain the wording that existed
when they were created.

### Material replacement

| Retired Concept | New Experimental Pattern | Relationship |
|-----------------|--------------------------|--------------|
| Upgrade Advisor | Dependency Migration | Materially different mechanism; no alias or evidence reassignment |

Unlike a canonical rename, this replacement has no compatibility anchor. `Dependency Migration`
must establish its own evidence for agentic changelog analysis, compatibility edits, validation,
and migration pull requests.

### Boundary and maturity changes

| Pattern | Change | Migration |
|---------|--------|-----------|
| Bounded Autonomy | Promoted | `experiments/README.md#bounded-autonomy` → `README.md#bounded-autonomy` |
| Model Routing | Renamed + promoted | `experiments/README.md#context-optimization` → `README.md#model-routing` |
| Code Research | Renamed + promoted | `experiments/README.md#asynchronous-research` → `README.md#code-research` |
| Drift Remediation | Promoted | `experiments/README.md#drift-remediation` → `README.md#drift-remediation` |
| Guided Chaos | Renamed + promoted | `experiments/README.md#chaos-engineering` → `README.md#guided-chaos` |
| Evidence Automation | Promoted | `experiments/README.md#evidence-automation` → `README.md#evidence-automation` |
| Debt Forecasting | Promoted | `experiments/README.md#debt-forecasting` → `README.md#debt-forecasting` |
| Security Orchestration | Demoted | `README.md#security-orchestration` → `experiments/README.md#security-orchestration` |
| Autonomous Remediation | Demoted | `README.md#autonomous-remediation` → `experiments/README.md#autonomous-remediation` |
| Deployment Synthesis | Merged + retired | Folded into `experiments/README.md#pipeline-synthesis` |
| Release Synthesis | Retired | Deterministic release-note automation retained as supporting lifecycle guidance |

`Dependency Migration` is a new mechanism replacing the overly generic Upgrade Advisor concept.
The old dependency-update evidence is not reassigned; the new canonical slug remains pending until
a separately approved local evaluation validates agentic changelog analysis, compatibility edits,
test execution, and migration pull requests.

## Summary Statistics

### Initial November 2025 Migration
- **Total items**: 98 (42 patterns + 56 antipatterns)
- **Items renamed**: 90 (92%)
- **Items unchanged**: 8 (8%)
- **Compliance before**: 8/98 (8%)
- **Compliance after**: 98/98 (100%)

### By Category
- **Main Patterns**: 21 renamed, 1 unchanged
- **Main Antipatterns**: 28 renamed, 3 unchanged
- **Experimental Patterns**: 19 renamed, 1 unchanged
- **Experimental Antipatterns**: 22 renamed, 3 unchanged

### July 11, 2026 Consolidation
- **Active main patterns**: 29
- **Active experimental patterns**: 18
- **Active patterns total**: 47
- **Canonical renames**: 8
- **Promotions**: 7
- **Demotions**: 2
- **Merged or retired standalone patterns**: 2
- **Pending replacement patterns**: 1 (`Dependency Migration`)

---

## Migration Impact

### Internal Repository Changes

Core references within this repository were updated during the migration:

1. **README.md**
   - Complete Pattern Reference table
   - All pattern section headers
   - All hyperlinks and cross-references
   - All antipattern subsections

2. **experiments/README.md**
   - Experimental pattern reference table
   - All pattern section headers
   - All hyperlinks to main patterns (dependencies)
   - All antipattern subsections

3. **Example Directories**
   - Renamed to match new pattern names
   - Updated internal documentation

**Note**: The repository continues to evolve. If you find legacy names/anchors in other docs or example READMEs, treat them as stale references to be updated to match the current canonical names and anchors in `README.md`.

4. **Configuration Files**
   - CLAUDE.md updated with new pattern references
   - pattern-spec.md updated with comprehensive naming rules

### External Impact

If you have external references to these patterns (documentation, presentations, articles), you'll need to update them using this guide.

**Recommended approach:**
1. Use the mapping tables above to identify old pattern names
2. Replace with new pattern names
3. Test all hyperlinks if linking to this repository

### Backward Compatibility

Canonical IDs do not retain aliases. The pattern documents provide explicit compatibility anchors
for accepted July 2026 renames, the Deployment Synthesis merge, and Cross-Model Validation so
existing inbound links still land on the replacement section. Retired names remain deprecated and
are not used by internal links, registry entries, examples, active evidence filenames, or generated
pattern IDs. Promotions and demotions also retain a linked redirect notice in the former document,
so both the old file path and anchor continue to resolve.

**Migration window:** Users should update their references to canonical names immediately. Compatibility
anchors may be removed in a future major migration.

### Search and Replace Guidance

For bulk updates in external documentation:

1. **Create a find/replace list** from the mapping tables above
2. **Test on a copy** of your documentation first
3. **Review manually** for context-sensitive references
4. **Update hyperlinks** if linking to GitHub anchors (anchors have changed)

**Example regex patterns for bulk replacement:**
```bash
# Pattern: "AI Readiness Assessment" → "Agent Readiness"
find: "AI Readiness Assessment"
replace: "Agent Readiness"

# Pattern: "#ai-readiness-assessment" → "#agent-readiness"
find: "#ai-readiness-assessment"
replace: "#agent-readiness"
```

---

## Anchor Link Changes

All GitHub markdown anchor links have changed. Update your hyperlinks:

### Main Pattern Anchors

| Old Anchor | New Anchor |
|------------|------------|
| `#ai-readiness-assessment` | `#agent-readiness` |
| `#rules-as-code` | `#codified-rules` |
| `#ai-security-sandbox` | `#security-sandbox` |
| `#ai-developer-lifecycle` | `#developer-lifecycle` |
| `#ai-tool-integration` | `#tool-integration` |
| `#ai-issue-generation` | `#issue-generation` |
| `#specification-driven-development` | `#spec-driven-development` |
| `#ai-plan-first-development` | `#planned-implementation` |
| `#progressive-ai-enhancement` | `#incremental-generation` |
| `#ai-choice-generation` | `#choice-generation` |
| `#choice-generation` | `#cross-model-validation` |
| `#question-generation` | `#planned-implementation` (merged) |
| `#constrained-generation` | `#planned-implementation` (merged) |
| `#automated-traceability` | `#spec-driven-development` (merged) |
| `#guided-architecture` | `experiments/README.md#guided-architecture` (demoted) |
| `#baseline-management` | (archived, no replacement) |
| `#atomic-task-decomposition` | `#atomic-decomposition` |
| `#parallelized-ai-coding-agents` | `#parallel-agents` |
| `#ai-context-persistence` | `#agent-memory` |
| `#constraint-based-ai-development` | `#constrained-generation` |
| `#observable-ai-development` | `#agent-observability` |
| `#ai-driven-refactoring` | `#guided-refactoring` |
| `#ai-driven-architecture-design` | `#guided-architecture` |
| `#ai-driven-traceability` | `#automated-traceability` |
| `#policy-as-code-generation` | `#policy-generation` |
| `#security-scanning-orchestration` | `#security-orchestration` |
| `#performance-baseline-management` | `#baseline-management` |

### Experimental Pattern Anchors

| Old Anchor | New Anchor |
|------------|------------|
| `#human-ai-handoff-protocol` | `#handoff-protocols` |
| `#comprehensive-ai-testing-strategy` | `#testing-orchestration` |
| `#ai-workflow-orchestration` | `#workflow-orchestration` |
| `#ai-review-automation` | `#review-automation` |
| `#technical-debt-forecasting` | `#debt-forecasting` |
| `#ai-guided-blue-green-deployment` | `#pipeline-synthesis` (merged) |
| `#drift-detection--remediation` | `#drift-remediation` |
| `#release-note-synthesis` | (retired; lifecycle guidance) |
| `#incident-response-automation` | `#incident-automation` |
| `#test-suite-health-management` | `#flake-management` |
| `#dependency-upgrade-advisor` | `#dependency-migration` (replacement; no compatibility anchor) |
| `#on-call-handoff-automation` | `#on-call-handoff` |
| `#chaos-engineering-scenarios` | `#guided-chaos` |
| `#chatops-security-integration` | `#chatops-security` |
| `#compliance-evidence-automation` | `#evidence-automation` |
| `#context-window-optimization` | `#model-routing` |
| `#visual-context-scaffolding` | `#image-spec` |
| `#ai-event-automation` | `#agent-hooks` |
| `#custom-ai-commands` | `#custom-commands` |

---

## Naming Convention Rules

All patterns now follow these strict rules:

### Pattern Naming Rules

1. **Exactly two words, Title Case** (e.g., "Agent Memory", "Guided Refactoring")
2. **Format: Noun + Noun OR Adjective + Noun**
3. **Must clearly imply what the pattern solves or how it works**
4. **Use concrete, domain-specific AI-native engineering terms**
5. **Each word must be short, clear, and recognizable to engineers**
6. **Unique within catalog**
7. **Parallel structure across related pattern sets** (e.g., "Agent Memory", "Agent Hooks")
8. **Test: "Use the X Y pattern to..." must sound natural**

### Antipattern Naming Rules

1. **Prefix with negative or cautionary modifier** ("Broken", "Blind", "Over-", "Under-", "False", "Un-")
2. **Two words, Title Case**
3. **Must imply a failure mode or misuse of a valid pattern**
4. **Symmetrical with positive patterns where logical**
5. **Technical focus, not judgmental or humorous**

For complete naming rules and examples, see `/pattern-spec.md`.

---

## FAQ

### Why remove "AI" from pattern names?

The entire repository is about AI development patterns. Adding "AI" to every pattern name is redundant and verbose. It's like writing "Software Design Patterns" instead of just "Design Patterns" in a design patterns book.

### Why change "X-Driven" to "Guided" or "Automated"?

"X-Driven" is three syllables and less concise than alternatives. "Guided" implies AI assistance, "Automated" implies AI automation, both in two syllables or less.

### What if I prefer the old names?

The old names are deprecated. This change improves consistency, discoverability, and alignment with industry standards. We encourage updating to the new names.

### Are there any exceptions to the two-word rule?

No. All 98 patterns and antipatterns now comply with exactly two words (hyphenated compounds like "Spec-Driven" count as one word in this context).

### Will the old names ever be brought back?

No. This is a permanent change to align with pattern naming best practices.

### How do I update my local references?

Use the mapping tables above to find the old name and replace it with the new name. Update any hyperlinks to match new anchor links.

---

## Support

For questions about this migration:
1. Review this guide thoroughly
2. Check the mapping tables for specific pattern renames
3. Consult `/pattern-spec.md` for naming rules
4. Open a GitHub issue if you find migration errors

---

## Version History

- **v1.2** (July 11, 2026): Recorded full-catalog taxonomy consolidation
  - Applied 8 exact two-word canonical renames and 1 materially different replacement
  - Promoted 7 and demoted 2 patterns
  - Merged Deployment Synthesis and retired Release Synthesis
  - Established the 29-main / 18-experimental / 47-total catalog
- **v1.1** (July 10, 2026): Recorded evidence-led canonical refinements
  - Readiness Assessment → Agent Readiness
  - Progressive Enhancement → Incremental Generation
  - Context Persistence → Agent Memory
- **v1.0** (November 2025): Initial migration guide created
  - 98 total naming changes documented
  - Complete mapping tables for all patterns and antipatterns
  - Anchor link changes documented
  - Migration guidance provided

---

**Document Status**: Official Migration Guide
**Maintained By**: AI Development Patterns Repository Maintainers
**Last Updated**: July 11, 2026
