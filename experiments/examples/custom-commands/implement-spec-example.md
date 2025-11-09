# Implement-Spec Command Example

Link implementation directly to specifications with traceability.

## Command Definition

```markdown
---
description: Implement specification with full traceability and test-driven development
argument-hint: Specification ID (e.g., AUTH-001)
---

# Implement Specification

You are helping a developer implement a specification using test-driven development with full traceability from requirements to code.

## Usage
/implement-spec AUTH-001

## Process
1. Read specification file: @specs/$1.md
2. Extract acceptance criteria from spec
3. Generate failing tests for each criterion
4. Implement minimal code to pass tests
5. Add traceability comments: // Implements: specs/$1.md#AC-001
6. Run tests to verify 100% spec coverage
7. Generate traceability report linking code to requirements
```

## Use Case

Perfect for specification-driven development where you need:
- Direct traceability from requirements to code
- Test-driven implementation
- Compliance documentation
- Audit trails for regulated environments

## Example Workflow

```bash
# 1. Create specification file
cat > specs/AUTH-001.md << 'EOF'
# Authentication Specification

## AC-001: User Login
Users can log in with valid email and password

## AC-002: Invalid Credentials
Login fails with invalid password, shows error message

## AC-003: Account Lockout
Account locked after 5 failed login attempts
EOF

# 2. Implement specification
/implement-spec AUTH-001

# AI will:
# - Read specs/AUTH-001.md
# - Generate 3 failing tests (one per AC)
# - Implement minimal auth logic
# - Add traceability comments
# - Generate coverage report
```

## Output Example

```markdown
## Traceability Report: AUTH-001

| AC ID | Description | Tests | Implementation | Status |
|-------|-------------|-------|----------------|--------|
| AC-001 | User login with valid credentials | test_auth001_ac001_user_login_success | src/auth.py:login() | ✅ PASS |
| AC-002 | Login fails with invalid password | test_auth001_ac002_invalid_password | src/auth.py:login() | ✅ PASS |
| AC-003 | Account locked after 5 failed attempts | test_auth001_ac003_account_lockout | src/auth.py:login() | ✅ PASS |

**Coverage**: 100% (3/3 acceptance criteria implemented and tested)
```

## Related Patterns

- [Specification Driven Development](../../README.md#specification-driven-development)
- [AI-Driven Traceability](../../README.md#ai-driven-traceability)
