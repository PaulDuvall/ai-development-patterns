# Real CI Failure Example: Terraform and Shellcheck Errors

This is a real error from GitHub Actions workflow run `18578261366` in the `recurring-billing-notifier` repository.

## Error Context

### Workflow Run Information
- **Run ID**: 18578261366
- **Repository**: recurring-billing-notifier
- **Workflow**: Validation checks

### Error Output

```
Run terraform fmt -check -recursive
    terraform fmt -check -recursive
    shell: /usr/bin/bash -e {0}
    env:
      PYTHON_VERSION: 3.11
      TERRAFORM_CLI_PATH: /home/runner/work/_temp/dfb4b73c-5286-4fe6-8e63-d27de45a9f41
  main.tf
  outputs.tf
  Error: Terraform exited with code 3.
  Error: Process completed with exit code 1.
```

```
Run if command -v shellcheck &> /dev/null; then

  In scripts/validate-deployment.sh line 32:
  log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
                  ^----------------------------^ SC2317 (info): Command appears to be unreachable. Check usage (or ignore if invoked indirectly).


  In scripts/verify-mvp-completeness.sh line 15:
      GREEN=''; RED=''; YELLOW=''; NC=''
                        ^----^ SC2034 (warning): YELLOW appears unused. Verify use (or export if used externally).

  For more information:
    https://www.shellcheck.net/wiki/SC2034 -- YELLOW appears unused. Verify use...
    https://www.shellcheck.net/wiki/SC2317 -- Command appears to be unreachable...
  Error: Process completed with exit code 1.
```

```
Run if [ "failure" != "success" ] || \
    if [ "failure" != "success" ] || \
       [ "failure" != "success" ] || \
       [ "success" != "success" ] || \
       [ "failure" != "success" ]; then
      echo "❌ Validation failed"
      exit 1
    fi
    echo "✅ All validation checks passed"
    shell: /usr/bin/bash -e {0}
    env:
      PYTHON_VERSION: 3.11
  ❌ Validation failed
  Error: Process completed with exit code 1.
```

## AI Diagnosis

### Root Cause Analysis

**Issue 1: Terraform Formatting**
- `main.tf` and `outputs.tf` are not formatted according to Terraform standards
- Terraform fmt check exits with code 3 when formatting is needed
- Files need to be reformatted with `terraform fmt`

**Issue 2: Shellcheck SC2317 - Unreachable Function**
- `log_warning()` function defined in `scripts/validate-deployment.sh` line 32 but never called
- Either the function should be used, removed, or marked as intentionally unused

**Issue 3: Shellcheck SC2034 - Unused Variable**
- `YELLOW` variable defined in `scripts/verify-mvp-completeness.sh` line 15 but never used
- Variable should either be used in logging or removed

**Issue 4: Validation Logic**
- The validation check is failing because previous steps (terraform, shellcheck) failed
- The conditional logic checks if any step status is not "success"

### Immediate Fixes

```bash
# Fix 1: Format Terraform files
terraform fmt main.tf outputs.tf

# Verify formatting
terraform fmt -check -recursive
# Should show no output if successful

# Fix 2: Remove unused log_warning function (Option A)
# In scripts/validate-deployment.sh, remove or comment out:
# log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }

# OR Fix 2: Use the function somewhere (Option B)
# Add a call to log_warning in the script where appropriate

# OR Fix 2: Mark as intentionally unused (Option C)
# Add above the function:
# # shellcheck disable=SC2317

# Fix 3: Remove unused YELLOW variable
# In scripts/verify-mvp-completeness.sh line 15, remove YELLOW:
# Before: GREEN=''; RED=''; YELLOW=''; NC=''
# After:  GREEN=''; RED=''; NC=''

# OR Fix 3: Use the YELLOW variable
# Add logging that uses YELLOW:
# log_info() { echo -e "${YELLOW}[INFO]${NC} $1"; }
```

### Validation Steps

```bash
# After applying fixes, validate locally:

# 1. Check Terraform formatting
terraform fmt -check -recursive
# Expected: No output (all files properly formatted)

# 2. Check shell scripts
shellcheck scripts/*.sh
# Expected: No SC2317 or SC2034 warnings

# 3. Run full validation workflow locally (if possible)
# Or commit and push to trigger CI
```

### Prevention Strategy

**1. Add Pre-commit Hook**

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.83.5
    hooks:
      - id: terraform_fmt
        name: Terraform format

  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.9.0.5
    hooks:
      - id: shellcheck
        name: Shellcheck
```

Install and enable:
```bash
pip install pre-commit
pre-commit install
```

**2. Add Local Validation Script**

Create `scripts/run-ci-checks-locally.sh`:

```bash
#!/bin/bash
# Run same checks as CI pipeline

echo "🔍 Running Terraform format check..."
terraform fmt -check -recursive || {
    echo "❌ Terraform files need formatting"
    echo "Run: terraform fmt -recursive"
    exit 1
}

echo "🔍 Running Shellcheck..."
shellcheck scripts/*.sh || {
    echo "❌ Shellcheck found issues"
    exit 1
}

echo "✅ All checks passed - safe to push"
```

Make executable:
```bash
chmod +x scripts/run-ci-checks-locally.sh
```

Run before pushing:
```bash
./scripts/run-ci-checks-locally.sh
```

**3. Update Documentation**

Add to README.md or CONTRIBUTING.md:

```markdown
## Before Committing

Run local validation:
```bash
# Format Terraform files
terraform fmt -recursive

# Check shell scripts
shellcheck scripts/*.sh

# Or run all checks
./scripts/run-ci-checks-locally.sh
```

## Risk Assessment

- **Risk Level**: Low
- **Potential Issues**:
  - Terraform fmt may change file formatting unexpectedly (review diff before committing)
  - Removing shellcheck warnings might hide legitimate issues (review each case)
- **Rollback**: If issues arise, `git revert` the commit

## Summary

This CI failure was caused by:
1. Unformatted Terraform files (easily fixed with `terraform fmt`)
2. Unused code detected by shellcheck (cleanup or disable warnings)

Both are code quality issues rather than functional bugs. The fixes are straightforward and low-risk.

**Estimated time to fix**: 5-10 minutes
**Impact**: None - purely formatting and cleanup

## Commands to Apply

```bash
# Apply all fixes
cd /path/to/recurring-billing-notifier

# Fix Terraform formatting
terraform fmt -recursive

# Fix shellcheck issues (example - adjust based on your choice)
# Option: Remove unused code
sed -i '/log_warning()/d' scripts/validate-deployment.sh
sed -i "s/GREEN=''; RED=''; YELLOW=''; NC=''/GREEN=''; RED=''; NC=''/" scripts/verify-mvp-completeness.sh

# Verify fixes
terraform fmt -check -recursive
shellcheck scripts/*.sh

# Commit
git add -A
git commit -m "fix: resolve terraform formatting and shellcheck warnings

- Format main.tf and outputs.tf with terraform fmt
- Remove unused log_warning function in validate-deployment.sh
- Remove unused YELLOW variable in verify-mvp-completeness.sh

Resolves CI failure in run 18578261366"

git push
```
