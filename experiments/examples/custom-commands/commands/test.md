---
description: Smart test runner with filtering, coverage, and health monitoring
argument-hint: Test target and optional flags (backend, frontend, --coverage, --watch)
---

# Test Suite Runner

You are helping a developer run tests with smart filtering, comprehensive reporting, and test suite health monitoring. Parse arguments to determine test scope, execute appropriate test commands, analyze results, and provide actionable recommendations.

## Usage

```bash
/test                          # Run all tests
/test backend                  # Run backend tests only
/test frontend --watch         # Run frontend tests in watch mode
/test integration --verbose    # Run integration tests with verbose output
/test --coverage               # Run with coverage report
```

## Implementation

### 1. Parse Arguments

Extract test target and flags from arguments:

**Test Targets** (first positional argument):
- `backend` - Run backend/server tests
- `frontend` - Run frontend/client tests
- `integration` - Run integration tests only
- `unit` - Run unit tests only
- `e2e` - Run end-to-end tests
- `[specific-file]` - Run specific test file
- No argument - Run all tests

**Flags** (optional parameters):
- `--watch` - Watch mode (re-run on file changes)
- `--coverage` - Generate coverage report
- `--verbose` - Detailed output with logs
- `--bail` - Stop on first failure
- `--update-snapshots` - Update test snapshots

### 2. Determine Test Command

Map arguments to appropriate test commands:

```bash
# Examples
backend           → pytest tests/backend/ -v
frontend          → npm test -- --testPathPattern=frontend
integration       → pytest tests/integration/ -v
backend --coverage → pytest tests/backend/ --cov=src/backend --cov-report=html
frontend --watch  → npm test -- --watch --testPathPattern=frontend
```

### 3. Execute Tests

Run the determined test command:

```bash
# Set up test environment
export NODE_ENV=test
export TESTING=true

# Run tests with appropriate flags
[test_command]
```

### 4. Parse Test Results

Extract key metrics from test output:
- Total tests run
- Tests passed/failed/skipped
- Test duration
- Coverage percentage (if --coverage flag used)
- Failed test details (if any)

### 5. Generate Test Report

Create structured test report:

```markdown
## Test Report

**Target**: [backend/frontend/integration/all]
**Date**: 2025-01-10 14:45:12
**Duration**: 8.2 seconds

### Results
- ✅ Passed: 245
- ❌ Failed: 2
- ⏭️ Skipped: 5
- **Total**: 252 tests

### Coverage (if applicable)
- Statements: 85%
- Branches: 78%
- Functions: 90%
- Lines: 84%

### Failed Tests
1. **test_user_authentication_with_expired_token**
   - Location: tests/backend/test_auth.py:42
   - Error: AssertionError: Expected 401, got 200
   - Duration: 0.05s

2. **test_checkout_with_invalid_payment**
   - Location: tests/backend/test_checkout.py:78
   - Error: Timeout after 5000ms
   - Duration: 5.2s

### Recommendations
- Fix failed authentication test (expired token not being rejected)
- Investigate checkout test timeout (possible mock issue)
- Consider increasing coverage for src/payment.js (currently 65%)
```

### 6. Smart Test Selection

If no arguments provided, intelligently determine what to test:

**Check Recent Changes**:
```bash
# Find recently modified files
git diff --name-only HEAD~1 HEAD
```

**Run Affected Tests**:
- If backend files changed → Run backend tests
- If frontend files changed → Run frontend tests
- If both changed → Run integration tests
- If config/infrastructure changed → Run all tests

### 7. Test Health Monitoring

Track test suite health over time:

```markdown
### Test Suite Health
- Test suite duration trend: ⬆️ +12% (last 7 days)
  - Suggestion: Investigate slow tests, consider parallelization
- Flaky tests detected: 3
  - test_api_timeout (flaky rate: 15%)
  - test_websocket_connection (flaky rate: 8%)
  - test_cache_expiration (flaky rate: 5%)
- Coverage trend: 📈 85% → 87% (+2%)
```

## Advanced Features

### Parallel Execution

For large test suites, run tests in parallel:
```bash
# Pytest parallel
pytest -n auto tests/

# Jest parallel (default)
npm test -- --maxWorkers=4
```

### Test Prioritization

Run critical tests first:
1. Recently failed tests
2. Tests covering recently changed code
3. High-value integration tests
4. Remaining unit tests

### Watch Mode Intelligence

In watch mode, only re-run tests related to changed files:
```bash
# Watch backend changes
npm test -- --watch --testPathPattern=backend

# Automatically run related tests when files change
```

## Common Test Patterns by Technology

**Node.js / Jest**:
```bash
npm test -- --testPathPattern=$ARGUMENTS
npm test -- --watch
npm test -- --coverage --coverageThreshold='{"global":{"branches":80,"functions":80,"lines":80}}'
```

**Python / Pytest**:
```bash
pytest tests/$ARGUMENTS -v
pytest tests/$ARGUMENTS --cov=src --cov-report=html
pytest tests/$ARGUMENTS -x  # Stop on first failure
```

**Go**:
```bash
go test ./... -v
go test ./... -cover
go test -run $ARGUMENTS
```

**Ruby / RSpec**:
```bash
rspec spec/$ARGUMENTS
rspec spec/$ARGUMENTS --format documentation
```

## Argument Handling

Parse $ARGUMENTS to extract test target and flags:

- First positional argument: Test target (backend, frontend, integration, etc.)
- Remaining arguments: Flags (--watch, --coverage, --verbose, --bail)
- If no arguments: Use smart test selection based on recent git changes

## Core Principles

- Always provide test summary with pass/fail counts
- Show failed test details with file locations
- Suggest fixes for common test failures
- Track test suite health metrics
- Recommend coverage improvements for low-coverage files
- Detect and report flaky tests
- Provide clear next steps based on results
- Use smart test selection when no target specified
