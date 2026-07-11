# Experimental Pattern Examples

This directory contains working implementations of selected experimental patterns from the catalog in [experiments/README.md](../README.md).

## Example Catalog

| Experimental Pattern | Example Directory | Notes |
|----------------------|------------------|-------|
| [Autonomous Remediation](../README.md#autonomous-remediation) | [`autonomous-remediation/`](autonomous-remediation/) | Detector-driven remediation loop under further evaluation |
| [Dependency Migration](../README.md#dependency-migration) | [`dependency-migration/`](dependency-migration/) | Agentic compatibility analysis and staged migration |
| [Feedback Flywheel](../README.md#feedback-flywheel) | [`feedback-flywheel/`](feedback-flywheel/) | Retrospective-driven rule improvement |
| [Handoff Protocols](../README.md#handoff-protocols) | [`handoff-protocols/`](handoff-protocols/) | Human ↔ AI handoff decisioning and procedures |
| [Incident Automation](../README.md#incident-automation) | [`incident-automation/`](incident-automation/) | Generate incident response playbooks |
| [Pipeline Synthesis](../README.md#pipeline-synthesis) | [`pipeline-synthesis/`](pipeline-synthesis/) | Convert build specs into validated build, deployment, and release workflows |
| [Review Automation](../README.md#review-automation) | [`review-automation/`](review-automation/) | Automate review of parallel outputs |
| [Security Orchestration](../README.md#security-orchestration) | [`security-orchestration/`](security-orchestration/) | Aggregate security findings for review |
| [Test Promotion](../README.md#test-promotion) | [`test-promotion/`](test-promotion/) | Separate generated tests from golden tests |
| [Testing Orchestration](../README.md#testing-orchestration) | [`testing-orchestration/`](testing-orchestration/) | Coordinated testing strategy and automation |
| [Workflow Orchestration](../README.md#workflow-orchestration) | [`workflow-orchestration/`](workflow-orchestration/) | Coordinate sequential and parallel workflows |

## Getting Started

1. Review stable prerequisites in the main catalog:
   - [Security Sandbox](../../README.md#security-sandbox)
   - [Tool Integration](../../README.md#tool-integration)
   - [Spec-Driven Development](../../README.md#spec-driven-development)
2. Pick an experimental example directory from the table above.
3. Follow the `README.md` in that directory.

Examples for promoted patterns now live in the main [examples directory](../../examples/), including [Bounded Autonomy](../../examples/bounded-autonomy/), [Code Research](../../examples/code-research/), [Debt Forecasting](../../examples/debt-forecasting/), and [Drift Remediation](../../examples/drift-remediation/).
