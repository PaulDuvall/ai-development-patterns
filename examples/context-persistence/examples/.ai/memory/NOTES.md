# Session Notes - Auth System Implementation

---

## Session 2024-01-16

**Context**: Debugging intermittent JWT verification failures (5% error rate)

**Discoveries**:
- Clock skew on api-gateway-2 was 47 seconds behind (NTP sync disabled in container)
- Added 60s clock skew tolerance to JWT library → failures dropped from 5% to 0.1%
- Enabled NTP sync on all containers → failures dropped to 0%
- RS256 verification performance impact is negligible: 2ms slower than HS256 at p99

**Blockers**:
- None - clock skew issue resolved

**Next Actions**:
- Add clock drift monitoring to observability stack
- Document clock skew tolerance decision in DECISIONS.log
- Update Docker Compose to enable NTP sync by default

**References**:
- `docker exec api-gateway-2 date` for clock comparison
- JWT library: jsonwebtoken v9.0.2 with `clockTolerance` option

---

## Session 2024-01-15

**Context**: Implementing JWT authentication with RS256 signing

**Discoveries**:
- bcrypt has performance degradation above 100 req/s under load testing (wrk)
  - 12 rounds: ~150ms/hash at 100 req/s
  - 10 rounds: ~70ms/hash but less secure
- RS256 JWT verification is only 2ms slower than HS256 at p99 (tested with 1000 req/s)
- httpOnly cookies prevent XSS attacks but require CSRF protection
  - sameSite=strict is most secure but breaks OAuth flows
  - sameSite=lax balances security and compatibility

**Blockers**:
- Need to decide on refresh token storage approach (DB vs Redis vs JWT-in-JWT)
- Unclear how to handle token revocation for RS256 (no shared state between services)

**Next Actions**:
- Benchmark argon2 vs bcrypt for password hashing at scale
- Research token revocation patterns:
  - Blocklist approach (Redis with TTL)
  - Short-lived tokens only (no explicit revocation)
  - Token versioning (increment version in DB on revoke)
- Document RS256 decision in DECISIONS.log

**References**:
- [OWASP JWT Security Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [Auth0 Refresh Token Best Practices](https://auth0.com/docs/secure/tokens/refresh-tokens)
- Local benchmarks: `benchmarks/auth-performance.md`

---

## Session 2024-01-14

**Context**: Setting up development environment for auth system

**Discoveries**:
- Docker network isolation (`network_mode: none`) prevents accidental secret leaks
- Generated RSA 2048-bit key pair using `openssl genrsa` and `openssl rsa`
- Private key requires file permissions 0600 or JWT library throws security error
- Environment variable size limits make them unsuitable for PEM-encoded keys

**Blockers**:
- None

**Next Actions**:
- Research JWT signing algorithms (RS256 vs HS256 vs ES256)
- Set up test suite for auth middleware
- Create Docker Compose configuration for auth service

**References**:
- `scripts/generate-jwt-keys.sh` for key generation automation
- Docker Compose: `docker-compose.auth.yml`

---

## Previously On...

As of 2024-01-16, we're implementing a JWT-based authentication system for the microservices architecture. Key decisions include using RS256 for signing (asymmetric keys for better key rotation) and 15-minute access token expiry with refresh tokens. Current focus is completing the JWT middleware implementation with rate limiting and CSRF protection. Recent blocker (clock skew causing 5% verification failures) has been resolved with NTP sync and clock tolerance. Next milestone is completing the full auth flow with token refresh and revocation strategy.

---
