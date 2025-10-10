# Security Review

Comprehensive security analysis of recent changes with multi-layer vulnerability detection.

## Usage

```bash
/security-review              # Review recent changes
/security-review --full       # Full codebase scan
/security-review --secrets    # Focus on secret detection
```

## Implementation

### 1. Secret Detection

Scan for hardcoded sensitive data:

**API Keys and Tokens**
- AWS keys (AKIA*, ASIA*)
- GitHub tokens (ghp_*, gho_*)
- Stripe keys (sk_live_*, pk_live_*)
- Generic patterns (api_key=, apiKey:, API_TOKEN)

**Credentials**
- Hardcoded passwords (password=, pwd=)
- Database connection strings with passwords
- Private keys (BEGIN PRIVATE KEY, BEGIN RSA PRIVATE KEY)
- Certificate files (.pem, .key, .p12)

**Environment Variables**
- Check for proper usage: `process.env.API_KEY`, `os.getenv('DB_PASSWORD')`
- Verify credentials are not committed
- Identify credential files (.env, secrets.json, config/credentials.yml)

### 2. Vulnerability Analysis

**Dependency Vulnerabilities**
- Check dependencies against CVE databases
- Identify outdated packages with known vulnerabilities
- Assess severity (CRITICAL/HIGH/MEDIUM/LOW)
- Suggest specific version upgrades

**Authentication & Authorization**
- Verify authentication on all protected endpoints
- Check for authorization bypass vulnerabilities
- Review session management (token expiration, refresh logic)
- Identify missing authentication checks

**Input Validation**
- Check for SQL injection vulnerabilities
- Identify XSS (Cross-Site Scripting) risks
- Verify input sanitization for user data
- Check file upload validation (file type, size, content)

### 3. Configuration Security

**Network Security**
- Verify HTTPS enforcement (no HTTP fallback)
- Check TLS version (TLS 1.2+ required)
- Validate certificate configuration
- Review redirect policies

**CORS Policies**
- Check Access-Control-Allow-Origin (avoid wildcards in production)
- Verify credentials handling
- Review allowed methods and headers

**Security Headers**
- Content-Security-Policy (CSP)
- HTTP Strict-Transport-Security (HSTS)
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY/SAMEORIGIN
- Referrer-Policy

### 4. Code Security Patterns

**Common Vulnerabilities**
- Command injection (shell execution with user input)
- Path traversal (../../../etc/passwd)
- Insecure deserialization
- Race conditions
- Memory leaks

**Cryptography**
- Check for weak algorithms (MD5, SHA1 for security)
- Verify proper use of crypto libraries
- Review key management practices
- Check for hardcoded encryption keys

### 5. Output Format

For each issue found, provide:

```markdown
## Security Issue: [Title]

**Severity**: CRITICAL/HIGH/MEDIUM/LOW

**Location**: file.js:42

**Risk Explanation**:
Detailed explanation of the security risk with concrete examples of exploitation.

**Example Attack Scenario**:
```javascript
// Attacker could exploit this by:
malicious_input = "'; DROP TABLE users; --"
```

**Remediation**:
```javascript
// Before (vulnerable):
query = `SELECT * FROM users WHERE id = ${userId}`

// After (secure):
query = db.prepare("SELECT * FROM users WHERE id = ?")
query.run(userId)
```

**References**:
- OWASP Top 10: [Relevant category]
- CWE-XXX: [Weakness description]
```

### 6. Security Summary

Provide final summary:
- Total issues found (by severity)
- Critical issues requiring immediate attention
- Compliance status (OWASP Top 10 coverage)
- Recommended next steps
- Security score (0-100)

## Tools Integration

Leverage these tools when available:
- `gitleaks` - Secret detection
- `npm audit` / `pip-audit` - Dependency vulnerabilities
- `bandit` (Python) / `gosec` (Go) - Static security analysis
- `eslint-plugin-security` - JavaScript security patterns

## Argument Support

- `--full`: Scan entire codebase (not just recent changes)
- `--secrets`: Focus only on secret detection
- `--deps`: Focus only on dependency vulnerabilities
- `--config`: Focus only on configuration security
- No arguments: Comprehensive review of recent changes
