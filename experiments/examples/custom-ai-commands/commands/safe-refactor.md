# Safe Refactor

Safe refactoring with automated review, testing, and rollback capabilities.

## Usage

```bash
/safe-refactor                    # Interactive refactoring
/safe-refactor --auto             # Automatic refactoring with approval gates
```

## Process

### 1. Pre-Refactoring Analysis

Run built-in review command to analyze current code state:
```bash
/review
```

Capture baseline metrics:
- Current test coverage percentage
- Cyclomatic complexity scores
- Performance benchmarks (if available)
- Code quality metrics

### 2. Create Safety Branch

Create isolated git branch for refactoring:
```bash
git checkout -b refactor-$(date +%Y%m%d-%H%M%S)
```

Branch naming convention:
- `refactor-YYYYMMDD-HHMMSS` for timestamp-based tracking
- Example: `refactor-20250110-143022`

### 3. Perform Refactoring Changes

Execute refactoring based on analysis:
- Apply specific refactoring patterns (Extract Method, Introduce Parameter Object, etc.)
- Maintain existing functionality (behavior-preserving changes only)
- Update related tests if necessary
- Add inline comments explaining complex refactoring decisions

### 4. Run Existing Test Suite

Verify all existing tests still pass:
```bash
# Run full test suite
npm test  # or pytest, go test, etc.
```

Requirements:
- 100% of existing tests must pass
- No test modifications allowed unless absolutely necessary
- If tests fail, explain failure and provide fix options

### 5. Generate New Tests for Refactored Code

Create additional tests for refactored code:
- Test new methods created during refactoring
- Verify edge cases for extracted functions
- Add integration tests if refactoring spans multiple modules
- Ensure code coverage remains at or above baseline

### 6. Compare Performance Before/After

Run performance benchmarks (if applicable):
```bash
# Example for Node.js
npm run benchmark

# Example for Python
python -m pytest tests/benchmarks/ --benchmark-only
```

Acceptable outcomes:
- Performance improvement (ideal)
- No significant performance change (acceptable)
- Performance regression <5% (requires justification)
- Performance regression >5% (requires approval or rollback)

### 7. Generate Refactoring Report

Create comprehensive report:

```markdown
## Refactoring Report

**Branch**: refactor-20250110-143022
**Date**: 2025-01-10 14:30:22
**Status**: READY FOR REVIEW / NEEDS ATTENTION

### Changes Summary
- Files modified: X
- Lines added: Y
- Lines removed: Z
- Net change: +/-N lines

### Refactoring Patterns Applied
1. Extract Method (src/api.js:45 → extractUserValidation())
2. Introduce Parameter Object (src/checkout.js:120)
3. Replace Conditional with Polymorphism (src/payment.js:78)

### Test Results
- Existing tests: ✅ 287/287 passed
- New tests added: 12
- Code coverage: 85% (baseline: 83%)

### Performance Comparison
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| API Response Time | 245ms | 198ms | -19% ✅ |
| Memory Usage | 128MB | 125MB | -2% ✅ |
| Test Suite Duration | 12.5s | 12.3s | -1.6% ✅ |

### Quality Metrics
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Cyclomatic Complexity | 8.2 | 5.4 | -34% ✅ |
| Lines per Method | 24 | 15 | -37% ✅ |
| Method Count | 45 | 52 | +16% |

### Risks
- None identified

### Recommendation
✅ Safe to merge - All quality gates passed
```

### 8. Create Pull Request

Generate pull request with refactoring summary:
```bash
gh pr create --title "Refactor: [Description]" --body "$(cat refactoring-report.md)"
```

Include in PR description:
- Refactoring patterns applied
- Test results and coverage
- Performance impact
- Rollback plan

### 9. Rollback Plan (if needed)

If refactoring introduces issues:
```bash
# Return to main branch
git checkout main

# Delete refactoring branch
git branch -D refactor-YYYYMMDD-HHMMSS
```

Rollback criteria:
- Test failures that cannot be quickly resolved
- Performance regression >5%
- Unexpected behavior in production-like environment
- Team vote to abandon refactoring

## Safety Gates

Automatic approval if ALL conditions met:
- ✅ All existing tests pass
- ✅ Code coverage maintained or improved
- ✅ No performance regression >5%
- ✅ Cyclomatic complexity reduced or unchanged
- ✅ No new security issues

Manual review required if ANY condition fails.

## Best Practices

- Always create a safety branch
- Never modify existing test behavior without justification
- Run full test suite, not just affected tests
- Compare performance metrics before/after
- Document all refactoring patterns applied
- Keep refactoring PRs focused (single responsibility)
- Have clear rollback plan before starting
