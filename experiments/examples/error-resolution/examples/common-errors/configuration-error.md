# Configuration Error Example

This example demonstrates how to use the Error Resolution pattern for configuration-related errors.

## Error Scenario

```
Error: Configuration validation failed
  - Invalid value for 'database.port': expected number, got string
  - Missing required field 'api.secret_key'
  - Unknown configuration key 'cache.ttl_seconds'
```

## Error Context Collection

```bash
cat > .error-context.md << 'EOF'
# Configuration Error Analysis

## Error Output
```
Application startup failed:
  ConfigValidationError: Invalid configuration

Details:
  1. database.port: Expected type 'number', got type 'string'
     Value: "5432"
     Location: config/production.yaml:12

  2. api.secret_key: Required field missing
     Location: config/production.yaml

  3. cache.ttl_seconds: Unknown configuration key
     Valid keys: cache.ttl, cache.max_size
     Location: config/production.yaml:34
```

## Configuration File (config/production.yaml)
```yaml
database:
  host: db.example.com
  port: "5432"  # Line 12
  username: app_user
  # password loaded from environment

api:
  base_url: https://api.example.com
  timeout: 30
  # secret_key missing

cache:
  enabled: true
  ttl_seconds: 3600  # Line 34 - wrong key name
  max_size: 1000
```

## Recent Changes
```
git log --oneline -3 config/
abc123 Updated production config for new deployment
def456 Added cache configuration
ghi789 Split dev/prod configs
```

## Environment
- Application: Node.js API Server v2.1.0
- Config Library: node-config v3.3.9
- Environment: production
- Node.js: v18.17.0

EOF
```

## AI Diagnosis

```bash
ai "Diagnose this configuration error:

$(cat .error-context.md)

Provide:
1. What's wrong with each configuration item
2. Correct configuration
3. How to validate before deployment
4. Prevention strategies"
```

## Expected AI Response

### Root Cause Analysis

**Error 1: Type Mismatch**
- `database.port` is defined as string `"5432"` but application expects number `5432`
- YAML interprets unquoted numbers as integers, quoted numbers as strings
- Application config schema enforces type safety

**Error 2: Missing Required Field**
- `api.secret_key` is required by application but not present in config
- Should be loaded from environment variable or secrets manager
- Missing field blocks application startup

**Error 3: Unknown Configuration Key**
- `cache.ttl_seconds` doesn't exist in config schema
- Correct key name is `cache.ttl` (without _seconds suffix)
- Typo or outdated configuration

### Immediate Fixes

```bash
# Fix 1: Correct type for database.port
sed -i 's/port: "5432"/port: 5432/' config/production.yaml

# Fix 2: Add secret_key (environment variable approach)
cat >> config/production.yaml << 'YAML'
api:
  base_url: https://api.example.com
  timeout: 30
  secret_key: ${API_SECRET_KEY}  # Loaded from environment
YAML

# Fix 3: Correct cache key name
sed -i 's/ttl_seconds: 3600/ttl: 3600/' config/production.yaml

# Updated config file should be:
cat > config/production.yaml << 'YAML'
database:
  host: db.example.com
  port: 5432  # Fixed: number, not string
  username: app_user
  password: ${DB_PASSWORD}

api:
  base_url: https://api.example.com
  timeout: 30
  secret_key: ${API_SECRET_KEY}  # Fixed: added required field

cache:
  enabled: true
  ttl: 3600  # Fixed: correct key name
  max_size: 1000
YAML
```

### Validation

```bash
# Validate configuration before deploying
node -e "
  const config = require('config');
  console.log('✓ Configuration loaded successfully');
  console.log('Config:', JSON.stringify(config, null, 2));
" || echo "❌ Configuration invalid"

# Or use config library's validate command
npx config validate config/production.yaml

# Test with production environment variables
export API_SECRET_KEY="your-secret-key"
export DB_PASSWORD="your-db-password"
export NODE_ENV=production
npm start  # Should start successfully
```

### Prevention Strategy

**1. Add Configuration Schema**

Create `config/schema.json`:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["database", "api", "cache"],
  "properties": {
    "database": {
      "type": "object",
      "required": ["host", "port", "username"],
      "properties": {
        "host": { "type": "string" },
        "port": { "type": "number", "minimum": 1, "maximum": 65535 },
        "username": { "type": "string" }
      }
    },
    "api": {
      "type": "object",
      "required": ["base_url", "secret_key"],
      "properties": {
        "base_url": { "type": "string", "format": "uri" },
        "timeout": { "type": "number", "minimum": 1 },
        "secret_key": { "type": "string", "minLength": 32 }
      }
    },
    "cache": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean" },
        "ttl": { "type": "number", "minimum": 0 },
        "max_size": { "type": "number", "minimum": 1 }
      }
    }
  }
}
```

**2. Add Validation Script**

Create `scripts/validate-config.js`:
```javascript
const Ajv = require('ajv');
const yaml = require('js-yaml');
const fs = require('fs');

const ajv = new Ajv();
const schema = JSON.parse(fs.readFileSync('config/schema.json', 'utf8'));
const config = yaml.load(fs.readFileSync(process.argv[2], 'utf8'));

const validate = ajv.compile(schema);
const valid = validate(config);

if (!valid) {
  console.error('❌ Configuration validation failed:');
  console.error(JSON.stringify(validate.errors, null, 2));
  process.exit(1);
}

console.log('✓ Configuration valid');
```

Usage:
```bash
node scripts/validate-config.js config/production.yaml
```

**3. Pre-deployment Checklist**

Create `.github/workflows/config-validation.yml`:
```yaml
name: Validate Configuration
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Validate all configs
        run: |
          for config in config/*.yaml; do
            echo "Validating $config..."
            node scripts/validate-config.js $config
          done

      - name: Check for secrets in config
        run: |
          if grep -r "password\|secret\|key" config/ --exclude="*.example"; then
            echo "❌ Found hardcoded secrets in config files"
            exit 1
          fi
```

**4. Use Environment-Specific Examples**

```bash
# Create example configs
cp config/production.yaml config/production.yaml.example

# Remove sensitive values
sed -i 's/secret_key:.*/secret_key: ${API_SECRET_KEY}/' config/production.yaml.example
sed -i 's/password:.*/password: ${DB_PASSWORD}/' config/production.yaml.example

# Add to .gitignore
echo "config/*.yaml" >> .gitignore
echo "!config/*.yaml.example" >> .gitignore
```

**5. Documentation**

Create `config/README.md`:
```markdown
# Configuration Guide

## Setup

1. Copy example config:
   ```bash
   cp config/production.yaml.example config/production.yaml
   ```

2. Set environment variables:
   ```bash
   export API_SECRET_KEY="your-32-char-secret"
   export DB_PASSWORD="your-password"
   ```

3. Validate configuration:
   ```bash
   node scripts/validate-config.js config/production.yaml
   ```

## Required Environment Variables

- `API_SECRET_KEY`: 32+ character secret for JWT signing
- `DB_PASSWORD`: Database password
- `NODE_ENV`: Environment name (development/production)

## Configuration Schema

See `config/schema.json` for full schema documentation.
```

## Common Configuration Error Patterns

### Type Errors
```yaml
# ❌ Wrong
timeout: "30"  # String
max_connections: "100"  # String

# ✅ Correct
timeout: 30  # Number
max_connections: 100  # Number
```

### Missing Environment Variables
```yaml
# ❌ Wrong
secret_key: ""  # Empty

# ✅ Correct
secret_key: ${SECRET_KEY:?SECRET_KEY environment variable required}
```

### Nested Key Errors
```yaml
# ❌ Wrong
database.host: localhost  # Dot notation doesn't work

# ✅ Correct
database:
  host: localhost
```

## Troubleshooting Tips

1. **Validate early**: Check config on application startup
2. **Use schema validation**: Catch errors before deployment
3. **Default values**: Provide sensible defaults when possible
4. **Clear error messages**: Show exact location and expected format
5. **Separate secrets**: Never commit secrets to version control

## Key Takeaways

- **Validate configurations** before deployment
- **Use schemas** to enforce structure and types
- **Environment variables** for secrets and environment-specific values
- **Example configs** for documentation and onboarding
- **Automated testing** in CI/CD pipeline
