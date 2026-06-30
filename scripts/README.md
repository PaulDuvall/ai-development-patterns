# Scripts Directory

This directory contains automation scripts for maintaining the AI Development Patterns repository.

## Available Scripts

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

1. **Deploy rebuild (server)** — `.github/workflows/deploy-pages.yml` runs `scripts/build.sh` before every GitHub Pages publish (triggered on every push to `main`), so the live site is regenerated from README on each change — even if a committed artifact was stale.
2. **Drift gate (CI)** — `.github/workflows/pattern-validation.yml` runs `generate-patterns-data.py --check` on pushes and PRs and **fails** if the committed artifacts are out of sync, so drift is caught before merge.
3. **Pre-commit rebuild (local, optional)** — `pre-commit-patterns.sh` regenerates and stages artifacts at commit time.

`tests/test_patterns_data.py::TestRefreshMechanism` guards this wiring so it cannot be silently removed.

**Stdlib only** — no third-party dependencies.

**Integration**:
- `deploy-pages.yml` runs it (write mode) before publishing, so the deployed site always reflects README.md
- `pattern-validation.yml` runs it with `--check` to fail PRs that change README without regenerating
- `tests/test_patterns_data.py` validates the dataset is well-formed and in sync

### Pattern Count Management

#### `update-pattern-count.py`
**Purpose**: Automatically updates the pattern count badges in README.md and index.html based on the current number of patterns in `tests/conftest.py`.

**Usage**:
```bash
python3 scripts/update-pattern-count.py
```

**Features**:
- Counts patterns from the `EXPECTED_PATTERNS` list in conftest.py
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
- **Job**: `readme-accuracy`
- **When**: On every push and pull request
- **Action**:
  1. Runs `update-pattern-count.py` to update the badge
  2. Checks if any changes were made to README.md
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
✓ Found 22 patterns
📝 Updating pattern count badges...
✅ Successfully updated pattern count badges to 22
```

## Troubleshooting

### Badge Not Found
If the script reports "No badge pattern found to update":
- Verify the badge exists in README.md with format: `[![Patterns](https://img.shields.io/badge/patterns-XX-blue.svg)]`
- Check that the badge URL follows the expected shields.io pattern

### Pattern Count Mismatch
If the count seems wrong:
- Check `tests/conftest.py` for the `EXPECTED_PATTERNS` list
- Verify that pattern names in the list match the actual patterns in README.md
- Run the test suite to check for pattern compliance issues

### Pre-commit Hook Issues
If the pre-commit hook fails:
- Ensure Python is available in your PATH
- Check that `scripts/update-pattern-count.py` is executable
- Verify the script can find `tests/conftest.py` and `README.md`

This automation ensures the pattern count badge always reflects the current state of the repository without manual maintenance overhead.
