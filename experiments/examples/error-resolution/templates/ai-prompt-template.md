# AI Prompt Template for Error Diagnosis

Use this structured prompt template to get the best results from AI error diagnosis.

## Basic Prompt Structure

```
Analyze this error and provide actionable fixes:

ERROR CONTEXT:
[Insert error context here - use error-context-template.md]

REQUIRED OUTPUT:
1. Root cause analysis
2. Specific fix commands (executable bash/shell commands)
3. Prevention strategy (tests, hooks, validation)

Format all fixes as copy-pasteable commands.
```

## Enhanced Prompt with Constraints

```
Diagnose and fix this error with the following constraints:

ERROR CONTEXT:
[Insert error context]

CONSTRAINTS:
- Time to fix: [e.g., < 30 minutes]
- Acceptable changes: [e.g., only configuration files, no code changes]
- Testing requirements: [e.g., must pass existing test suite]
- Deployment impact: [e.g., must be backward compatible]

REQUIRED OUTPUT:
1. Root Cause Analysis
   - What caused the error
   - When it was introduced (based on git history)
   - Why it manifests now

2. Immediate Fix
   - Exact commands to apply
   - Expected output after fix
   - Validation steps

3. Prevention Strategy
   - Pre-commit hooks to add
   - Tests to create
   - Documentation to update
   - Monitoring/alerts to configure

4. Risk Assessment
   - What could go wrong with this fix
   - Rollback procedure if fix fails

Provide all commands as executable bash scripts.
```

## Prompt for Specific Error Types

### Configuration Errors

```
This is a configuration error. Analyze and fix:

ERROR: [error message]
CONFIG FILE: [filename]
RECENT CHANGES: [git log]

Provide:
1. Which configuration setting is wrong
2. Correct value and why
3. How to validate configuration before deployment
```

### Dependency Conflicts

```
This is a dependency conflict. Resolve:

ERROR: [error message]
DEPENDENCY MANIFEST: [package.json/requirements.txt/Gemfile content]
LOCK FILE: [lockfile content if relevant]

Provide:
1. Conflicting dependencies and versions
2. Resolution strategy (which version to use)
3. Update commands
4. How to prevent future conflicts
```

### Test Failures

```
Tests are failing. Diagnose:

ERROR: [test failure output]
TEST FILE: [failing test content]
CODE UNDER TEST: [relevant source code]
RECENT CHANGES: [git diff]

Provide:
1. Why test is failing (code bug vs test bug)
2. Fix for the failure
3. Additional tests to add
4. How to run tests locally before pushing
```

### Build/CI Failures

```
CI/CD pipeline failed. Fix:

ERROR: [build failure output]
WORKFLOW CONFIG: [.github/workflows/*.yml or similar]
BUILD LOGS: [relevant portions]
RECENT COMMITS: [git log -3]

Provide:
1. Which step failed and why
2. Fix for the failing step
3. Local reproduction steps
4. How to test workflow changes before pushing
```

## Expected AI Response Format

The AI should respond with this structure:

```markdown
## Root Cause Analysis

[2-3 sentences explaining what caused the error]

## Immediate Fix

```bash
# Step 1: [Description]
command1

# Step 2: [Description]
command2

# Step 3: Verify fix
command3
```

## Validation

After applying fix, verify:
```bash
# Run these commands to confirm fix worked
validation-command1
validation-command2
```

Expected output:
```
[What you should see if fix worked]
```

## Prevention Strategy

### Pre-commit Hook
```bash
# Add to .git/hooks/pre-commit
prevention-command1
```

### Tests to Add
```[language]
# Add to tests/
test-code-here
```

### Documentation Update
[What to document to prevent recurrence]

## Risk Assessment

- **Risk Level**: Low/Medium/High
- **Potential Issues**: [What could go wrong]
- **Rollback**:
  ```bash
  rollback-command
  ```
```

## Tips for Better AI Responses

1. **Be Specific**: Include exact error messages, not paraphrased versions
2. **Show Recent Changes**: Always include `git log` and `git diff` output
3. **Include File Contents**: Paste actual file content, not summaries
4. **State Constraints**: Tell AI what changes are/aren't acceptable
5. **Request Executable Commands**: Ask for copy-pasteable commands, not descriptions
6. **Ask for Validation**: Request verification steps to confirm fix works
7. **Request Prevention**: Always ask how to prevent error recurrence

## Example Usage

```bash
# 1. Fill out error context
cp templates/error-context-template.md my-error.md
vim my-error.md

# 2. Use prompt template
ai "$(cat templates/ai-prompt-template.md | sed 's/\[Insert error context\]/'"$(cat my-error.md)"'/')"

# 3. Save AI response
ai "..." > ai-diagnosis.md

# 4. Extract and apply fixes
grep -A 20 "## Immediate Fix" ai-diagnosis.md > fix.sh
bash fix.sh
```
