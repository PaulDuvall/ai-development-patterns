# Error Context Template

Use this template to collect comprehensive error context for AI diagnosis.

## Error Output

```
[Paste complete error message here]
[Include stack traces, error codes, and any diagnostic output]
```

**Exit Code**: [e.g., 1, 3, 127]

**Failed Command**:
```bash
[The exact command that failed]
```

## Recent Changes

```bash
# Last 5 commits
git log --oneline -5
```

**Output**:
```
[Paste git log output here]
```

## Affected Files

```bash
# Files changed in last commit
git diff --name-only HEAD~1
```

**Files**:
- file1.ext
- file2.ext
- file3.ext

## File Contents

### [filename1]
```[language]
[Paste relevant file content]
```

### [filename2]
```[language]
[Paste relevant file content]
```

## Environment Information

- **OS**: [e.g., Linux, macOS, Windows]
- **Shell**: [e.g., bash, zsh]
- **Tool Versions**:
  - [Tool 1]: [version]
  - [Tool 2]: [version]
- **Working Directory**: [path]

## Additional Context

### Configuration Files
```[yaml/json/toml]
[Relevant configuration if applicable]
```

### Environment Variables
```bash
# Only include non-sensitive variables
[Relevant env vars]
```

### System State
- **Available disk space**: [if relevant]
- **Memory usage**: [if relevant]
- **Running processes**: [if relevant]

## What I've Tried

1. [Attempted fix 1] - Result: [what happened]
2. [Attempted fix 2] - Result: [what happened]

## Expected Behavior

[Describe what should have happened instead of the error]

## Questions for AI

1. What is the root cause of this error?
2. What specific commands will fix it?
3. How can I prevent this error in the future?
