# Experimental Pattern Examples

This directory contains a mix of runnable prototypes, reference specifications, and design
documents for selected patterns in [experiments/README.md](../README.md). Each entry states its
implementation status and limitations; directory presence does not imply a complete implementation.

## Example Catalog

| Experimental Pattern | Example Directory | Notes |
|----------------------|------------------|-------|
| [Autonomous Remediation](../README.md#autonomous-remediation) | [`autonomous-remediation/`](autonomous-remediation/) | Runnable Claude Code hook prototype with Python/secret detectors |
| [Dependency Migration](../README.md#dependency-migration) | [`dependency-migration/`](dependency-migration/) | Documented migration contract and staged workflow; provider adapters are not shipped |
| [Feedback Flywheel](../README.md#feedback-flywheel) | [`feedback-flywheel/`](feedback-flywheel/) | Runnable file-based retrospective analyzer plus annotated example |
| [Handoff Protocols](../README.md#handoff-protocols) | [`handoff-protocols/`](handoff-protocols/) | Runnable pre-task assessor; the pattern's Return Contract is not implemented |
| [Incident Automation](../README.md#incident-automation) | [`incident-automation/`](incident-automation/) | Incident playbook reference; no generator or triage automation ships |
| [Pipeline Synthesis](../README.md#pipeline-synthesis) | [`pipeline-synthesis/`](pipeline-synthesis/) | CI and deployment reference specifications; no generator ships |
| [Review Automation](../README.md#review-automation) | [`review-automation/`](review-automation/) | Runnable inert diff reviewer for deterministic findings; no semantic model reviewer |
| [Security Orchestration](../README.md#security-orchestration) | [`security-orchestration/`](security-orchestration/) | Design reference for findings aggregation; no scan orchestrator ships |
| [Test Promotion](../README.md#test-promotion) | [`test-promotion/`](test-promotion/) | Runnable local scripts plus inactive hook/workflow/CODEOWNERS templates |
| [Testing Orchestration](../README.md#testing-orchestration) | [`testing-orchestration/`](testing-orchestration/) | Test-contract configurations and scenarios; no orchestration runner ships |
| [Workflow Orchestration](../README.md#workflow-orchestration) | [`workflow-orchestration/`](workflow-orchestration/) | Concept and contracts only; no workflow scripts ship |

## Getting Started

1. Review stable prerequisites in the main catalog:
   - [Security Sandbox](../../README.md#security-sandbox)
   - [Tool Integration](../../README.md#tool-integration)
   - [Spec-Driven Development](../../README.md#spec-driven-development)
2. Pick an experimental example directory from the table above.
3. Follow the `README.md` in that directory.

Examples for promoted patterns live in the main [examples directory](../../examples/), including [Bounded Autonomy](../../examples/bounded-autonomy/), [Code Research](../../examples/code-research/), [Debt Forecasting](../../examples/debt-forecasting/), and [Drift Remediation](../../examples/drift-remediation/).
