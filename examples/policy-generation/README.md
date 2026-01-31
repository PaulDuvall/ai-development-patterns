# Policy Generation Implementation

This directory contains a complete implementation of the Policy Generation pattern, transforming compliance requirements into executable Cedar/OPA policy files using AI assistance.

## Overview

This implementation demonstrates how to:
- Transform written compliance requirements into executable policy code
- Generate Cedar and OPA (Open Policy Agent) policies using AI
- Test and validate generated policies
- Integrate policy generation into CI/CD pipelines

## Files in this Implementation

- `iam_permissions.cedar` - Example Cedar IAM policy
- `network_policy.rego` - Example OPA network policy
- `config_rules.yml` - Configuration rules and compliance requirements
- `generate-policies.sh` - AI-powered policy generation script
- `test-policies.sh` - Policy testing and validation script
- `compliance-requirements.md` - Written requirements for transformation

## Quick Start

### Generate Policies from Requirements

```bash
# Transform written requirements into Cedar policies
./generate-policies.sh requirements/encryption.md cedar > policies/encryption.cedar

# Generate OPA policies for network access
./generate-policies.sh requirements/network.md opa > policies/network.rego

# Test generated policies
./test-policies.sh
```

### Example Transformation

**Input (compliance-requirements.md):**
```markdown
## SOC 2 Data Encryption Requirement
Data at rest must be AES-256 encrypted in transit and at rest per SOC 2.
All database connections must use TLS 1.2 or higher.
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
```yaml
# .github/workflows/policy-validation.yml
- name: Generate Policies
  run: |
    ai "Convert docs/compliance/*.md into Cedar policies" > policies/generated.cedar
    
- name: Test Policies
  run: |
    opa test policies/
    cedar validate policies/generated.cedar
```

### Compliance Automation
```bash
# Weekly compliance policy update
cron_job() {
    ai "Review compliance-requirements.md for changes, update policies accordingly"
    git add policies/
    git commit -m "feat: update compliance policies based on requirement changes"
}
```

## Testing and Validation

### Policy Testing Framework
- Unit tests for individual policy rules
- Integration tests with sample data
- Compliance verification tests
- Performance testing for policy evaluation

### Test Examples
```bash
# Test Cedar policies
cedar validate --schema schema.cedarschema policies/*.cedar

# Test OPA policies with sample data
opa test policies/ data/test-cases/
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

## Advanced Features

### AI-Powered Policy Generation
- Natural language to policy transformation
- Compliance framework mapping
- Automated policy updates
- Conflict detection and resolution

### Policy Optimization
- Performance optimization for policy evaluation
- Rule consolidation and simplification
- Dead code elimination
- Policy impact analysis

## Troubleshooting

### Common Issues
- **Syntax Errors**: Validate policy syntax before deployment
- **Conflicting Rules**: Use policy analyzers to detect conflicts
- **Performance Issues**: Profile policy evaluation times
- **Compliance Gaps**: Regular audit against requirements

### Debug Commands
```bash
# Validate Cedar policy syntax
cedar validate policies/generated.cedar

# Test OPA policy evaluation
opa eval -d policies/ "data.authz.allow"

# Check for policy conflicts
./analyze-conflicts.sh policies/
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
