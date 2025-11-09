# Rules as Code Example

Comprehensive rules framework for enforcing development standards, quality gates, and delivery practices through machine-readable rule files.

## Overview

This example demonstrates the **Rules as Code** pattern through three rule files that establish mandatory guardrails for AI-assisted development:

1. **DEVELOPMENT_RULES.md** - Test-first specification-driven development
2. **QUALITY_RULES.md** - Code quality standards and observability
3. **PIPELINE_RULES.md** - CI/CD pipeline and deployment requirements

## Quick Start

### 1. Review the Rule Files

```bash
# Read the three core rule files
cat DEVELOPMENT_RULES.md  # Test-first, specifications, traceability
cat QUALITY_RULES.md      # Code standards, SOLID principles, logging
cat PIPELINE_RULES.md     # CI/CD, deployment safety, monitoring
```

### 2. Integrate with CLAUDE.md

Copy `CLAUDE.md` to your project root to enforce rules automatically:

```bash
# For new projects
cp CLAUDE.md /path/to/your/project/.claude/CLAUDE.md

# Claude Code will automatically enforce these rules
```

### 3. Reference in AI Interactions

When working with AI coding assistants:

```bash
# Explicitly reference rules
"Please implement this feature following @DEVELOPMENT_RULES.md"
"Review this code against @QUALITY_RULES.md standards"
"Validate deployment readiness per @PIPELINE_RULES.md"
```

## Rule File Descriptions

### DEVELOPMENT_RULES.md

**Purpose**: Enforce test-first, specification-driven development

**Key Rules**:
- ✅ Write specifications before code (SPEC-XXX format)
- ✅ Write tests before implementation (TEST-XXX format)
- ✅ Maintain complete traceability (Spec → Test → Code)
- ✅ Size tasks appropriately (1-3 hours ideal, max 8 hours)
- ✅ Run all tests locally before committing

**Enforcement**:
```bash
# Before starting any feature
./check_specifications.sh  # Verify specs exist
pytest tests/ --cov=src    # Run test suite
./check_traceability.sh    # Verify spec-test-code links
```

### QUALITY_RULES.md

**Purpose**: Enforce code quality, clean architecture, and observability

**Key Rules**:
- ✅ Method length < 20 lines, complexity < 10
- ✅ Class size < 250 lines, < 20 methods
- ✅ SOLID principles enforced
- ✅ Structured JSON logging with correlation IDs
- ✅ Comprehensive error handling with remediation

**Enforcement**:
```bash
# Code quality checks
radon cc src/ -a         # Cyclomatic complexity
radon mi src/ -s         # Maintainability index
pylint src/ --max-line-length=100
```

### PIPELINE_RULES.md

**Purpose**: Enforce CI/CD safety, deployment practices, monitoring

**Key Rules**:
- ✅ Branch age < 2 days
- ✅ Build time < 10 minutes
- ✅ Feature flags for gradual rollout
- ✅ Operational Readiness Review (ORR) before deploy
- ✅ Infrastructure specs before IaC

**Enforcement**:
```bash
# Before deployment
./run_orr_checklist.sh        # Complete ORR
./validate_deployment.sh      # Pre-deploy checks
./check_feature_flags.sh      # Verify flags configured
```

## How This Example Works

### CLAUDE.md Integration

The `CLAUDE.md` file serves as the enforcement mechanism:

```markdown
## 🚨 MANDATORY RULE ENFORCEMENT

**CRITICAL: Before ANY code change, review and enforce ALL three rule files:**

### 1. DEVELOPMENT_RULES.md - Test-First Specification-Driven Development
- **NEVER** write implementation before tests
- **ALWAYS** create specifications with unique IDs (SPEC-XXX)
...

### 2. QUALITY_RULES.md - Code Quality & Standards
- **REJECT** methods > 20 lines, classes > 250 lines
- **ENFORCE** SOLID principles and clean architecture
...

### 3. PIPELINE_RULES.md - CI/CD Pipeline & Deployment
- **ENFORCE** branch age < 2 days
- **REQUIRE** build time < 10 minutes
...

**If ANY rule violation is detected, STOP and report the issue immediately.**
```

When placed in `.claude/CLAUDE.md`, Claude Code automatically:
1. Reads these rules before every interaction
2. Validates proposed changes against all three rule files
3. Rejects or warns about rule violations
4. Suggests corrections to align with rules

## Example Workflow

### 1. Feature Development

```bash
# Step 1: Create specification (DEVELOPMENT_RULES.md)
cat > specs/feature-123.md << 'EOF'
Feature ID: FEAT-123
Acceptance Criteria:
- AC-001: User can view subscription list
- AC-002: System sends reminders 7 days in advance
EOF

# Step 2: Write tests first (DEVELOPMENT_RULES.md)
cat > tests/test_feature_123.py << 'EOF'
def test_subscription_list():
    """Implements: specs/feature-123.md#AC-001"""
    assert subscription_service.get_list() is not None
EOF

# Step 3: Implement (QUALITY_RULES.md)
# - Keep methods < 20 lines
# - Follow SOLID principles
# - Add structured logging

# Step 4: Validate locally (PIPELINE_RULES.md)
pytest tests/ --cov=src --cov-fail-under=90
./check_traceability.sh
pre-commit run --all-files

# Step 5: Deploy safely (PIPELINE_RULES.md)
./run_orr_checklist.sh
./validate_deployment.sh
```

### 2. Code Review

AI assistant validates against all rules:

```bash
# AI checks DEVELOPMENT_RULES.md
- ✅ Specification exists (FEAT-123)
- ✅ Tests written first
- ✅ Traceability maintained

# AI checks QUALITY_RULES.md
- ✅ Methods < 20 lines
- ✅ Structured logging present
- ✅ Error handling included

# AI checks PIPELINE_RULES.md
- ✅ Branch < 2 days old
- ✅ All tests passing
- ✅ ORR complete
```

## Rule Customization

### Adapt to Your Project

1. **Copy rule files to your project**:
   ```bash
   cp DEVELOPMENT_RULES.md /your/project/docs/
   cp QUALITY_RULES.md /your/project/docs/
   cp PIPELINE_RULES.md /your/project/docs/
   ```

2. **Modify thresholds** to match your standards:
   ```markdown
   # QUALITY_RULES.md - Adjust for your team
   - Method length < 30 lines  # (was 20)
   - Code coverage > 80%       # (was 90%)
   ```

3. **Add project-specific rules**:
   ```markdown
   # DEVELOPMENT_RULES.md - Add custom requirements
   - API endpoints must have OpenAPI specs
   - Database migrations require rollback scripts
   ```

4. **Update CLAUDE.md** to reference your customized rules

## Enforcement Tools

### Automated Validation

```bash
#!/bin/bash
# check_rules.sh - Validate all rules

echo "Checking DEVELOPMENT_RULES.md..."
./check_specifications.sh
./check_traceability.sh

echo "Checking QUALITY_RULES.md..."
radon cc src/ -a -nb
pylint src/ --max-line-length=100

echo "Checking PIPELINE_RULES.md..."
./check_branch_age.sh
./validate_build_time.sh
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Enforce DEVELOPMENT_RULES.md
pytest tests/ --cov=src --cov-fail-under=90 || exit 1

# Enforce QUALITY_RULES.md
radon cc src/ -a -nb || exit 1

# Enforce PIPELINE_RULES.md
./check_branch_age.sh || exit 1

echo "✅ All rules validated"
```

## Benefits

### For AI Assistants
- Clear, unambiguous rules to follow
- Consistent code generation
- Automatic validation of suggestions
- Reduced back-and-forth on standards

### For Development Teams
- Codified best practices
- Consistent code quality
- Automated enforcement
- Reduced code review time
- Easier onboarding

### For Projects
- Maintainable codebase
- Predictable quality
- Safer deployments
- Better observability

## Integration with Main Patterns

This example demonstrates:
- **[Rules as Code](../../README.md#rules-as-code)** - Machine-readable development standards
- **[Specification Driven Development](../../README.md#specification-driven-development)** - Test-first with traceability
- **[Observable AI Development](../../README.md#observable-ai-development)** - Structured logging requirements
- **[AI-Driven Traceability](../../README.md#ai-driven-traceability)** - Spec-test-code linking

## Related Patterns

- [Progressive AI Enhancement](../../README.md#progressive-ai-enhancement) - Gradual feature rollout
- [AI Security Sandbox](../../README.md#ai-security-sandbox) - Security validation rules
- [AI Developer Lifecycle](../../README.md#ai-developer-lifecycle) - Complete workflow integration

## Contributing

To improve these rules:

1. Test changes in real projects
2. Document rule violations and their impact
3. Propose refinements based on experience
4. Submit improvements to the pattern repository
