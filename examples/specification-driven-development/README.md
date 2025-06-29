# Specification Driven Development - Complete Implementation

This directory contains the complete implementation of the **Specification Driven Development** pattern, demonstrating machine-readable specifications with authority levels, automated coverage tracking, and rigorous Test-Driven Development (TDD) integration.

## Pattern Overview

SpecDriven AI combines three key elements:
- **Machine-readable specifications** with unique identifiers and authority levels
- **Rigorous Test-Driven Development** with coverage tracking and automated validation
- **AI-powered implementation** with persistent context through structured specifications

For complete pattern documentation, see: [Specification Driven Development](../../README.md#specification-driven-development)

## Files in This Directory

### Core Implementation
- **`iam_policy_generator.py`** - Complete IAM Policy Generator implementation
- **`spec_validator.py`** - Automated specification coverage tracking tool
- **`iam_policy_spec.md`** - Machine-readable specification with authority levels
- **`.pre-commit-config.yaml`** - Pre-commit hooks for specification validation

### Testing Infrastructure
- **`tests/`** - Complete test suite with specification traceability
- **`requirements.txt`** - Dependencies for testing and validation
- **`pytest.ini`** - Pytest configuration with coverage tracking

## Key Features

### Authority Level System
Specifications use authority levels to resolve conflicts:
- **`authority=system`**: Core business logic and security requirements (highest precedence)
- **`authority=platform`**: Infrastructure and technical architecture decisions  
- **`authority=feature`**: User interface and experience requirements (lowest precedence)

### Automated Coverage Tracking
```bash
# Run specification compliance validation
python spec_validator.py --check-coverage --authority-conflicts

# Output shows specification coverage
Specification Coverage Report:
✅ cli_requirements: 100% (3/3 tests linked)
✅ input_validation: 85% (6/7 tests linked) 
⚠️  Missing test: [^test_malformed_arn] in line 23
```

### Traceability System
Each specification requirement links to automated tests:
```markdown
- Validate resource ARN format before policy generation [^test_arn_validation]

[^test_arn_validation]: tests/test_iam_validation.py::test_arn_format_validation
```

## Usage Examples

### 1. Running the IAM Policy Generator

```bash
# Install dependencies
pip install -r requirements.txt

# Run the IAM Policy Generator
python iam_policy_generator.py --policy-type s3-read --resource arn:aws:s3:::my-bucket/*

# Expected output: Valid IAM policy JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

### 2. Specification Validation

```bash
# Check specification coverage
python spec_validator.py --check-coverage

# Check for authority conflicts
python spec_validator.py --authority-conflicts

# Validate specification syntax
python spec_validator.py --validate-syntax iam_policy_spec.md
```

### 3. Running Tests with Coverage

```bash
# Run all tests with specification coverage
pytest --cov=src --cov-report=html --spec-coverage

# Run specific specification tests
pytest tests/test_iam_validation.py -v

# Generate coverage report
coverage html
open htmlcov/index.html
```

### 4. Pre-commit Hook Setup

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run pre-commit manually
pre-commit run --all-files
```

## Specification Structure

The IAM Policy Generator specification demonstrates machine-readable format:

```markdown
# IAM Policy Generator Specification {#iam_policy_gen}

## CLI Requirements {#cli_requirements authority=system}
The system MUST provide a command-line interface that:
- Accepts policy type via `--policy-type` flag [^test_cli_policy_type]
- Validates input parameters against AWS IAM constraints [^test_input_validation]
- Generates syntactically correct IAM policy JSON [^test_iam_syntax]
- Returns exit code 0 for success, 1 for validation errors [^test_exit_codes]

## Input Validation {#input_validation authority=platform}  
The system MUST:
- Reject invalid AWS service names with clear error messages [^test_invalid_service]
- Validate resource ARN format before policy generation [^test_arn_validation]
- Implement rate limiting for API calls [^test_rate_limit]

[^test_cli_policy_type]: tests/test_cli.py::test_policy_type_flag
[^test_input_validation]: tests/test_validation.py::test_input_validation
[^test_iam_syntax]: tests/test_iam_policy.py::test_policy_syntax
[^test_exit_codes]: tests/test_cli.py::test_exit_codes
[^test_invalid_service]: tests/test_validation.py::test_invalid_service_names
[^test_arn_validation]: tests/test_validation.py::test_arn_format_validation
[^test_rate_limit]: tests/test_rate_limiting.py::test_api_rate_limiting
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

## Git Workflow Integration

Commit messages reference specification anchors for traceability:

```bash
git commit -m "feat: implement ARN validation [spec:test_arn_validation]

Implements ARN format validation requirement from input_validation
section. Validates AWS ARN syntax before policy generation.

Closes specification anchor #input_validation.
Coverage: 89% (31/35 spec requirements covered)"
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
- Authority levels resolve conflicts automatically

## Integration with Other Patterns

This implementation demonstrates integration with:
- [AI Security Sandbox](../../sandbox/) - Secure testing environment
- [Comprehensive AI Testing Strategy](../../README.md#comprehensive-ai-testing-strategy) - Multi-layered testing approach
- [Observable AI Development](../../README.md#observable-ai-development) - Logging and debugging capabilities

## Running the Complete Example

1. **Install dependencies:**
   ```bash
   cd examples/specification-driven-development
   pip install -r requirements.txt
   ```

2. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

3. **Run specification validation:**
   ```bash
   python spec_validator.py --check-coverage
   ```

4. **Run tests with coverage:**
   ```bash
   pytest --cov=src --cov-report=html
   ```

5. **Generate IAM policies:**
   ```bash
   python iam_policy_generator.py --policy-type s3-read --resource arn:aws:s3:::my-bucket/*
   ```

6. **View coverage report:**
   ```bash
   open htmlcov/index.html
   ```

This example demonstrates how SpecDriven AI transforms AI development from ad-hoc prompting to a rigorous, specification-first approach with automated validation and comprehensive traceability.

## Further Reading

- [Blog Post: SpecDriven AI](https://www.paulmduvall.com/specdriven-ai-combining-specs-and-tdd-for-ai-powered-development/)
- [OpenAI Model Spec](https://cdn.openai.com/spec/model-spec-2024-05-08.html)
- [AI Development Patterns Collection](../../README.md)