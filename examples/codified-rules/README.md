# Codified Rules Example

Example rule documents for expressing development standards, quality gates, and delivery practices
as version-controlled guidance.

## Overview

This example demonstrates the **Codified Rules** pattern through three rule files that describe
guardrails for AI-assisted development:

1. **DEVELOPMENT_RULES.md** - Test-first specification-driven development
2. **QUALITY_RULES.md** - Code quality standards and observability
3. **PIPELINE_RULES.md** - CI/CD pipeline and deployment requirements

The example is runnable with Bash and Python 3 using only the Python standard library. It includes
three executable enforcement wrappers, a bounded validator that never executes candidate project
code, and `sample-project/` with specifications, traced tests and implementation, plus an ORR
checklist. The scripts validate deterministic structure and evidence; they do not replace code
review or authorize deployment.

## Quick Start

### 1. Review the Rule Files

```bash
# Read the three core rule files
cat DEVELOPMENT_RULES.md  # Test-first, specifications, traceability
cat QUALITY_RULES.md      # Code standards, SOLID principles, logging
cat PIPELINE_RULES.md     # CI/CD, deployment safety, monitoring
```

### 2. Run the Checked-In Enforcement

The default target is the checked-in sample project. Each command exits nonzero when its evidence
is missing, ambiguous, duplicated, oversized, non-UTF-8, or hidden behind a symbolic link:

```bash
./check_specifications.sh
./check_traceability.sh
./run_orr_checklist.sh
python3 -m unittest discover \
  -s sample-project/tests \
  -t sample-project
```

The ORR command validates checklist completeness and evidence fields. Its success is not human
release approval.

### 3. Integrate with CLAUDE.md

Copy the sample summary and all three rule documents into the target project:

```bash
# Demonstrate the complete copy without modifying an existing project
target_project="$(mktemp -d)"
cp CLAUDE.md *_RULES.md check_specifications.sh check_traceability.sh \
  run_orr_checklist.sh "$target_project/"
cp -R scripts sample-project "$target_project/"
printf 'Copied runnable example to %s\n' "$target_project"
```

The assistant can load `CLAUDE.md` as guidance and follow explicit `@..._RULES.md` references. It
does not execute checks or guarantee compliance. The checked-in scripts provide deterministic
local checks; projects should make the same commands required CI checks and retain human ownership
of policy decisions.

### 4. Reference in AI Interactions

When working with AI coding assistants:

```text
Please implement this feature following @DEVELOPMENT_RULES.md.
Review this code against @QUALITY_RULES.md standards.
Validate deployment readiness per @PIPELINE_RULES.md.
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

**Enforcement**:
```bash
# Validate the checked-in sample or pass another project root as argument 1
./check_specifications.sh
./check_traceability.sh
python3 -m unittest discover -s sample-project/tests -t sample-project
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
# Exercise the sample implementation with no third-party dependency
python3 -m unittest discover -s sample-project/tests -t sample-project
```

The rule document's complexity and lint thresholds require a project-selected analyzer. These
three validators deliberately do not pretend that Markdown policy alone measured source quality.

### PIPELINE_RULES.md

**Purpose**: Describe CI/CD safety, deployment practices, and monitoring expectations

**Key Rules**:
- ✅ Branch age < 2 days
- ✅ Build time < 10 minutes
- ✅ Feature flags for gradual rollout
- ✅ Operational Readiness Review (ORR) before deploy
- ✅ Infrastructure specs before IaC

**Enforcement**:
```bash
# Validate required checklist items and non-placeholder evidence
./run_orr_checklist.sh
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

The checked-in sample carries one specification through traced tests, implementation, and readiness
evidence. Run the complete workflow from this directory:

```bash
# Step 1: Validate specifications and rule-document integration
./check_specifications.sh sample-project

# Step 2: Require every acceptance criterion in both tests and source
./check_traceability.sh sample-project

# Step 3: Execute the traced implementation tests
python3 -m unittest discover -s sample-project/tests -t sample-project

# Step 4: Validate ORR structure and evidence fields (not release authorization)
./run_orr_checklist.sh sample-project/ORR_CHECKLIST.md
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
   target_rules="$(mktemp -d)"
   cp DEVELOPMENT_RULES.md QUALITY_RULES.md PIPELINE_RULES.md "$target_rules/"
   printf 'Copied customizable rules to %s\n' "$target_rules"
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

The three checked-in wrappers are intentionally narrow and compose cleanly in CI:

```bash
./check_specifications.sh sample-project
./check_traceability.sh sample-project
./run_orr_checklist.sh sample-project/ORR_CHECKLIST.md
```

`check_specifications.sh` and `check_traceability.sh` accept a project root. The ORR wrapper accepts
a checklist path. Set `PYTHON_BIN` when `python3` is not the desired interpreter. There are no
third-party runtime dependencies.

### CI and Hook Integration

Run the first two commands on every change and require them in CI. Run the ORR check before a
release, then route its structural result to the human-owned release policy. A hook can invoke the
same checked-in commands; it must not silently weaken their failures.

```bash
./check_specifications.sh sample-project
./check_traceability.sh sample-project
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
- Checked-in deterministic enforcement primitives
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
