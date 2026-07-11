# Drift Remediation Example

Supporting material for the [Drift Remediation](../../README.md#drift-remediation) pattern: detect infrastructure configuration drift, generate a reviewable corrective patch, and require approval before apply.

## Files in This Directory

- **[`infrastructure_drift.md`](infrastructure_drift.md)** - Drift detection and remediation reference covering Terraform drift scanning, scheduled drift monitoring in CI, AWS Config rules, AI-generated corrective patch workflows with risk classification, drift prevention (pre-commit validation and policy-as-code), monitoring and alerting, and emergency response procedures. Its scripts, workflows, and policies are illustrative implementations to adapt, not tooling shipped in this directory.

For complete pattern documentation, see: [Drift Remediation](../../README.md#drift-remediation)

## What Drift Remediation Provides

- Deterministic detection of infrastructure configuration drift
- Reviewable corrective Terraform/CloudFormation patches
- Drift risk classification to prioritize remediation
- A human approval gate preserved before infrastructure changes

## Types of Infrastructure Drift

### Configuration Drift
- Manual changes through console/CLI bypassing IaC
- Auto-scaling adjustments by cloud providers
- Changes made by external monitoring/security tools

### Resource Drift
- Resources deleted outside of IaC
- Resources created outside of IaC management
- Resource properties modified manually

### State Drift
- Orphaned resources (in cloud but not in state)
- Missing resources (in state but not in cloud)
- Import required (resources exist but not managed)

## Illustrative Workflow

Keep detection deterministic and remediation reviewable. Capture the declared state, observed state, provider plan, and risk classification before generating a candidate correction:

```bash
terraform plan -detailed-exitcode -out=drift.tfplan || rc=$?
[ "${rc:-0}" -eq 2 ] || exit "${rc:-0}"
terraform show -json drift.tfplan > drift.json

ai "Propose the smallest Terraform patch for drift.json.
Do not apply it. Identify destructive changes and required approvals." > remediation.md

terraform plan -out=candidate.tfplan  # deterministic re-check after review
```

Only a human-approved pipeline applies the resulting plan. The agent that proposes a patch cannot approve or apply it. [`infrastructure_drift.md`](infrastructure_drift.md) expands this approach with scan scripts, a scheduled detection workflow, remediation risk gates, and prevention policies to adapt to your own environment.
