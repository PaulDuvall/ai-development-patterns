# Security Standards for AI Development

## Authentication & Authorization
- All AWS SDK calls must use encrypted clients
- JWT tokens must use RS256 algorithm (never HS256)
- Access tokens expire in 15 minutes maximum
- Refresh tokens stored in httpOnly cookies only
- Include user.id and role in JWT payload

## Data Protection
- All data at rest must be AES-256 encrypted
- All data in transit must use TLS 1.2 minimum
- No secrets in environment variables or code
- Use AWS Parameter Store or HashiCorp Vault for secrets

## Input Validation
- Validate all user inputs against whitelist patterns
- Sanitize all data before database operations
- Use parameterized queries to prevent SQL injection
- Implement rate limiting on all public endpoints

## Error Handling
- Never expose internal system details in error messages
- Log security events to centralized logging system
- Implement proper exception handling for all authentication flows
- Return generic error messages for authentication failures