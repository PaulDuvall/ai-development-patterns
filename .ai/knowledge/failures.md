# Common AI Development Failures and Gotchas

## Security Anti-Patterns

### ❌ "Make authentication secure"
**Problem:** Too vague - AI adds unnecessary complexity
**Symptoms:**
- Implements complex OAuth flows when simple JWT suffices
- Adds multiple authentication methods causing confusion
- Creates overly complicated password policies
- Generates insecure default configurations

**Better approach:** Be specific about security requirements
```
✅ "Implement JWT with RS256, 15-minute expiration, refresh tokens in httpOnly cookies"
```

### ❌ AI defaults to HS256 (insecure)
**Problem:** Most AI models default to HMAC-based JWT signing
**Symptoms:**
- Uses shared secret for JWT signing
- Vulnerable to secret exposure attacks
- Doesn't scale across multiple services

**Solution:** Always specify RS256 algorithm explicitly
```python
# AI often generates this (insecure):
jwt.encode(payload, "secret", algorithm="HS256")

# Specify this instead:
jwt.encode(payload, private_key, algorithm="RS256")
```

### ❌ Storing secrets in environment variables
**Problem:** AI suggests env vars for everything including production secrets
**Symptoms:**
- Database passwords in .env files
- API keys committed to version control
- Secrets visible in process lists and logs

**Solution:** Use external secret management
```
✅ Use AWS Parameter Store, HashiCorp Vault, or Kubernetes secrets
```

## Database Anti-Patterns

### ❌ "Create a user table"
**Problem:** AI generates basic tables without considering real-world requirements
**Symptoms:**
- Missing audit fields (created_at, updated_at)
- No soft delete capability
- Poor indexing strategy
- No foreign key constraints

**Better prompt:**
```
✅ "Create user table with audit fields, soft deletes, proper indexes for email lookup, and foreign key constraints"
```

### ❌ AI often uses deprecated bcrypt methods
**Problem:** Training data includes outdated security practices
**Symptoms:**
- Uses bcrypt.hashpw() instead of bcrypt.generate_password_hash()
- Incorrect salt generation
- Hardcoded salt rounds (too low)

**Solution:** Specify current best practices
```python
# AI might generate (outdated):
bcrypt.hashpw(password, bcrypt.gensalt())

# Specify modern approach:
bcrypt.generate_password_hash(password, rounds=12)
```

## API Development Failures

### ❌ "Create REST API"
**Problem:** Generates basic CRUD without real-world considerations
**Symptoms:**
- No input validation
- Missing error handling
- No rate limiting
- Inconsistent response formats
- No authentication

**Better approach:**
```
✅ "Create REST API with Pydantic validation, rate limiting, JWT auth, standardized error responses"
```

### ❌ Inconsistent error responses
**Problem:** AI generates different error formats for each endpoint
**Example failures:**
```python
# Endpoint 1 returns:
{"error": "User not found"}

# Endpoint 2 returns:
{"message": "Invalid input", "code": 400}

# Endpoint 3 returns:
{"detail": [{"msg": "field required"}]}
```

**Solution:** Define error response schema upfront

### ❌ Missing input validation
**Problem:** AI focuses on happy path implementation
**Symptoms:**
- SQL injection vulnerabilities
- Type confusion errors
- Buffer overflow possibilities
- No bounds checking

## Testing Anti-Patterns

### ❌ "Add some tests"
**Problem:** Generates minimal, non-comprehensive tests
**Symptoms:**
- Only tests happy path
- No edge case coverage
- Tests that don't actually verify behavior
- Missing error condition tests

**Better prompt:**
```
✅ "Generate comprehensive tests covering happy path, edge cases, error conditions, with >90% coverage"
```

### ❌ Tests that mirror implementation
**Problem:** AI generates tests based on code structure rather than behavior
**Symptoms:**
- Tests internal methods instead of public interface
- Brittle tests that break on refactoring
- No business logic validation

### ❌ Flaky test generation
**Problem:** AI doesn't account for timing and concurrency issues
**Symptoms:**
- Tests depend on external services
- Race conditions in async tests
- Hardcoded delays instead of proper waiting

## Frontend Development Failures

### ❌ "Create a form component"
**Problem:** Generates basic forms without real-world requirements
**Symptoms:**
- No input validation
- Poor accessibility
- No error handling
- Inconsistent styling

**Better approach:**
```
✅ "Create form with Formik validation, ARIA labels, error states, loading indicators"
```

### ❌ Missing TypeScript types
**Problem:** AI often generates JavaScript-style React components
**Symptoms:**
- Props without type definitions
- Any types everywhere
- Missing interface definitions
- No compile-time safety

## Performance Anti-Patterns

### ❌ "Improve performance"
**Problem:** Too vague, leads to premature optimization
**Symptoms:**
- Adds caching everywhere
- Complex optimizations without measurement
- Over-engineering simple operations

**Better approach:**
```
✅ "Profile current performance, identify bottlenecks, optimize specific slow queries"
```

### ❌ N+1 query generation
**Problem:** AI doesn't consider database query patterns
**Symptoms:**
- Loops that trigger individual database queries
- Missing eager loading
- No query batching

## Deployment Gotchas

### ❌ AI generates non-production Docker configs
**Problem:** Focuses on development convenience over production security
**Symptoms:**
- Running as root user
- No health checks
- Exposing unnecessary ports
- Including development dependencies

### ❌ Missing environment configuration
**Problem:** Hardcodes values instead of using environment variables
**Symptoms:**
- Database URLs in code
- API keys in source
- Environment-specific logic

## Prompt Engineering Failures

### ❌ Asking for "best practices"
**Problem:** Gets generic advice instead of specific implementation
**Result:** Vague recommendations that don't translate to code

### ❌ Not providing context
**Problem:** AI doesn't understand existing codebase patterns
**Symptoms:**
- Code that doesn't match project style
- Dependencies that conflict with existing ones
- Architecture that doesn't fit current design

### ❌ Accepting first AI response
**Problem:** First response is often generic or incomplete
**Solution:** Iterate and refine prompts for specific needs

## Context Window Limitations

### ❌ Feeding entire codebase to AI
**Problem:** Important details get lost in large context
**Symptoms:**
- AI focuses on wrong parts of code
- Suggestions don't consider all constraints
- Performance degrades with large inputs

**Solution:** Provide focused, relevant context only