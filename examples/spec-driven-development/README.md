# Spec-Driven Development - Executable Example

This directory contains a bounded executable implementation of the **Spec-Driven Development** pattern, demonstrating machine-readable specifications, collected-test traceability, and an enforced implementation coverage gate.

## Prerequisites

- Python 3.10 or newer
- Git, if you want to install the optional pre-commit and commit-message hooks

## Pattern Overview

SpecDriven AI combines three key elements:
- **Machine-readable specifications** with unique identifiers and authority levels
- **Rigorous Test-Driven Development** with coverage tracking and automated validation
- **AI-powered implementation** with persistent context through structured specifications

For complete pattern documentation, see: [Spec-Driven Development](../../README.md#spec-driven-development)

## Files in This Directory

### Core Implementation
- **`iam_policy_generator.py`** - Complete IAM Policy Generator implementation
- **`spec_validator.py`** - Validates collected pytest nodes and their requirement bindings
- **`iam_policy_spec.md`** - Machine-readable specification with seven normative requirements
- **`traceability.yaml`** - Explicit specification, implementation, and quality-gate scope
- **`.pre-commit-config.yaml`** - Pre-commit hooks for specification validation

### Specification Examples
- **`user_authentication.feature`** - Gherkin scenarios for authentication workflows
- **`user_authentication_structured.md`** - Structured specification with authority levels and anchored sections
- **`api_openapi.yaml`** - OpenAPI specification for authentication API endpoints
- **`cli_spec.md`** - Command-line interface specification with detailed usage examples

### Testing Infrastructure
- **`tests/`** - Complete test suite with specification traceability
- **`requirements.txt`** - Reproducibly pinned dependencies for testing and validation
- **`pytest.ini`** - Pytest configuration enforcing at least 85% implementation coverage

### Traceability Automation
- **`maintain_traceability.sh`** - Read-only wrapper around the deterministic validator, tests, and managed pre-commit flow
- **`test_requirement_coverage.py`** - Tests that validate requirement-to-test coverage tracking

## Key Features

### Authority Level System
Specifications use authority levels to make precedence explicit when humans resolve conflicts:
- **`authority=system`**: Core business logic and security requirements (highest precedence)
- **`authority=platform`**: Infrastructure and technical architecture decisions  
- **`authority=feature`**: User interface and experience requirements (lowest precedence)

### Automated Coverage Tracking
```bash
# Run specification compliance validation
python spec_validator.py --check-coverage --authority-conflicts

# Output shows specification coverage
Total specifications: 4
Total test references: 21
Validated test references: 21
Invalid test references: 0
Unlinked requirements: 0
Collection failures: 0
Coverage: 100.0%
```

### Traceability System
Each specification requirement links to an actually collected pytest node. The cited node must
declare the same `REQ-NNN` identifier in its docstring:
```markdown
- **REQ-003**: The generator MUST reject malformed ARNs with an actionable error. [^test_arn_validation]

[^test_arn_validation]: tests/test_validation.py::TestInputValidation::test_arn_format_validation
```

## Usage Examples

### 1. Running the IAM Policy Generator

```bash
# Create an isolated Python 3.10+ environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --requirement requirements.txt

# Run the IAM Policy Generator
python iam_policy_generator.py --policy-type s3-read --resource 'arn:aws:s3:::my-bucket/*' --no-validation-info

# Expected output: Valid IAM policy JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::my-bucket"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

For a wildcard below a prefix, the generated `ListBucket` statement includes an `s3:prefix`
condition with the same scope. For one exact object, the generator omits `ListBucket` entirely.
Bucket names are checked against the relevant
[general-purpose S3 bucket naming rules](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html),
including reserved prefixes and suffixes.

### 2. Working with Specification Examples

These optional examples require separately installed Cucumber and Swagger Codegen tools; they are
not part of the embedded quality gate.

```bash
# Validate Gherkin scenarios
cucumber user_authentication.feature --dry-run

# Validate OpenAPI specification
swagger-codegen validate -i api_openapi.yaml

# Generate API client from OpenAPI spec
swagger-codegen generate -i api_openapi.yaml -l python -o ./generated-client/

# Validate a different structured specification
python spec_validator.py --validate-syntax user_authentication_structured.md
```

### 3. Specification Validation

```bash
# Check specification coverage
python spec_validator.py --check-coverage

# Check for authority conflicts
python spec_validator.py --authority-conflicts

# Validate specification syntax
python spec_validator.py --validate-syntax iam_policy_spec.md
```

The deterministic maintenance wrapper exposes the same supported flow without writing hook files
itself or invoking a model:

```bash
./maintain_traceability.sh --validate
./maintain_traceability.sh --test
./maintain_traceability.sh --all
```

Use `./maintain_traceability.sh --install-hooks` only when you explicitly want `pre-commit` to
install its managed pre-commit and commit-message hooks.

### 4. Running the Complete Embedded Suite

```bash
# Run behavior, collected-node traceability, and the enforced 85% coverage gate
python -m pytest
```

The command fails if tests fail, a citation does not resolve to a collected test under `tests/`, a
cited test does not declare the matching requirement ID, or combined coverage of
`iam_policy_generator.py` and `spec_validator.py` falls below 85%. An HTML coverage report is
written to `htmlcov/`.

### 5. Pre-commit Hook Setup

```bash
# Run these commands from the repository root. The configuration installs both
# the pre-commit quality gates and the feature commit-message traceability hook.
pre-commit install \
  --config examples/spec-driven-development/.pre-commit-config.yaml

# Run pre-commit manually
pre-commit run \
  --config examples/spec-driven-development/.pre-commit-config.yaml \
  --all-files
```

Feature commit messages must include an anchor that actually exists in
`iam_policy_spec.md`, for example:

```text
feat(generator): split S3 resource statements [spec:policy_generation]
```

## Specification Structure

The IAM Policy Generator specification demonstrates machine-readable format:

```markdown
# IAM Policy Generator Specification {#iam_policy_gen}

## CLI Contract {#cli_contract authority=system}
- **REQ-001**: The CLI MUST require `--policy-type` and `--resource`. [^test_cli_policy_type]

## Input Validation {#input_validation authority=platform}  
- **REQ-003**: The generator MUST reject malformed ARNs with an actionable error. [^test_arn_validation]
- **REQ-005**: The generator MUST reject unsafe input without rewriting resource identity. [^test_unsafe_input]

[^test_cli_policy_type]: tests/test_cli.py::TestCLIRequirements::test_policy_type_flag
[^test_arn_validation]: tests/test_validation.py::TestInputValidation::test_arn_format_validation
[^test_unsafe_input]: tests/test_validation.py::TestInputValidation::test_unsafe_input_rejected_without_rewriting
```

## Authority Conflict Resolution

When requirements conflict, higher authority levels take precedence:

```markdown
## CLI Output Format {#output_format authority=feature}
The system SHOULD output policies in compact JSON format.

## Security Requirements {#security authority=system}  
The system MUST output policies with proper indentation for human review.

# Resolution: authority=system takes precedence
# Result: Policies output with proper indentation
```

## Domain Fragments and Outcome Cases

Keep global invariants separate from bounded domain specifications so an implementation task loads
only the requirements it needs:

```text
specs/
├── global-invariants.md
├── authentication.md
└── payments.md
```

Each domain fragment should cover three observable outcomes before implementation begins:

| Outcome | What the specification must make explicit |
|---|---|
| Successful | Preconditions, resulting state, and externally visible behavior |
| Rejected | Invalid or prohibited input, stable error behavior, and unchanged state |
| Degraded | Dependency failure, the safe fallback, and the recovery signal |

Anchor these outcomes and link normative requirements to tests that actually exist. Do not create
placeholder test citations to make traceability appear complete.

## Git Workflow Integration

Commit messages reference specification anchors for traceability:

```bash
git commit -m "feat: implement ARN validation [spec:input_validation]

Implements ARN format validation requirement from input_validation
section. Validates AWS ARN syntax before policy generation.

Closes specification anchor #input_validation.
Traceability: 100% (7/7 requirements linked)"
```

## Benefits Demonstrated

### AI Tool Independence
- Switch between different AI tools while maintaining behavioral requirements
- Specifications persist regardless of implementation approach

### Automated Compliance
- Machine-readable structure enables automated requirement validation
- Pre-commit hooks prevent specification violations

### Precise Traceability
- Each requirement links directly to test implementations
- Coverage tracking shows specification completeness

### Living Documentation
- Specifications evolve with system while maintaining context
- Authority levels document precedence and make potential conflicts reviewable

## Integration with Other Patterns

This implementation demonstrates integration with:
- [Security Sandbox](../security-sandbox/) - Secure testing environment
- [Testing Orchestration](../../experiments/README.md#testing-orchestration) - Multi-layered testing approach
- [Agent Observability](../../README.md#agent-observability) - Tracing and debugging capabilities

## Running the Complete Example

1. **Install dependencies:**
   ```bash
   cd examples/spec-driven-development
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --requirement requirements.txt
   ```

2. **Set up both repository hooks from the repository root:**
   ```bash
   cd ../..
   pre-commit install \
     --config examples/spec-driven-development/.pre-commit-config.yaml
   ```

3. **Run specification validation:**
   ```bash
   cd examples/spec-driven-development
   python spec_validator.py --check-coverage
   ```

4. **Run the complete embedded suite and coverage gate:**
   ```bash
   python -m pytest
   ```

5. **Generate IAM policies:**
   ```bash
   python iam_policy_generator.py --policy-type s3-read --resource 'arn:aws:s3:::my-bucket/*'
   ```

This example demonstrates how SpecDriven AI transforms AI development from ad-hoc prompting to a rigorous, specification-first approach with automated validation and comprehensive traceability.

## Further Reading

- [Blog Post: SpecDriven AI](https://www.paulmduvall.com/specdriven-ai-combining-specs-and-tdd-for-ai-powered-development/)
- [OpenAI Model Spec](https://cdn.openai.com/spec/model-spec-2024-05-08.html)
- [AI Development Patterns Collection](../../README.md)
