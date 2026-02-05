# Universal Organization Rules

These rules apply to ALL projects regardless of language or framework.

## Security Standards

### Secret Management
- ❌ NEVER commit secrets, API keys, passwords, or credentials
- ✅ Use environment variables for all configuration
- ✅ Run secret scanning before commits: `gitleaks detect --no-git`
- ✅ Use secret management services (AWS Secrets Manager, 1Password)

### Sensitive Files
Block editing of these files:
- `.env`, `.env.*`
- `credentials.json`, `secrets.yaml`
- `**/config/production.yml`
- Any file containing API keys or tokens

### Security Scanning
Before any commit:
```bash
# Scan for hardcoded secrets
gitleaks detect --no-git --source=.

# Check dependencies for vulnerabilities
# Python: pip-audit or safety
# Node.js: npm audit
# Go: govulncheck
```

## Code Quality

### Testing Standards
- Write tests FIRST (Test-Driven Development)
- Minimum code coverage: **80%**
- Test edge cases and error conditions
- Use meaningful test names that describe behavior

### Code Style
- Follow existing patterns in the codebase
- Self-documenting code with clear variable/function names
- Comments explain **WHY**, not WHAT
- Keep functions small (<50 lines) and single-purpose

### Error Handling
- Handle ALL errors explicitly
- Never use bare `except:` or `catch (e) {}`
- Log errors with context (request ID, user ID, operation)
- Return meaningful error messages to users

## Git Workflow

### Commit Standards
- Use Conventional Commits format:
  - `feat: add user authentication`
  - `fix: prevent duplicate orders`
  - `docs: update API documentation`
  - `refactor: simplify payment logic`
- Reference issue numbers: `feat: add logout (#123)`
- Keep commits atomic (one logical change per commit)

### Branch Naming
- `feature/short-description`
- `fix/bug-description`
- `refactor/area-being-refactored`

### Before Pushing
Always run:
```bash
# 1. Run tests
npm test  # or pytest, go test, etc.

# 2. Check git diff
git diff --cached

# 3. Verify no secrets
gitleaks detect --no-git
```

## AI Development Standards

### Specification-Driven
- Write specifications BEFORE implementation
- Use formal specs: OpenAPI, JSON Schema, Gherkin
- Link code to specification IDs for traceability

### Progressive Disclosure
When working in specialized areas, load additional rules:
- **API work**: Load API design rules
- **Security changes**: Load security-specific rules
- **Database migrations**: Load database rules

### Communication
- Ask clarifying questions before major changes
- Explain non-obvious implementation decisions
- Propose alternatives when requirements are ambiguous

## Compliance

### Data Protection
- Never log PII (emails, names, addresses)
- Redact sensitive data in error messages
- Follow GDPR/CCPA data handling requirements

### Audit Trail
- Log significant actions (authentication, data changes)
- Include: timestamp, user ID, action, result
- Retention: 90 days minimum for audit logs

## Development Environment

### Documentation
- Update README.md when adding features
- Document environment variables in `.env.example`
- Keep API documentation current (OpenAPI/Swagger)

### Dependencies
- Pin versions in production (`package-lock.json`, `requirements.txt`)
- Review security advisories before upgrading
- Test upgrades in staging before production

---

**Questions about these rules?** Contact: dev-leads@yourorg.com
**Rule updates:** Create PR in `ai-rules-central` repository
