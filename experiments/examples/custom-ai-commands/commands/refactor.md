# Refactoring Assistant

Interactive refactoring assistant based on Martin Fowler's refactoring catalog.

## Usage Examples

```bash
/refactor              # Full analysis
/refactor --smell      # Code smells only
/refactor --duplicates # Find duplicate code
```

## Implementation

### 1. Code Smell Detection

Analyze codebase for maintainability issues:

- **Long methods** (>20 lines)
- **Duplicate code blocks** (repeated patterns across files)
- **Complex conditionals** (cyclomatic complexity >10)
- **Large classes** (>250 lines)

For each smell found:
- Identify exact location (file:line)
- Assess severity (CRITICAL/HIGH/MEDIUM/LOW)
- Suggest specific refactoring from Fowler's catalog
- Estimate effort and risk

### 2. Bloater Detection

Find oversized code structures:

- **Methods with excessive parameters** (>4)
- **Data clumps** (same variables passed together repeatedly)
- **Primitive obsession** (overuse of primitives vs objects)
- **Long parameter lists** (>3-4 parameters)

### 3. Refactoring Strategy

For each issue identified:

1. **Name the code smell** (e.g., "Long Method", "Feature Envy", "Shotgun Surgery")
2. **Recommend specific refactoring technique** from Fowler's catalog:
   - Extract Method
   - Move Method
   - Replace Temp with Query
   - Introduce Parameter Object
   - Replace Conditional with Polymorphism
3. **Show before/after example** with actual code snippets
4. **Estimate maintainability improvement** (complexity reduction, testability increase)

### 4. Output Format

Generate step-by-step refactoring plan prioritized by impact:

```markdown
## Refactoring Report

### Summary
- Total smells found: X
- Critical issues: Y
- Estimated total effort: Z hours

### Priority 1: Critical Issues
1. **Long Method in src/api/users.js:45-120**
   - Smell: Long Method (75 lines)
   - Severity: CRITICAL
   - Recommended refactoring: Extract Method
   - Estimated effort: 1 hour
   - Impact: Improves testability, reduces complexity by 40%

### Priority 2: High Issues
...

### Refactoring Plan
Step-by-step implementation guide with code examples
```

## Argument Support

- `--smell`: Focus only on code smell detection
- `--duplicates`: Focus only on duplicate code analysis
- `--suggest`: Provide refactoring suggestions without detailed analysis
- No arguments: Full comprehensive analysis
