# Open Policy Agent (OPA) Rego Policy for Network Security Controls
# Generated from security requirements using AI assistance

package network.security

# Default deny policy - all traffic denied unless explicitly allowed
default allow = false
default deny_reason = "Default deny - no matching allow rule"

# Allow internal service-to-service communication
allow {
    input.source.namespace == "ai-development"
    input.destination.namespace == "ai-development"  
    input.destination.port in [8080, 8443, 5432, 6379]
    input.protocol == "tcp"
}

# Allow ingress traffic to public endpoints
allow {
    input.source.type == "external"
    input.destination.namespace == "ai-development"
    input.destination.service == "api-gateway"
    input.destination.port in [80, 443]
    input.protocol == "tcp"
}

# Database access restrictions
allow {
    input.source.namespace == "ai-development"
    input.source.service in ["api-server", "worker"]
    input.destination.service == "postgresql"
    input.destination.port == 5432
    input.protocol == "tcp"
}

# Redis cache access
allow {
    input.source.namespace == "ai-development"
    input.source.service in ["api-server", "session-manager"]
    input.destination.service == "redis"
    input.destination.port == 6379
    input.protocol == "tcp"
}

# Deny direct database access from external sources
deny_reason = "Direct database access from external source prohibited" {
    input.source.type == "external"
    input.destination.service in ["postgresql", "redis"]
}

# AI Sandbox network isolation
deny_reason = "AI sandbox cannot access external networks" {
    input.source.namespace == "ai-sandbox"
    input.destination.type == "external"
}

deny_reason = "External access to AI sandbox prohibited" {
    input.source.type == "external"
    input.destination.namespace == "ai-sandbox"
}

# Allow AI sandbox internal communication only
allow {
    input.source.namespace == "ai-sandbox"
    input.destination.namespace == "ai-sandbox"
    input.protocol == "tcp"
}

# Time-based access controls
deny_reason = "Access denied during maintenance window" {
    maintenance_window
    not emergency_access
}

maintenance_window {
    time.parse_ns("15:04:05Z07:00", time.now_ns()) >= time.parse_ns("02:00:00Z", "02:00:00Z")
    time.parse_ns("15:04:05Z07:00", time.now_ns()) <= time.parse_ns("04:00:00Z", "04:00:00Z")
}

emergency_access {
    input.source.labels.emergency == "true"
    input.source.labels.justification != ""
}

# Geographic restrictions
deny_reason = "Access from restricted geographic location" {
    input.source.country in ["CN", "KP", "IR", "SY"]
    input.destination.namespace == "ai-development"
}

# Rate limiting enforcement
deny_reason = "Rate limit exceeded for source IP" {
    rate_limit_exceeded
}

rate_limit_exceeded {
    input.source.ip
    request_count := data.rate_limits[input.source.ip].count
    request_count > 1000
    window_start := data.rate_limits[input.source.ip].window_start
    (time.now_ns() - window_start) < 3600000000000  # 1 hour in nanoseconds
}

# Protocol restrictions
deny_reason = "Unsupported protocol" {
    not input.protocol in ["tcp", "udp", "icmp"]
}

# Port scanning detection
deny_reason = "Port scanning detected" {
    port_scan_detected
}

port_scan_detected {
    input.source.ip
    ports := [port | port := data.connection_logs[input.source.ip][_].destination_port]
    count(ports) > 10
    # Multiple unique destination ports from same source in short time
}

# SSL/TLS enforcement
deny_reason = "Unencrypted traffic to sensitive services" {
    input.destination.service in ["api-server", "admin-panel"]
    input.destination.port in [80, 8080]  # Non-SSL ports
    not input.encryption == "tls"
}

# Service mesh security
allow {
    input.source.service_account != ""
    input.destination.service_account != ""
    input.mutual_tls == true
    service_account_authorized
}

service_account_authorized {
    allowed_connections := data.service_mesh.allowed_connections
    some i
    allowed_connections[i].source == input.source.service_account
    allowed_connections[i].destination == input.destination.service_account
}

# Monitoring and logging requirements
allow {
    input.source.namespace == "monitoring"
    input.destination.namespace in ["ai-development", "ai-sandbox"]
    input.destination.port in [9090, 9093, 3000]  # Prometheus, Alertmanager, Grafana
    input.protocol == "tcp"
}

# CI/CD pipeline access
allow {
    input.source.namespace == "ci-cd"
    input.destination.namespace == "ai-development"
    input.source.service == "github-runner"
    input.destination.service == "deployment-api"
    input.destination.port == 8443
    input.protocol == "tcp"
}

# Emergency access procedures
allow {
    input.source.labels.emergency_access == "true"
    input.source.labels.incident_id != ""
    input.source.labels.authorized_by != ""
    emergency_time_window
}

emergency_time_window {
    incident_start := time.parse_rfc3339_ns(input.source.labels.incident_start)
    current_time := time.now_ns()
    (current_time - incident_start) < 14400000000000  # 4 hours in nanoseconds
}

# Data residency compliance
deny_reason = "Data transfer to non-compliant region" {
    input.destination.region not in ["us-east-1", "us-west-2", "eu-west-1"]
    input.data_classification == "sensitive"
}

# Zero-trust network validation
allow {
    zero_trust_validated
}

zero_trust_validated {
    # Identity verification
    input.source.identity_verified == true
    
    # Device compliance
    input.source.device_compliant == true
    
    # Application authorization
    input.destination.application_authorized == true
    
    # Risk assessment
    input.risk_score < 50
}

# Logging and audit trail
audit_log = {
    "timestamp": time.now_ns(),
    "source": input.source,
    "destination": input.destination,
    "action": "network_access",
    "decision": allow,
    "reason": deny_reason,
    "policy_version": "1.0"
}

# Policy violation severity levels
violation_severity = "critical" {
    deny_reason in [
        "AI sandbox cannot access external networks",
        "Direct database access from external source prohibited"
    ]
}

violation_severity = "high" {
    deny_reason in [
        "Access from restricted geographic location",
        "Unencrypted traffic to sensitive services"
    ]
}

violation_severity = "medium" {
    deny_reason in [
        "Rate limit exceeded for source IP",
        "Port scanning detected"
    ]
}

violation_severity = "low" {
    not violation_severity in ["critical", "high", "medium"]
}