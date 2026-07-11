# Policy Generation Example

This directory provides a runnable generator wrapper, written requirements, and example Cedar,
Rego, and AWS Config artifacts for the [Policy Generation](../../README.md#policy-generation)
pattern. Generated output is a review candidate, not an approved or semantically validated policy.

## Overview

This example demonstrates how to:
- Transform written compliance requirements into candidate policy code
- Generate Cedar and OPA (Open Policy Agent) text through an `ai` CLI
- Syntax-parse generated candidates with the official CLIs
- Compare candidates with reviewed policy files before a human-owned adoption decision

## Files in this Example

- `iam_permissions.cedar` - Example Cedar IAM policy
- `network_policy.rego` - Example OPA network policy
- `config_rules.yml` - AWS Config rules (CloudFormation) generated from compliance requirements
- `generate-policies.sh` - AI-powered policy generation script
- `compliance-requirements.md` - Written requirements for transformation

## Quick Start

### Generate Policies from Requirements

```bash
# Transform written requirements into Cedar policies
./generate-policies.sh compliance-requirements.md cedar > generated.cedar

# Generate OPA policies from the same requirements
./generate-policies.sh compliance-requirements.md opa > generated.rego

# Validate the generated policies with the Cedar and OPA CLIs
cedar check-parse --policies generated.cedar
opa check generated.rego
```

The generation script requires an `ai` CLI on your PATH; validation requires the [Cedar CLI](https://github.com/cedar-policy/cedar) and [OPA](https://www.openpolicyagent.org/docs/latest/#running-opa).

### Example Transformation

**Input (from compliance-requirements.md):**
```markdown
## REQ-001: Data Encryption at Rest
**Authority**: SOC 2 Type II
**Description**: All sensitive data must be encrypted at rest using AES-256 encryption or stronger
**Implementation**: Database encryption, file system encryption, automated key rotation every 90 days
```

**Generated Cedar Policy:**
```cedar
permit(
    principal,
    action == Action::"s3:PutObject",
    resource
) when {
    resource has encryption &&
    resource.encryption.algorithm == "AES-256" &&
    resource.encryption.enabled == true
};
```

## Policy Languages Supported

### Cedar Policies
- AWS native policy language
- Type-safe policy evaluation
- Human-readable syntax
- Integration with AWS services

### OPA/Rego Policies
- Cloud-native policy framework
- Kubernetes integration
- Flexible rule evaluation
- JSON/YAML input support

## Integration Examples

### CI/CD Pipeline Integration

**Cedar Pipeline:**
```yaml
# .github/workflows/cedar-policy-validation.yml
- name: Generate Cedar Policies
  run: |
    ./generate-policies.sh compliance-requirements.md cedar > generated.cedar

- name: Validate Cedar Policies
  run: |
    cedar check-parse --policies generated.cedar
```

**OPA/Rego Pipeline:**
```yaml
# .github/workflows/opa-policy-validation.yml
- name: Generate OPA Policies
  run: |
    ./generate-policies.sh compliance-requirements.md opa > generated.rego

- name: Parse OPA Policies
  run: |
    opa check generated.rego
```

### Compliance Automation
```bash
# Generate candidates; validation and human review decide whether to adopt them
./generate-policies.sh compliance-requirements.md cedar > candidate.cedar
./generate-policies.sh compliance-requirements.md opa > candidate.rego
cedar check-parse --policies candidate.cedar
opa check candidate.rego
git diff --no-index iam_permissions.cedar candidate.cedar || true
git diff --no-index network_policy.rego candidate.rego || true
```

## Testing and Validation

### Validation Boundary

The shipped commands parse syntax only. An adopter must add unit cases for each authorization rule,
integration inputs, compliance traceability, conflict analysis, and performance tests before
deployment; those test suites and schemas are not included here.

### Test Examples
```bash
# Parse the shipped Cedar policy
cedar check-parse --policies iam_permissions.cedar

# Parse the shipped Rego policy
opa check network_policy.rego
```

## Compliance Requirements Format

### Structured Requirements
Requirements should be written in a consistent format:
- **Requirement ID**: Unique identifier
- **Description**: Clear compliance requirement
- **Authority**: Regulatory source (SOC 2, PCI DSS, etc.)
- **Implementation**: Technical implementation details

### Example Format
```markdown
## REQ-001: Data Encryption
**Authority**: SOC 2 Type II
**Description**: All sensitive data must be encrypted at rest using AES-256
**Implementation**: Database encryption, file system encryption, key rotation
```

## Possible Extensions (Not Shipped)

### Generation Workflow
- Natural language to policy transformation
- Compliance framework mapping
- Reviewed policy-update proposals
- Schema- and test-backed conflict analysis supplied by the adopter

### Policy Optimization
- Performance optimization for policy evaluation
- Rule consolidation and simplification
- Dead code elimination
- Policy impact analysis

## Troubleshooting

### Common Issues
- **Syntax Errors**: Validate policy syntax before deployment
- **Conflicting Rules**: Syntax checks cannot detect semantic conflicts; add an application schema,
  authorization test cases, and a reviewed analyzer before making conflict-detection claims
- **Performance Issues**: Profile policy evaluation times
- **Compliance Gaps**: Regular audit against requirements

### Debug Commands
```bash
# Validate Cedar policy syntax
cedar check-parse --policies generated.cedar

# Validate OPA policy syntax
opa check generated.rego

# No conflict analyzer or Cedar schema ships in this example.
# Add project-specific schemas and authorization tests for semantic validation.
```

## Contributing

When adding new policy generation capabilities:
1. Update the requirements format documentation
2. Add test cases for new policy types
3. Validate against relevant compliance frameworks
4. Update CI/CD integration examples

## Security Considerations

⚠️ **Important Security Notes**
- Review all AI-generated policies before deployment
- Test policies with realistic data scenarios
- Maintain audit logs for policy changes
- Regular compliance validation and testing
