# Infrastructure Drift Detection & Remediation

## Overview
Automated detection of infrastructure configuration drift and AI-generated corrective patches to maintain infrastructure as intended.

## Drift Detection Framework

### What is Infrastructure Drift?
Infrastructure drift occurs when the actual state of infrastructure resources differs from the desired state defined in Infrastructure as Code (IaC) templates.

### Common Drift Scenarios
```yaml
drift_types:
  configuration_drift:
    - manual_changes: "Changes made through console/CLI bypassing IaC"
    - auto_scaling: "Resources automatically adjusted by AWS"
    - external_tools: "Changes made by monitoring/security tools"
    
  resource_drift:
    - resource_deletion: "Resources deleted outside of IaC"
    - resource_creation: "Resources created outside of IaC"
    - property_changes: "Resource properties modified manually"
    
  state_drift:
    - orphaned_resources: "Resources in cloud but not in state"
    - missing_resources: "Resources in state but not in cloud"
    - import_required: "Resources exist but not managed by IaC"
```

## Terraform Drift Detection

### Automated Drift Scanning
```bash
#!/bin/bash
# terraform_drift_scan.sh

echo "=== Infrastructure Drift Detection ==="
echo "Timestamp: $(date)"

# Initialize Terraform
terraform init -input=false

# Run plan to detect drift
echo "Scanning for infrastructure drift..."
terraform plan -detailed-exitcode -out=drift.plan

EXIT_CODE=$?

case $EXIT_CODE in
  0)
    echo "✅ No drift detected"
    ;;
  1)
    echo "❌ Terraform execution error"
    exit 1
    ;;
  2)
    echo "⚠️  Infrastructure drift detected"
    
    # Generate human-readable drift report
    terraform show -json drift.plan > drift.json
    
    # AI-powered drift analysis
    ai "Analyze Terraform drift in drift.json:
    
    1. Summarize what resources have drifted
    2. Categorize drift by severity (critical, medium, low)
    3. Identify likely causes (manual changes, auto-scaling, etc.)
    4. Suggest remediation strategy for each drifted resource
    5. Prioritize fixes by business impact
    
    Format as markdown report with:
    - Executive summary
    - Detailed findings
    - Remediation plan
    - Prevention recommendations"
    
    ;;
esac
```

### Continuous Drift Monitoring
```yaml
# .github/workflows/drift-detection.yml
name: Infrastructure Drift Detection

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  detect-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0
          
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
          
      - name: Detect drift
        id: drift
        run: |
          terraform init
          terraform plan -detailed-exitcode -out=drift.plan
          echo "exit_code=$?" >> $GITHUB_OUTPUT
          
      - name: Generate drift report
        if: steps.drift.outputs.exit_code == '2'
        run: |
          terraform show -json drift.plan > drift.json
          python scripts/generate_drift_report.py drift.json
          
      - name: Create drift issue
        if: steps.drift.outputs.exit_code == '2'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const driftReport = fs.readFileSync('drift_report.md', 'utf8');
            
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Infrastructure Drift Detected - ${new Date().toISOString().split('T')[0]}`,
              body: driftReport,
              labels: ['infrastructure', 'drift', 'automation']
            });
            
      - name: Notify teams
        if: steps.drift.outputs.exit_code == '2'
        run: |
          curl -X POST "${{ secrets.SLACK_WEBHOOK }}" \
            -H 'Content-type: application/json' \
            --data '{"text":"🚨 Infrastructure drift detected! Check GitHub issues for details."}'
```

## AWS Config Rules for Drift Detection

### Custom Config Rules
```yaml
# aws-config-drift-rules.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'AWS Config Rules for Infrastructure Drift Detection'

Resources:
  # Detect untagged resources
  UntaggedResourcesRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: untagged-resources-drift
      Description: 'Detects resources missing required tags (potential drift)'
      Source:
        Owner: AWS
        SourceIdentifier: REQUIRED_TAGS
      InputParameters: |
        {
          "tag1Key": "Environment",
          "tag2Key": "Owner", 
          "tag3Key": "Project"
        }
      Scope:
        ComplianceResourceTypes:
          - AWS::EC2::Instance
          - AWS::S3::Bucket
          - AWS::RDS::DBInstance
          
  # Detect security group changes
  SecurityGroupDriftRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: security-group-drift-detection
      Description: 'Detects unauthorized security group rule changes'
      Source:
        Owner: AWS
        SourceIdentifier: INCOMING_SSH_DISABLED
      Scope:
        ComplianceResourceTypes:
          - AWS::EC2::SecurityGroup
          
  # Detect S3 bucket policy changes
  S3BucketPolicyDrift:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: s3-bucket-policy-drift
      Description: 'Detects S3 bucket policy changes outside of IaC'
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_PUBLIC_ACCESS_PROHIBITED
      Scope:
        ComplianceResourceTypes:
          - AWS::S3::Bucket

  # Custom rule for Terraform-managed resources
  TerraformManagedResourceRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: terraform-managed-resource-drift
      Description: 'Detects changes to Terraform-managed resources'
      Source:
        Owner: AWS_CONFIG_RULE
        SourceIdentifier: !GetAtt TerraformDriftLambda.Arn
      InputParameters: |
        {
          "terraformStateS3Bucket": "my-terraform-state-bucket",
          "terraformStateKey": "infrastructure/terraform.tfstate"
        }

  # Lambda function for custom drift detection
  TerraformDriftLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: terraform-drift-detector
      Runtime: python3.9
      Handler: index.lambda_handler
      Role: !GetAtt TerraformDriftRole.Arn
      Code:
        ZipFile: |
          import json
          import boto3
          import urllib.parse
          
          def lambda_handler(event, context):
              # Get Terraform state from S3
              s3 = boto3.client('s3')
              config = boto3.client('config')
              
              # Parse Config rule parameters
              rule_parameters = json.loads(event['ruleParameters'])
              bucket = rule_parameters['terraformStateS3Bucket']
              key = rule_parameters['terraformStateKey']
              
              try:
                  # Get Terraform state
                  response = s3.get_object(Bucket=bucket, Key=key)
                  tf_state = json.loads(response['Body'].read())
                  
                  # Extract managed resources
                  managed_resources = {}
                  for resource in tf_state.get('resources', []):
                      for instance in resource.get('instances', []):
                          if 'attributes' in instance:
                              managed_resources[instance['attributes'].get('id')] = {
                                  'type': resource['type'],
                                  'name': resource['name'],
                                  'attributes': instance['attributes']
                              }
                  
                  # Check current resource against Terraform state
                  configuration_item = event['configurationItem']
                  resource_id = configuration_item['resourceId']
                  
                  compliance = 'COMPLIANT'
                  annotation = 'Resource matches Terraform state'
                  
                  if resource_id not in managed_resources:
                      compliance = 'NON_COMPLIANT'
                      annotation = 'Resource not managed by Terraform'
                  else:
                      # Deep comparison of attributes could go here
                      tf_resource = managed_resources[resource_id]
                      # Simplified check - in real implementation, compare all relevant attributes
                      
                  # Report compliance
                  config.put_evaluations(
                      Evaluations=[
                          {
                              'ComplianceResourceType': configuration_item['resourceType'],
                              'ComplianceResourceId': resource_id,
                              'ComplianceType': compliance,
                              'Annotation': annotation,
                              'OrderingTimestamp': configuration_item['configurationItemCaptureTime']
                          }
                      ],
                      ResultToken=event['resultToken']
                  )
                  
              except Exception as e:
                  print(f"Error: {str(e)}")
                  # Report as non-compliant if we can't verify
                  config.put_evaluations(
                      Evaluations=[
                          {
                              'ComplianceResourceType': configuration_item['resourceType'],
                              'ComplianceResourceId': configuration_item['resourceId'],
                              'ComplianceType': 'NON_COMPLIANT',
                              'Annotation': f'Unable to verify against Terraform state: {str(e)}',
                              'OrderingTimestamp': configuration_item['configurationItemCaptureTime']
                          }
                      ],
                      ResultToken=event['resultToken']
                  )
              
              return {'statusCode': 200}
```

## Automated Drift Remediation

### AI-Generated Patch Creation
```python
# drift_remediation.py
import json
import subprocess
import openai
from typing import Dict, List

class DriftRemediationEngine:
    def __init__(self):
        self.terraform_state = self.load_terraform_state()
        
    def detect_and_remediate_drift(self) -> Dict:
        """Main drift remediation workflow"""
        
        # Step 1: Detect drift
        drift_results = self.run_terraform_plan()
        
        if not drift_results['has_drift']:
            return {'status': 'no_drift', 'message': 'Infrastructure in sync'}
            
        # Step 2: Analyze drift with AI
        drift_analysis = self.analyze_drift_with_ai(drift_results['plan'])
        
        # Step 3: Generate remediation patches
        remediation_patches = self.generate_remediation_patches(drift_analysis)
        
        # Step 4: Validate patches
        validation_results = self.validate_patches(remediation_patches)
        
        # Step 5: Apply patches (if auto-remediation enabled)
        if self.should_auto_remediate(drift_analysis):
            application_results = self.apply_patches(remediation_patches)
            return {
                'status': 'auto_remediated',
                'drift_analysis': drift_analysis,
                'patches_applied': application_results
            }
        else:
            return {
                'status': 'manual_review_required',
                'drift_analysis': drift_analysis,
                'proposed_patches': remediation_patches,
                'validation_results': validation_results
            }
    
    def analyze_drift_with_ai(self, terraform_plan: str) -> Dict:
        """Use AI to analyze drift and recommend remediation strategy"""
        
        prompt = f"""
        Analyze this Terraform plan showing infrastructure drift:
        
        {terraform_plan}
        
        For each drifted resource:
        1. Identify the type of drift (configuration, manual change, etc.)
        2. Assess severity (critical, medium, low)
        3. Determine likely cause
        4. Recommend remediation approach:
           - Import existing resource into state
           - Update Terraform configuration
           - Revert manual changes
           - Accept drift as expected
        
        Format response as JSON with this structure:
        {{
            "summary": "Brief overview of drift",
            "drifted_resources": [
                {{
                    "resource": "resource_name",
                    "drift_type": "configuration|resource|state",
                    "severity": "critical|medium|low",
                    "cause": "likely cause description",
                    "remediation": "recommended action",
                    "auto_remediable": true/false
                }}
            ],
            "overall_risk": "assessment of overall risk",
            "recommended_action": "immediate|scheduled|monitor"
        }}
        """
        
        # In real implementation, call your AI service
        # This is a placeholder for the AI analysis
        response = self.call_ai_service(prompt)
        return json.loads(response)
    
    def generate_remediation_patches(self, drift_analysis: Dict) -> List[Dict]:
        """Generate specific remediation patches for each drifted resource"""
        
        patches = []
        
        for resource in drift_analysis['drifted_resources']:
            if not resource['auto_remediable']:
                continue
                
            patch = self.create_patch_for_resource(resource)
            if patch:
                patches.append(patch)
                
        return patches
    
    def create_patch_for_resource(self, resource: Dict) -> Dict:
        """Create a specific patch for a drifted resource"""
        
        if resource['remediation'] == 'import_resource':
            return {
                'type': 'terraform_import',
                'resource': resource['resource'],
                'command': f"terraform import {resource['resource']} {resource.get('resource_id')}",
                'description': f"Import {resource['resource']} into Terraform state"
            }
            
        elif resource['remediation'] == 'update_configuration':
            # Generate Terraform configuration update
            ai_prompt = f"""
            Generate Terraform configuration update for resource: {resource['resource']}
            
            Current drift: {resource.get('current_state')}
            Desired state: {resource.get('desired_state')}
            
            Provide the exact HCL configuration block that should be updated.
            """
            
            updated_config = self.call_ai_service(ai_prompt)
            
            return {
                'type': 'configuration_update',
                'resource': resource['resource'],
                'updated_config': updated_config,
                'description': f"Update configuration for {resource['resource']}"
            }
            
        elif resource['remediation'] == 'revert_changes':
            return {
                'type': 'terraform_apply',
                'resource': resource['resource'],
                'command': f"terraform apply -target={resource['resource']} -auto-approve",
                'description': f"Revert manual changes to {resource['resource']}"
            }
            
        return None
    
    def validate_patches(self, patches: List[Dict]) -> Dict:
        """Validate patches before application"""
        
        validation_results = {
            'valid_patches': [],
            'invalid_patches': [],
            'warnings': []
        }
        
        for patch in patches:
            try:
                if patch['type'] == 'terraform_apply':
                    # Dry run validation
                    result = subprocess.run(
                        ['terraform', 'plan', f"-target={patch['resource']}", '-detailed-exitcode'],
                        capture_output=True, text=True
                    )
                    
                    if result.returncode == 0:
                        validation_results['valid_patches'].append(patch)
                    else:
                        validation_results['invalid_patches'].append({
                            'patch': patch,
                            'error': result.stderr
                        })
                        
                elif patch['type'] == 'configuration_update':
                    # Validate HCL syntax
                    if self.validate_hcl_syntax(patch['updated_config']):
                        validation_results['valid_patches'].append(patch)
                    else:
                        validation_results['invalid_patches'].append({
                            'patch': patch,
                            'error': 'Invalid HCL syntax'
                        })
                        
            except Exception as e:
                validation_results['invalid_patches'].append({
                    'patch': patch,
                    'error': str(e)
                })
                
        return validation_results
    
    def should_auto_remediate(self, drift_analysis: Dict) -> bool:
        """Determine if drift should be auto-remediated"""
        
        # Auto-remediate if:
        # 1. No critical severity issues
        # 2. All changes are low-risk
        # 3. Auto-remediation is enabled
        
        has_critical = any(
            resource['severity'] == 'critical' 
            for resource in drift_analysis['drifted_resources']
        )
        
        return (
            not has_critical and 
            drift_analysis['overall_risk'] in ['low', 'medium'] and
            drift_analysis['recommended_action'] == 'immediate'
        )
    
    def apply_patches(self, patches: List[Dict]) -> Dict:
        """Apply validated patches"""
        
        results = {
            'successful': [],
            'failed': [],
            'rollback_required': False
        }
        
        for patch in patches:
            try:
                if patch['type'] == 'terraform_apply':
                    result = subprocess.run(
                        patch['command'].split(),
                        capture_output=True, text=True
                    )
                    
                    if result.returncode == 0:
                        results['successful'].append(patch)
                    else:
                        results['failed'].append({
                            'patch': patch,
                            'error': result.stderr
                        })
                        results['rollback_required'] = True
                        break  # Stop on first failure
                        
                elif patch['type'] == 'configuration_update':
                    # Update configuration file
                    self.update_terraform_config(patch)
                    results['successful'].append(patch)
                    
            except Exception as e:
                results['failed'].append({
                    'patch': patch,
                    'error': str(e)
                })
                results['rollback_required'] = True
                break
                
        return results
```

### Automated Remediation Workflow
```bash
#!/bin/bash
# automated_drift_remediation.sh

set -euo pipefail

DRIFT_THRESHOLD="medium"  # low, medium, high
AUTO_REMEDIATE="true"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

main() {
    echo "🔍 Starting automated drift detection and remediation"
    
    # Step 1: Detect drift
    echo "Detecting infrastructure drift..."
    python3 drift_remediation.py detect > drift_results.json
    
    DRIFT_STATUS=$(jq -r '.status' drift_results.json)
    
    case $DRIFT_STATUS in
        "no_drift")
            echo "✅ No infrastructure drift detected"
            exit 0
            ;;
            
        "auto_remediated")
            echo "🔧 Drift automatically remediated"
            REMEDIATED_COUNT=$(jq '.patches_applied.successful | length' drift_results.json)
            echo "Successfully applied $REMEDIATED_COUNT patches"
            
            # Verify remediation
            verify_remediation_success
            
            # Notify teams
            notify_slack "✅ Infrastructure drift automatically remediated ($REMEDIATED_COUNT patches applied)"
            ;;
            
        "manual_review_required")
            echo "⚠️  Manual review required for drift remediation"
            
            # Create GitHub issue for manual review
            create_drift_issue drift_results.json
            
            # Notify teams
            notify_slack "⚠️ Infrastructure drift detected - manual review required. GitHub issue created."
            ;;
            
        *)
            echo "❌ Unknown drift status: $DRIFT_STATUS"
            exit 1
            ;;
    esac
}

verify_remediation_success() {
    echo "🔍 Verifying remediation success..."
    
    # Run terraform plan again to confirm no drift
    terraform plan -detailed-exitcode -out=verify.plan
    EXIT_CODE=$?
    
    if [[ $EXIT_CODE -eq 0 ]]; then
        echo "✅ Remediation successful - no remaining drift"
    elif [[ $EXIT_CODE -eq 2 ]]; then
        echo "⚠️  Remediation incomplete - drift still detected"
        
        # Generate rollback plan
        echo "Generating rollback plan..."
        python3 drift_remediation.py rollback
        
        notify_slack "⚠️ Drift remediation incomplete - manual intervention required"
    else
        echo "❌ Error verifying remediation"
        exit 1
    fi
}

create_drift_issue() {
    local results_file=$1
    
    # Extract key information for GitHub issue
    SUMMARY=$(jq -r '.drift_analysis.summary' "$results_file")
    RESOURCE_COUNT=$(jq '.drift_analysis.drifted_resources | length' "$results_file")
    
    # AI-generated issue description
    ISSUE_DESCRIPTION=$(ai "Create GitHub issue description for infrastructure drift:
    
    Drift summary: $SUMMARY
    Number of drifted resources: $RESOURCE_COUNT
    
    Generate:
    - Clear problem description
    - Impact assessment  
    - Recommended actions
    - Urgency level
    
    Format as markdown for GitHub issue.")
    
    # Create GitHub issue
    gh issue create \
        --title "Infrastructure Drift Detected - $RESOURCE_COUNT resources affected" \
        --body "$ISSUE_DESCRIPTION" \
        --label "infrastructure,drift,ops" \
        --assignee "@infrastructure-team"
}

notify_slack() {
    local message=$1
    
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        curl -X POST "$SLACK_WEBHOOK_URL" \
            -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}"
    fi
}

# Schedule this script to run every 6 hours
# 0 */6 * * * /path/to/automated_drift_remediation.sh
main "$@"
```

## Drift Prevention Strategies

### Git Hooks for IaC Changes
```bash
#!/bin/bash
# pre-commit-terraform-validate.sh

echo "🔍 Validating Terraform changes..."

# Check if Terraform files changed
if git diff --cached --name-only | grep -q '\.tf$'; then
    
    # Run terraform validate
    terraform validate || {
        echo "❌ Terraform validation failed"
        exit 1
    }
    
    # Run terraform plan
    terraform plan -detailed-exitcode -out=plan.tmp
    
    # Check for resource deletions
    if terraform show -json plan.tmp | jq -e '.resource_changes[] | select(.change.actions[] == "delete")' > /dev/null; then
        echo "⚠️  WARNING: This change includes resource deletions"
        echo "Please review carefully before merging"
    fi
    
    # Cleanup
    rm -f plan.tmp
    
    echo "✅ Terraform validation passed"
fi
```

### Policy-as-Code for Change Control
```yaml
# opa_change_policy.rego
package terraform.changes

# Deny dangerous operations during business hours
deny[msg] {
    input.change.actions[_] == "delete"
    input.resource.type in ["aws_rds_cluster", "aws_s3_bucket"]
    business_hours
    msg := sprintf("Deletion of %s not allowed during business hours", [input.resource.type])
}

# Require approval for security group changes
deny[msg] {
    input.resource.type == "aws_security_group"
    input.change.actions[_] != "no-op"
    not approved_by_security_team
    msg := "Security group changes require security team approval"
}

# Prevent manual console changes
deny[msg] {
    input.change_source == "console"
    msg := "Manual console changes not allowed - use Infrastructure as Code"
}

business_hours {
    time.now_ns() >= time.parse_rfc3339_ns("2023-01-01T09:00:00Z")
    time.now_ns() <= time.parse_rfc3339_ns("2023-01-01T17:00:00Z")
}

approved_by_security_team {
    input.approvals[_].team == "security"
}
```

## Monitoring and Alerting

### CloudWatch Alarms for Drift Detection
```yaml
# cloudwatch-drift-alarms.yaml
AWSTemplateFormatVersion: '2010-09-09'

Resources:
  ConfigComplianceAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: Infrastructure-Drift-Detected
      AlarmDescription: Alarm when Config rules detect infrastructure drift
      MetricName: ComplianceByConfigRule
      Namespace: AWS/Config
      Statistic: Average
      Period: 300
      EvaluationPeriods: 1
      Threshold: 1
      ComparisonOperator: LessThanThreshold
      Dimensions:
        - Name: ConfigRuleName
          Value: terraform-managed-resource-drift
      AlarmActions:
        - !Ref DriftNotificationTopic

  TerraformPlanAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: Terraform-Plan-Drift-Detected
      AlarmDescription: Alarm when Terraform plan detects changes
      MetricName: TerraformPlanChanges
      Namespace: Custom/Infrastructure
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 1
      Threshold: 0
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref DriftNotificationTopic

  DriftNotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: infrastructure-drift-alerts
      Subscription:
        - Protocol: email
          Endpoint: ops-team@company.com
        - Protocol: https
          Endpoint: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

## Best Practices

1. **Regular Scanning**: Run drift detection every 6 hours
2. **Immediate Alerts**: Alert on critical drift within minutes
3. **Graduated Response**: Auto-fix low risk, escalate high risk
4. **Change Documentation**: Track all infrastructure changes
5. **Rollback Capability**: Always maintain rollback procedures
6. **Team Training**: Educate teams on IaC best practices
7. **Compliance Integration**: Tie drift detection to compliance frameworks

## Emergency Procedures

### Critical Drift Response
```bash
#!/bin/bash
# emergency_drift_response.sh

echo "🚨 EMERGENCY DRIFT RESPONSE 🚨"

# Immediately stop any automated changes
echo "Disabling automated remediation..."
kubectl patch deployment terraform-controller -p '{"spec":{"replicas":0}}'

# Create emergency state backup
echo "Creating emergency state backup..."
terraform state pull > "emergency-backup-$(date +%Y%m%d-%H%M%S).tfstate"

# Assess critical systems
echo "Checking critical system status..."
for system in database load-balancer security-groups; do
    echo "Checking $system..."
    aws_resource_health_check "$system"
done

# Generate immediate assessment
ai "Emergency infrastructure drift assessment:
- Analyze current drift for critical impact
- Identify immediate threats to availability/security  
- Recommend emergency containment actions
- Provide step-by-step recovery plan
- Estimate time to restore normal operations"

# Notify all stakeholders
emergency_notification "Critical infrastructure drift detected - war room activated"
```