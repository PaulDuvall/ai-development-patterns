# Drift Remediation Implementation

This directory contains a complete implementation of the Drift Remediation pattern, detecting infrastructure configuration drift and generating corrective patches automatically.

## Overview

Drift Remediation enables teams to:
- Automatically detect infrastructure configuration drift
- Generate corrective Terraform/CloudFormation patches
- Assess drift risk levels and prioritize remediation
- Maintain infrastructure as intended by IaC definitions

## Files in this Implementation

For complete pattern documentation, see: [Drift Remediation](../../README.md#drift-remediation)

- `infrastructure_drift.md` - Complete drift detection pattern documentation
- `drift_scanners/` - Automated drift detection tools for various platforms
- `remediation_scripts/` - AI-generated corrective patch generators
- `risk_assessment/` - Drift impact analysis and prioritization tools
- `continuous_monitoring/` - Scheduled drift detection automation

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

## Quick Start

```bash
# Detect drift across infrastructure
./detect-drift.sh --platform aws --scan-all

# Generate remediation plan
ai "Compare current AWS infrastructure against Terraform state:
1. Identify configuration drift in EC2, RDS, S3
2. Generate corrective Terraform plan
3. Assess drift risk level (critical/medium/low)
4. Create automated remediation script with approval gates"

# Apply remediation with approval
./remediate-drift.sh --approve-critical --plan-others
```

**Complete Implementation**: This directory contains the full drift detection and remediation system with automated scanning, AI-powered analysis, and corrective patch generation.
