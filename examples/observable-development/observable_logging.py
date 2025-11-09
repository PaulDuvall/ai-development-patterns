import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
import uuid
import threading

# Thread-local storage for correlation IDs
_local = threading.local()

def setup_logging(level: str = "INFO", format_type: str = "structured"):
    """Initialize structured logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(message)s' if format_type == "structured" else '%(asctime)s - %(levelname)s - %(message)s'
    )

def get_correlation_id() -> str:
    """Get or create correlation ID for request tracing"""
    if not hasattr(_local, 'correlation_id'):
        _local.correlation_id = str(uuid.uuid4())
    return _local.correlation_id

def set_correlation_id(correlation_id: str):
    """Set correlation ID for request tracing"""
    _local.correlation_id = correlation_id

def log_operation(operation: str, level: str = "INFO", **context: Any):
    """
    Log structured operation data for AI analysis
    
    Args:
        operation: The operation being performed (e.g., "order_start", "payment_success")
        level: Logging level (DEBUG, INFO, WARN, ERROR)
        **context: Additional context data for the operation
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,
        "correlation_id": get_correlation_id(),
        "context": context
    }
    
    logger = logging.getLogger(__name__)
    log_method = getattr(logger, level.lower())
    log_method(json.dumps(log_entry))

def log_error(operation: str, error: Exception, **context: Any):
    """
    Log error with full context for AI debugging
    
    Args:
        operation: The operation that failed
        error: The exception that occurred
        **context: Additional context data
    """
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "error_details": getattr(error, '__dict__', {}),
        **context
    }
    
    log_operation(f"{operation}_error", level="ERROR", **error_context)

def log_performance(operation: str, duration_ms: float, **context: Any):
    """
    Log performance metrics for AI analysis
    
    Args:
        operation: The operation being measured
        duration_ms: Duration in milliseconds
        **context: Additional performance context
    """
    performance_context = {
        "duration_ms": duration_ms,
        "performance_category": "slow" if duration_ms > 1000 else "normal",
        **context
    }
    
    log_operation(f"{operation}_performance", **performance_context)

# Observable business logic example
def process_order(order):
    """Example of observable order processing"""
    log_operation("order_start", order_id=order.id, total=order.total)
    
    try:
        log_operation("validation_start")
        validate_order(order)
        log_operation("validation_success")
        
        log_operation("payment_start", method=order.payment_method)
        result = charge_payment(order)
        log_operation("payment_success", transaction_id=result.transaction_id)
        
        return result
        
    except ValidationError as e:
        log_error("validation", e, field=e.field, order_id=order.id)
        raise
    except PaymentError as e:
        log_error("payment", e, code=e.code, order_id=order.id)
        raise

# Mock classes for example
class ValidationError(Exception):
    def __init__(self, message, field):
        super().__init__(message)
        self.field = field

class PaymentError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code

class Order:
    def __init__(self, id, total, payment_method):
        self.id = id
        self.total = total
        self.payment_method = payment_method

class PaymentResult:
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id

def validate_order(order):
    """Mock validation function"""
    if order.total <= 0:
        raise ValidationError("Invalid order total", "total")

def charge_payment(order):
    """Mock payment function"""
    if order.payment_method == "invalid":
        raise PaymentError("Invalid payment method", "INVALID_METHOD")
    return PaymentResult(f"txn_{uuid.uuid4()}")

if __name__ == "__main__":
    # Example usage
    setup_logging(level="INFO", format_type="structured")
    
    # Set correlation ID for this request
    set_correlation_id("req_123456")
    
    # Process sample order
    sample_order = Order("ord_001", 99.99, "credit_card")
    
    try:
        result = process_order(sample_order)
        print(f"Order processed successfully: {result.transaction_id}")
    except Exception as e:
        print(f"Order processing failed: {e}")