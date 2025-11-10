# CI Failure Example: Terraform and Shellcheck Errors

Example of using the Error Resolution pattern with a GitHub Actions validation failure.

## Step 1: Error Output

```
Run terraform fmt -check -recursive
  main.tf
  outputs.tf
  Error: Terraform exited with code 3.
  Error: Process completed with exit code 1.

Run shellcheck scripts/*.sh
  In scripts/validate-deployment.sh line 32:
  log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
  SC2317: Command appears to be unreachable.

  In scripts/verify-mvp-completeness.sh line 15:
  YELLOW='';
  SC2034: YELLOW appears unused.

  Error: Process completed with exit code 1.

❌ Validation failed
```

## Step 2: Collect Context

```bash
cat > .error-context.md << 'EOF'
## Error
- Terraform fmt check failed: main.tf, outputs.tf
- Shellcheck warnings: SC2317, SC2034
- Validation: FAILED

## Recent Changes
$(git log --oneline -3)

## Files
- terraform/main.tf
- terraform/outputs.tf
- scripts/validate-deployment.sh
- scripts/verify-mvp-completeness.sh
EOF
```

## Step 3: AI Diagnosis

```bash
ai "Fix this CI failure:

$(cat .error-context.md)

Provide:
1. Root cause
2. Fix commands
3. Prevention (one method)"
```

## Step 4: Apply Fix

```bash
# Root cause: Unformatted terraform, unused shell code

# Fix terraform formatting
terraform fmt terraform/main.tf terraform/outputs.tf

# Fix shellcheck (remove unused code)
sed -i '/log_warning()/d' scripts/validate-deployment.sh
sed -i 's/YELLOW=.*;//' scripts/verify-mvp-completeness.sh

# Verify
terraform fmt -check -recursive
shellcheck scripts/*.sh

# Commit
git add -A
git commit -m "fix: resolve terraform formatting and shellcheck warnings"
git push
```

## Prevention

Add pre-commit hook:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    hooks:
      - id: terraform_fmt
  - repo: https://github.com/shellcheck-py/shellcheck-py
    hooks:
      - id: shellcheck
```

Install: `pip install pre-commit && pre-commit install`
