# Error Resolution Pattern - Examples

This directory contains working examples and templates for the Error Resolution pattern.

## Directory Structure

```
examples/error-resolution/
├── templates/                      # Reusable templates
│   ├── error-context-template.md  # Generic error context collection
│   └── ai-prompt-template.md      # Structured AI prompts for diagnosis
├── examples/
│   ├── common-errors/             # Example error scenarios
│   │   ├── test-failure.md        # Pytest failure example
│   │   ├── dependency-conflict.md # Version/dependency issues
│   │   └── configuration-error.md # Environment config issues
│   └── github-actions/            # CI/CD integration
│       ├── ci-failure-example.md  # GitHub Actions workflow failure
│       ├── collect-from-workflow.sh # Script to extract error context from CI
│       └── README.md              # Integration guide
```

## Quick Start

### Using Templates

```bash
# 1. Copy error context template
cp templates/error-context-template.md .error-context.md

# 2. Fill in your error details
vim .error-context.md

# 3. Use AI prompt template
cat templates/ai-prompt-template.md | sed "s/ERROR_CONTEXT/$(cat .error-context.md)/" | ai
```

### GitHub Actions Integration

```bash
# Fetch error context from failed workflow run
./examples/github-actions/collect-from-workflow.sh <run-id>

# AI diagnosis with collected context
ai "$(cat .error-context.md)"
```

## Example Scenarios

### 1. Test Failures
See `examples/common-errors/test-failure.md` for:
- Pytest failure diagnosis
- Context collection from test output
- AI-powered root cause analysis

### 2. Dependency Conflicts
See `examples/common-errors/dependency-conflict.md` for:
- Version mismatch resolution
- Package compatibility analysis
- Automated fix generation

### 3. Configuration Errors
See `examples/common-errors/configuration-error.md` for:
- Environment configuration issues
- Missing variable detection
- Configuration validation

### 4. CI/CD Failures
See `examples/github-actions/` for:
- GitHub Actions workflow errors
- Automated context extraction
- Integration with CI systems

## Pattern Documentation

For complete pattern documentation, see the [Error Resolution](../../README.md#error-resolution) pattern in the main README.
