# Chaos Engineering Scenarios

## Overview
This directory contains chaos engineering scenarios based on the AI Development Patterns. Each scenario is designed to test system resilience and recovery capabilities.

## Scenario 1: Service Instance Failure

### Target: Authentication Service
```yaml
scenario: auth_service_instance_failure
description: Kill 1 of 3 authentication service instances every 5 minutes
targets:
  - service: auth-service
    namespace: ai-development
    instances: 3
    kill_count: 1
actions:
  - type: pod_kill
    frequency: 5m
    selection: random
validation:
  - service_available: true
  - response_time_p95: <1000ms
  - error_rate: <5%
```

### AI Generation Prompt
```bash
ai "From services.json, generate a Gremlin script to:
- Target auth-service pods in ai-development namespace
- Kill 1 of 3 instances every 5 minutes
- Validate service remains available
- Alert if error rate exceeds 5%"
```

## Scenario 2: Database Connection Chaos

### Target: PostgreSQL Connections
```yaml
scenario: database_connection_chaos
description: Randomly drop database connections to test connection pool resilience
targets:
  - service: postgresql
    port: 5432
    connection_pool_size: 20
actions:
  - type: network_blackhole
    frequency: 10m
    duration: 30s
    percentage: 25
validation:
  - connection_pool_recovery: <5s
  - queries_failed: <1%
  - application_recovery: automatic
```

## Scenario 3: Memory Pressure Test

### Target: API Server Pods
```yaml
scenario: memory_pressure_test
description: Gradually increase memory usage to test OOM handling
targets:
  - service: api-server
    memory_limit: 512MB
actions:
  - type: memory_stress
    start: 100MB
    increment: 50MB
    interval: 2m
    max: 450MB
validation:
  - garbage_collection: triggered
  - response_degradation: <20%
  - pod_restart: graceful
```

## Scenario 4: Network Latency Injection

### Target: Inter-Service Communication
```yaml
scenario: network_latency_chaos
description: Inject variable latency between microservices
targets:
  - source: api-gateway
    destination: auth-service
  - source: auth-service
    destination: database
actions:
  - type: network_latency
    min_delay: 50ms
    max_delay: 500ms
    distribution: normal
    duration: 15m
validation:
  - circuit_breaker: activated
  - fallback_responses: working
  - user_experience: degraded_but_functional
```

## Scenario 5: Cache Failure Simulation

### Target: Redis Cache
```yaml
scenario: cache_failure
description: Simulate Redis cache unavailability
targets:
  - service: redis
    port: 6379
actions:
  - type: service_stop
    duration: 5m
    recovery: automatic
validation:
  - cache_fallback: database
  - performance_impact: <50% degradation
  - data_consistency: maintained
```

## Running Chaos Experiments

### Prerequisites
```bash
# Install chaos engineering tools
pip install chaostoolkit
brew install gremlin

# Verify cluster access
kubectl get pods -n ai-development
```

### Execute Scenarios
```bash
# Run specific scenario
chaos run monitoring/chaos/scenario_1.json

# Run with AI assistance
ai "Execute chaos scenario for auth service failure and generate report"

# Schedule recurring chaos
kubectl apply -f monitoring/chaos/schedules/weekly_chaos.yaml
```

### Monitoring During Chaos
```bash
# Watch service metrics
watch -n 1 'kubectl top pods -n ai-development'

# Monitor error rates
curl -s http://prometheus:9090/api/v1/query?query=http_requests_errors_total

# Check circuit breaker status
kubectl logs -n ai-development deployment/api-gateway | grep circuit
```

## Best Practices

1. **Start Small**: Begin with single instance failures before complex scenarios
2. **Monitor Actively**: Have dashboards open during experiments
3. **Document Findings**: Record all failures and recovery patterns
4. **Automate Recovery**: Ensure all scenarios have automated recovery
5. **Game Days**: Run chaos experiments during business hours with teams present

## AI-Generated Chaos Patterns

### Generate New Scenarios
```bash
ai "Based on our architecture in services.json:
- Identify top 5 failure points
- Generate chaos scenarios for each
- Include validation criteria
- Suggest monitoring queries"
```

### Analyze Results
```bash
ai "Analyze chaos experiment results from last week:
- Identify patterns in failures
- Suggest architectural improvements
- Recommend new chaos scenarios
- Generate executive summary"
```