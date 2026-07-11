# Scripts Directory

This directory contains automation scripts for maintaining the AI Development Patterns repository.

## Available Scripts

### Local Pattern-Adoption Evaluation

Model-backed adoption research is a local Codex-agent workflow. Invoke
`$evaluate-pattern-adoption` from a local Codex app, CLI, or IDE session that is signed in with the
intended ChatGPT account. Local execution follows the active authentication: ChatGPT-plan sign-in
uses that plan's Codex allowance or credits, while API-key authentication is billed as OpenAI
Platform API usage. Do not use API-key authentication for this workflow.

#### `plan-local-verification.py`

Builds the deterministic catalog inventory and immutable run plan before any model or subagent is
called. It refuses GitHub Actions and known evaluator API-key environment variables. Supported
scopes are `stale`, `stable`, `exploratory`, `all`, `single`, and `discovery`.
It also reads open main-targeting PR file metadata through `gh`: stale selection excludes in-flight
evidence, while exact scopes stop rather than silently reduce their promised unit count.

Run it only from a dedicated clean branch or worktree whose `HEAD` is the current `origin/main` and
whose `git status --short` output is empty. The final scope validator intentionally fails when the
worktree contains paths outside the approved run; do not hide unrelated changes with a stash or
fold them into the evaluation.

```bash
python3 scripts/plan-local-verification.py plan \
  --scope stale \
  --surface codex-app \
  --attest-chatgpt
```

Review the printed unit counts and bounds, then bind the exact human response requested by the
planner:

```bash
python3 scripts/plan-local-verification.py approve \
  --manifest verification/local-runs/codex-local-<uuid>.yaml \
  --confirmation "APPROVE LOCAL EVALUATION <plan-id>"
```

Approval records the exact plan and makes the manifest read-only. It is an operator attestation
about the active client, not cryptographic proof of billing mode or of the operator's identity. CI
proves byte and plan consistency; it cannot prove that a repository writer did not forge YAML.

If a pending plan is declined, remove only its pending manifest and its ephemeral inventory,
worklist, and `verification/run-plan/` artifacts. Do not commit the pending plan or delete an
approved manifest.

#### `local_verification.py`

Provides fail-closed local run-manifest and search-ledger parsing, canonical plan/event hashing,
UUID-bound paths, content hashing, duplicate-key and YAML-alias rejection, approval validation, and
exact evidence-to-ledger reconciliation. Complete local evidence binds the exact committed manifest
bytes with `run_ref` and `run_manifest_sha256`.

#### `record-local-search-event.py`

Records one sanitized receipt immediately after an approved local research search. The root task
passes the visible tool identifier, exact mode/query, and each distinct public candidate URL that
was actually examined. Trusted code validates the URLs, derives the candidate count, discards the
URLs, and appends only the tool/mode/query/count to a run-bound hash chain:

```bash
python3 scripts/record-local-search-event.py \
  --manifest verification/local-runs/codex-local-<uuid>.yaml \
  --manifest-sha256 <approved-manifest-sha256> \
  --unit dependency-migration \
  --mode artifact \
  --tool web.search_query \
  --query "dependency update agent migration pull request" \
  --candidate-url https://example.com/public-source
```

The recorder refuses GitHub Actions and evaluator API-key environments. It rejects credentials,
credential-bearing URLs, out-of-scope units, and more than 12 events per unit. A truthful retry may
repeat the exact query; its distinct sequence number and event hash preserve the ordered attempt.
It never accepts or stores raw tool output or reasoning. The resulting
`codex-local-<uuid>-search-events.yaml` file binds the run ID, approved-manifest digest, and
research-contract digest and is written with owner-only local permissions.

#### `finalize-local-verification.py`

Finalizes one approved run without publishing it. It first validates complete ledger coverage and
exactly reconciles every evidence mode's ordered queries and candidate count. It then enforces exact
changed-path and provenance scope, updates the pending list and generated status, synchronizes
evidence-derived decision signals, recomputes verdicts, scans candidate files for credentials, and
runs the deterministic evidence tests.

```bash
python3 scripts/finalize-local-verification.py \
  --manifest verification/local-runs/codex-local-<uuid>.yaml \
  --manifest-sha256 <sha256>
```

The finalizer does not commit, push, create a PR, or merge. The skill requires a second human
approval after the final diff is available, then permits one draft evidence PR and never
auto-merges it. GitHub Actions runs only deterministic validation plus read-only link/content
checks for this capability.

### Canonical Pattern-Name Validation

#### `validate-pattern-names.py`

Validates every active canonical name: stable patterns from `patterns.yaml` and experimental
patterns from the bounded reference table in `experiments/README.md`. It enforces the exact
two-word, Title Case, no-`AI`-prefix rules from `pattern-spec.md`, as well as unique names/slugs,
canonical IDs and anchors, table parity and order, and matching content sections. Historical prose
and compatibility anchors are intentionally outside the active-name surface.

```bash
python3 scripts/validate-pattern-names.py
```

The deterministic pattern-validation workflow runs this check on pull requests, pushes to `main`,
its weekly schedule, and manual `workflow_dispatch` runs. It never invokes a model or uses a
provider API key.

### Patterns Website Data

#### `generate-patterns-data.py`
**Purpose**: Generates the dataset that powers the interactive patterns website (the GitHub Pages `index.html`). README.md is the single source of record — this script parses it at build time so the site never drifts from the docs.

**Usage**:
```bash
python3 scripts/generate-patterns-data.py          # write artifacts
python3 scripts/generate-patterns-data.py --check   # verify in sync (CI/tests)
```

**What it does**:
- Parses the **Complete Pattern Reference** table (card metadata: name, maturity, type, brief description, dependencies)
- Extracts each pattern's full section (rendered as rich detail in the page's modal)
- Generates a branded, in-page-clickable dependency diagram from the parsed data (`siteDiagram`)
- Writes `assets/js/patterns-data.js` (`window.PATTERNS_DATA`)
- Refreshes the generated diagram in `index.html` between the `<!-- PATTERNS:DIAGRAM:START/END -->` markers

The standalone site is brand-matched to Redacted Ventures: it loads the vendored `assets/css/global.css` (brand tokens, fonts, editorial primitives, header/footer/marquee styles) plus the catalog-specific `assets/css/patterns.css`. The RV logo (`assets/logos/`) and favicon (`assets/icons/`) are vendored too. Keep `assets/css/global.css` in sync with the source in the `redactedventurescom` repo.

#### `build.sh`
**Purpose**: The canonical build entrypoint — rebuilds every generated artifact from README.md in one command (refreshes pattern-count badges, regenerates `patterns-data.js`, and re-injects the dependency diagram).

```bash
bash scripts/build.sh
```

Set this as the build command on any static host (Vercel/Netlify) and it will rebuild on every deploy.

#### `pre-commit-patterns.sh`
**Purpose**: Pre-commit hook that runs `build.sh` and re-stages the generated artifacts whenever README.md (or a site source) is part of a commit — so a stale site can never be committed.

```bash
cp scripts/pre-commit-patterns.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

### How the site stays in sync with README.md

README.md is the **single source of record**. Three layers guarantee the published site always reflects it:

1. **Deploy rebuild (server)** — `.github/workflows/deploy-pages.yml` runs `scripts/build.sh` before each GitHub Pages publish. Pushes that change a site input trigger it; metadata-only pushes do not.
2. **Drift gate (CI)** — `.github/workflows/pattern-validation.yml` runs `generate-patterns-data.py --check` in its single deterministic suite and **fails** if the committed artifacts are out of sync, so drift is caught before merge.
3. **Pre-commit rebuild (local, optional)** — `pre-commit-patterns.sh` regenerates and stages artifacts at commit time.

`tests/test_patterns_data.py::TestRefreshMechanism` guards this wiring so it cannot be silently removed.

**Stdlib only** — no third-party dependencies.

**Integration**:
- `deploy-pages.yml` runs it (write mode) before publishing, so the deployed site always reflects README.md
- `pattern-validation.yml` runs it with `--check` to fail PRs that change README without regenerating
- `tests/test_patterns_data.py` validates the dataset is well-formed and in sync

### Pattern Count Management

#### `update-pattern-count.py`
**Purpose**: Automatically updates the pattern count badges in README.md and index.html based on the current number of stable patterns in `patterns.yaml`.

**Usage**:
```bash
python3 scripts/update-pattern-count.py
```

**Features**:
- Counts stable patterns from `patterns.yaml`, the catalog source of truth
- Updates the shields.io badge in README.md and index.html with the exact count
- Outputs pattern count for GitHub Actions integration
- Validates that the badge pattern exists before updating

**Integration**:
- Runs automatically in GitHub Actions `readme-accuracy` job
- Can be used as a pre-commit hook (see below)

#### `pre-commit-pattern-count.sh`
**Purpose**: Pre-commit hook that automatically updates the pattern count badge before commits.

**Installation**:
```bash
# Install as a pre-commit hook
cp scripts/pre-commit-pattern-count.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Or for warning-only mode (doesn't block commits)
export PATTERN_COUNT_WARN_ONLY=1
cp scripts/pre-commit-pattern-count.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Behavior**:
- **Default mode**: Blocks commit if pattern count is out of date, automatically stages the fix
- **Warning mode**: Updates badge and continues with commit, just shows a warning

## GitHub Actions Integration

The pattern count automation is integrated into the GitHub Actions workflow:

### Pattern Count Validation
- **Job**: `deterministic-validation`
- **When**: On relevant pushes, every pull request, weekly, and on demand
- **Action**:
  1. Runs `update-pattern-count.py` to update the badge
  2. Checks if any changes were made to README.md or index.html
  3. Fails the job if the badge was out of date (to remind developers to commit the update)

### Benefits
- **Always accurate**: Badge shows the exact current pattern count
- **Automated maintenance**: No manual updates required when patterns are added/removed
- **CI validation**: Ensures the badge stays in sync with actual pattern count
- **Developer-friendly**: Clear error messages and automatic staging

## Usage Patterns

### For Developers
When adding or removing patterns:

1. **Automatic (recommended)**: Install the pre-commit hook for automatic updates
2. **Manual**: Run `python3 scripts/update-pattern-count.py` before committing
3. **CI-only**: Let GitHub Actions catch and report badge mismatches

### For CI/CD
The GitHub Actions integration ensures:
- Pattern count badge accuracy is validated on every change
- Clear error messages when badges need updates
- Automated badge updates in the validation process

### Example Output
```bash
🔍 Counting patterns from conftest.py...
✓ Found 29 patterns
📝 Updating pattern count badges...
✅ Successfully updated pattern count badges to 29
```

## Troubleshooting

### Badge Not Found
If the script reports "No badge pattern found to update":
- Verify the badge exists in README.md with format: `[![Patterns](https://img.shields.io/badge/patterns-XX-blue.svg)]`
- Check that the badge URL follows the expected shields.io pattern

### Pattern Count Mismatch
If the count seems wrong:
- Check the `patterns` list in `patterns.yaml`
- Verify that registry names match the stable reference table and sections in README.md
- Run the test suite to check for pattern compliance issues

### Pre-commit Hook Issues
If the pre-commit hook fails:
- Ensure Python is available in your PATH
- Check that `scripts/update-pattern-count.py` is executable
- Verify the script can find `tests/conftest.py` and `README.md`

This automation ensures the pattern count badge always reflects the current state of the repository without manual maintenance overhead.
