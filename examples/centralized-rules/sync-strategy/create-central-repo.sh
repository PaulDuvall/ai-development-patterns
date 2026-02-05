#!/bin/bash
# create-central-repo.sh
# Quick-start script to create a central AI rules repository for your organization

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Rules Central Repository Setup ===${NC}\n"

# Get organization name
read -p "Organization name (e.g., yourorg): " ORG_NAME
ORG_NAME=${ORG_NAME:-yourorg}

# Get repository name
REPO_NAME="ai-rules-central"
read -p "Repository name [${REPO_NAME}]: " INPUT_REPO
REPO_NAME=${INPUT_REPO:-$REPO_NAME}

# Create directory structure
echo -e "\n${GREEN}Creating directory structure...${NC}"
mkdir -p "${REPO_NAME}"
cd "${REPO_NAME}"

mkdir -p base
mkdir -p languages
mkdir -p frameworks
mkdir -p domains
mkdir -p compliance

# Create base universal rules
echo -e "${GREEN}Creating base/universal-rules.md...${NC}"
cat > base/universal-rules.md << 'EOF'
# Universal Organization Rules

These rules apply to ALL projects regardless of language or framework.

## Security Standards

### Secret Management
- ❌ NEVER commit secrets, API keys, passwords, or credentials
- ✅ Use environment variables for all configuration
- ✅ Run secret scanning before commits: `gitleaks detect --no-git`

### Security Scanning
Before any commit:
```bash
# Scan for hardcoded secrets
gitleaks detect --no-git --source=.
```

## Code Quality

### Testing Standards
- Write tests FIRST (Test-Driven Development)
- Minimum code coverage: **80%**
- Test edge cases and error conditions

### Code Style
- Follow existing patterns in the codebase
- Self-documenting code with clear variable/function names
- Comments explain **WHY**, not WHAT

### Error Handling
- Handle ALL errors explicitly
- Log errors with context (request ID, user ID, operation)
- Return meaningful error messages to users

## Git Workflow

### Commit Standards
- Use Conventional Commits format:
  - `feat: add user authentication`
  - `fix: prevent duplicate orders`
  - `docs: update API documentation`
- Reference issue numbers: `feat: add logout (#123)`

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

### Communication
- Ask clarifying questions before major changes
- Explain non-obvious implementation decisions
- Propose alternatives when requirements are ambiguous

---

**Questions about these rules?** Contact: dev-leads@${ORG_NAME}.com
**Rule updates:** Create PR in `${REPO_NAME}` repository
EOF

# Create Python rules
echo -e "${GREEN}Creating languages/python.md...${NC}"
cat > languages/python.md << 'EOF'
# Python Development Rules

## Code Style
- **Tool**: Black (line length: 88 characters)
- **Import sorting**: isort with Black-compatible settings
- **Linting**: Ruff (replaces flake8, pylint)

### Type Hints
Required for all functions (parameters and return types):
```python
def process_payment(user_id: int, amount: Decimal) -> PaymentResult:
    ...
```

## Testing
- **Framework**: pytest
- **Coverage**: pytest-cov (minimum 80%)
- **Fixtures**: Define in `tests/conftest.py`

## Security
- Use Pydantic models for all API inputs
- Never trust user input
- Parameterized queries only (prevent SQL injection)

## Tools
```bash
# Format code
black . && isort .

# Type check
mypy src/

# Test
pytest -v --cov=src
```
EOF

# Create TypeScript rules
echo -e "${GREEN}Creating languages/typescript.md...${NC}"
cat > languages/typescript.md << 'EOF'
# TypeScript Development Rules

## Code Style
- **Strict mode**: Always enabled in `tsconfig.json`
- **Linting**: ESLint with recommended rules
- **Formatting**: Prettier (line length: 100)

## Type Safety
- ✅ Type all function parameters and return values
- ❌ Never use `any` (use `unknown` if type is truly unknown)
- ✅ Use strict null checks

```typescript
// CORRECT
function getUser(id: number): Promise<User | null> {
  ...
}

// WRONG - using any
function getUser(id: any): any {
  ...
}
```

## Testing
- **Framework**: Jest or Vitest
- **Coverage**: Minimum 80%
- **Mocking**: Use jest.mock() or vi.mock()

## Tools
```bash
# Type check
tsc --noEmit

# Lint
eslint src/

# Test
npm test
```
EOF

# Create React rules
echo -e "${GREEN}Creating frameworks/react.md...${NC}"
cat > frameworks/react.md << 'EOF'
# React Development Rules

## Component Structure
- ✅ Always use functional components with hooks
- ❌ No class components
- ✅ One component per file
- ✅ TypeScript required

## Hooks
- Always call hooks at top level
- Use ESLint plugin: `eslint-plugin-react-hooks`
- Extract reusable logic into custom hooks

## State Management
- **Local state**: useState for component-specific state
- **Global state**: Context API (avoid prop drilling >2 levels)
- **Server state**: SWR or React Query

## Testing
- **Framework**: React Testing Library
- **Focus**: Test user behavior, not implementation
- **Accessibility**: Test with screen readers in mind

```tsx
// CORRECT - Testing user behavior
expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();

// WRONG - Testing implementation
expect(component.state.isOpen).toBe(true);
```
EOF

# Create Django rules
echo -e "${GREEN}Creating frameworks/django.md...${NC}"
cat > frameworks/django.md << 'EOF'
# Django Development Rules

## Project Structure
- Use Django's recommended layout
- Settings split by environment (base, dev, prod)
- Migrations tracked in version control

## Models
- Always add `__str__()` method
- Use `verbose_name` and `help_text` for fields
- Add database indexes for frequently queried fields

## Security
- NEVER disable CSRF protection
- Use Django's built-in auth system
- Validate all user input with forms/serializers

## Testing
- Use Django's TestCase for database tests
- Use pytest-django for complex scenarios
- Factory Boy for test data generation

```python
# CORRECT - Using Django TestCase
from django.test import TestCase

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create(username="test")
        self.assertEqual(user.username, "test")
```
EOF

# Create README
echo -e "${GREEN}Creating README.md...${NC}"
cat > README.md << EOF
# ${ORG_NAME} AI Rules Central Repository

Central repository for organization-wide AI development rules.

## Structure

\`\`\`
${REPO_NAME}/
├── base/              # Universal rules for all projects
├── languages/         # Language-specific rules
├── frameworks/        # Framework-specific rules
├── domains/           # Domain-specific rules (fintech, healthcare)
└── compliance/        # Compliance frameworks (PCI-DSS, HIPAA)
\`\`\`

## Usage

In your project repository:

\`\`\`bash
# Download sync script
curl -O https://raw.githubusercontent.com/${ORG_NAME}/${REPO_NAME}/main/sync-ai-rules.sh
chmod +x sync-ai-rules.sh

# Run sync
./sync-ai-rules.sh

# Generates CLAUDE.md, AGENTS.md, .cursorrules with relevant rules
\`\`\`

## Adding New Rules

1. Create PR with new rule file (e.g., \`languages/go.md\`)
2. Follow existing format (see \`base/universal-rules.md\`)
3. Get approval from tech leads
4. Merge → automatically available to all projects on next sync

## Updating Rules

1. Edit rule files in this repository
2. Create PR with changes
3. After merge, projects sync with \`./sync-ai-rules.sh\`

## Questions?

Contact: dev-leads@${ORG_NAME}.com
EOF

# Copy sync script
echo -e "${GREEN}Copying sync-ai-rules.sh...${NC}"
cp ../sync-ai-rules.sh .

# Initialize git
echo -e "${GREEN}Initializing git repository...${NC}"
git init
git add .
git commit -m "Initial commit: AI rules central repository"

# Display next steps
echo -e "\n${GREEN}✅ Central repository created successfully!${NC}\n"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Review and customize rules in ${BLUE}${REPO_NAME}/${NC}"
echo -e "   - base/universal-rules.md"
echo -e "   - languages/*.md"
echo -e "   - frameworks/*.md"
echo ""
echo -e "2. Create remote repository:"
echo -e "   ${BLUE}cd ${REPO_NAME}${NC}"
echo -e "   ${BLUE}gh repo create ${ORG_NAME}/${REPO_NAME} --private --source=. --push${NC}"
echo ""
echo -e "3. In your project repositories:"
echo -e "   ${BLUE}curl -O https://raw.githubusercontent.com/${ORG_NAME}/${REPO_NAME}/main/sync-ai-rules.sh${NC}"
echo -e "   ${BLUE}chmod +x sync-ai-rules.sh${NC}"
echo -e "   ${BLUE}./sync-ai-rules.sh${NC}"
echo ""
echo -e "${GREEN}Done! Your organization now has centralized AI rules.${NC}"
