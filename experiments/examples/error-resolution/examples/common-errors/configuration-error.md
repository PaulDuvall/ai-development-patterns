# Configuration Error Example

Example of using the Error Resolution pattern with YAML configuration validation errors.

## Step 1: Error Output

```
Application startup failed: ConfigValidationError

  1. database.port: Expected type 'number', got type 'string'
     Value: "5432"
     Location: config/production.yaml:12

  2. api.secret_key: Required field missing
     Location: config/production.yaml

  3. cache.ttl_seconds: Unknown configuration key
     Valid keys: cache.ttl, cache.max_size
     Location: config/production.yaml:34
```

## Step 2: Collect Context

```bash
cat > .error-context.md << 'EOF'
## Error
- database.port: string "5432" should be number 5432
- api.secret_key: missing required field
- cache.ttl_seconds: unknown key (should be cache.ttl)

## Recent Changes
$(git log --oneline -3 config/)

## Configuration File (config/production.yaml)
```yaml
database:
  port: "5432"  # Line 12 - string instead of number

api:
  base_url: https://api.example.com
  timeout: 30
  # secret_key missing

cache:
  ttl_seconds: 3600  # Line 34 - wrong key name
```
EOF
```

## Step 3: AI Diagnosis

```bash
ai "Fix this configuration error:

$(cat .error-context.md)

Provide:
1. Root cause for each error
2. Fix commands
3. Prevention (one method)"
```

## Step 4: Apply Fix

```bash
# Root cause: Type errors and missing required fields

# Fix configuration
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

# Set environment variables
export API_SECRET_KEY="your-secret-key"
export DB_PASSWORD="your-db-password"

# Validate
npm start  # Should start successfully

# Commit
git add config/production.yaml
git commit -m "fix: correct config types and add missing fields"
git push
```

## Prevention

Add config validation script:

```javascript
// scripts/validate-config.js
const Ajv = require('ajv');
const yaml = require('js-yaml');
const fs = require('fs');

const schema = JSON.parse(fs.readFileSync('config/schema.json'));
const config = yaml.load(fs.readFileSync(process.argv[2]));

const validate = new Ajv().compile(schema);
if (!validate(config)) {
  console.error('❌ Invalid config:', validate.errors);
  process.exit(1);
}
console.log('✓ Config valid');
```

Usage: `node scripts/validate-config.js config/production.yaml`
