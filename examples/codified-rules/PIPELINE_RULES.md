# DELIVERY_RULES - CI/CD Pipeline & Deployment Excellence

**CRITICAL: Review these rules before EVERY change to code, pipeline, or infrastructure. Non-negotiable requirements for continuous delivery.**

## CORE MANDATES

1. **Build quality in** - Fix problems at the source, not downstream
2. **Automate everything** - No manual steps in the delivery process  
3. **Version control everything** - Code, config, infrastructure, pipelines
4. **Small, frequent integrations** - Merge to trunk daily minimum
5. **Fast feedback** - Commit stage < 10 minutes
6. **Stop the line** - Broken builds are highest priority
7. **Everyone owns the pipeline** - Not a separate team's problem
8. **AI output validation** - All AI-generated code must pass automated gates

---

## IMMEDIATE VALIDATION CHECKS

### On Every Code Change:
```
CHECK: Tests written for new/changed code?
  IF NO → REJECT: "Write tests first, then implementation"
  
CHECK: Pre-commit hooks configured and passing?
  IF NO → REJECT: "Configure pre-commit hooks: linting, formatting, secrets scan"
  
CHECK: Branch age < 24 hours?
  IF NO → WARNING: "Branch too old - merge trunk changes and integrate"
  
CHECK: Build time < 10 minutes?
  IF NO → OPTIMIZE: "Split slow tests into later stages"
  
CHECK: AI-generated code validated?
  IF NO → REJECT: "AI output must pass security and quality gates"
  
CHECK: Infrastructure changes have specifications?
  IF NO → REJECT: "Write infrastructure spec before IaC code"
```

---

## VERSION CONTROL REQUIREMENTS

### What MUST Be in Version Control:
```yaml
required_in_vcs:
  - application_code: All source files
  - test_code: Unit, integration, e2e tests  
  - pipeline_definitions: CI/CD config files
  - infrastructure_code: Terraform, CloudFormation, CDK
  - infrastructure_specs: Plain-English IaC specifications
  - deployment_scripts: All deploy automation
  - database_migrations: Schema changes, data scripts
  - configuration_templates: Environment configs
  - documentation: README, architecture, runbooks
  - ai_configurations: .ai/ directory with prompts, validation rules
  - orr_checklists: Operational readiness review templates
```

### Branch & Integration Rules:
```
ENFORCE:
  - Trunk-based development (main/master as primary branch)
  - Branches live < 2 days maximum
  - Merge from trunk to branch daily if branch exists
  - Commit to trunk at least daily
  - No feature branches beyond one iteration

IF branch_age > 2 days:
  ERROR: "Branch too old. Merge or abandon."
  
IF last_trunk_merge > 24 hours:
  ERROR: "Pull latest from trunk before continuing"
```

---

## AI TOOL SECURITY & ISOLATION

### Security by Design for AI Tools
```yaml
ai_tool_requirements:
  network_access: "none"  # No internet access
  system_privileges: "read-only"  # Cannot modify system
  code_access: "read-only"  # Cannot change source files
  execution_environment: "sandboxed"  # Isolated container
  
  secrets_protection:
    - Never expose credentials to AI tools
    - Use temporary, scoped tokens if needed
    - Rotate credentials after AI tool usage
    - Audit all AI tool access logs

REJECT IF:
  - AI tool has write access to production systems
  - AI tool can access secrets/credentials
  - AI-generated IaC contains hardcoded secrets
```

**ENFORCEMENT:**
```bash
# AI tool isolation check
if ai_tool_has_network_access || ai_tool_has_write_access:
    REJECT: "AI tools must run in isolated, read-only environments"

# Secrets scan for AI output
git diff --cached | detect-secrets scan - || {
    REJECT: "AI-generated code contains secrets"
}
```

---

## AI OUTPUT VALIDATION GATES

### Automated AI Validation Pipeline
```yaml
ai_validation_stages:
  static_analysis:
    - syntax_check: "Verify code compiles/parses"
    - linting: "Check style and conventions"
    - complexity: "Reject if cyclomatic complexity > 10"
    
  security_scanning:
    - sast: "Static application security testing"
    - dependency_check: "Known vulnerabilities in dependencies"
    - secrets_scan: "No hardcoded credentials"
    - permission_check: "No overly permissive access"
    
  contract_validation:
    - interface_check: "AI components have defined contracts"
    - error_handling: "Proper error boundaries"
    - fallback_mechanisms: "Graceful degradation defined"
    
  performance_baseline:
    - latency_test: "Compare against baseline"
    - resource_usage: "Memory/CPU within limits"
    - load_test: "Handles expected traffic"
    
  ai_specific_checks:
    - model_version: "Documented model used"
    - confidence_thresholds: "Minimum confidence defined"
    - bias_testing: "No discriminatory behavior"
    - explainability: "Decision reasoning available"
```

**ENFORCEMENT:**
```python
# Every AI-generated code must pass:
def validate_ai_output(code_path):
    checks = [
        run_static_analysis(code_path),
        run_security_scan(code_path),
        verify_contracts(code_path),
        test_performance(code_path),
        validate_ai_specifics(code_path)
    ]
    
    if not all(checks):
        REJECT: "AI output failed validation gates"
```

---

## INFRASTRUCTURE AS SPECIFICATIONS

### Specification-First Infrastructure
```yaml
# REJECT: Direct IaC coding without spec
resource "aws_instance" "web" {  # ❌ Where's the spec?
  ami           = "ami-123456"
  instance_type = "t2.micro"
}

# REQUIRE: Specification → IaC generation
specification:  # ✓ Write this first
  description: "Web server for customer portal"
  requirements:
    - "High availability across 2 AZs"
    - "Auto-scaling 2-10 instances"
    - "HTTPS only with WAF"
    - "Automated backups daily"
    
generated_iac:  # ✓ AI generates from spec
  - Auto-scaling group with health checks
  - Application Load Balancer with SSL
  - WAF rules for common attacks
  - Backup plan with lifecycle policies
```

**ENFORCEMENT:**
```bash
# Check for infrastructure specifications
for iac_file in $(git diff --cached --name-only | grep -E "\.(tf|yaml|json)$"); do
    spec_file="${iac_file%.tf}.spec.md"
    if [ ! -f "$spec_file" ]; then
        REJECT: "Infrastructure code requires specification: $spec_file"
    fi
done
```

---

## OPERATIONAL READINESS REVIEWS (ORR)

### Pre-Deployment ORR Checklist
```yaml
orr_requirements:
  automated_checks:  # Must pass before deployment
    rollback_plan:
      - tested: true
      - automated: true
      - time_to_rollback: "< 5 minutes"
    
    monitoring:
      - health_checks: "Endpoint configured"
      - metrics: "CloudWatch/Datadog configured"
      - logging: "Structured JSON with correlation IDs"
      - alerts: "Critical paths covered"
    
    security:
      - secrets_management: "Using vault/KMS"
      - iam_least_privilege: true
      - network_isolation: "Security groups configured"
      - encryption: "At rest and in transit"
    
    operational:
      - runbook: "Updated for this release"
      - oncall: "Team notified"
      - communication_plan: "Stakeholders informed"
      - feature_flags: "Kill switch available"
    
  historical_learning:  # From past incidents
    - check_memory_limits: "Prevents OOM from incident #123"
    - verify_timeout_settings: "Prevents cascade from incident #456"
    - validate_retry_logic: "Prevents storm from incident #789"
```

**ENFORCEMENT:**
```python
def pre_deployment_orr():
    """Run before any production deployment."""
    orr_checklist = load_orr_checklist()
    
    # Add checks from historical incidents
    orr_checklist.extend(get_incident_derived_checks())
    
    for check in orr_checklist:
        if not check.validate():
            REJECT: f"ORR failed: {check.name} - {check.remediation}"
    
    generate_orr_report()
```

---

## BUILD & ARTIFACT MANAGEMENT

### Build Once, Deploy Everywhere:
```python
# CORRECT Pattern:
build_stage:
  - compile_code()
  - run_unit_tests()  
  - validate_ai_output()  # New: AI validation
  - create_artifact(version="1.2.3")
  - sign_artifact()  # Sign for integrity
  - store_in_repository(artifact_id)
  
deploy_to_env(environment, artifact_id):
  - fetch_artifact(artifact_id)  # Same artifact
  - verify_signature()  # Verify integrity
  - apply_config(environment)     # Environment-specific config
  - deploy()
  - run_orr_checks()  # Pre-deployment validation

# REJECT Pattern:
deploy_to_prod:
  - compile_code()  # ❌ NO! Rebuilding for each env
  - deploy()
```

### Artifact Requirements:
```yaml
every_artifact_must_have:
  - unique_version: "Traceable to commit SHA"
  - digital_signature: "Verify integrity"
  - dependency_lock_file: "Reproducible builds"
  - build_metadata: "Timestamp, builder, commit"
  - ai_generation_metadata: "Model version, prompts used"
  - sbom: "Software Bill of Materials"
```

---

## MODEL & AI COMPONENT CI/CD

### Continuous Integration for AI
```yaml
ai_ci_pipeline:
  model_validation:
    - version_check: "Model version documented"
    - performance_regression: "Accuracy >= baseline"
    - latency_check: "Inference time < SLA"
    - bias_detection: "Fairness metrics pass"
    
  integration_testing:
    - api_contract: "Model API matches specification"
    - error_handling: "Graceful degradation works"
    - fallback_behavior: "Non-AI fallback available"
    - resource_limits: "Memory/CPU within bounds"
    
  data_validation:
    - schema_check: "Input/output formats verified"
    - edge_cases: "Handles empty, null, malformed"
    - volume_testing: "Handles production scale"
    
  model_artifacts:
    - model_registry: "Version stored with metadata"
    - reproducibility: "Training can be reproduced"
    - rollback_capability: "Previous version available"
```

**ENFORCEMENT:**
```bash
# AI component deployment gate
if deploying_ai_component; then
    pytest tests/model_validation/ --benchmark-baseline || {
        REJECT: "Model performance regression detected"
    }
    
    pytest tests/bias_detection/ || {
        REJECT: "Model bias detected"
    }
    
    verify_model_contract || {
        REJECT: "Model API contract violation"
    }
fi
```

---

## TESTING AUTOMATION

### Test Pyramid Enforcement:
```
Unit Tests (70%):
  - Run on EVERY commit
  - Must complete < 2 minutes
  - No external dependencies
  - Mock AI model responses
  
Integration Tests (20%):
  - Run after unit tests pass
  - Test component interactions
  - Test AI model integration points
  - Use test doubles for external services
  
E2E Tests (10%):
  - Run in staging environment
  - Test critical user journeys only
  - Include AI-assisted workflows
  - Parallel execution required

AI-Specific Tests:
  - Model performance benchmarks
  - Confidence threshold validation
  - Fallback mechanism testing
  - Bias and fairness checks

REJECT if:
  - No tests for new code
  - Tests require manual setup
  - Flaky tests not fixed/removed
  - Test coverage decreases
  - AI components lack contract tests
```

---

## DEPLOYMENT SAFETY

### Progressive Deployment Patterns:
```yaml
deployment_strategy:
  required_capabilities:
    - blue_green: "Zero-downtime deployments"
    - canary: "Gradual rollout with monitoring"
    - feature_flags: "Decouple deploy from release"
    - automated_rollback: "Revert on error detection"
    - ai_model_gradual_rollout: "Progressive AI model deployment"
    
  ai_deployment_specific:
    - shadow_mode: "Run new model alongside old"
    - confidence_gating: "Only use high-confidence predictions"
    - gradual_traffic_shift: "5% → 25% → 50% → 100%"
    - performance_monitoring: "Track model metrics in real-time"
    
  reject_patterns:
    - all_at_once: "Big bang deployments"
    - manual_rollback: "Requiring human intervention"
    - downtime_required: "Taking service offline"
    - untested_ai_models: "Deploying without validation"
```

---

## MONITORING & OBSERVABILITY

### Required Metrics:
```yaml
dora_metrics:
  deployment_frequency: "> 1/day"
  lead_time: "< 1 day"
  mttr: "< 1 hour"
  change_failure_rate: "< 15%"

pipeline_metrics:
  build_time: "< 10 min"
  test_coverage: "> 80%"
  pipeline_success_rate: "> 90%"
  
ai_metrics:
  model_accuracy: "> baseline"
  inference_latency: "< 100ms"
  model_drift: "< 5% monthly"
  ai_generation_success_rate: "> 95%"
  fallback_activation_rate: "< 1%"
```

### Monitoring Requirements:
```python
# Every service MUST expose:
health_endpoint = "/health"
metrics_endpoint = "/metrics"
readiness_probe = "/ready"
model_info_endpoint = "/model/info"  # AI model metadata

# Every deployment MUST:
- Log deployment events with correlation IDs
- Track error rates per deployment
- Monitor performance vs baseline
- Alert on anomalies
- Track AI model performance metrics
```

---

## DATABASE CHANGE REQUIREMENTS

### Migration Rules:
```sql
-- EVERY database change MUST:
-- 1. Be backwards compatible
-- 2. Be in a versioned migration file
-- 3. Include rollback script
-- 4. Be tested in staging first
-- 5. Pass ORR checklist

-- CORRECT:
-- V1_add_user_email.up.sql
ALTER TABLE users ADD COLUMN email VARCHAR(255);

-- V1_add_user_email.down.sql  
ALTER TABLE users DROP COLUMN email;

-- REJECT: Direct production changes
```

---

## ANTI-PATTERNS TO REJECT

### ❌ REJECT: Manual Processes
```bash
# If documentation includes:
"SSH into server and run..."
"Copy files manually to..."
"Ask DevOps team to..."
"Manually validate AI output..."
→ ERROR: "Automate this process"
```

### ❌ REJECT: Long-Lived Branches
```python
if (datetime.now() - branch_created) > timedelta(days=2):
    ERROR: "Branch exceeds 2-day limit"
```

### ❌ REJECT: Unvalidated AI Output
```python
if ai_generated_code and not validation_passed:
    ERROR: "AI output must pass all validation gates"
```

### ❌ REJECT: Missing ORR
```python
if production_deployment and not orr_completed:
    ERROR: "Operational Readiness Review required"
```

---

## QUICK REFERENCE COMMANDS

### Daily Development Flow:
```bash
# Morning sync
git checkout main
git pull
./run_tests.sh  # Verify clean state

# Feature development
git checkout -b feature-xyz
# Write tests first...
# Implement feature...
# Validate AI output if used...
./run_tests.sh  # Local validation
./run_orr_checks.sh  # Pre-deployment checks

# Integration (same day!)
git checkout main
git pull
git merge feature-xyz
./run_tests.sh
git push

# Monitor pipeline
watch_pipeline_status
verify_deployment_metrics
```

### Pre-Commit Checklist:
```bash
#!/bin/bash
# Add to .git/hooks/pre-commit

echo "Running pre-commit checks..."
check_secrets || exit 1
run_linters || exit 1
run_unit_tests || exit 1
check_branch_age || exit 1
validate_ai_output || exit 1
check_infrastructure_specs || exit 1
echo "✓ All checks passed"
```

---

## FOR CLAUDE CODE / AI ASSISTANTS

When reviewing changes:

### 1. CHECK VERSION CONTROL
```python
if not in_version_control(change):
    REJECT("All changes must be in version control")
    
if "infrastructure_spec" not in files:
    REJECT("Infrastructure needs specification first")
```

### 2. VALIDATE TESTING
```python
if not tests_exist_for(change):
    REJECT("Write tests before implementation")
    
if ai_component and not contract_tests:
    REJECT("AI components need contract tests")
```

### 3. SCAN SECURITY
```python
if contains_secrets(code):
    REJECT("Remove hardcoded secrets")
    
if ai_tool_has_write_access:
    REJECT("AI tools must be read-only")
```

### 4. VERIFY AI OUTPUT
```python
if ai_generated_code:
    if not passed_static_analysis:
        REJECT("AI output failed static analysis")
    if not passed_security_scan:
        REJECT("AI output has security issues")
    if not has_performance_baseline:
        REJECT("Establish performance baseline")
```

### 5. CHECK OPERATIONAL READINESS
```python
if production_deployment:
    if not orr_checklist_complete:
        REJECT("Complete ORR checklist")
    if not rollback_tested:
        REJECT("Test rollback procedure")
```

---

## ENFORCEMENT CONFIGURATION

### Add to `.claude/config.json`:
```json
{
  "ci_cd_rules": {
    "enforce": true,
    "max_branch_age_hours": 48,
    "min_test_coverage": 80,
    "max_build_minutes": 10,
    "require_pre_commit_hooks": true,
    "require_ai_validation": true,
    "require_infrastructure_specs": true,
    "require_orr": true
  },
  "ai_validation": {
    "static_analysis": true,
    "security_scan": true,
    "contract_validation": true,
    "performance_baseline": true
  },
  "validation_commands": {
    "pre_commit": "pre-commit run --all-files",
    "test": "./run_tests.sh",
    "security": "security_scan .",
    "pipeline": "validate_pipeline_config",
    "ai_output": "validate_ai_output",
    "orr": "run_orr_checklist"
  }
}
```

---

## REVIEW CHECKLIST

Before approving ANY change:

### Version Control & Integration
- [ ] In version control
- [ ] Branch < 2 days old
- [ ] Tests written and passing
- [ ] Infrastructure has specifications

### AI & Security
- [ ] AI output validated
- [ ] AI tools properly isolated
- [ ] No hardcoded secrets
- [ ] Security scans passing

### Build & Deployment
- [ ] Build time < 10 minutes
- [ ] Artifacts properly versioned
- [ ] Progressive deployment configured
- [ ] Rollback procedure tested

### Operational Readiness
- [ ] ORR checklist complete
- [ ] Monitoring configured
- [ ] Alerts defined
- [ ] Runbooks updated
- [ ] Historical incident checks passed

### Quality Gates
- [ ] Test coverage > 80%
- [ ] Static analysis passing
- [ ] Performance baselines met
- [ ] Documentation updated

**Remember: If it's not automated, it's broken. If it's not tested, it doesn't work. If there's no rollback, don't deploy.**