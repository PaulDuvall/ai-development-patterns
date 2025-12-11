#!/bin/bash
# Script to apply all pattern name renames in README.md and experiments/README.md

set -e

echo "Applying pattern name renames..."

# Function to apply renames to a file
apply_renames() {
    local file="$1"
    echo "Processing $file..."

    # Main Pattern Renames (headers and references)
    sed -i 's/## AI Readiness Assessment/## Readiness Assessment/g' "$file"
    sed -i 's/\[AI Readiness Assessment\](#ai-readiness-assessment)/[Readiness Assessment](#readiness-assessment)/g' "$file"
    sed -i 's/#ai-readiness-assessment/#readiness-assessment/g' "$file"

    sed -i 's/## Rules as Code/## Codified Rules/g' "$file"
    sed -i 's/\[Rules as Code\](#rules-as-code)/[Codified Rules](#codified-rules)/g' "$file"
    sed -i 's/#rules-as-code/#codified-rules/g' "$file"

    sed -i 's/## AI Security Sandbox/## Security Sandbox/g' "$file"
    sed -i 's/\[AI Security Sandbox\](#ai-security-sandbox)/[Security Sandbox](#security-sandbox)/g' "$file"
    sed -i 's/#ai-security-sandbox/#security-sandbox/g' "$file"

    sed -i 's/## AI Developer Lifecycle/## Developer Lifecycle/g' "$file"
    sed -i 's/\[AI Developer Lifecycle\](#ai-developer-lifecycle)/[Developer Lifecycle](#developer-lifecycle)/g' "$file"
    sed -i 's/#ai-developer-lifecycle/#developer-lifecycle/g' "$file"

    sed -i 's/## AI Tool Integration/## Tool Integration/g' "$file"
    sed -i 's/\[AI Tool Integration\](#ai-tool-integration)/[Tool Integration](#tool-integration)/g' "$file"
    sed -i 's/#ai-tool-integration/#tool-integration/g' "$file"

    sed -i 's/## AI Issue Generation/## Issue Generation/g' "$file"
    sed -i 's/\[AI Issue Generation\](#ai-issue-generation)/[Issue Generation](#issue-generation)/g' "$file"
    sed -i 's/#ai-issue-generation/#issue-generation/g' "$file"

    sed -i 's/## Specification Driven Development/## Spec-First/g' "$file"
    sed -i 's/\[Specification Driven Development\](#specification-driven-development)/[Spec-First](#spec-first)/g' "$file"
    sed -i 's/#specification-driven-development/#spec-first/g' "$file"

    sed -i 's/## AI Plan-First Development/## Planned Implementation/g' "$file"
    sed -i 's/\[AI Plan-First Development\](#ai-plan-first-development)/[Planned Implementation](#planned-implementation)/g' "$file"
    sed -i 's/#ai-plan-first-development/#planned-implementation/g' "$file"

    sed -i 's/## Progressive AI Enhancement/## Progressive Enhancement/g' "$file"
    sed -i 's/\[Progressive AI Enhancement\](#progressive-ai-enhancement)/[Progressive Enhancement](#progressive-enhancement)/g' "$file"
    # No anchor change needed for Progressive Enhancement

    sed -i 's/## AI Choice Generation/## Choice Generation/g' "$file"
    sed -i 's/\[AI Choice Generation\](#ai-choice-generation)/[Choice Generation](#choice-generation)/g' "$file"
    sed -i 's/#ai-choice-generation/#choice-generation/g' "$file"

    sed -i 's/## Atomic Task Decomposition/## Atomic Decomposition/g' "$file"
    sed -i 's/\[Atomic Task Decomposition\](#atomic-task-decomposition)/[Atomic Decomposition](#atomic-decomposition)/g' "$file"
    sed -i 's/#atomic-task-decomposition/#atomic-decomposition/g' "$file"

    sed -i 's/## Parallelized AI Coding Agents/## Parallel Agents/g' "$file"
    sed -i 's/\[Parallelized AI Coding Agents\](#parallelized-ai-coding-agents)/[Parallel Agents](#parallel-agents)/g' "$file"
    sed -i 's/#parallelized-ai-coding-agents/#parallel-agents/g' "$file"

    sed -i 's/## AI Context Persistence/## Context Persistence/g' "$file"
    sed -i 's/\[AI Context Persistence\](#ai-context-persistence)/[Context Persistence](#context-persistence)/g' "$file"
    sed -i 's/#ai-context-persistence/#context-persistence/g' "$file"

    sed -i 's/## Constraint-Based AI Development/## Constrained Generation/g' "$file"
    sed -i 's/\[Constraint-Based AI Development\](#constraint-based-ai-development)/[Constrained Generation](#constrained-generation)/g' "$file"
    sed -i 's/#constraint-based-ai-development/#constrained-generation/g' "$file"

    sed -i 's/## Observable AI Development/## Observable Development/g' "$file"
    sed -i 's/\[Observable AI Development\](#observable-ai-development)/[Observable Development](#observable-development)/g' "$file"
    sed -i 's/#observable-ai-development/#observable-development/g' "$file"

    sed -i 's/## AI-Driven Refactoring/## Guided Refactoring/g' "$file"
    sed -i 's/\[AI-Driven Refactoring\](#ai-driven-refactoring)/[Guided Refactoring](#guided-refactoring)/g' "$file"
    sed -i 's/#ai-driven-refactoring/#guided-refactoring/g' "$file"

    sed -i 's/## AI-Driven Architecture Design/## Guided Architecture/g' "$file"
    sed -i 's/\[AI-Driven Architecture Design\](#ai-driven-architecture-design)/[Guided Architecture](#guided-architecture)/g' "$file"
    sed -i 's/#ai-driven-architecture-design/#guided-architecture/g' "$file"

    sed -i 's/## AI-Driven Traceability/## Automated Traceability/g' "$file"
    sed -i 's/\[AI-Driven Traceability\](#ai-driven-traceability)/[Automated Traceability](#automated-traceability)/g' "$file"
    sed -i 's/#ai-driven-traceability/#automated-traceability/g' "$file"

    sed -i 's/## Policy-as-Code Generation/## Policy Generation/g' "$file"
    sed -i 's/\[Policy-as-Code Generation\](#policy-as-code-generation)/[Policy Generation](#policy-generation)/g' "$file"
    sed -i 's/#policy-as-code-generation/#policy-generation/g' "$file"

    sed -i 's/## Security Scanning Orchestration/## Security Orchestration/g' "$file"
    sed -i 's/\[Security Scanning Orchestration\](#security-scanning-orchestration)/[Security Orchestration](#security-orchestration)/g' "$file"
    sed -i 's/#security-scanning-orchestration/#security-orchestration/g' "$file"

    sed -i 's/## Performance Baseline Management/## Baseline Management/g' "$file"
    sed -i 's/\[Performance Baseline Management\](#performance-baseline-management)/[Baseline Management](#baseline-management)/g' "$file"
    sed -i 's/#performance-baseline-management/#baseline-management/g' "$file"

    # Antipattern Renames
    sed -i 's/\*\*Anti-pattern: Rushing Into AI\*\*/\*\*Anti-pattern: Premature Adoption\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Context Drift\*\*/\*\*Anti-pattern: Broken Context\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Shared Agent Workspaces\*\*/\*\*Anti-pattern: Conflicting Workspaces\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Ad-Hoc AI Development\*\*/\*\*Anti-pattern: Unplanned Development\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Prompt-Only AI Development\*\*/\*\*Anti-pattern: Disconnected Prompting\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Vague Issue Generation\*\*/\*\*Anti-pattern: Under-Specified Issues\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Missing CI Integration\*\*/\*\*Anti-pattern: Broken Integration\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Implementation-First AI\*\*/\*\*Anti-pattern: Spec-Ignored\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Prompt Hoarding\*\*/\*\*Anti-pattern: Over-Prompting\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Blind Code Generation\*\*/\*\*Anti-pattern: Blind Generation\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Analysis Paralysis\*\*/\*\*Anti-pattern: Over-Analysis\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Big Bang Generation\*\*/\*\*Anti-pattern: Monolithic Generation\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Uncoordinated Parallel Execution\*\*/\*\*Anti-pattern: Uncoordinated Agents\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Knowledge Hoarding\*\*/\*\*Anti-pattern: Over-Documentation\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Context Bloat\*\*/\*\*Anti-pattern: Bloated Context\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Pseudo-Atomic Tasks\*\*/\*\*Anti-pattern: False Atomicity\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Black Box Development\*\*/\*\*Anti-pattern: Blind Development\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Shotgun Surgery\*\*/\*\*Anti-pattern: Scattered Refactoring\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Speculative Refactoring\*\*/\*\*Anti-pattern: Premature Refactoring\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Architecture Astronaut AI\*\*/\*\*Anti-pattern: Over-Architecting\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Manual Traceability Management\*\*/\*\*Anti-pattern: Broken Traceability\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Manual Policy Translation\*\*/\*\*Anti-pattern: Untested Policies\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: Alert Fatigue\*\*/\*\*Anti-pattern: Over-Alerting\*\*/g' "$file"
    sed -i 's/\*\*Anti-pattern: One-Off Alerts\*\*/\*\*Anti-pattern: Static Thresholds\*\*/g' "$file"

    echo "  ✅ Completed $file"
}

# Apply to main README
apply_renames "/home/user/ai-development-patterns/README.md"

echo ""
echo "✅ Pattern rename script completed successfully!"
echo "Note: Experimental patterns and other cross-references will be handled separately"
