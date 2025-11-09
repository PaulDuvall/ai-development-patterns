# Security Review Command Example

Multi-layer security analysis beyond simple scanning.

## Command Definition

```markdown
---
description: Comprehensive security analysis with multi-layer vulnerability detection
argument-hint: Optional flags (--full, --secrets, --deps, --config)
---

# Security Review

You are helping a developer identify security vulnerabilities in code changes. Perform multi-layer security analysis covering secrets, dependencies, authentication, input validation, and configuration security.

## Implementation

### Secret Detection
- Scan for hardcoded API keys, passwords, tokens
- Check environment variable usage patterns
- Identify credential files (.env, secrets.json)

### Vulnerability Analysis
- Check dependencies against CVE databases
- Analyze authentication/authorization logic
- Review input validation and sanitization

### Configuration Security
- Verify HTTPS enforcement
- Check CORS policies and headers
- Review security headers (CSP, HSTS)

For each issue found:
- Severity: CRITICAL/HIGH/MEDIUM/LOW
- Location: file:line
- Risk explanation with examples
- Specific remediation with code example
```

## Use Case

Perfect for:
- Pre-commit security checks
- Pull request reviews
- Security audits
- Compliance validation

## Example Output

```markdown
## Security Issue: Hardcoded API Key

**Severity**: CRITICAL

**Location**: src/api.js:42

**Risk Explanation**:
API key is hardcoded in source code, exposing it to anyone with repository access.
If committed to public repository, key can be discovered by automated scanners within minutes.

**Example Attack Scenario**:
```javascript
// Attacker finds this in git history:
const API_KEY = "sk_live_51H3Lp2K..." // $50,000 in fraudulent charges
```

**Remediation**:
```javascript
// Before (vulnerable):
const API_KEY = "sk_live_51H3Lp2K..."

// After (secure):
const API_KEY = process.env.STRIPE_API_KEY
if (!API_KEY) throw new Error("STRIPE_API_KEY required")
```

**References**:
- OWASP Top 10: A02:2021 - Cryptographic Failures
- CWE-798: Use of Hard-coded Credentials
```

## Integration with Tools

```bash
# Combine with gitleaks for enhanced detection
/security-review --secrets

# Full codebase scan
/security-review --full

# Focus on dependencies
/security-review --deps
```

## Related Patterns

- [Security Scanning Orchestration](../../README.md#security-scanning-orchestration)
- [AI Security Sandbox](../../README.md#ai-security-sandbox)
