# Test Command Example

Parameterized test runner with smart filtering and comprehensive reporting.

## Command Definition

```markdown
---
description: Smart test runner with filtering, coverage, and health monitoring
argument-hint: Test target and optional flags (backend, frontend, --coverage, --watch)
---

# Test Suite Runner

You are helping a developer run tests with smart filtering, comprehensive reporting, and test suite health monitoring.

## Usage
/test backend        # Run backend tests
/test frontend --watch  # Watch mode

## Implementation
Run tests: $ARGUMENTS
If no arguments: run full test suite
Parse flags: --watch, --coverage, --verbose
```

## Use Case

Perfect for:
- Targeted test execution
- Coverage tracking
- Test suite health monitoring
- CI/CD integration

## Example Usage

```bash
# Run all tests
/test

# Target specific areas
/test backend
/test frontend --watch
/test integration --coverage

# With specific flags
/test --verbose --bail
```

## Test Report Example

```markdown
## Test Report

**Target**: backend
**Duration**: 8.2 seconds

### Results
- ✅ Passed: 245
- ❌ Failed: 2
- ⏭️ Skipped: 5
- **Total**: 252 tests

### Coverage
- Statements: 85%
- Branches: 78%
- Functions: 90%
- Lines: 84%

### Failed Tests
1. **test_user_authentication_with_expired_token**
   - Location: tests/backend/test_auth.py:42
   - Error: AssertionError: Expected 401, got 200

### Recommendations
- Fix expired token validation in src/auth.py
- Increase coverage for src/payment.js (currently 65%)
```

## Smart Test Selection

When no arguments provided, intelligently determine what to test:

```bash
# Check recent changes
git diff --name-only HEAD~1 HEAD

# Run affected tests
# - Backend files changed → Run backend tests
# - Frontend files changed → Run frontend tests
# - Both changed → Run integration tests
```

## Test Health Monitoring

```markdown
### Flake Management
- Duration trend: ⬆️ +12% (last 7 days)
  - Suggestion: Investigate slow tests
- Flaky tests detected: 3
  - test_api_timeout (flaky rate: 15%)
- Coverage trend: 📈 85% → 87% (+2%)
```

## Related Patterns

- [Testing Orchestration](../../experiments/README.md#testing-orchestration)
- [Flake Management](../../experiments/README.md#flake-management)
