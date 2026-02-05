# Centralized Rules

Sync organization-wide AI development rules from a central Git repository to your projects. Auto-generates CLAUDE.md, AGENTS.md, and .cursorrules with language/framework-specific rules.

For complete pattern documentation, see: [Centralized Rules](../../README.md#centralized-rules)

## TL;DR - 30 Second Start

```bash
# 1. Get the quick-start script
./sync-strategy/create-central-repo.sh
# Creates ai-rules-central/ with example rules

# 2. In your project
curl -O https://raw.githubusercontent.com/yourorg/ai-rules-central/main/sync-ai-rules.sh
chmod +x sync-ai-rules.sh
./sync-ai-rules.sh

# 3. Done! CLAUDE.md, AGENTS.md, .cursorrules auto-generated
# Claude Code, Cursor, Gemini now follow your org rules
```

## How It Works

```
┌─────────────────────────────────────────┐
│  Central Rules Repo (Git)               │
│  github.com/yourorg/ai-rules-central    │
│                                          │
│  ├── base/universal-rules.md           │
│  ├── languages/python.md               │
│  └── frameworks/react.md               │
└─────────────────────────────────────────┘
              ↓ [sync-ai-rules.sh]
┌─────────────────────────────────────────┐
│  Your Project                           │
│                                          │
│  ├── CLAUDE.md      (auto-generated)    │
│  ├── AGENTS.md      (auto-generated)    │
│  └── .cursorrules   (auto-generated)    │
└─────────────────────────────────────────┘
```

**What happens during sync:**

1. **Detects your stack** - Finds Python, TypeScript, React, Django, etc.
2. **Fetches relevant rules** - Pulls universal + language + framework rules
3. **Generates config files** - Creates CLAUDE.md, .cursorrules, etc.
4. **Your AI assistant reads them** - Claude Code, Cursor, Gemini automatically follow the rules

**Key benefits:**
- ✅ **Works with all AI tools** - Claude Code, Cursor, Gemini (uses standard config files)
- ✅ **Offline-friendly** - No API calls, works without internet after sync
- ✅ **Auto-detection** - Finds your language/framework automatically
- ✅ **Simple** - One bash script, no services to deploy
- ✅ **Git-based** - Version-controlled, auditable changes

## Complete Setup Guide

### Step 1: Create Central Rules Repository (One-Time Org Setup)

**Quick way - Use the generator:**
```bash
cd sync-strategy/
./create-central-repo.sh
# Follow prompts to create ai-rules-central/
```

**Manual way:**
```bash
gh repo create yourorg/ai-rules-central --private
cd ai-rules-central
mkdir -p base languages frameworks
```

Create **base/universal-rules.md** (applies to all projects):
```markdown
# Universal Organization Rules

## Security
- ❌ NEVER commit secrets, API keys, or credentials
- ✅ Use environment variables for configuration
- ✅ Run `gitleaks detect --no-git` before committing

## Code Quality
- Write tests FIRST (Test-Driven Development)
- Minimum code coverage: 80%
- Follow existing patterns in the codebase

## Git Workflow
- Use Conventional Commits: `feat:`, `fix:`, `docs:`
- Reference issue numbers: `feat: add logout (#123)`
- Always run tests before pushing
```

Create **languages/python.md**:
```markdown
# Python Development Rules

## Code Style
- **Black** for formatting (line length: 88)
- **Type hints** required for all functions
- **Ruff** for linting

## Testing
- **pytest** for all tests
- **pytest-cov** for coverage (minimum 80%)
- Fixtures in `tests/conftest.py`

## Security
- Pydantic models for all API inputs
- Parameterized queries only (prevent SQL injection)
```

Create **frameworks/react.md**:
```markdown
# React Development Rules

## Component Structure
- ✅ Functional components with hooks only
- ❌ No class components
- ✅ TypeScript required
- ✅ One component per file

## State Management
- Local state: `useState`
- Global state: Context API
- Server state: SWR or React Query

## Testing
- React Testing Library (test user behavior, not implementation)
- Minimum 80% coverage
```

See [sync-strategy/example-central-repo/](sync-strategy/example-central-repo/) for complete examples.

### Step 2: Add Sync Script to Your Projects

```bash
# In your project repository
curl -O https://raw.githubusercontent.com/yourorg/ai-rules-central/main/sync-ai-rules.sh
chmod +x sync-ai-rules.sh

# Optional: Configure sync behavior
mkdir -p .ai
cat > .ai/sync-config.json << 'EOF'
{
  "centralRepo": "git@github.com:yourorg/ai-rules-central.git",
  "rules": {
    "base": ["universal-rules"],
    "languages": "auto-detect",
    "frameworks": "auto-detect"
  },
  "outputFormats": ["CLAUDE.md", "AGENTS.md", ".cursorrules"]
}
EOF
```

### Step 3: Run Sync

```bash
./sync-ai-rules.sh

# Output:
# [sync-ai-rules] Starting AI rules synchronization...
# [sync-ai-rules] Detected languages: python
# [sync-ai-rules] Detected frameworks: fastapi
# [sync-ai-rules] Adding base rules...
# [sync-ai-rules] Adding python rules...
# [sync-ai-rules] Adding fastapi rules...
# [sync-ai-rules] Generating CLAUDE.md...
# [sync-ai-rules] Generating AGENTS.md...
# [sync-ai-rules] Generating .cursorrules...
# [sync-ai-rules] ✅ Sync complete!
```

**Generated CLAUDE.md:**
```markdown
# AI Development Rules
# Auto-generated - DO NOT EDIT MANUALLY
# Last synced: 2025-12-13 10:30 UTC
# Rules version: abc123
# Source: github.com/yourorg/ai-rules-central

## Universal Organization Rules
[... your universal rules ...]

## Python Development Rules
[... your Python rules ...]

## FastAPI Development Rules
[... your FastAPI rules ...]

---
To update: ./sync-ai-rules.sh
```

### Step 4: AI Assistants Automatically Follow Rules

- **Claude Code** reads `CLAUDE.md`
- **Cursor IDE** reads `.cursorrules`
- **Gemini/other tools** read `AGENTS.md`

No configuration needed - they just work!

## Language & Framework Detection

The sync script auto-detects your stack:

| Language | Detection Files |
|----------|----------------|
| **Python** | `pyproject.toml`, `requirements.txt`, `setup.py`, `*.py` |
| **TypeScript** | `tsconfig.json`, `package.json` with `@types/*` |
| **JavaScript** | `package.json` (without TypeScript) |
| **Go** | `go.mod`, `go.sum` |
| **Rust** | `Cargo.toml` |
| **Java** | `pom.xml`, `build.gradle` |
| **Ruby** | `Gemfile`, `*.gemspec` |

| Framework | Detection Files |
|-----------|----------------|
| **React** | `package.json` with `"react"` dependency |
| **Vue** | `package.json` with `"vue"` dependency |
| **Next.js** | `package.json` with `"next"` dependency |
| **Django** | `manage.py`, `"django"` in dependencies |
| **FastAPI** | `"fastapi"` in `pyproject.toml` or `requirements.txt` |
| **Flask** | `"flask"` in dependencies |
| **Express** | `package.json` with `"express"` dependency |

**Override auto-detection:**
```json
// .ai/sync-config.json
{
  "languages": ["python", "typescript"],
  "frameworks": ["react", "fastapi"],
  "excludeRules": ["frameworks/vue"]
}
```

## Keeping Rules Updated

### Option A: Manual Sync
```bash
./sync-ai-rules.sh  # Run when you need latest rules
```

### Option B: Pre-commit Hook (Recommended)
Auto-sync before every commit:
```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
./sync-ai-rules.sh --quiet
git add CLAUDE.md AGENTS.md .cursorrules 2>/dev/null || true
EOF
chmod +x .git/hooks/pre-commit
```

### Option C: CI/CD Check
Ensure rules are current in pull requests:
```yaml
# .github/workflows/check-rules.yml
name: Check AI Rules Current
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./sync-ai-rules.sh --check-only
      # Fails if local rules are outdated
```

## Central Repository Organization

Recommended structure for `ai-rules-central`:

```
ai-rules-central/
├── base/
│   ├── universal-rules.md       # All projects
│   ├── security-baseline.md     # Security standards
│   └── git-workflow.md          # Commit standards
├── languages/
│   ├── python.md
│   ├── typescript.md
│   ├── go.md
│   ├── rust.md
│   └── java.md
├── frameworks/
│   ├── react.md
│   ├── vue.md
│   ├── django.md
│   ├── fastapi.md
│   └── express.md
├── domains/                     # Optional: Industry-specific
│   ├── fintech.md
│   ├── healthcare.md
│   └── ecommerce.md
├── compliance/                  # Optional: Compliance frameworks
│   ├── pci-dss.md
│   ├── hipaa.md
│   └── soc2.md
└── sync-ai-rules.sh
```

## Troubleshooting

**Rules not updating?**
```bash
# Force refresh (deletes cache)
./sync-ai-rules.sh --force

# Check current version
cat .ai/.rules-version
```

**Wrong language/framework detected?**
```bash
# Override in config
cat > .ai/sync-config.json << 'EOF'
{
  "languages": ["python"],
  "frameworks": ["django"],
  "excludeRules": ["frameworks/react"]
}
EOF
./sync-ai-rules.sh
```

**Want project-specific customizations?**
```bash
# Generate base rules, then append custom rules
./sync-ai-rules.sh

cat >> CLAUDE.md << 'EOF'

## Project-Specific Rules

- Use our custom logging: `from myapp.logger import log`
- Database migrations: `alembic revision --autogenerate`
- API base URL: `https://api.example.com/v1`
EOF
```

**Sync script not found?**
```bash
# Download from central repo
curl -O https://raw.githubusercontent.com/yourorg/ai-rules-central/main/sync-ai-rules.sh
chmod +x sync-ai-rules.sh
```

## Advanced Features

### Multi-Environment Rule Sets

Different rules for production vs prototyping:

```json
// .ai/sync-config.json
{
  "centralRepo": "git@github.com:yourorg/ai-rules-central.git",
  "ruleSet": "production-critical",  // or "prototyping"
  "rules": {
    "base": ["universal-rules", "production-baseline"],
    "languages": "auto-detect"
  }
}
```

```
ai-rules-central/
├── rulesets/
│   ├── production-critical/
│   │   └── extra-validation.md    # Strict rules
│   └── prototyping/
│       └── relaxed-standards.md   # Faster iteration
```

### Custom Rule Categories

```json
{
  "customRules": [
    "compliance/hipaa",      // Healthcare compliance
    "domains/fintech",       // Financial services rules
    "internal/api-gateway"   // Internal tool rules
  ]
}
```

## Alternative: Gateway Strategy (Advanced)

For organizations needing **policy enforcement**, **input/output filtering**, or **usage logging**, see [gateway-strategy/](gateway-strategy/) for an API gateway approach.

**When to use Gateway instead:**
- ❌ Block secrets from being sent to AI providers
- ❌ Scan AI outputs for banned APIs or license violations
- ❌ Enforce policy-as-code (OPA, Cedar) before operations
- ❌ Centralized audit logging for compliance (SOC 2, HIPAA)
- ❌ Usage metrics aggregation across teams

**Trade-offs:**
- ✅ Enforceable guardrails (not just suggestions)
- ❌ Complex infrastructure (Node.js API service)
- ❌ Doesn't work with Claude Code, Cursor (requires custom CLI)
- ❌ Network dependency (API must be available)

**For most organizations**: Start with sync strategy (this approach). Add gateway later for specific high-security projects if needed.

## Quick Comparison

| Feature | Sync Strategy ⭐ | Gateway Strategy |
|---------|-----------------|------------------|
| **Setup Time** | 5 minutes | 1-2 hours |
| **Infrastructure** | None (Git only) | Node.js API service |
| **AI Tool Support** | All (Claude, Cursor, Gemini) | Custom CLI only |
| **Offline Support** | ✅ Yes | ❌ No |
| **Language Detection** | ✅ Automatic | ❌ Manual |
| **Policy Enforcement** | ❌ Suggestions only | ✅ Enforceable |
| **Input/Output Filtering** | ❌ No | ✅ Yes |
| **Usage Logging** | ❌ No | ✅ Yes |
| **Best For** | Most teams | Enterprises, regulated industries |

## Examples & Templates

- **[sync-ai-rules.sh](sync-strategy/sync-ai-rules.sh)** - Main sync script
- **[create-central-repo.sh](sync-strategy/create-central-repo.sh)** - Quick-start generator
- **[example-central-repo/](sync-strategy/example-central-repo/)** - Sample organization rules
  - [Universal rules](sync-strategy/example-central-repo/base/universal-rules.md)
  - [Python rules](sync-strategy/example-central-repo/languages/python.md)
  - [React rules](sync-strategy/example-central-repo/frameworks/react.md)

## Next Steps

1. **Create central repository**: Run `./sync-strategy/create-central-repo.sh`
2. **Customize rules**: Edit markdown files in `ai-rules-central/`
3. **Push to GitHub**: `gh repo create yourorg/ai-rules-central --private --source=. --push`
4. **Sync to projects**: Add sync script to each project repository
5. **Automate**: Add pre-commit hook or CI check

## Questions?

**Which strategy should I use?**
- Start with Sync Strategy unless you specifically need policy enforcement or input/output filtering
- You can always add Gateway later for specific high-security repos

**Does this work with my AI tool?**
- ✅ Claude Code (reads `CLAUDE.md`)
- ✅ Cursor IDE (reads `.cursorrules`)
- ✅ Gemini CLI (reads `AGENTS.md`)
- ✅ Any tool reading standard config files

**How often should I sync?**
- Use pre-commit hook for automatic updates
- Or manually sync when you need latest rule changes

**Can I have project-specific rules?**
- Yes! Generate base rules with sync, then append custom rules to the generated files
- Or override languages/frameworks in `.ai/sync-config.json`

**How do I update organization rules?**
- Edit markdown files in `ai-rules-central` repository
- Create PR, get approval, merge
- Projects sync automatically (if using pre-commit hook) or manually
