# Repository Validation Tests

This directory contains the deterministic checks for the pattern catalog, examples, generated
site, adoption-evidence records, local evaluation controls, workflows, and repository governance.
Plain `pytest` is the canonical runner; every `test_*.py` module is discovered automatically.

## Setup

Use Python 3.11 or newer and install the pinned dependencies:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --requirement tests/requirements.txt
```

Node.js 24 and npm 11 are also required to reproduce the locked TypeScript example builds.

## Commands

Run the same two non-network suites used by the required `Validation gate`:

```bash
(cd examples/spec-driven-development && python3 -m pytest -q)
python3 -m pytest -m "not slow" -q
```

Run one module or test while developing:

```bash
python3 -m pytest tests/test_pattern_compliance.py -q
python3 -m pytest \
  tests/test_pattern_compliance.py::TestPatternSpecCompliance -q
```

Run network-backed checks explicitly. They are excluded from the default command because remote
sites can fail transiently:

```bash
python3 -m pytest \
  tests/test_links.py \
  tests/test_evidence_files.py \
  tests/test_evidence_content.py \
  -m slow -v --tb=short
```

Build and test the locked TypeScript examples:

```bash
for directory in \
  examples/centralized-rules/gateway-strategy/ai-dev-cli \
  examples/centralized-rules/gateway-strategy/ai-gateway \
  examples/centralized-rules/gateway-strategy/org-ai-client
do
  (cd "$directory" && npm ci --ignore-scripts && npm run build && npm run test --if-present)
done
```

## Test surfaces

### Catalog and generated site

- `test_pattern_compliance.py` — required pattern structure and formatting.
- `test_readme_accuracy.py` — reference-table and catalog consistency.
- `test_yaml_readme_sync.py` — `patterns.yaml` parity with the stable README catalog.
- `test_validate_pattern_names.py` — canonical pattern and anti-pattern names.
- `test_dependencies.py` and `test_diagram.py` — dependency validity and rendered graph accuracy.
- `test_patterns_data.py` — generated `assets/js/patterns-data.js` and site wiring.
- `test_taxonomy_migration.py` and `test_issue_generation_sizing.py` — retained migration and
  terminology invariants.

### Documentation and examples

- `test_links.py` — internal links by default and external links under the `slow` marker.
- `test_examples.py` — tracked example layout and syntax.

### Adoption evidence and local evaluation

- `test_evidence_files.py`, `test_evidence_content.py`, and `test_verification_status.py` — evidence
  schema, source admission, derived verdicts, and generated status.
- `test_verification_inventory.py` — bounded catalog inventory and execution-plan generation.
- `test_local_research_scope.py` and `test_local_verification.py` — approved local-only scope,
  provenance, search-ledger, and publication gates.
- `test_candidate_secret_scan.py` — credential-pattern rejection in publishable candidate data.

### CI, dependencies, and governance

- `test_verification_workflows.py` and `test_workflow_policy.py` — model-free workflows,
  deterministic required gates, advisory network checks, immutable trusted checkouts, least
  privilege, and provider-call rejection.
- `test_repository_rules.py` — repository rules, Actions policy, and security-setting configuration.
- `test_dependency_security.py` — lockfile, Dependabot, audit, and dependency-review coverage.
- `test_docker_examples.py` — provider-free simulator behavior, sandbox fail-closed probes, and
  parallel-branch merge integration.
- `test_pytest_configuration.py` — marker registration and test-discovery policy.

## Utilities

`tests/utils/` contains reusable parsers and validators:

- `pattern_parser.py` and `experimental_pattern_parser.py`
- `link_checker.py` and `markdown_link_validator.py`
- `example_validator.py`
- `git_utils.py`

Shared fixtures and canonical catalog expectations live in `tests/conftest.py`. Marker definitions
and discovery exclusions live in the root `pytest.ini`.

## GitHub Actions

- `.github/workflows/pattern-validation.yml` builds locked TypeScript examples, runs the embedded
  Spec-Driven Development gate plus the complete repository non-slow suite, uploads their reports,
  and exposes the required `Validation gate`.
- `.github/workflows/docker-example-compatibility.yml` builds and smoke-tests the two maintained
  Docker examples on relevant changes, on demand, and weekly. It deliberately pulls mutable live
  images/packages, so its `Docker example compatibility` result is advisory rather than a required
  deterministic check. It receives no provider credentials and makes no model calls.
- `.github/workflows/evidence-validation.yml` recomputes adoption verdicts and runs the focused
  evidence/governance subset on demand, on relevant changes, and weekly.
- `.github/workflows/trusted-evidence-validation.yml` treats pull-request files as inert data and
  executes only validator code from the immutable base revision.
- `.github/workflows/dependency-security.yml` rejects newly introduced vulnerable dependencies.

The weekly link and Docker compatibility jobs are advisory because network availability and live
upstreams are outside repository control. Deterministic failures block the stable aggregate checks.

## Reports

The pattern-validation workflow writes reports under `tests/test-results/` in one execution:

- `junit.xml`
- `spec-driven-junit.xml`
- `spec-driven-report.json`
- `report.html`
- `report.json`
- `coverage/`

The directory is ignored locally and uploaded as the `deterministic-validation-report` artifact in
GitHub Actions. A failed run also renders `scripts/generate-audit-prompt.py` output in the workflow
summary for a signed-in local coding-agent session.

## Adding validation

1. Add or extend a `tests/test_*.py` module; pytest discovers it without a registry edit.
2. Keep default tests deterministic and credential-free. Mark live network checks with `slow`.
3. Add focused fixtures to `tests/conftest.py` or a utility under `tests/utils/` only when reused.
4. Update this file when a new validation surface changes the repository contract.
5. Run the complete non-slow suite and the relevant generated-artifact checks before committing.
