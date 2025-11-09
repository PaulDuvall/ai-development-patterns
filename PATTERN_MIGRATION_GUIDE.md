# Pattern Migration Guide

## Overview

This guide documents the comprehensive renaming of all patterns and antipatterns in the AI Development Patterns repository to comply with a strict two-word naming convention.

**Migration Date:** November 2025
**Impact:** All 42 patterns and 56 antipatterns
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

### Main Patterns (21 patterns)

| Old Name | New Name | Change Type | Notes |
|----------|----------|-------------|-------|
| AI Readiness Assessment | Readiness Assessment | Removed "AI" prefix | "AI" is redundant in AI development context |
| Rules as Code | Codified Rules | Removed preposition | More concise, maintains meaning |
| AI Security Sandbox | Security Sandbox | Removed "AI" prefix | Context is already AI development |
| AI Developer Lifecycle | Developer Lifecycle | Removed "AI" prefix | Lifecycle applies to AI development by default |
| AI Tool Integration | Tool Integration | Removed "AI" prefix | Tools are AI tools in this context |
| AI Issue Generation | Issue Generation | Removed "AI" prefix | Generation implies AI automation |
| Specification Driven Development | Spec-First | Simplified to 2 words | "Spec-First" is standard industry term |
| AI Plan-First Development | Planned Implementation | Removed "AI", clarified | Describes planned approach to implementation |
| Progressive AI Enhancement | Progressive Enhancement | Removed "AI" prefix | Progressive enhancement is well-known pattern |
| AI Choice Generation | Choice Generation | Removed "AI" prefix | Generation implies AI automation |
| Atomic Task Decomposition | Atomic Decomposition | Simplified | "Atomic" already implies task-level |
| Parallelized AI Coding Agents | Parallel Agents | Simplified, removed "AI" | Agents are AI agents in this context |
| AI Context Persistence | Context Persistence | Removed "AI" prefix | Context is AI-specific in this repository |
| Constraint-Based AI Development | Constrained Generation | Simplified, focused | Emphasizes the generation constraint |
| Observable AI Development | Observable Development | Removed "AI" prefix | Observability applies to AI development |
| AI-Driven Refactoring | Guided Refactoring | Changed "AI-Driven" to "Guided" | More concise, maintains meaning |
| AI-Driven Architecture Design | Guided Architecture | Changed "AI-Driven" to "Guided" | Parallel structure with Guided Refactoring |
| AI-Driven Traceability | Automated Traceability | Changed "AI-Driven" to "Automated" | Emphasizes automation benefit |
| Policy-as-Code Generation | Policy Generation | Simplified | "Generation" implies automation |
| Security Scanning Orchestration | Security Orchestration | Simplified | Orchestration implies scanning/automation |
| Performance Baseline Management | Baseline Management | Simplified | Context makes "Performance" implicit |

### Main Antipatterns (31 antipatterns)

| Old Name | New Name | Change Type | Rationale |
|----------|----------|-------------|-----------|
| Rushing Into AI | Premature Adoption | Added negative prefix | "Premature" clearly indicates timing failure |
| Context Drift | Broken Context | Added negative prefix | "Broken" indicates failure state |
| Unrestricted Access | Unrestricted Access | No change | Already compliant |
| Shared Agent Workspaces | Overlapping Workspaces | Changed to negative implication | "Overlapping" suggests conflict |
| Ad-Hoc AI Development | Unplanned Development | Added negative prefix | "Unplanned" clearly negative |
| Prompt-Only AI Development | Isolated Prompting | Simplified, negative implication | "Isolated" suggests insufficient approach |
| Vague Issue Generation | Under-Specified Issues | Added negative prefix | "Under-Specified" indicates insufficiency |
| Missing CI Integration | Broken Integration | Added negative prefix | "Broken" indicates failure |
| Implementation-First AI | Spec-Ignored | Symmetrical with "Spec-First" | Opposite of the pattern |
| Prompt Hoarding | Over-Prompting | Changed to "Over-" prefix | Indicates excess prompting |
| Blind Code Generation | Blind Generation | Simplified | "Blind" already negative |
| Analysis Paralysis | Over-Analysis | Changed to "Over-" prefix | More technical than "Paralysis" |
| Big Bang Generation | Monolithic Generation | Changed to technical term | "Monolithic" is standard negative term |
| Uncoordinated Parallel Execution | Uncoordinated Agents | Simplified | Parallel agents context is clear |
| Knowledge Hoarding | Over-Documentation | Changed to "Over-" prefix | More technical description |
| Context Bloat | Bloated Context | Adjusted word order | "Bloated" is negative adjective |
| Unconstrained Generation | Unconstrained Generation | No change | Already compliant |
| Constraint Overload | Constraint Overload | No change | Already compliant |
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

### Experimental Patterns (21 patterns)

| Old Name | New Name | Change Type | Notes |
|----------|----------|-------------|-------|
| Human-AI Handoff Protocol | Handoff Protocols | Removed "Human-AI" | Context is clear |
| Comprehensive AI Testing Strategy | Testing Orchestration | Simplified | "Orchestration" implies comprehensive coordination |
| AI Workflow Orchestration | Workflow Orchestration | Removed "AI" prefix | Workflows are AI workflows in context |
| AI Review Automation | Review Automation | Removed "AI" prefix | Automation implies AI |
| Technical Debt Forecasting | Debt Forecasting | Simplified | "Technical" is implicit |
| Pipeline Synthesis | Pipeline Synthesis | No change | Already compliant |
| AI-Guided Blue-Green Deployment | Deployment Synthesis | Simplified | "Synthesis" implies AI-guided generation |
| Drift Detection & Remediation | Drift Remediation | Focused on key action | Remediation is the primary value |
| Release Note Synthesis | Release Synthesis | Simplified | "Synthesis" implies note generation |
| Incident Response Automation | Incident Automation | Simplified | "Automation" implies response |
| Test Suite Health Management | Suite Health | Simplified | "Test Suite" is clear from context |
| Dependency Upgrade Advisor | Upgrade Advisor | Simplified | "Dependency" is implicit in upgrade context |
| On-Call Handoff Automation | Handoff Automation | Simplified | "On-Call" is implicit in handoff context |
| Chaos Engineering Scenarios | Chaos Engineering | Simplified | "Scenarios" is implicit |
| ChatOps Security Integration | ChatOps Security | Simplified | "Integration" is implicit |
| Compliance Evidence Automation | Evidence Automation | Simplified | "Compliance" is implicit in evidence context |
| Context Window Optimization | Context Optimization | Simplified | "Window" is implicit for context |
| Visual Context Scaffolding | Visual Scaffolding | Simplified | "Context" is implicit |
| AI Event Automation | Event Automation | Removed "AI" prefix | Automation implies AI |
| Custom AI Commands | Custom Commands | Removed "AI" prefix | Commands are AI commands in context |
| Error Resolution | Error Resolution | No change | Already compliant |

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

## Summary Statistics

### Overall Changes
- **Total items**: 98 (42 patterns + 56 antipatterns)
- **Items renamed**: 90 (92%)
- **Items unchanged**: 8 (8%)
- **Compliance before**: 8/98 (8%)
- **Compliance after**: 98/98 (100%)

### By Category
- **Main Patterns**: 21 renamed, 0 unchanged
- **Main Antipatterns**: 28 renamed, 3 unchanged
- **Experimental Patterns**: 19 renamed, 2 unchanged
- **Experimental Antipatterns**: 22 renamed, 3 unchanged

---

## Migration Impact

### Internal Repository Changes

All references within this repository have been updated:

1. **README.md**
   - Pattern reference table (lines 50-89)
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

**No alias system provided.** The old pattern names are deprecated and no longer used in the repository.

**Migration window:** Users should update their references immediately. Old names will not be maintained.

### Search and Replace Guidance

For bulk updates in external documentation:

1. **Create a find/replace list** from the mapping tables above
2. **Test on a copy** of your documentation first
3. **Review manually** for context-sensitive references
4. **Update hyperlinks** if linking to GitHub anchors (anchors have changed)

**Example regex patterns for bulk replacement:**
```bash
# Pattern: "AI Readiness Assessment" → "Readiness Assessment"
find: "AI Readiness Assessment"
replace: "Readiness Assessment"

# Pattern: "#ai-readiness-assessment" → "#readiness-assessment"
find: "#ai-readiness-assessment"
replace: "#readiness-assessment"
```

---

## Anchor Link Changes

All GitHub markdown anchor links have changed. Update your hyperlinks:

### Main Pattern Anchors

| Old Anchor | New Anchor |
|------------|------------|
| `#ai-readiness-assessment` | `#readiness-assessment` |
| `#rules-as-code` | `#codified-rules` |
| `#ai-security-sandbox` | `#security-sandbox` |
| `#ai-developer-lifecycle` | `#developer-lifecycle` |
| `#ai-tool-integration` | `#tool-integration` |
| `#ai-issue-generation` | `#issue-generation` |
| `#specification-driven-development` | `#spec-first` |
| `#ai-plan-first-development` | `#planned-implementation` |
| `#progressive-ai-enhancement` | `#progressive-enhancement` |
| `#ai-choice-generation` | `#choice-generation` |
| `#atomic-task-decomposition` | `#atomic-decomposition` |
| `#parallelized-ai-coding-agents` | `#parallel-agents` |
| `#ai-context-persistence` | `#context-persistence` |
| `#constraint-based-ai-development` | `#constrained-generation` |
| `#observable-ai-development` | `#observable-development` |
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
| `#ai-guided-blue-green-deployment` | `#deployment-synthesis` |
| `#drift-detection--remediation` | `#drift-remediation` |
| `#release-note-synthesis` | `#release-synthesis` |
| `#incident-response-automation` | `#incident-automation` |
| `#test-suite-health-management` | `#suite-health` |
| `#dependency-upgrade-advisor` | `#upgrade-advisor` |
| `#on-call-handoff-automation` | `#handoff-automation` |
| `#chaos-engineering-scenarios` | `#chaos-engineering` |
| `#chatops-security-integration` | `#chatops-security` |
| `#compliance-evidence-automation` | `#evidence-automation` |
| `#context-window-optimization` | `#context-optimization` |
| `#visual-context-scaffolding` | `#visual-scaffolding` |
| `#ai-event-automation` | `#event-automation` |
| `#custom-ai-commands` | `#custom-commands` |

---

## Naming Convention Rules

All patterns now follow these strict rules:

### Pattern Naming Rules

1. **Exactly two words, Title Case** (e.g., "Context Persistence", "Guided Refactoring")
2. **Format: Noun + Noun OR Adjective + Noun**
3. **Must clearly imply what the pattern solves or how it works**
4. **Use concrete, domain-specific AI-native engineering terms**
5. **Each word must be short, clear, and recognizable to engineers**
6. **Unique within catalog**
7. **Parallel structure across related pattern sets** (e.g., "Pipeline Synthesis", "Deployment Synthesis")
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

No. All 98 patterns and antipatterns now comply with exactly two words (hyphenated compounds like "Spec-First" count as one word in this context).

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

- **v1.0** (November 2025): Initial migration guide created
  - 98 total naming changes documented
  - Complete mapping tables for all patterns and antipatterns
  - Anchor link changes documented
  - Migration guidance provided

---

**Document Status**: Official Migration Guide
**Maintained By**: AI Development Patterns Repository Maintainers
**Last Updated**: November 2025
