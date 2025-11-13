# CLI Interface Specification

## Application CLI: `aiapp`

### Global Options
- `--help, -h`: Show help information
- `--version, -v`: Show application version
- `--config, -c PATH`: Specify configuration file path
- `--verbose`: Enable verbose output
- `--quiet, -q`: Suppress non-error output

### Authentication Commands

#### `aiapp auth login`
**Purpose**: Authenticate user and store credentials

**Usage**: `aiapp auth login [OPTIONS]`

**Options**:
- `--email EMAIL`: User email address (required)
- `--password PASSWORD`: User password (prompt if not provided)
- `--save-token`: Save authentication token to file
- `--token-file PATH`: Specify token file location (default: ~/.aiapp/token)

**Input**:
```bash
aiapp auth login --email user@example.com
Password: [hidden input]
```

**Output Success**:
```
✓ Login successful
Token saved to ~/.aiapp/token
Expires: 2024-01-01 15:30:00 UTC
```

**Output Failure**:
```
✗ Authentication failed: Invalid credentials
```

**Exit Codes**:
- 0: Success
- 1: Authentication failed
- 2: Network error
- 3: Invalid arguments

#### `aiapp auth logout`
**Purpose**: Remove stored authentication credentials

**Usage**: `aiapp auth logout`

**Output**:
```
✓ Logout successful
Token removed from ~/.aiapp/token
```

### User Management Commands

#### `aiapp user profile`
**Purpose**: Display current user profile information

**Usage**: `aiapp user profile [OPTIONS]`

**Options**:
- `--format FORMAT`: Output format (json, table, yaml) [default: table]
- `--output FILE`: Write output to file

**Output (table format)**:
```
User Profile
============
ID:         12345
Email:      user@example.com
Role:       user
Created:    2023-12-01 10:30:00 UTC
Last Login: 2024-01-01 14:25:00 UTC
```

**Output (json format)**:
```json
{
  "id": 12345,
  "email": "user@example.com",
  "role": "user",
  "created_at": "2023-12-01T10:30:00Z",
  "last_login": "2024-01-01T14:25:00Z"
}
```

#### `aiapp user update`
**Purpose**: Update user profile information

**Usage**: `aiapp user update [OPTIONS]`

**Options**:
- `--email EMAIL`: New email address
- `--password`: Prompt for new password
- `--confirm`: Skip confirmation prompt

**Input**:
```bash
aiapp user update --email newemail@example.com
```

**Output**:
```
✓ Profile updated successfully
Email changed from user@example.com to newemail@example.com
```

### Project Management Commands

#### `aiapp project init`
**Purpose**: Initialize new AI development project

**Usage**: `aiapp project init [PROJECT_NAME] [OPTIONS]`

**Options**:
- `--template TEMPLATE`: Project template (fastapi, react, fullstack) [default: fastapi]
- `--directory DIR`: Target directory [default: current directory]
- `--no-git`: Skip git repository initialization
- `--no-rules`: Skip AI rules setup

**Input**:
```bash
aiapp project init my-ai-project --template fullstack
```

**Output**:
```
Creating AI development project: my-ai-project
✓ Project structure created
✓ Git repository initialized
✓ AI rules configured (.ai/rules/)
✓ Security sandbox configured (docker-compose.ai-sandbox.yml)
✓ CI/CD pipeline created (.github/workflows/)

Next steps:
1. cd my-ai-project
2. aiapp project setup
3. Start developing with AI assistance
```

#### `aiapp project setup`
**Purpose**: Set up development environment for AI project

**Usage**: `aiapp project setup [OPTIONS]`

**Options**:
- `--install-deps`: Install project dependencies
- `--setup-db`: Initialize database
- `--start-services`: Start development services

**Output**:
```
Setting up AI development environment...
✓ Dependencies installed
✓ Database initialized
✓ AI security sandbox started
✓ Development server ready on http://localhost:8000

Run 'aiapp project status' to check service health
```

### Development Commands

#### `aiapp dev generate`
**Purpose**: Generate code using AI with project rules

**Usage**: `aiapp dev generate [TYPE] [OPTIONS]`

**Types**:
- `api`: Generate API endpoint
- `model`: Generate data model
- `test`: Generate test cases
- `migration`: Generate database migration

**Options**:
- `--prompt TEXT`: Generation prompt
- `--file FILE`: Output file path
- `--review`: Enable AI code review
- `--apply`: Apply generated code immediately

**Input**:
```bash
aiapp dev generate api --prompt "Create user profile endpoint with authentication"
```

**Output**:
```
Generating API endpoint...
✓ Code generated: src/api/users.py
✓ Tests generated: tests/test_users.py
✓ Security review passed
✓ Code style validated

Run 'aiapp dev review' to perform detailed review
```

### Error Handling

**Network Errors**:
```
✗ Connection failed: Unable to reach API server
  Check your internet connection and try again
  If the problem persists, contact support
```

**Authentication Errors**:
```
✗ Authentication required
  Run 'aiapp auth login' to authenticate
```

**Permission Errors**:
```
✗ Insufficient permissions
  Contact your administrator to grant required access
```

**Configuration Errors**:
```
✗ Invalid configuration
  Check ~/.aiapp/config.yaml for syntax errors
  Run 'aiapp config validate' for detailed validation
```

### Configuration File Format

**Location**: `~/.aiapp/config.yaml`

```yaml
api:
  url: https://api.example.com/v1
  timeout: 30
  retry_attempts: 3

auth:
  token_file: ~/.aiapp/token
  auto_refresh: true

project:
  default_template: fastapi
  ai_rules_enabled: true
  security_sandbox: true

output:
  format: table
  color: auto
  verbose: false
```

### Environment Variables

- `AIAPP_API_URL`: Override API URL
- `AIAPP_CONFIG`: Override config file path
- `AIAPP_TOKEN`: Override token file path
- `AIAPP_LOG_LEVEL`: Set log level (debug, info, warn, error)
- `NO_COLOR`: Disable colored output