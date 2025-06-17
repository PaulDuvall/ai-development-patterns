# Blue-Green Deployment Pattern

## Overview
AI-guided blue-green deployment scripts with validation to ensure proper atomic traffic switching, based on Martin Fowler's blue-green deployment pattern.

⚠️ **CRITICAL**: This is NOT canary deployment. Traffic switches 100% atomically, not gradually.

## Core Principles from Martin Fowler

1. **Two Identical Environments**: Blue (live) and Green (idle)
2. **Deploy to Idle Environment**: New version goes to the idle environment only
3. **Test Thoroughly**: Complete validation in idle environment before switch
4. **Atomic Traffic Switch**: 100% traffic switches instantly via load balancer
5. **Keep Previous Version**: Blue environment remains as rollback option

## Blue-Green Reference Documentation

```markdown
# Blue-Green Deployment Pattern

## Key Principles
1. Maintain two identical production environments: Blue (live) and Green (idle)
2. Deploy new version to the idle environment
3. Test thoroughly in idle environment
4. Switch traffic from Blue to Green atomically
5. Keep Blue as rollback option

## Critical: This is NOT canary deployment
- NO gradual traffic shifting
- NO percentage-based rollout
- Traffic switches 100% at once
```

## AWS Blue-Green Implementation

### Environment Setup
```bash
#!/bin/bash
# setup_blue_green_env.sh

# Blue-Green environment configuration
BLUE_ENV="ai-platform-blue"
GREEN_ENV="ai-platform-green"
ALB_ARN="arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/ai-platform-alb/abc123"

# Determine current active environment
CURRENT_ENV=$(aws elbv2 describe-target-groups \
  --load-balancer-arn $ALB_ARN \
  --query 'TargetGroups[0].TargetGroupName' \
  --output text)

if [[ $CURRENT_ENV == *"blue"* ]]; then
  ACTIVE_ENV="blue"
  IDLE_ENV="green"
  ACTIVE_TG_ARN=$(aws elbv2 describe-target-groups --names ai-platform-blue-tg --query 'TargetGroups[0].TargetGroupArn' --output text)
  IDLE_TG_ARN=$(aws elbv2 describe-target-groups --names ai-platform-green-tg --query 'TargetGroups[0].TargetGroupArn' --output text)
else
  ACTIVE_ENV="green"
  IDLE_ENV="blue"  
  ACTIVE_TG_ARN=$(aws elbv2 describe-target-groups --names ai-platform-green-tg --query 'TargetGroups[0].TargetGroupArn' --output text)
  IDLE_TG_ARN=$(aws elbv2 describe-target-groups --names ai-platform-blue-tg --query 'TargetGroups[0].TargetGroupArn' --output text)
fi

echo "Current active environment: $ACTIVE_ENV"
echo "Deploying to idle environment: $IDLE_ENV"
```

### Deployment Script with AI Validation
```bash
#!/bin/bash
# deploy_blue_green.sh

set -euo pipefail

# Import blue-green principles
source blue_green_principles.sh

# Validate this is blue-green, not canary
validate_deployment_pattern() {
  ai "Validate this deployment script follows blue-green pattern:
  
  Script: $0
  Current logic: $1
  
  Verify:
  1. Deploys ONLY to idle environment
  2. No gradual traffic shifting
  3. Atomic 100% traffic switch
  4. Previous environment kept for rollback
  
  If this looks like canary deployment, FAIL with explanation."
  
  if [[ $? -ne 0 ]]; then
    echo "❌ ERROR: AI detected canary deployment pattern"
    exit 1
  fi
}

# Step 1: Deploy to IDLE environment only
deploy_to_idle() {
  echo "🚀 Deploying to IDLE environment: $IDLE_ENV"
  
  # Update ECS service in idle environment
  aws ecs update-service \
    --cluster "ai-platform-$IDLE_ENV" \
    --service "api-server-$IDLE_ENV" \
    --task-definition "ai-platform-api:$BUILD_NUMBER" \
    --force-new-deployment
    
  # Wait for deployment to complete
  aws ecs wait services-stable \
    --cluster "ai-platform-$IDLE_ENV" \
    --services "api-server-$IDLE_ENV"
    
  echo "✅ Deployment to $IDLE_ENV completed"
}

# Step 2: Health check idle environment
health_check_idle() {
  echo "🔍 Running health checks on IDLE environment"
  
  # Get idle environment endpoint
  IDLE_ENDPOINT=$(aws elbv2 describe-target-groups \
    --target-group-arns $IDLE_TG_ARN \
    --query 'TargetGroups[0].HealthCheckPath' \
    --output text)
    
  # Direct health check (bypass load balancer)
  IDLE_INSTANCE=$(aws ecs describe-tasks \
    --cluster "ai-platform-$IDLE_ENV" \
    --tasks $(aws ecs list-tasks --cluster "ai-platform-$IDLE_ENV" --query 'taskArns[0]' --output text) \
    --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
    --output text)
    
  IDLE_IP=$(aws ec2 describe-network-interfaces \
    --network-interface-ids $IDLE_INSTANCE \
    --query 'NetworkInterfaces[0].PrivateIpAddress' \
    --output text)
    
  # Comprehensive health checks
  for check in health api-status database-connectivity auth-service; do
    echo "Checking $check..."
    response=$(curl -sf "http://$IDLE_IP:8080/$check" || echo "FAILED")
    
    if [[ $response == "FAILED" ]]; then
      echo "❌ Health check failed: $check"
      exit 1
    fi
    
    echo "✅ $check: OK"
  done
  
  echo "✅ All health checks passed on IDLE environment"
}

# Step 3: Run full test suite against idle
run_idle_tests() {
  echo "🧪 Running test suite against IDLE environment"
  
  export TEST_ENDPOINT="http://$IDLE_IP:8080"
  
  # Run comprehensive test suite
  npm run test:integration || {
    echo "❌ Integration tests failed on IDLE environment"
    exit 1
  }
  
  npm run test:e2e || {
    echo "❌ E2E tests failed on IDLE environment"
    exit 1
  }
  
  # AI-powered smoke test validation
  ai "Run smoke tests against IDLE environment at $TEST_ENDPOINT:
  - Verify all critical user journeys work
  - Check authentication flow
  - Validate database connectivity
  - Confirm no 5xx errors in logs
  - Report any anomalies found"
  
  echo "✅ All tests passed on IDLE environment"
}

# Step 4: ATOMIC traffic switch
atomic_traffic_switch() {
  echo "🔄 Performing ATOMIC traffic switch"
  
  # Validate this is atomic switch, not gradual
  validate_deployment_pattern "atomic_switch"
  
  # Confirm atomic switch with operator
  echo "About to switch ALL traffic from $ACTIVE_ENV to $IDLE_ENV"
  echo "This is an ATOMIC operation - 100% traffic switches instantly"
  read -p "Continue? (yes/no): " confirm
  
  if [[ $confirm != "yes" ]]; then
    echo "Deployment cancelled by operator"
    exit 1
  fi
  
  # Get current listener rules
  LISTENER_ARN=$(aws elbv2 describe-listeners \
    --load-balancer-arn $ALB_ARN \
    --query 'Listeners[0].ListenerArn' \
    --output text)
  
  # ATOMIC SWITCH: Update listener to point to idle target group
  aws elbv2 modify-listener \
    --listener-arn $LISTENER_ARN \
    --default-actions Type=forward,TargetGroupArn=$IDLE_TG_ARN
    
  echo "🚀 ATOMIC traffic switch completed!"
  echo "All traffic now routed to: $IDLE_ENV"
  
  # Update environment labels
  ACTIVE_ENV=$IDLE_ENV
  if [[ $IDLE_ENV == "blue" ]]; then
    IDLE_ENV="green"
  else
    IDLE_ENV="blue" 
  fi
}

# Step 5: Post-switch validation
post_switch_validation() {
  echo "🔍 Post-switch validation"
  
  # Wait for traffic to flow
  sleep 30
  
  # Check error rates
  ERROR_RATE=$(aws cloudwatch get-metric-statistics \
    --namespace AWS/ApplicationELB \
    --metric-name HTTPCode_Target_5XX_Count \
    --dimensions Name=LoadBalancer,Value=$ALB_ARN \
    --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text)
    
  if [[ $ERROR_RATE != "None" && $ERROR_RATE -gt 10 ]]; then
    echo "⚠️  High error rate detected: $ERROR_RATE errors in 5 minutes"
    echo "Consider immediate rollback"
  fi
  
  # AI-powered traffic analysis
  ai "Analyze traffic patterns after blue-green switch:
  - Compare error rates before/after switch
  - Check response time distribution
  - Identify any anomalous patterns
  - Recommend rollback if issues detected"
  
  echo "✅ Post-switch validation completed"
}

# Step 6: Cleanup previous version (optional)
cleanup_previous_version() {
  echo "🧹 Previous version cleanup (idle environment: $IDLE_ENV)"
  echo "Previous version kept running for rollback capability"
  echo "To stop previous version: aws ecs update-service --cluster ai-platform-$IDLE_ENV --service api-server-$IDLE_ENV --desired-count 0"
}

# Main deployment flow
main() {
  echo "🔵🟢 Blue-Green Deployment Starting"
  echo "=================================="
  
  # Validation that this is blue-green, not canary
  if grep -q "canary\|gradual\|percentage" "$0"; then
    echo "❌ ERROR: Canary deployment detected in blue-green script"
    exit 1
  fi
  
  setup_blue_green_env
  validate_deployment_pattern "initial"
  deploy_to_idle
  health_check_idle
  run_idle_tests
  atomic_traffic_switch
  post_switch_validation
  cleanup_previous_version
  
  echo "✅ Blue-Green deployment completed successfully!"
  echo "Active environment: $ACTIVE_ENV"
  echo "Idle environment: $IDLE_ENV (available for rollback)"
}

# Rollback function
rollback() {
  echo "🔙 EMERGENCY ROLLBACK"
  
  # Switch back to previous environment atomically
  if [[ $ACTIVE_ENV == "blue" ]]; then
    ROLLBACK_TG_ARN=$(aws elbv2 describe-target-groups --names ai-platform-green-tg --query 'TargetGroups[0].TargetGroupArn' --output text)
  else
    ROLLBACK_TG_ARN=$(aws elbv2 describe-target-groups --names ai-platform-blue-tg --query 'TargetGroups[0].TargetGroupArn' --output text)
  fi
  
  aws elbv2 modify-listener \
    --listener-arn $LISTENER_ARN \
    --default-actions Type=forward,TargetGroupArn=$ROLLBACK_TG_ARN
    
  echo "✅ Rollback completed - traffic restored to previous version"
}

# Execute main deployment or rollback
if [[ ${1:-} == "rollback" ]]; then
  rollback
else
  main
fi
```

### Kubernetes Blue-Green Implementation
```yaml
# blue-green-k8s.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: ai-platform-rollout
spec:
  replicas: 5
  strategy:
    blueGreen:
      # Blue-green specific configuration
      activeService: ai-platform-active
      previewService: ai-platform-preview
      autoPromotionEnabled: false  # Manual promotion only
      
      # Pre-promotion analysis
      prePromotionAnalysis:
        templates:
        - templateName: health-check
        - templateName: integration-test
        args:
        - name: service-name
          value: ai-platform-preview
          
      # Post-promotion analysis  
      postPromotionAnalysis:
        templates:
        - templateName: post-deployment-validation
        args:
        - name: service-name
          value: ai-platform-active
          
      # Rollback configuration
      scaleDownDelaySeconds: 30
      prePromotionAnalysisRunMetadata:
        labels:
          deployment-type: blue-green
          
  selector:
    matchLabels:
      app: ai-platform
      
  template:
    metadata:
      labels:
        app: ai-platform
    spec:
      containers:
      - name: ai-platform
        image: ai-platform:BUILD_NUMBER
        ports:
        - containerPort: 8080
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10

---
# Analysis Templates
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: health-check
spec:
  args:
  - name: service-name
  metrics:
  - name: health-endpoint
    provider:
      web:
        url: "http://{{args.service-name}}/health"
        headers:
        - key: Host
          value: "ai-platform.example.com"
        jsonPath: "{$.status}"
    successCondition: result == "healthy"
    interval: 10s
    count: 5

---
apiVersion: argoproj.io/v1alpha1  
kind: AnalysisTemplate
metadata:
  name: integration-test
spec:
  args:
  - name: service-name
  metrics:
  - name: integration-tests
    provider:
      job:
        spec:
          template:
            spec:
              containers:
              - name: integration-test
                image: ai-platform-tests:latest
                env:
                - name: TEST_ENDPOINT
                  value: "http://{{args.service-name}}"
                command: ["npm", "run", "test:integration"]
              restartPolicy: Never
          backoffLimit: 1
    successCondition: result == "Succeeded"
```

### AI-Powered Blue-Green Validation
```bash
# AI validation throughout deployment
ai_validate_blue_green() {
  local phase=$1
  local context=$2
  
  ai "Validate blue-green deployment phase: $phase
  
  Context: $context
  
  Blue-Green Requirements:
  1. Two identical environments maintained
  2. Deploy only to idle environment  
  3. No traffic to new version until switch
  4. Atomic 100% traffic switch (not gradual)
  5. Previous version kept for rollback
  
  Current Phase: $phase
  Validation Points:
  - Is deployment going to correct (idle) environment?
  - Are we avoiding gradual traffic shifting?
  - Is switch atomic (100% at once)?
  - Is previous version preserved?
  
  FAIL if any canary deployment patterns detected.
  PASS only if pure blue-green pattern followed."
  
  if [[ $? -ne 0 ]]; then
    echo "❌ AI validation failed for blue-green pattern"
    exit 1
  fi
}
```

## Anti-Pattern Detection

### Canary vs Blue-Green Validation
```bash
# detect_deployment_pattern.sh
#!/bin/bash

detect_anti_patterns() {
  local script_file=$1
  
  echo "🔍 Detecting deployment anti-patterns..."
  
  # Check for canary deployment patterns
  if grep -qE "percentage|gradual|weight|traffic.*[0-9]+%" "$script_file"; then
    echo "❌ CANARY DEPLOYMENT DETECTED in blue-green script!"
    echo "Found patterns suggesting gradual traffic shifting:"
    grep -nE "percentage|gradual|weight|traffic.*[0-9]+%" "$script_file"
    exit 1
  fi
  
  # Check for proper blue-green patterns
  if ! grep -q "atomic" "$script_file"; then
    echo "⚠️  Missing 'atomic' traffic switch specification"
  fi
  
  if ! grep -qE "100%|all.*traffic" "$script_file"; then
    echo "⚠️  Missing 100% traffic switch confirmation"
  fi
  
  echo "✅ Blue-green pattern validation passed"
}

# AI-powered pattern analysis
ai "Analyze this deployment script for anti-patterns:

Script: $(cat $1)

Check for:
1. Canary deployment patterns (gradual rollout, percentage traffic)
2. Missing atomic switch logic
3. Improper environment management
4. Lack of rollback capability

Report any violations of blue-green deployment principles."
```

## Monitoring and Observability

### Blue-Green Deployment Metrics
```yaml
# blue-green-metrics.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: blue-green-metrics
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      
    scrape_configs:
    - job_name: blue-green-deployment
      static_configs:
      - targets: ['ai-platform-blue:9090', 'ai-platform-green:9090']
      
    rule_files:
    - "blue-green-rules.yml"
    
  blue-green-rules.yml: |
    groups:
    - name: blue-green-deployment
      rules:
      - alert: BlueGreenTrafficSwitchDetected
        expr: increase(http_requests_total[1m]) > 0
        for: 0m
        labels:
          severity: info
        annotations:
          summary: "Traffic switch detected in blue-green deployment"
          
      - alert: BlueGreenErrorSpike
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error rate spike after blue-green deployment"
          description: "Consider immediate rollback"
          
      - alert: BlueGreenDeploymentStuck
        expr: deployment_status{phase="switching"} == 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Blue-green deployment stuck in switching phase"
```

## Best Practices

1. **Environment Parity**: Blue and green environments must be identical
2. **Database Considerations**: Use backward-compatible schema changes
3. **Stateful Services**: Handle session state and data consistency
4. **Testing Rigor**: Comprehensive testing in idle environment
5. **Rollback Readiness**: Always keep previous version ready
6. **Monitoring**: Watch metrics closely during and after switch
7. **Documentation**: Clear procedures for emergency rollback

## Emergency Procedures

### Immediate Rollback
```bash
#!/bin/bash
# emergency_rollback.sh

echo "🚨 EMERGENCY BLUE-GREEN ROLLBACK 🚨"

# Get current ALB listener
LISTENER_ARN=$(aws elbv2 describe-listeners \
  --load-balancer-arn $ALB_ARN \
  --query 'Listeners[0].ListenerArn' \
  --output text)

# Determine rollback target group
if [[ $ACTIVE_ENV == "blue" ]]; then
  ROLLBACK_TG="ai-platform-green-tg"
else
  ROLLBACK_TG="ai-platform-blue-tg"
fi

ROLLBACK_TG_ARN=$(aws elbv2 describe-target-groups \
  --names $ROLLBACK_TG \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# ATOMIC ROLLBACK
aws elbv2 modify-listener \
  --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$ROLLBACK_TG_ARN

echo "✅ Emergency rollback completed"
echo "Traffic restored to previous environment: $ROLLBACK_TG"

# Notify teams
slack-notify "#alerts" "🚨 Emergency blue-green rollback executed"
```

## Deployment Checklist

### Pre-Deployment
- [ ] Both environments healthy and identical
- [ ] Database migrations backward compatible
- [ ] Feature flags configured for rollback
- [ ] Test suite passing in CI
- [ ] Monitoring dashboards ready

### During Deployment
- [ ] Deploy only to idle environment
- [ ] Health checks pass in idle environment
- [ ] Full test suite passes against idle environment
- [ ] Performance metrics within acceptable range
- [ ] No error rate spikes

### Post-Deployment
- [ ] Traffic successfully switched (100% atomic)
- [ ] Error rates remain stable
- [ ] Response times unchanged
- [ ] Business metrics normal
- [ ] Previous environment available for rollback

### Rollback Criteria
- [ ] Error rate >1% for >2 minutes
- [ ] Response time degradation >20%
- [ ] Failed health checks
- [ ] Customer impact reports
- [ ] Business metric anomalies