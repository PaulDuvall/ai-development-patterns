import time
import functools
from typing import Callable, Any
from observable_logging import log_performance, log_operation

def monitor_performance(func: Callable) -> Callable:
    """
    Decorator to automatically monitor function performance
    
    Args:
        func: Function to monitor
        
    Returns:
        Wrapped function with performance logging
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        operation_name = func.__name__
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log successful operation with performance data
            log_performance(operation_name, duration_ms, status="success")
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Log failed operation with performance data
            log_performance(operation_name, duration_ms, 
                          status="error", 
                          error_type=type(e).__name__,
                          error_message=str(e))
            raise
            
    return wrapper

def monitor_database_query(query_type: str = "unknown"):
    """
    Specialized decorator for database query monitoring
    
    Args:
        query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation_name = f"db_{query_type.lower()}_{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Determine performance category
                performance_category = "slow" if duration_ms > 100 else "normal"
                
                log_performance(operation_name, duration_ms,
                              query_type=query_type,
                              performance_category=performance_category,
                              status="success")
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                log_performance(operation_name, duration_ms,
                              query_type=query_type,
                              status="error",
                              error_type=type(e).__name__,
                              error_message=str(e))
                raise
                
        return wrapper
    return decorator

def monitor_api_endpoint(endpoint_name: str):
    """
    Decorator for API endpoint performance monitoring
    
    Args:
        endpoint_name: Name of the API endpoint
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation_name = f"api_{endpoint_name}"
            
            log_operation(f"{operation_name}_start")
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Categorize API response time
                if duration_ms > 2000:
                    category = "very_slow"
                elif duration_ms > 500:
                    category = "slow"
                else:
                    category = "normal"
                
                log_performance(operation_name, duration_ms,
                              endpoint=endpoint_name,
                              performance_category=category,
                              status="success")
                
                log_operation(f"{operation_name}_success", duration_ms=duration_ms)
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                log_performance(operation_name, duration_ms,
                              endpoint=endpoint_name,
                              status="error",
                              error_type=type(e).__name__,
                              error_message=str(e))
                
                log_operation(f"{operation_name}_error", 
                            duration_ms=duration_ms,
                            error=str(e))
                raise
                
        return wrapper
    return decorator

# Example usage classes and functions
class DatabaseConnection:
    """Mock database connection for examples"""
    
    @monitor_database_query("SELECT")
    def get_user_by_id(self, user_id: int):
        """Simulate database query with artificial delay"""
        time.sleep(0.05)  # Simulate 50ms query time
        if user_id == 999:
            raise Exception("User not found")
        return {"id": user_id, "name": f"User {user_id}"}
    
    @monitor_database_query("INSERT")
    def create_user(self, user_data: dict):
        """Simulate user creation with variable delay"""
        # Simulate longer operation for complex inserts
        time.sleep(0.15)  # Simulate 150ms insert time
        return {"id": 12345, **user_data}
    
    @monitor_database_query("UPDATE")
    def update_user(self, user_id: int, updates: dict):
        """Simulate user update operation"""
        time.sleep(0.08)  # Simulate 80ms update time
        return {"id": user_id, "updated": True}

class APIController:
    """Mock API controller for examples"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    @monitor_api_endpoint("get_user")
    def get_user_endpoint(self, user_id: int):
        """API endpoint with database dependency"""
        user = self.db.get_user_by_id(user_id)
        return {"status": "success", "user": user}
    
    @monitor_api_endpoint("create_user")
    def create_user_endpoint(self, user_data: dict):
        """API endpoint for user creation"""
        # Simulate validation delay
        time.sleep(0.02)
        
        user = self.db.create_user(user_data)
        return {"status": "created", "user": user}

@monitor_performance
def expensive_computation(n: int):
    """Example of expensive computation monitoring"""
    # Simulate CPU-intensive work
    result = sum(i * i for i in range(n))
    return result

@monitor_performance
def get_user_data(user_id: int):
    """Example function from README"""
    # Simulate database query
    time.sleep(0.03)  # 30ms query time
    if user_id == 0:
        raise ValueError("Invalid user ID")
    return {"id": user_id, "name": f"User {user_id}"}

if __name__ == "__main__":
    # Example usage and testing
    from observable_logging import setup_logging, set_correlation_id
    
    setup_logging(level="INFO", format_type="structured")
    set_correlation_id("perf_test_001")
    
    # Test database operations
    db = DatabaseConnection()
    api = APIController()
    
    print("Testing performance monitoring...")
    
    # Test successful operations
    user = db.get_user_by_id(123)
    print(f"Retrieved user: {user}")
    
    new_user = db.create_user({"name": "Alice", "email": "alice@example.com"})
    print(f"Created user: {new_user}")
    
    # Test API endpoints
    api_response = api.get_user_endpoint(456)
    print(f"API response: {api_response}")
    
    # Test expensive computation
    result = expensive_computation(1000)
    print(f"Computation result: {result}")
    
    # Test error scenarios
    try:
        db.get_user_by_id(999)  # This will raise an exception
    except Exception as e:
        print(f"Expected error caught: {e}")
    
    try:
        get_user_data(0)  # This will raise a ValueError
    except ValueError as e:
        print(f"Expected validation error: {e}")
    
    print("Performance monitoring test completed!")