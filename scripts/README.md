# Repository Scripts

These scripts maintain the catalog, generated site, adoption-evidence records, local-only research
controls, and repository governance. Use Python 3.11 or newer. Install the pinned project/test
dependencies before running evidence or YAML-backed commands.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --requirement tests/requirements.txt
```

## Catalog and site

### `validate-pattern-names.py`

Validates canonical stable and experimental names against `pattern-spec.md`, including exact
two-word spelling, identifiers, anchors, table/section parity, and anti-pattern conventions.
Primary caller: `.github/workflows/pattern-validation.yml`.

```bash
python3 scripts/validate-pattern-names.py
```

### `update-pattern-count.py`

Counts stable entries in `patterns.yaml` and rewrites the matching badges in `README.md` and
`index.html`. Primary callers: `build.sh` and the deterministic validation workflow.

```bash
python3 scripts/update-pattern-count.py
```

Typical output:

```text
Found 29 patterns
Updated 1 badge(s) in README.md
Updated 1 badge(s) in index.html
All badges updated to 29
```

If the count is unexpected, inspect the `patterns` list in `patterns.yaml`, then run the name and
README/YAML synchronization tests. The command requires PyYAML through the pinned dependencies.

### `generate-patterns-data.py`

Parses the stable reference table and pattern sections in `README.md`, writes
`assets/js/patterns-data.js`, and refreshes the generated dependency diagram in `index.html`.
Primary callers: `build.sh`, the Pages workflow, and deterministic validation.

```bash
python3 scripts/generate-patterns-data.py
python3 scripts/generate-patterns-data.py --check
```

This generator uses the Python standard library. The broader site build is not stdlib-only because
the count updater reads YAML. Site styling lives in `assets/css/`; the favicon is
`assets/img/patterns-favicon.svg`.

### `build.sh`

Canonical generated-site entrypoint. It updates count badges, regenerates site data and the
diagram, and writes ignored deployment metadata to `build-info.json`. Primary caller:
`.github/workflows/deploy-pages.yml`.

```bash
bash scripts/build.sh
```

### `pre-commit-patterns.sh`

Optional local pre-commit hook that runs `build.sh` when a catalog/site source is staged and
re-stages the generated artifacts. This is the sole supported pre-commit hook in `scripts/`.

```bash
cp scripts/pre-commit-patterns.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Local pattern-adoption evaluation

Model-backed research is allowed only in a signed-in local Codex session through the
`evaluate-pattern-adoption` skill. GitHub Actions and evaluator API-key environments are rejected.
See `verification/README.md` for the end-to-end method and approval boundaries.

### `build-verification-inventory.py`

Builds the stable/exploratory inventory, selects bounded work, and emits the immutable local
execution matrix and per-unit worklists. Primary caller: `plan-local-verification.py`.

### `plan-local-verification.py`

Creates and approves content-bound local run manifests. It checks clean-worktree/origin state,
scope, unit/turn/search bounds, client attestation, and exact human approval text. Primary caller:
the local evaluation skill.

```bash
python3 scripts/plan-local-verification.py plan \
  --scope single \
  --pattern "Dependency Migration" \
  --surface codex-app \
  --attest-chatgpt
```

### `local_verification.py`

Shared fail-closed library for manifest parsing, canonical hashing, approval validation,
search-ledger reconciliation, path limits, and local-only environment checks. Primary callers: the
planner, recorder, finalizer, and deterministic tests.

### `record-local-search-event.py`

Validates one actual local search receipt, discards candidate URLs after counting them, and appends
a sanitized hash-chained event bound to the approved run. Primary caller: the local evaluation
skill after each visible search.

### `hydrate-evidence-content.py`

Fetches admitted public evidence URLs through bounded SSRF-safe retrieval and records normalized
content/quote hashes and retrieval metadata. Primary caller: the local evaluation skill before
independent verification.

### `evidence_content.py`

Shared source-admission, DNS/IP safety, content normalization, quote-matching, deadline, and hash
logic. Primary callers: the hydrator, evidence validator, and evidence tests.

### `validate-research-scope.py`

Enforces the exact allowed changed-path set for evidence and discovery units and rejects hidden
worktree additions. Primary caller: `finalize-local-verification.py`.

### `finalize-local-verification.py`

Reconciles an approved manifest and sanitized search ledger, validates scope/provenance, updates
derived evidence state, scans for credentials, and runs focused deterministic tests. It never
commits, pushes, opens a pull request, or merges. Primary caller: the local evaluation skill after
independent review.

## Evidence validation and derived records

### `validate-evidence.py`

Validates every evidence file, source tier, mechanism quote, score, verdict, provenance binding,
catalog relationship, and pending-evidence exception. Primary callers: evidence workflows,
trusted pull-request validation, and the local finalizer.

### `generate-verification-status.py`

Recomputes `verification/STATUS.md` from evidence plus the stable and exploratory catalogs.
Primary callers: the evidence workflow and local finalizer.

### `sync-verification-decisions.py`

Synchronizes evidence-derived naming signals in `verification/DECISIONS.md` without making the
maintainer's adoption or rename decision. Primary caller: the local finalizer.

### `scan-candidate-secrets.py`

Scans the bounded publishable candidate surface for credential-like values and provider secrets.
Primary callers: trusted pull-request validation and the local finalizer.

## CI and repository governance

### `validate-workflow-policy.py`

Parses candidate workflows and the protected trust-root inventory as inert data. It rejects hosted
model/provider surfaces, credentials, unsafe action references, overbroad permissions, executable
candidate indirection, tracked caches, unsafe modes, and unapproved trust-root changes. Primary
caller: `.github/workflows/trusted-evidence-validation.yml`.

```bash
python3 scripts/validate-workflow-policy.py \
  --trusted-root . \
  --candidate-root . \
  .github/workflows
```

### `configure-repository-rules.py`

Audits or applies the main-branch ruleset, Actions allowlist/SHA pinning, fork approval policy,
retired secret/variable cleanup, secret scanning, push protection, and CodeQL default setup. For
checked-in workflows and PR candidates, direct hosted-model surfaces in workflow YAML are rejected by
workflow policy, named retired credentials are removed, and Actions is limited to the selected
SHA-pinned action allowlist; the unavailable public-preview Models Settings route is not treated as an
attested control. A changed protected script requires the commit-bound owner trust approval documented
in `verification/README.md`. These are not account-wide controls and cannot inspect an unreviewed
same-repository branch before it runs. Primary caller: a maintainer from a clean `main` checkout. See
`verification/README.md` for the enforcement boundary.

```bash
python3 scripts/configure-repository-rules.py
python3 scripts/configure-repository-rules.py --apply
```

### `generate-audit-prompt.py`

Converts the deterministic pytest JSON report into a bounded local-agent repair prompt. Primary
caller: the failure-summary step in `.github/workflows/pattern-validation.yml`. The optional
`--rerun-command` keeps a nested-suite prompt bound to that suite's exact local reproduction
command instead of the repository-root default.

```bash
python3 scripts/generate-audit-prompt.py tests/test-results/report.json
python3 scripts/generate-audit-prompt.py \
  --rerun-command \
  'cd examples/spec-driven-development && python3 -m pytest -x -q' \
  tests/test-results/spec-driven-report.json
```

## Routine consistency gate

After editing catalog or tooling files, run:

```bash
python3 scripts/validate-pattern-names.py
python3 scripts/update-pattern-count.py
bash scripts/build.sh
python3 scripts/generate-patterns-data.py --check
python3 -m pytest -m "not slow" -q
```

Do not stage the ignored `build-info.json`. Commit generated `index.html` or
`assets/js/patterns-data.js` only when the canonical source changes them.
