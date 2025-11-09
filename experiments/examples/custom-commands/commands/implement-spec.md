---
description: Implement specification with full traceability and test-driven development
argument-hint: Specification ID (e.g., AUTH-001)
---

# Implement Specification

You are helping a developer implement a specification using test-driven development with full traceability from requirements to code. Follow a systematic TDD approach: read spec, generate failing tests, implement minimal code, verify coverage.

## Usage

```bash
/implement-spec AUTH-001      # Implement authentication spec
/implement-spec PAYMENT-042   # Implement payment spec
```

## Process

### 1. Read Specification

Read specification file from project specs directory:
- Location: `@specs/$1.md` (e.g., `@specs/AUTH-001.md`)
- Parse specification structure:
  - Requirements section
  - Acceptance criteria
  - Test cases
  - Dependencies

### 2. Extract Acceptance Criteria

Identify all acceptance criteria from the specification:
- Format: `AC-001`, `AC-002`, etc.
- Extract expected behavior for each criterion
- Identify edge cases and error conditions
- Note any dependencies between criteria

### 3. Generate Failing Tests

Create test suite for each acceptance criterion:
- Write failing tests FIRST (Red phase)
- Test naming: `test_<spec_id>_<criterion_id>_<behavior>`
- Include docstring linking to spec: `"""Implements: specs/$1.md#AC-001"""`
- Cover happy path and error conditions
- Use realistic test data

Example:
```python
def test_auth001_ac001_user_login_success():
    """Implements: specs/AUTH-001.md#AC-001

    AC-001: User can log in with valid email and password
    """
    user = create_test_user(email="test@example.com", password="SecurePass123")
    result = login(email="test@example.com", password="SecurePass123")
    assert result.success is True
    assert result.token is not None
```

### 4. Implement Minimal Code

Write minimal implementation to pass tests:
- Follow test-driven development (TDD) approach
- Implement only what's needed to satisfy acceptance criteria
- Add traceability comments linking code to spec:
  ```python
  # Implements: specs/AUTH-001.md#AC-001
  def login(email: str, password: str) -> LoginResult:
      # Implementation here
  ```

### 5. Verify 100% Spec Coverage

Run tests to verify all acceptance criteria are satisfied:
```bash
pytest tests/test_$1.py -v --cov=src --cov-report=term-missing
```

Ensure:
- All tests pass
- All acceptance criteria have corresponding tests
- Code coverage meets project standards (typically >80%)

### 6. Generate Traceability Report

Create traceability matrix showing:
- Spec ID → Acceptance Criteria → Tests → Implementation
- Coverage percentage per acceptance criterion
- Any gaps or missing implementations

Example report:
```markdown
## Traceability Report: AUTH-001

| AC ID | Description | Tests | Implementation | Status |
|-------|-------------|-------|----------------|--------|
| AC-001 | User login with valid credentials | test_auth001_ac001_user_login_success | src/auth.py:login() | ✅ PASS |
| AC-002 | Login fails with invalid password | test_auth001_ac002_invalid_password | src/auth.py:login() | ✅ PASS |
| AC-003 | Account locked after 5 failed attempts | test_auth001_ac003_account_lockout | src/auth.py:login() | ✅ PASS |

**Coverage**: 100% (3/3 acceptance criteria implemented and tested)
```

### 7. Output Summary

Provide implementation summary:
- Number of acceptance criteria implemented
- Number of tests created
- Code coverage percentage
- Files created/modified
- Next steps or remaining work

## Argument Handling

Parse $ARGUMENTS to extract specification ID:
- First argument ($1) is the specification ID
- Example: `/implement-spec AUTH-001` → Read `@specs/AUTH-001.md`

## Core Principles

- Always read the spec file FIRST before implementation
- Write tests BEFORE implementation (TDD Red-Green-Refactor)
- Add traceability comments linking code to specific AC IDs
- Verify 100% coverage of acceptance criteria
- Generate traceability report for documentation
- Maintain bidirectional traceability (requirements → code → tests)
