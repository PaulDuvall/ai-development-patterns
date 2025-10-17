# Dependency Conflict Error Example

This example demonstrates how to use the Error Resolution pattern for dependency version conflicts.

## Error Scenario

```
ERROR: Cannot install package-a and package-b because they have conflicting dependencies
  package-a requires library-x>=2.0.0
  package-b requires library-x<2.0.0
```

## Error Context Collection

```bash
# Collect error context
cat > .error-context.md << 'EOF'
# Dependency Conflict Analysis

## Error Output
```
ERROR: Cannot install package-a 3.5.0 and package-b 1.2.0
  package-a (3.5.0) requires library-x>=2.0.0
  package-b (1.2.0) requires library-x<2.0.0,>=1.5.0

Installation failed: dependency resolution impossible
```

## Package Manifest
```json
{
  "dependencies": {
    "package-a": "^3.5.0",
    "package-b": "^1.2.0"
  }
}
```

## Lock File (relevant section)
```
library-x@1.8.0  # Currently installed
package-a@3.5.0  # Wants library-x@2.1.0
package-b@1.2.0  # Wants library-x@1.8.0
```

## Recent Changes
```
git log --oneline -3
abc123 Added package-a for new feature
def456 Updated dependencies
ghi789 Initial project setup
```

## Environment
- Package Manager: npm 9.8.0
- Node.js: v18.17.0
- OS: Ubuntu 22.04

EOF
```

## AI Diagnosis

```bash
ai "Diagnose this dependency conflict:

$(cat .error-context.md)

Provide:
1. Root cause of the conflict
2. Resolution strategy
3. Commands to resolve
4. How to prevent future conflicts"
```

## Expected AI Response

### Root Cause
Two packages require incompatible versions of the same dependency:
- `package-a@3.5.0` requires `library-x@>=2.0.0`
- `package-b@1.2.0` requires `library-x@<2.0.0`

This is a hard dependency conflict that cannot be resolved without updating one of the packages.

### Resolution Strategy

**Option 1: Update package-b** (Recommended)
```bash
# Check if newer version of package-b supports library-x@2.x
npm info package-b versions
npm info package-b@latest peerDependencies

# If package-b@2.x supports library-x@2.x:
npm install package-b@^2.0.0
npm install  # Retry installation
```

**Option 2: Downgrade package-a**
```bash
# Find version of package-a compatible with library-x@1.x
npm info package-a versions
npm info package-a@3.4.0 peerDependencies

# If package-a@3.4.0 works with library-x@1.x:
npm install package-a@3.4.0
npm install  # Retry installation
```

**Option 3: Use package aliases** (if both versions needed)
```bash
# Install package-a with alias
npm install package-a-v3@npm:package-a@^3.5.0
npm install package-b@^1.2.0

# Update imports in code
# Before: import { func } from 'package-a'
# After:  import { func } from 'package-a-v3'
```

### Validation

```bash
# After resolving, verify:
npm install --dry-run
npm list library-x  # Should show single version
npm audit
npm test
```

### Prevention Strategy

**1. Add dependency conflict check**
```bash
# In package.json scripts:
"scripts": {
  "preinstall": "npm-check-updates --dep dev,prod"
}
```

**2. Use resolutions field** (npm/yarn)
```json
{
  "resolutions": {
    "library-x": "^2.0.0"
  }
}
```

**3. Regular dependency updates**
```bash
# Weekly dependency review
npx npm-check-updates -i
npm test
```

**4. Add to CI pipeline**
```yaml
# .github/workflows/dependencies.yml
- name: Check for conflicts
  run: |
    npm install --dry-run
    npm list || exit 1
```

## Common Dependency Conflict Patterns

### Python (pip)

```bash
# Error
ERROR: package-a 2.0.0 has requirement library-x>=3.0
ERROR: package-b 1.5.0 has requirement library-x<3.0

# Resolution
pip install package-a==1.9.0  # Downgrade
# OR
pip install package-b==2.0.0  # Upgrade

# Prevention: Use pip-compile
pip-compile requirements.in
```

### Ruby (bundler)

```bash
# Error
Bundler could not find compatible versions for gem "library-x"

# Resolution
bundle update library-x

# Prevention: Gemfile.lock in git
git add Gemfile.lock
```

### Go (modules)

```bash
# Error
go: package-a@v2.0.0 requires library-x@v3.0.0
go: package-b@v1.0.0 requires library-x@v2.5.0

# Resolution
go get package-a@v1.9.0
go mod tidy

# Prevention
go mod verify
```

## Troubleshooting Tips

1. **Check upstream issue trackers**: Often conflicts are known issues
2. **Use dependency graphs**: Visualize the conflict
   ```bash
   npm ls library-x
   ```
3. **Test compatibility**: Try versions in isolation
4. **Contact maintainers**: Report incompatibility
5. **Consider alternatives**: Find packages without conflicts

## Key Takeaways

- **Always check compatibility** before adding new dependencies
- **Keep dependencies updated** regularly to avoid conflicts
- **Use lock files** and commit them to version control
- **Run tests** after resolving to ensure functionality
- **Document resolution** for future reference
