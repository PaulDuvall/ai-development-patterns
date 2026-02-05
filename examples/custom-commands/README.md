# Custom Commands Example

Complete implementation of the Custom Commands pattern with ready-to-use command examples.

## Quick Start

### 1. Install Commands (Claude Code)

```bash
# Copy commands to your project
mkdir -p .claude/commands
cp commands/*.md .claude/commands/

# Optional: Copy configuration
cp claude-settings.json .claude/settings.json
```

### 2. Use Commands

```bash
# Refactoring assistant
/refactor              # Full analysis
/refactor --smell      # Code smells only

# Implement specification
/implement-spec AUTH-001

# Security review
/security-review       # Review recent changes

# Safe refactoring
/safe-refactor

# Run tests
/test backend --coverage
```

## Command Catalog

| Command | Purpose | Example Usage |
|---------|---------|---------------|
| **refactor** | Interactive refactoring assistant based on Martin Fowler's catalog | `/refactor --duplicates` |
| **implement-spec** | Implement specifications with full traceability | `/implement-spec AUTH-001` |
| **security-review** | Multi-layer security analysis of code changes | `/security-review --secrets` |
| **safe-refactor** | Safe refactoring with automated testing and rollback | `/safe-refactor --auto` |
| **test** | Smart test runner with filtering and reporting | `/test backend --watch` |

## Command Details

### Refactor Command

**File**: `commands/refactor.md`

Systematic code improvement based on Martin Fowler's refactoring catalog.

**Features**:
- Code smell detection (long methods, duplicate code, complex conditionals)
- Bloater identification (excessive parameters, data clumps)
- Refactoring strategy generation
- Before/after examples with effort estimates

**Usage**:
```bash
/refactor              # Full comprehensive analysis
/refactor --smell      # Focus on code smell detection
/refactor --duplicates # Find duplicate code patterns
```

### Implement-Spec Command

**File**: `commands/implement-spec.md`

Specification-driven implementation with test-driven development and traceability.

**Features**:
- Reads specification from `@specs/[ID].md`
- Generates failing tests for each acceptance criterion
- Implements minimal code to satisfy requirements
- Adds traceability comments linking code to specifications
- Generates traceability matrix report

**Usage**:
```bash
/implement-spec AUTH-001      # Implement authentication spec
/implement-spec PAYMENT-042   # Implement payment spec
```

**Prerequisites**: Specification files in `specs/` directory following structured format with acceptance criteria.

### Security-Review Command

**File**: `commands/security-review.md`

Comprehensive security analysis beyond simple scanning.

**Features**:
- Secret detection (API keys, tokens, credentials)
- Dependency vulnerability analysis
- Authentication/authorization review
- Configuration security (HTTPS, CORS, security headers)
- Code security patterns (injection, XSS, cryptography)

**Usage**:
```bash
/security-review         # Review recent changes
/security-review --full  # Full codebase scan
/security-review --secrets  # Focus on secret detection
```

**Optional Tools**: `gitleaks`, `npm audit`, `bandit`, `gosec` for enhanced scanning.

### Safe-Refactor Command

**File**: `commands/safe-refactor.md`

Safe refactoring with automated review, testing, and rollback capabilities.

**Features**:
- Pre-refactoring analysis with `/review`
- Automatic safety branch creation
- Full test suite execution
- Performance comparison before/after
- Comprehensive refactoring report
- Pull request generation with summary

**Usage**:
```bash
/safe-refactor           # Interactive refactoring with safety checks
/safe-refactor --auto    # Automatic refactoring with approval gates
```

### Test Command

**File**: `commands/test.md`

Smart test runner with filtering, coverage, and health monitoring.

**Features**:
- Smart test selection based on recent changes
- Support for multiple test targets (backend, frontend, integration)
- Coverage reporting
- Test suite health tracking
- Flaky test detection

**Usage**:
```bash
/test                        # Run all tests
/test backend                # Run backend tests
/test frontend --watch       # Watch mode
/test integration --coverage # With coverage report
```

## Tool Compatibility

### Claude Code

Full support with `.claude/commands/` directory.

**Setup**:
```bash
mkdir -p .claude/commands
cp commands/*.md .claude/commands/
```

**Configuration** (optional):
```json
{
  "commandDirectories": [
    ".claude/commands",
    ".ai/commands"
  ]
}
```

### Cursor IDE

Adapt commands to `.cursorrules` format:

```bash
# Copy command content to .cursorrules
cat commands/refactor.md >> .cursorrules
```

### Gemini CLI

Custom commands supported in IDE mode. CLI enhancement planned.

## Customization

### Modify Commands

Edit command files to match your project:

```bash
# Edit refactoring thresholds
vim commands/refactor.md
# Change: - Long methods (>20 lines)
# To:     - Long methods (>30 lines)

# Add project-specific patterns
vim commands/security-review.md
# Add custom secret patterns
# Add internal security policies
```

### Add New Commands

Create new command files following the pattern:

```markdown
# [Command Name]

Brief description of command purpose.

## Usage

bash
/command-name [arguments]


## Implementation

Step-by-step instructions for AI to execute.

### 1. [Step Name]
Detailed instructions...

### 2. [Next Step]
More instructions...

## Output Format

Expected output structure.
```

### Project-Specific Integration

Adapt commands to your tech stack:

**Node.js Project**:
```markdown
# test.md modification
Run tests: npm test -- $ARGUMENTS
Coverage: npm test -- --coverage
```

**Python Project**:
```markdown
# test.md modification
Run tests: pytest tests/$ARGUMENTS -v
Coverage: pytest tests/$ARGUMENTS --cov=src --cov-report=html
```

## Examples

### Example 1: Refactoring Workflow

```bash
# 1. Analyze code for smells
/refactor --smell

# 2. Perform safe refactoring
/safe-refactor

# 3. Run tests to verify
/test --coverage

# 4. Security review
/security-review
```

### Example 2: Specification Implementation

```bash
# 1. Implement specification
/implement-spec USER-REGISTRATION-001

# 2. Verify implementation
/test integration --verbose

# 3. Security check
/security-review --full
```

### Example 3: Continuous Improvement

```bash
# Daily code quality check
/refactor
/security-review
/test --coverage

# Review recommendations and address high-priority issues
```

## Best Practices

### Command Design

- **Encode expertise**: Commands should capture domain knowledge, not just wrap shell commands
- **Parameterize**: Use `$ARGUMENTS`, `$1`, `$2` for flexibility
- **Structured output**: Provide consistent, actionable output formats
- **Error handling**: Include failure scenarios and remediation steps

### Command Usage

- **Discover first**: Check built-in commands before creating custom ones (`/help`)
- **Start simple**: Begin with basic commands, add complexity as needed
- **Test thoroughly**: Verify commands work as expected before team rollout
- **Document**: Maintain command catalog with usage examples

### Project Integration

- **Version control**: Commit command files to repository for team sharing
- **Team alignment**: Review and approve commands as a team
- **Regular review**: Update commands as project standards evolve
- **Tool-agnostic**: Use generic `.ai/commands/` for cross-tool compatibility

## Troubleshooting

### Command Not Found

**Issue**: `/command-name` shows "command not found"

**Solution**:
1. Verify file exists in `.claude/commands/` directory
2. Ensure file has `.md` extension
3. Check file permissions (should be readable)
4. Restart Claude Code if needed

### Command Doesn't Work as Expected

**Issue**: Command executes but produces incorrect results

**Solution**:
1. Review command markdown structure (sections, formatting)
2. Test with simpler arguments first
3. Check AI instructions are clear and actionable
4. Add more specific examples in command file

### Parameter Substitution Not Working

**Issue**: `$ARGUMENTS` or `$1` not being replaced

**Solution**:
1. Verify parameter syntax (use `$ARGUMENTS`, `$1`, `$2`)
2. Test with explicit arguments first
3. Check command file format (markdown code blocks)

## Contributing

To improve these commands:

1. Test commands in your project
2. Document issues or enhancement ideas
3. Submit improvements back to the pattern repository

## Additional Resources

- [Custom Commands Pattern](../../README.md#custom-commands) - Full pattern documentation
- [Claude Code Slash Commands](https://docs.claude.com/en/docs/claude-code/slash-commands) - Official documentation
- [Martin Fowler's Refactoring Catalog](https://refactoring.com/catalog/) - Refactoring reference
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Security guidelines
