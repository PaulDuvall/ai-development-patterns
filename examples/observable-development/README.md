# Observable AI Development Implementation

This directory contains a complete implementation of the Observable AI Development pattern, providing comprehensive logging, tracing, and debugging capabilities that enable AI to understand system behavior and diagnose issues effectively.

## Overview

Observable AI Development ensures that:
- All system operations are logged with structured, AI-readable data
- Performance metrics are captured automatically
- Error conditions include sufficient context for AI diagnosis
- Debug information is easily extractable for AI analysis

## Files in this Implementation

- `observable_logging.py` - Core structured logging framework
- `performance_monitoring.py` - Performance monitoring decorators and utilities
- `debug_helpers.py` - AI-friendly debugging and log analysis tools
- `examples/` - Working examples of observable business logic
- `config/logging_config.json` - Logging configuration for different environments
- `tests/` - Test suite for observability features

## Quick Start

### Basic Observable Logging

```python
from observable_logging import log_operation, setup_logging

# Initialize logging
setup_logging(level="INFO", format="structured")

# Log business operations
def process_user_registration(user_data):
    log_operation("registration_start", user_id=user_data.get('id'))
    
    try:
        validate_user_data(user_data)
        log_operation("validation_success", user_id=user_data.get('id'))
        
        create_user_account(user_data)
        log_operation("account_created", user_id=user_data.get('id'))
        
    except ValidationError as e:
        log_operation("validation_error", 
                     user_id=user_data.get('id'), 
                     field=e.field, 
                     error=str(e))
        raise
```

### Performance Monitoring

```python
from performance_monitoring import monitor_performance

@monitor_performance
def expensive_database_operation(query_params):
    # Automatically logs duration and success/failure
    return database.execute_complex_query(query_params)
```

### Debug Analysis

```bash
# Extract AI-friendly debug information
python debug_helpers.py --analyze-errors --last-hour
python debug_helpers.py --performance-issues --threshold 500ms
```

## Core Features

### Structured Logging
- JSON-formatted log entries for easy parsing
- Consistent timestamp and operation identification
- Rich context data for AI analysis
- Correlation IDs for request tracing

### Performance Monitoring
- Automatic duration tracking for decorated functions
- Memory usage monitoring
- Database query performance tracking
- API response time measurement

### Error Context
- Detailed error information with stack traces
- Business context preservation during exceptions
- Error categorization and severity levels
- Recovery action suggestions

### AI-Friendly Debug Tools
- Log analysis utilities for pattern recognition
- Performance bottleneck identification
- Error clustering and categorization
- Automated troubleshooting suggestions

## Implementation Examples

### E-commerce Order Processing
```python
def process_order(order):
    log_operation("order_start", 
                 order_id=order.id, 
                 total=order.total,
                 items_count=len(order.items))
    
    try:
        # Inventory check with observability
        log_operation("inventory_check_start")
        inventory_result = check_inventory(order.items)
        log_operation("inventory_check_success", 
                     available_items=inventory_result.available_count)
        
        # Payment processing with monitoring
        log_operation("payment_start", 
                     method=order.payment_method,
                     amount=order.total)
        payment_result = charge_payment(order)
        log_operation("payment_success", 
                     transaction_id=payment_result.transaction_id,
                     processing_time_ms=payment_result.duration)
        
        return payment_result
        
    except InventoryError as e:
        log_operation("inventory_error", 
                     error=str(e), 
                     unavailable_items=e.unavailable_items)
        raise
    except PaymentError as e:
        log_operation("payment_error", 
                     error=str(e), 
                     code=e.code,
                     gateway_response=e.gateway_message)
        raise
```

### User Authentication System
```python
@monitor_performance
def authenticate_user(credentials):
    log_operation("auth_start", username=credentials.username)
    
    try:
        # Rate limiting check
        log_operation("rate_limit_check", username=credentials.username)
        check_rate_limits(credentials.username)
        
        # Password verification
        log_operation("password_verification_start")
        user = verify_credentials(credentials)
        log_operation("password_verification_success", user_id=user.id)
        
        # JWT token generation
        log_operation("token_generation_start")
        token = generate_jwt_token(user)
        log_operation("token_generation_success", 
                     user_id=user.id,
                     token_expires_at=token.expires_at)
        
        return token
        
    except RateLimitExceeded as e:
        log_operation("rate_limit_exceeded", 
                     username=credentials.username,
                     attempts=e.attempt_count,
                     reset_time=e.reset_at)
        raise
    except AuthenticationError as e:
        log_operation("authentication_failed", 
                     username=credentials.username,
                     reason=e.reason)
        raise
```

## Configuration

### Logging Levels by Environment
```json
{
  "development": {
    "level": "DEBUG",
    "format": "structured",
    "include_stack_trace": true
  },
  "staging": {
    "level": "INFO", 
    "format": "structured",
    "include_stack_trace": true
  },
  "production": {
    "level": "WARN",
    "format": "structured", 
    "include_stack_trace": false,
    "sanitize_sensitive_data": true
  }
}
```

### Performance Monitoring Thresholds
```python
PERFORMANCE_THRESHOLDS = {
    "database_query": 100,  # ms
    "api_request": 500,     # ms
    "file_operation": 50,   # ms
    "cache_lookup": 10      # ms
}
```

## AI Integration

### Automated Log Analysis
```python
# AI-powered log analysis for issue detection
ai_analyze_logs = """
Analyze the following log entries and identify:
1. Performance bottlenecks (>500ms operations)
2. Error patterns and root causes
3. Resource utilization issues
4. Suggested optimizations

Log data: {log_entries}
"""
```

### Debug Session Automation
```bash
# Generate AI debugging session from recent errors
python debug_helpers.py --generate-ai-session \
  --time-range "last 2 hours" \
  --include-context \
  --export-format "claude-prompt"
```

## Testing Observability

### Unit Tests for Logging
```python
def test_order_processing_logs():
    with LogCapture() as capture:
        process_order(sample_order)
        
    # Verify expected log entries
    assert_log_contains(capture, "order_start")
    assert_log_contains(capture, "payment_success")
    assert_performance_logged(capture, "process_order")
```

### Integration Tests for Monitoring
```python
def test_performance_monitoring():
    @monitor_performance
    def slow_operation():
        time.sleep(0.1)
        return "completed"
    
    result = slow_operation()
    
    # Verify performance metrics were captured
    assert_performance_metric_exists("slow_operation")
    assert_duration_approximately(100, tolerance=10)
```

## Troubleshooting

### Common Issues
- **Missing Context**: Ensure all business operations include relevant context
- **Performance Overhead**: Use sampling for high-frequency operations
- **Log Volume**: Implement log rotation and retention policies
- **Sensitive Data**: Configure data sanitization for production

### Debug Commands
```bash
# Find recent errors with context
grep -A10 -B5 "ERROR" logs/app.log | tail -50

# Analyze performance patterns
python debug_helpers.py --performance-analysis --time-range "last hour"

# Generate AI troubleshooting prompt
python debug_helpers.py --ai-prompt --error-type "payment_error"
```

## Best Practices

### Observability Guidelines
1. **Log operations, not implementations** - Focus on business events
2. **Include timing for all operations** - Enable performance analysis
3. **Preserve error context** - Don't lose information in exception handling
4. **Use correlation IDs** - Track requests across service boundaries
5. **Structure log data** - Use consistent JSON format for AI parsing

### Performance Considerations
- Use async logging for high-throughput applications
- Implement sampling for frequent operations
- Configure appropriate log levels for each environment
- Monitor logging system performance and disk usage

## Contributing

When extending observability features:
1. Add comprehensive logging to new business operations
2. Include performance monitoring for time-sensitive functions
3. Update debug helpers for new error types
4. Add tests for observability features
5. Document new logging patterns and conventions

## Security Considerations

⚠️ **Important Security Notes**
- Never log sensitive data (passwords, tokens, PII)
- Implement data sanitization for production logs
- Secure log storage and transmission
- Regular audit of logged data for compliance
- Configure appropriate log retention policies