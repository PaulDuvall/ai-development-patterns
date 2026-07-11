# Testing Orchestration Example

This example implements the experimental [Testing Orchestration](../../README.md#testing-orchestration) pattern: a coordination layer generates candidate tests from human-owned specifications, evaluates them against quality gates, and promotes only reviewed tests into a protected baseline.

## Current Status

What ships here is declarative test-specification content, not an executable harness:

- Two machine-parsable configuration files — [`pipeline_tests/pipeline_tests.yaml`](pipeline_tests/pipeline_tests.yaml) and [`unit_tests/unit_tests.yml`](unit_tests/unit_tests.yml) — defining CI pipeline validation rules and function-to-test contracts for a sample authentication service.
- A human-readable catalog of acceptance test scenarios in [`acceptance_tests/README.md`](acceptance_tests/README.md).

The orchestration machinery the pattern describes — AI test generation, quality-gate enforcement, flake analysis, promotion review — is documented concept only. No script, runner, or pipeline in this directory executes these specifications; adopters supply their own runner (a CI job, an agent workflow, or a test-framework plugin) that consumes these files.

## Files

- [`acceptance_tests/README.md`](acceptance_tests/README.md) — acceptance test scenarios for a sample authentication API: end-to-end login/refresh/logout journeys, profile CRUD and input-validation cases, JWT and HTTPS security checks, performance targets, and failure-recovery scenarios, each with explicit steps and success criteria.
- [`pipeline_tests/pipeline_tests.yaml`](pipeline_tests/pipeline_tests.yaml) — machine-parsable CI pipeline validation rules: build success criteria, test-execution commands with coverage thresholds, lint and complexity quality gates, security scans, performance benchmarks, deployment checks, environment-specific overrides, and failure-handling policy.
- [`unit_tests/unit_tests.yml`](unit_tests/unit_tests.yml) — machine-parsable unit-test contract mapping source functions to test files, fixtures, mocks, named test cases, and per-function coverage targets, plus fixture, mock, and factory definitions and execution settings.

## Quick Start

The specification files are input contracts for whatever executes the tests. Confirm they parse before wiring them into a runner (requires PyYAML):

```bash
python -c "import yaml, sys; [yaml.safe_load(open(f)) for f in sys.argv[1:]]" \
  pipeline_tests/pipeline_tests.yaml unit_tests/unit_tests.yml
```

No generator ships with this example. To exercise the contract, ask your own configured AI
assistant to use `unit_tests/unit_tests.yml` as the authoritative contract and generate candidate
pytest tests for `src.auth.service.authenticate_user`. The request should cover every listed test
case, fixture, and mock, and treat coverage targets as minimums rather than goals to relax.

Generated tests remain candidates: your runner evaluates them against the gates in `pipeline_tests/pipeline_tests.yaml` and a human reviews them before they join the protected baseline.

## Integration with AI Development Patterns

### [Spec-Driven Development](../../../README.md#spec-driven-development)
- The YAML files are human-owned specifications; generated tests are checked against them rather than redefining expected behavior
- `unit_tests/unit_tests.yml` links each function to named test cases and coverage targets, preserving traceability between contract and tests
- Acceptance criteria in `acceptance_tests/README.md` are written as concrete steps with explicit success criteria, ready for conversion to executable tests

### [Agent Observability](../../../README.md#agent-observability)
- The pattern calls for recording prompts, test commands, coverage deltas, and promotion decisions; the reporting section of `pipeline_tests/pipeline_tests.yaml` defines the output formats and directories for that record
- Failure-handling and retry policy in the pipeline rules give an observability layer defined events to capture and analyze

## Known Limitations

- No executable orchestration ships here: nothing in this directory generates, runs, or gates tests. The specifications describe what a runner must enforce.
- The specifications target a fictional Python authentication service using pytest, Docker, and GitHub Actions; other stacks must translate the commands and tool names.
- Tool references inside the YAML files (trivy, bandit, radon, safety, trufflehog) are examples, not pinned dependencies of this repository.
- Coverage thresholds and performance targets are illustrative defaults, not calibrated recommendations.

## Promotion Path

Promotion requires a working reference runner that consumes these specifications end to end (candidate generation, gate evaluation, promotion review), evidence that gated promotion catches weakened or self-serving assertions in practice, and independent practitioner adoption beyond a single language stack.

## Anti-pattern: Scattered Testing

Generating tests ad hoc — without a specification contract, an execution record, or a promotion gate — produces duplicated coverage and false confidence. Keep human-owned specifications like the files in this directory authoritative, and treat every generated test as a candidate until it passes review.
