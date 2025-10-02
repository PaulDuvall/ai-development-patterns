# Task Tracking - Auth System Implementation

## Current Tasks

- [ ] Implement JWT middleware with RS256 signing
  - **Status**: in-progress
  - **Dependencies**: Public/private key generation (completed)
  - **Started**: 2024-01-15
  - **Notes**: Using jsonwebtoken v9.0.2, need to handle clock skew

- [ ] Add rate limiting to auth endpoints
  - **Status**: pending
  - **Dependencies**: JWT middleware completion
  - **Notes**: Research token bucket vs sliding window approach

- [ ] Configure CSRF protection for cookie-based auth
  - **Status**: pending
  - **Dependencies**: JWT middleware completion
  - **Notes**: Consider sameSite=strict vs lax for cookie security

## Blocked Tasks

- [ ] Implement token revocation strategy
  - **Blocked By**: Architectural decision needed - blocklist vs short expiry vs token versioning
  - **Impact**: Cannot complete auth system without revocation mechanism
  - **Next Action**: Benchmark each approach and document decision in DECISIONS.log

- [ ] Benchmark argon2 vs bcrypt for password hashing
  - **Blocked By**: Need to set up performance testing environment
  - **Impact**: May need to replace bcrypt if performance degrades at scale
  - **Next Action**: Create wrk benchmark scripts for both algorithms

## Completed

- [x] Research JWT signing algorithms (Completed: 2024-01-15)
  - **Outcome**: Chose RS256 over HS256 for better key rotation
  - **Learnings**: Documented in DECISIONS.log

- [x] Set up Docker environment with network isolation (Completed: 2024-01-14)
  - **Outcome**: Auth service running in isolated container
  - **Learnings**: NTP sync critical for JWT exp validation

- [x] Generate RSA key pair for JWT signing (Completed: 2024-01-15)
  - **Outcome**: 2048-bit keys stored in /etc/ssl/jwt-*.pem
  - **Learnings**: Private key requires strict file permissions (0600)
