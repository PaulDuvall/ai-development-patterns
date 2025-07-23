# Auth Failures

### ❌ "Make auth secure"
**Problem**: Too vague → AI adds OAuth + sessions + JWT complexity
**Time Wasted**: 2 hours debugging over-engineered solution
**Better Approach**: "Implement JWT auth with RS256, 15min expiry, secure httpOnly cookies"
**Date**: 2024-01-10

### ❌ "Add authentication"
**Problem**: No constraints → 500 lines of unnecessary middleware
**Time Wasted**: 45 minutes simplifying generated code
**Better Approach**: "Simple JWT middleware: verify token, attach user to req, 401 on invalid"
**Date**: 2024-01-08

### ❌ "Implement secure login"
**Problem**: Generated vulnerable code with SQL injection
**Time Wasted**: 1 hour fixing security issues
**Better Approach**: "Parameterized queries, input validation, bcrypt for passwords"
**Date**: 2024-01-05