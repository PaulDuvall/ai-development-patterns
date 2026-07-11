# Codified Rules Example

Example rule documents for expressing development standards, quality gates, and delivery practices
as version-controlled guidance.

## Overview

This example demonstrates the **Codified Rules** pattern through three rule files that describe
guardrails for AI-assisted development:

1. **DEVELOPMENT_RULES.md** - Test-first specification-driven development
2. **QUALITY_RULES.md** - Code quality standards and observability
3. **PIPELINE_RULES.md** - CI/CD pipeline and deployment requirements

This example ships markdown files only: the three rule files plus a sample `CLAUDE.md`. The `.sh` enforcement scripts named throughout this README (for example, `check_traceability.sh` and `run_orr_checklist.sh`) are illustrative names for scripts your team would implement to automate rule checks — they are not included here.

## Quick Start

### 1. Review the Rule Files

```bash
# Read the three core rule files
cat DEVELOPMENT_RULES.md  # Test-first, specifications, traceability
cat QUALITY_RULES.md      # Code standards, SOLID principles, logging
cat PIPELINE_RULES.md     # CI/CD, deployment safety, monitoring
```

### 2. Integrate with CLAUDE.md

Copy the sample summary and all three rule documents into the target project:

```bash
# For a new project
cp CLAUDE.md *_RULES.md /path/to/your/project/
```

The assistant can load `CLAUDE.md` as guidance and follow explicit `@..._RULES.md` references. It
does not execute checks or guarantee compliance. Binding enforcement requires real hooks, scripts,
and required CI checks, which this example does not ship.

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

**Purpose**: Describe test-first, specification-driven development expectations

**Key Rules**:
- ✅ Write specifications before code (SPEC-XXX format)
- ✅ Write tests before implementation (TEST-XXX format)
- ✅ Maintain complete traceability (Spec → Test → Code)
- ✅ Size tasks appropriately (1-3 hours ideal, max 8 hours)
- ✅ Run all tests locally before committing

**Enforcement** (example scripts a team would implement for this rule file):
```bash
# Before starting any feature
./check_specifications.sh  # Would verify specs exist
pytest tests/ --cov=src    # Run test suite
./check_traceability.sh    # Would verify spec-test-code links
```

### QUALITY_RULES.md

**Purpose**: Describe code quality, clean architecture, and observability expectations

**Key Rules**:
- ✅ Method length < 20 lines, complexity < 10
- ✅ Class size < 250 lines, < 20 methods
- ✅ SOLID principles required by the guidance
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

**Purpose**: Describe CI/CD safety, deployment practices, and monitoring expectations

**Key Rules**:
- ✅ Branch age < 2 days
- ✅ Build time < 10 minutes
- ✅ Feature flags for gradual rollout
- ✅ Operational Readiness Review (ORR) before deploy
- ✅ Infrastructure specs before IaC

**Enforcement** (example scripts a team would implement for this rule file):
```bash
# Before deployment
./run_orr_checklist.sh        # Would walk through the ORR checklist
./validate_deployment.sh      # Would run pre-deploy checks
./check_feature_flags.sh      # Would verify flags are configured
```

## How This Example Works

### CLAUDE.md Integration

The `CLAUDE.md` file provides a concise assistant-facing summary:

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

When placed at the target project root, an assistant can use this summary as guidance, while the
three copied rule files remain available for explicit review. Instruction following is
probabilistic: deterministic tools must validate measurable requirements and required CI/human
policy must decide whether a change is acceptable.

## Example Workflow

### 1. Feature Development

The workflow below mixes standard tools (`pytest`, `pre-commit`) with team-implemented enforcement scripts; the `.sh` names illustrate checks your team would automate.

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
./check_traceability.sh    # Team-implemented: verify spec-test-code links
pre-commit run --all-files

# Step 5: Deploy safely (PIPELINE_RULES.md)
./run_orr_checklist.sh     # Team-implemented: walk through ORR checklist
./validate_deployment.sh   # Team-implemented: pre-deploy checks
```

### 2. Code Review

Use the rule files to build a review checklist. The unchecked items below are illustrative criteria,
not observed output; deterministic tools or human reviewers must supply the result:

```markdown
Development
- [ ] Specification exists and has a stable identifier
- [ ] Tests and traceability links are present

Quality
- [ ] Complexity thresholds pass in the configured analyzer
- [ ] Logging and error handling meet project policy

Pipeline
- [ ] Required tests and readiness checks pass
- [ ] A human-owned deployment policy authorizes release
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

A wrapper script your team could implement to validate all three rule files (the helper scripts it calls are likewise team-implemented):

```bash
#!/bin/bash
# check_rules.sh - Validate all rules

echo "Checking DEVELOPMENT_RULES.md..."
./check_specifications.sh   # Team-implemented: verify specs exist
./check_traceability.sh     # Team-implemented: verify spec-test-code links

echo "Checking QUALITY_RULES.md..."
radon cc src/ -a -nb
pylint src/ --max-line-length=100

echo "Checking PIPELINE_RULES.md..."
./check_branch_age.sh       # Team-implemented: enforce branch age < 2 days
./validate_build_time.sh    # Team-implemented: enforce build time < 10 minutes
```

### Pre-commit Hook

An example hook wiring the same checks into git (`check_branch_age.sh` is a script your team would implement):

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
- Explicit criteria for reviewing suggestions
- Reduced back-and-forth on standards

### For Development Teams
- Codified best practices
- Consistent code quality
- A source for team-implemented automated checks
- Reduced code review time
- Easier onboarding

### For Projects
- Maintainable codebase
- Predictable quality
- Safer deployments
- Better observability

## Integration with Main Patterns

This example demonstrates:
- **[Codified Rules](../../README.md#codified-rules)** - Version-controlled development standards
- **[Spec-Driven Development](../../README.md#spec-driven-development)** - Test-first with traceability
- **[Agent Observability](../../README.md#agent-observability)** - Structured tracing and diagnostic requirements

## Related Patterns

- [Incremental Generation](../../README.md#incremental-generation) - Gradual feature rollout
- [Security Sandbox](../../README.md#security-sandbox) - Security validation rules
- [Developer Lifecycle](../../README.md#developer-lifecycle) - Complete workflow integration

## Contributing

To improve these rules:

1. Test changes in real projects
2. Document rule violations and their impact
3. Propose refinements based on experience
4. Submit improvements to the pattern repository
