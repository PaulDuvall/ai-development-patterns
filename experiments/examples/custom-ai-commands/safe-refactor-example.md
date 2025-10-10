# Safe-Refactor Command Example

Combine built-in commands with custom logic for safe refactoring.

## Command Definition

```markdown
# .claude/commands/safe-refactor.md
Safe refactoring with automated review.

## Process
1. Run /review to analyze current code state
2. Create git branch: refactor-$TIMESTAMP
3. Perform refactoring changes
4. Run existing test suite
5. Generate new tests for refactored code
6. Compare performance before/after
7. Create PR with refactoring summary
```

## Use Case

Perfect for:
- High-risk refactoring with safety checks
- Performance-sensitive code changes
- Team refactoring workflows
- Automated quality gates

## Example Workflow

```bash
# Run safe refactoring
/safe-refactor

# AI executes:
# 1. /review (built-in command) for baseline analysis
# 2. git checkout -b refactor-20250110-143022
# 3. Apply refactoring patterns
# 4. npm test (verify all pass)
# 5. Generate new tests for extracted methods
# 6. npm run benchmark (performance comparison)
# 7. gh pr create with report
```

## Refactoring Report Example

```markdown
## Refactoring Report

**Branch**: refactor-20250110-143022
**Status**: ✅ READY FOR REVIEW

### Changes Summary
- Files modified: 3
- Lines added: 45
- Lines removed: 87
- Net change: -42 lines

### Refactoring Patterns Applied
1. Extract Method (src/api.js:45 → extractUserValidation())
2. Introduce Parameter Object (src/checkout.js:120)

### Test Results
- Existing tests: ✅ 287/287 passed
- New tests added: 12
- Code coverage: 85% → 87% (+2%)

### Performance Comparison
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| API Response Time | 245ms | 198ms | -19% ✅ |
| Memory Usage | 128MB | 125MB | -2% ✅ |

### Recommendation
✅ Safe to merge - All quality gates passed
```

## Safety Gates

Automatic approval if ALL conditions met:
- ✅ All existing tests pass
- ✅ Code coverage maintained or improved
- ✅ No performance regression >5%
- ✅ Cyclomatic complexity reduced
- ✅ No new security issues

## Related Patterns

- [AI-Driven Refactoring](../../README.md#ai-driven-refactoring)
- [Comprehensive AI Testing Strategy](../README.md#comprehensive-ai-testing-strategy)
