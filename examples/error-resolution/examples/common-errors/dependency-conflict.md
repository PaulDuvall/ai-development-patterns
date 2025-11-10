# Dependency Conflict Error Example

Example of using the Error Resolution pattern with npm dependency version conflicts.

## Step 1: Error Output

```
ERROR: Cannot install package-a 3.5.0 and package-b 1.2.0
  package-a (3.5.0) requires library-x>=2.0.0
  package-b (1.2.0) requires library-x<2.0.0,>=1.5.0

Installation failed: dependency resolution impossible
```

## Step 2: Collect Context

```bash
cat > .error-context.md << 'EOF'
## Error
- package-a@3.5.0 requires library-x>=2.0.0
- package-b@1.2.0 requires library-x<2.0.0
- Currently installed: library-x@1.8.0

## Recent Changes
$(git log --oneline -3)

## Package Manifest (package.json)
```json
{
  "dependencies": {
    "package-a": "^3.5.0",
    "package-b": "^1.2.0"
  }
}
```
EOF
```

## Step 3: AI Diagnosis

```bash
ai "Fix this dependency conflict:

$(cat .error-context.md)

Provide:
1. Root cause
2. Resolution strategy (update or downgrade)
3. Fix commands
4. Prevention (one method)"
```

## Step 4: Apply Fix

```bash
# Root cause: Incompatible version requirements for library-x

# Option 1: Update package-b (if newer version exists)
npm info package-b versions
npm install package-b@^2.0.0
npm install

# Option 2: Downgrade package-a (if feature allows)
npm info package-a versions
npm install package-a@3.4.0
npm install

# Verify resolution
npm list library-x  # Should show single version
npm test

# Commit
git add package.json package-lock.json
git commit -m "fix: resolve library-x dependency conflict"
git push
```

## Prevention

Add dependency check to CI:

```yaml
# .github/workflows/dependencies.yml
name: Check Dependencies
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - name: Validate dependencies
        run: |
          npm install --dry-run
          npm list || exit 1
```

## Other Package Managers

**Python (pip)**:
```bash
# Error
ERROR: package-a 2.0.0 requires library-x>=3.0
ERROR: package-b 1.5.0 requires library-x<3.0

# Fix
pip install package-b==2.0.0  # Upgrade to compatible version
pip-compile requirements.in  # Lock dependencies
```

**Go (modules)**:
```bash
# Error
go: conflicting requirements for library-x

# Fix
go get package-a@v1.9.0  # Downgrade to compatible version
go mod tidy
```
