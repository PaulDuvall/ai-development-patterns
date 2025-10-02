# Auth Patterns

### JWT Auth (95% success)
**Prompt**: "JWT with RS256, 15min access, 7day refresh in httpOnly cookie"
**Context**: Node.js APIs
**Gotcha**: AI defaults to insecure HS256 - always specify RS256
**Last Used**: 2024-01-15
**Success Rate**: 95% (19/20 attempts)

### Password Hash (90% success)
**Prompt**: "bcrypt with salt rounds=12, async/await, bcrypt.compare for validation"
**Context**: Any Node.js backend
**Gotcha**: AI uses deprecated hashSync - specify async
**Last Used**: 2024-01-12
**Success Rate**: 90% (18/20 attempts)

### OAuth2 Integration (85% success)
**Prompt**: "OAuth2 with Passport.js: Google strategy, session storage, redirect handling"
**Context**: Express.js applications needing social login
**Gotcha**: AI forgets to handle OAuth errors and edge cases
**Last Used**: 2024-01-10
**Success Rate**: 85% (17/20 attempts)