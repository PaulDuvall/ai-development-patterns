# Scripts Directory

This directory contains automation scripts for maintaining the AI Development Patterns repository.

## Available Scripts

### Pattern Count Management

#### `update-pattern-count.py`
**Purpose**: Automatically updates the pattern count badge in README.md based on the current number of patterns in `tests/conftest.py`.

**Usage**:
```bash
python scripts/update-pattern-count.py
```

**Features**:
- Counts patterns from the `EXPECTED_PATTERNS` list in conftest.py
- Updates the shields.io badge in README.md with the exact count
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
2. **Manual**: Run `python scripts/update-pattern-count.py` before committing
3. **CI-only**: Let GitHub Actions catch and report badge mismatches

### For CI/CD
The GitHub Actions integration ensures:
- Pattern count badge accuracy is validated on every change
- Clear error messages when badges need updates
- Automated badge updates in the validation process

### Example Output
```bash
🔍 Counting patterns from conftest.py...
✓ Found 21 patterns
📝 Updating README.md badge...
✅ Successfully updated pattern count badge to 21
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