#!/bin/bash
# Script to apply all experimental pattern name renames in experiments/README.md

set -e

echo "Applying experimental pattern name renames..."

file="/home/user/ai-development-patterns/experiments/README.md"

echo "Processing $file..."

# Experimental Pattern Renames (headers and references)
sed -i 's/## Human-AI Handoff Protocol/## Handoff Protocols/g' "$file"
sed -i 's/\[Human-AI Handoff Protocol\](#human-ai-handoff-protocol)/[Handoff Protocols](#handoff-protocols)/g' "$file"
sed -i 's/#human-ai-handoff-protocol/#handoff-protocols/g' "$file"

sed -i 's/## Comprehensive AI Testing Strategy/## Testing Orchestration/g' "$file"
sed -i 's/\[Comprehensive AI Testing Strategy\](#comprehensive-ai-testing-strategy)/[Testing Orchestration](#testing-orchestration)/g' "$file"
sed -i 's/#comprehensive-ai-testing-strategy/#testing-orchestration/g' "$file"

sed -i 's/## AI Workflow Orchestration/## Workflow Orchestration/g' "$file"
sed -i 's/\[AI Workflow Orchestration\](#ai-workflow-orchestration)/[Workflow Orchestration](#workflow-orchestration)/g' "$file"
sed -i 's/#ai-workflow-orchestration/#workflow-orchestration/g' "$file"

sed -i 's/## AI Review Automation/## Review Automation/g' "$file"
sed -i 's/\[AI Review Automation\](#ai-review-automation)/[Review Automation](#review-automation)/g' "$file"
sed -i 's/#ai-review-automation/#review-automation/g' "$file"

sed -i 's/## Technical Debt Forecasting/## Debt Forecasting/g' "$file"
sed -i 's/\[Technical Debt Forecasting\](#technical-debt-forecasting)/[Debt Forecasting](#debt-forecasting)/g' "$file"
sed -i 's/#technical-debt-forecasting/#debt-forecasting/g' "$file"

# Pipeline Synthesis - no change
sed -i 's/## AI-Guided Blue-Green Deployment/## Deployment Synthesis/g' "$file"
sed -i 's/\[AI-Guided Blue-Green Deployment\](#ai-guided-blue-green-deployment)/[Deployment Synthesis](#deployment-synthesis)/g' "$file"
sed -i 's/#ai-guided-blue-green-deployment/#deployment-synthesis/g' "$file"

sed -i 's/## Drift Detection & Remediation/## Drift Remediation/g' "$file"
sed -i 's/\[Drift Detection & Remediation\](#drift-detection--remediation)/[Drift Remediation](#drift-remediation)/g' "$file"
sed -i 's/#drift-detection--remediation/#drift-remediation/g' "$file"

sed -i 's/## Release Note Synthesis/## Release Synthesis/g' "$file"
sed -i 's/\[Release Note Synthesis\](#release-note-synthesis)/[Release Synthesis](#release-synthesis)/g' "$file"
sed -i 's/#release-note-synthesis/#release-synthesis/g' "$file"

sed -i 's/## Incident Response Automation/## Incident Automation/g' "$file"
sed -i 's/\[Incident Response Automation\](#incident-response-automation)/[Incident Automation](#incident-automation)/g' "$file"
sed -i 's/#incident-response-automation/#incident-automation/g' "$file"

sed -i 's/## Test Suite Health Management/## Suite Health/g' "$file"
sed -i 's/\[Test Suite Health Management\](#test-suite-health-management)/[Suite Health](#suite-health)/g' "$file"
sed -i 's/#test-suite-health-management/#suite-health/g' "$file"

sed -i 's/## Dependency Upgrade Advisor/## Upgrade Advisor/g' "$file"
sed -i 's/\[Dependency Upgrade Advisor\](#dependency-upgrade-advisor)/[Upgrade Advisor](#upgrade-advisor)/g' "$file"
sed -i 's/#dependency-upgrade-advisor/#upgrade-advisor/g' "$file"

sed -i 's/## On-Call Handoff Automation/## Handoff Automation/g' "$file"
sed -i 's/\[On-Call Handoff Automation\](#on-call-handoff-automation)/[Handoff Automation](#handoff-automation)/g' "$file"
sed -i 's/#on-call-handoff-automation/#handoff-automation/g' "$file"

sed -i 's/## Chaos Engineering Scenarios/## Chaos Engineering/g' "$file"
sed -i 's/\[Chaos Engineering Scenarios\](#chaos-engineering-scenarios)/[Chaos Engineering](#chaos-engineering)/g' "$file"
sed -i 's/#chaos-engineering-scenarios/#chaos-engineering/g' "$file"

sed -i 's/## ChatOps Security Integration/## ChatOps Security/g' "$file"
sed -i 's/\[ChatOps Security Integration\](#chatops-security-integration)/[ChatOps Security](#chatops-security)/g' "$file"
sed -i 's/#chatops-security-integration/#chatops-security/g' "$file"

sed -i 's/## Compliance Evidence Automation/## Evidence Automation/g' "$file"
sed -i 's/\[Compliance Evidence Automation\](#compliance-evidence-automation)/[Evidence Automation](#evidence-automation)/g' "$file"
sed -i 's/#compliance-evidence-automation/#evidence-automation/g' "$file"

sed -i 's/## Context Window Optimization/## Context Optimization/g' "$file"
sed -i 's/\[Context Window Optimization\](#context-window-optimization)/[Context Optimization](#context-optimization)/g' "$file"
sed -i 's/#context-window-optimization/#context-optimization/g' "$file"

sed -i 's/## Visual Context Scaffolding/## Visual Scaffolding/g' "$file"
sed -i 's/\[Visual Context Scaffolding\](#visual-context-scaffolding)/[Visual Scaffolding](#visual-scaffolding)/g' "$file"
sed -i 's/#visual-context-scaffolding/#visual-scaffolding/g' "$file"

sed -i 's/## AI Event Automation/## Event Automation/g' "$file"
sed -i 's/\[AI Event Automation\](#ai-event-automation)/[Event Automation](#event-automation)/g' "$file"
sed -i 's/#ai-event-automation/#event-automation/g' "$file"

sed -i 's/## Custom AI Commands/## Custom Commands/g' "$file"
sed -i 's/\[Custom AI Commands\](#custom-ai-commands)/[Custom Commands](#custom-commands)/g' "$file"
sed -i 's/#custom-ai-commands/#custom-commands/g' "$file"

# Error Resolution - no change needed

# Experimental Antipattern Renames
sed -i 's/\*\*Anti-pattern: Unclear Boundaries\*\*/\*\*Anti-pattern: Broken Boundaries\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Test Generation Without Strategy\*\*/\*\*Anti-pattern: Scattered Testing\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Uncoordinated Multi-Tool Usage\*\*/\*\*Anti-pattern: Chaotic Orchestration\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Unsafe Parallel Execution\*\*/\*\*Anti-pattern: Unsafe Parallelism\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Manual-Only Review\*\*/\*\*Anti-pattern: Manual Reviews\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Reactive Debt Management\*\*/\*\*Anti-pattern: Reactive Debt\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Manual Pipeline Maintenance\*\*/\*\*Anti-pattern: Manual Pipelines\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Blue-Green-Canary Confusion\*\*/\*\*Anti-pattern: Confused Deployment\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Manual Drift Checking\*\*/\*\*Anti-pattern: Manual Drift\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Manual Release Notes\*\*/\*\*Anti-pattern: Manual Releases\*\*/g' "$file"
# Static Runbooks - no change
sed -i 's/\*\*Anti-pattern: Ignoring Flaky Tests\*\*/\*\*Anti-pattern: Ignored Flakiness\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Batch Upgrades\*\*/\*\*Anti-pattern: Reckless Upgrades\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Verbal-Only Handoffs\*\*/\*\*Anti-pattern: Undocumented Handoffs\*\*/g' "$file"
# Random Chaos - no change
sed -i 's/\*\*Anti-pattern: Delayed Security Feedback\*\*/\*\*Anti-pattern: Delayed Security\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Manual Evidence Collection\*\*/\*\*Anti-pattern: Manual Evidence\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: One-Size-Fits-All\*\*/\*\*Anti-pattern: Wasteful Context\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Kitchen Sink Upload\*\*/\*\*Anti-pattern: Overwhelming Visuals\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Unchecked Event Commands\*\*/\*\*Anti-pattern: Unchecked Events\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Ignoring Built-in Commands\*\*/\*\*Anti-pattern: Redundant Commands\*\*/g' "$file"
# Shallow Commands - no change
# Hardcoded Context - no change
sed -i 's/\*\*Anti-pattern: Context-Free Error Messages\*\*/\*\*Anti-pattern: Contextless Errors\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Blind Fix Application\*\*/\*\*Anti-pattern: Blind Fixes\*\*/g' "$file"
sed -i 's/\*\*Anti-pattern: Missing Rollback Strategy\*\*/\*\*Anti-pattern: Unprotected Fixes\*\*/g' "$file"

# Update references to main patterns (from README.md) in experimental patterns
sed -i 's/AI Developer Lifecycle](\.\.\/README\.md#ai-developer-lifecycle)/Developer Lifecycle](..\/README.md#developer-lifecycle)/g' "$file"
sed -i 's/Observable AI Development](\.\.\/README\.md#observable-ai-development)/Observable Development](..\/README.md#observable-development)/g' "$file"
sed -i 's/Specification Driven Development](\.\.\/README\.md#specification-driven-development)/Spec-First](..\/README.md#spec-first)/g' "$file"
sed -i 's/AI Tool Integration](\.\.\/README\.md#ai-tool-integration)/Tool Integration](..\/README.md#tool-integration)/g' "$file"
sed -i 's/Atomic Task Decomposition](\.\.\/README\.md#atomic-task-decomposition)/Atomic Decomposition](..\/README.md#atomic-decomposition)/g' "$file"
sed -i 's/AI-Driven Refactoring](\.\.\/README\.md#ai-driven-refactoring)/Guided Refactoring](..\/README.md#guided-refactoring)/g' "$file"
sed -i 's/AI-Driven Architecture Design](\.\.\/README\.md#ai-driven-architecture-design)/Guided Architecture](..\/README.md#guided-architecture)/g' "$file"
sed -i 's/Progressive AI Enhancement](\.\.\/README\.md#progressive-ai-enhancement)/Progressive Enhancement](..\/README.md#progressive-enhancement)/g' "$file"
sed -i 's/Rules as Code](\.\.\/README\.md#rules-as-code)/Codified Rules](..\/README.md#codified-rules)/g' "$file"
sed -i 's/AI Security Sandbox](\.\.\/README\.md#ai-security-sandbox)/Security Sandbox](..\/README.md#security-sandbox)/g' "$file"
sed -i 's/Performance Baseline Management](\.\.\/README\.md#performance-baseline-management)/Baseline Management](..\/README.md#baseline-management)/g' "$file"
sed -i 's/Security Scanning Orchestration](\.\.\/README\.md#security-scanning-orchestration)/Security Orchestration](..\/README.md#security-orchestration)/g' "$file"

echo "  ✅ Completed $file"

echo ""
echo "✅ Experimental pattern rename script completed successfully!"
