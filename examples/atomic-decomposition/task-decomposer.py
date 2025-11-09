#!/usr/bin/env python3
"""
Atomic Task Decomposer

Breaks down complex features into atomic, independently implementable tasks
suitable for parallel AI agent execution.
"""

import json
import argparse
import sys
from datetime import datetime
from typing import List, Dict, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class TaskContract:
    """Contract definition for an atomic task."""
    id: str
    name: str
    description: str
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    side_effects: List[str]
    estimated_hours: float
    dependencies: List[str]
    acceptance_criteria: List[str]
    agent_requirements: List[str]
    
    def validate_atomic(self) -> List[str]:
        """Validate that task meets atomic criteria."""
        violations = []
        
        # Check time bounds (1-2 hours)
        if self.estimated_hours > 2.0:
            violations.append(f"Estimated time {self.estimated_hours}h exceeds 2h limit")
        elif self.estimated_hours < 0.5:
            violations.append(f"Estimated time {self.estimated_hours}h too small (min 0.5h)")
        
        # Check for side effects (should be none)
        if self.side_effects:
            violations.append(f"Has side effects: {', '.join(self.side_effects)}")
        
        # Check for clear I/O contracts
        if not self.inputs and not self.outputs:
            violations.append("No clear input/output contract defined")
        
        # Check acceptance criteria
        if len(self.acceptance_criteria) < 2:
            violations.append("Insufficient acceptance criteria (minimum 2 required)")
        
        return violations
    
    def has_clear_io_contract(self) -> bool:
        """Check if task has well-defined inputs and outputs."""
        return bool(self.inputs or self.outputs)

class AtomicTaskDecomposer:
    def __init__(self):
        self.max_hours = 2.0
        self.min_hours = 0.5
        self.task_counter = 0
        
    def decompose_feature(self, feature_description: str) -> List[TaskContract]:
        """
        Decompose a feature into atomic tasks.
        
        Args:
            feature_description: High-level feature description
            
        Returns:
            List of atomic task contracts
        """
        print(f"🔨 Decomposing feature: {feature_description}")
        
        # Feature-specific decomposition logic
        if "authentication" in feature_description.lower():
            return self._decompose_authentication(feature_description)
        elif "payment" in feature_description.lower():
            return self._decompose_payment(feature_description)
        elif "dashboard" in feature_description.lower():
            return self._decompose_dashboard(feature_description)
        else:
            return self._decompose_generic(feature_description)
    
    def _decompose_authentication(self, description: str) -> List[TaskContract]:
        """Decompose authentication system into atomic tasks."""
        tasks = []
        
        # Task 1: Password validation service
        tasks.append(TaskContract(
            id=self._next_task_id(),
            name="Password validation service",
            description="Pure function to validate passwords against security rules",
            inputs={
                "password": "str",
                "validation_rules": "PasswordRules"
            },
            outputs={
                "is_valid": "bool",
                "errors": "List[str]",
                "strength_score": "int"
            },
            side_effects=[],  # Pure function, no side effects
            estimated_hours=1.5,
            dependencies=[],
            acceptance_criteria=[
                "Validates password length (8-128 characters)",
                "Checks for required character types",
                "Returns detailed error messages",
                "Calculates strength score (0-100)",
                "Handles unicode characters correctly",
                "Unit test coverage >95%"
            ],
            agent_requirements=["python", "security-knowledge"]
        ))
        
        # Task 2: JWT token generation service
        tasks.append(TaskContract(
            id=self._next_task_id(),
            name="JWT token generation service",
            description="Generate and sign JWT tokens with configurable claims",
            inputs={
                "user_id": "str",
                "role": "str",
                "expiration_config": "TokenConfig"
            },
            outputs={
                "access_token": "str",
                "refresh_token": "str",
                "expires_at": "datetime"
            },
            side_effects=[],  # Stateless token generation
            estimated_hours=1.0,
            dependencies=[],
            acceptance_criteria=[
                "Generates cryptographically secure tokens",
                "Supports configurable expiration times",
                "Includes standard JWT claims (iss, aud, exp)",
                "Uses RS256 signing algorithm",
                "Validates input parameters",
                "Unit test coverage >90%"
            ],
            agent_requirements=["python", "cryptography", "jwt-libraries"]
        ))
        
        # Task 3: Rate limiting middleware
        tasks.append(TaskContract(
            id=self._next_task_id(),
            name="Rate limiting middleware",
            description="Request rate limiting with configurable rules",
            inputs={
                "request_metadata": "RequestInfo",
                "rate_config": "RateLimitConfig"
            },
            outputs={
                "allow_request": "bool",
                "retry_after": "Optional[int]",
                "remaining_requests": "int"
            },
            side_effects=[],  # Uses external cache, not direct side effects
            estimated_hours=2.0,
            dependencies=[],
            acceptance_criteria=[
                "Implements sliding window rate limiting",
                "Supports per-IP and per-user limits",
                "Returns proper HTTP headers",
                "Handles distributed cache scenarios",
                "Configurable rate limit rules",
                "Integration test coverage >85%"
            ],
            agent_requirements=["python", "redis", "middleware-patterns"]
        ))
        
        # Task 4: Login endpoint integration
        tasks.append(TaskContract(
            id=self._next_task_id(),
            name="Login endpoint integration",
            description="HTTP endpoint that orchestrates authentication components",
            inputs={
                "credentials": "LoginRequest",
                "password_validator": "PasswordValidator",
                "token_generator": "TokenGenerator",
                "rate_limiter": "RateLimiter"
            },
            outputs={
                "response": "LoginResponse",
                "status_code": "int"
            },
            side_effects=["logs_authentication_attempt"],  # Logging only
            estimated_hours=1.5,
            dependencies=["auth-001", "auth-002", "auth-003"],
            acceptance_criteria=[
                "Integrates all authentication components",
                "Returns proper HTTP status codes",
                "Includes security headers",
                "Logs authentication attempts securely",
                "Handles all error scenarios gracefully",
                "End-to-end test coverage >90%"
            ],
            agent_requirements=["python", "fastapi", "integration-testing"]
        ))
        
        return tasks
    
    def _decompose_payment(self, description: str) -> List[TaskContract]:
        """Decompose payment processing into atomic tasks."""
        tasks = []
        
        # Task 1: Payment validation
        tasks.append(TaskContract(
            id=self._next_task_id(),
            name="Payment data validation",
            description="Validate payment request data and card information",
            inputs={
                "payment_request": "PaymentRequest",
                "validation_rules": "PaymentRules"
            },
            outputs={
                "is_valid": "bool",
                "validation_errors": "List[str]",
                "sanitized_data": "PaymentData"
            },
            side_effects=[],
            estimated_hours=1.5,
            dependencies=[],
            acceptance_criteria=[
                "Validates card number using Luhn algorithm",
                "Checks expiration date format and validity",
                "Validates CVV format",
                "Sanitizes input data for security",
                "Returns detailed validation errors"
            ],
            agent_requirements=["python", "payment-processing", "security"]
        ))
        
        # Task 2: Payment gateway integration
        tasks.append(TaskContract(
            id=self._next_task_id(),
            name="Payment gateway API client",
            description="HTTP client for payment gateway API communication",
            inputs={
                "payment_data": "PaymentData",
                "gateway_config": "GatewayConfig"
            },
            outputs={
                "transaction_result": "TransactionResult",
                "gateway_response": "GatewayResponse"
            },
            side_effects=[],
            estimated_hours=2.0,
            dependencies=[],
            acceptance_criteria=[
                "Handles API authentication securely",
                "Implements retry logic with exponential backoff",
                "Validates gateway responses",
                "Supports multiple payment gateways",
                "Handles network timeouts gracefully"
            ],
            agent_requirements=["python", "http-clients", "payment-apis"]
        ))
        
        return tasks
    
    def _decompose_dashboard(self, description: str) -> List[TaskContract]:
        """Decompose dashboard feature into atomic tasks."""
        tasks = []
        
        # Task 1: Metrics calculation service
        tasks.append(TaskContract(
            id=self._next_task_id(),
            name="Dashboard metrics calculator",
            description="Calculate dashboard metrics from raw data",
            inputs={
                "raw_data": "List[DataPoint]",
                "time_range": "TimeRange",
                "metric_configs": "List[MetricConfig]"
            },
            outputs={
                "calculated_metrics": "Dict[str, MetricValue]",
                "metadata": "MetricsMetadata"
            },
            side_effects=[],
            estimated_hours=1.5,
            dependencies=[],
            acceptance_criteria=[
                "Calculates standard metrics (avg, sum, count)",
                "Handles time-based aggregations",
                "Supports custom metric formulas",
                "Optimized for large datasets",
                "Returns metadata about calculations"
            ],
            agent_requirements=["python", "data-processing", "statistics"]
        ))
        
        return tasks
    
    def _decompose_generic(self, description: str) -> List[TaskContract]:
        """Generic decomposition for unknown features."""
        tasks = []
        
        # Create basic atomic tasks
        tasks.append(TaskContract(
            id=self._next_task_id(),
            name=f"Core logic: {description}",
            description=f"Main business logic implementation for {description}",
            inputs={"input_data": "Any", "config": "Config"},
            outputs={"result": "Any", "status": "Status"},
            side_effects=[],
            estimated_hours=2.0,
            dependencies=[],
            acceptance_criteria=[
                "Implements core functionality",
                "Handles edge cases",
                "Includes error handling",
                "Unit tests written"
            ],
            agent_requirements=["programming", "business-logic"]
        ))
        
        return tasks
    
    def _next_task_id(self) -> str:
        """Generate next sequential task ID."""
        self.task_counter += 1
        return f"task-{self.task_counter:03d}"
    
    def validate_decomposition(self, tasks: List[TaskContract]) -> Dict[str, Any]:
        """Validate entire task decomposition for atomicity."""
        validation_report = {
            "total_tasks": len(tasks),
            "atomic_tasks": 0,
            "violations": [],
            "dependency_graph": {},
            "estimated_total_hours": 0,
            "parallelizable_tasks": 0
        }
        
        # Validate each task
        for task in tasks:
            violations = task.validate_atomic()
            if violations:
                validation_report["violations"].append({
                    "task_id": task.id,
                    "task_name": task.name,
                    "violations": violations
                })
            else:
                validation_report["atomic_tasks"] += 1
            
            # Track dependencies
            validation_report["dependency_graph"][task.id] = task.dependencies
            validation_report["estimated_total_hours"] += task.estimated_hours
            
            # Count parallelizable tasks (no dependencies)
            if not task.dependencies:
                validation_report["parallelizable_tasks"] += 1
        
        # Calculate parallel efficiency
        if validation_report["total_tasks"] > 0:
            validation_report["parallel_efficiency"] = (
                validation_report["parallelizable_tasks"] / 
                validation_report["total_tasks"]
            )
        
        return validation_report
    
    def optimize_for_parallelization(self, tasks: List[TaskContract]) -> List[TaskContract]:
        """Analyze and suggest optimizations for better parallelization."""
        optimized_tasks = []
        
        for task in tasks:
            # Check if task can be split further
            if task.estimated_hours > 1.5:
                # Suggest splitting large tasks
                print(f"⚠️ Task '{task.name}' ({task.estimated_hours}h) could be split further")
            
            # Check for unnecessary dependencies
            if len(task.dependencies) > 2:
                print(f"⚠️ Task '{task.name}' has many dependencies - consider restructuring")
            
            optimized_tasks.append(task)
        
        return optimized_tasks
    
    def generate_execution_plan(self, tasks: List[TaskContract], num_agents: int = 3) -> Dict[str, Any]:
        """Generate execution plan for parallel agents."""
        # Simple topological sort for dependency ordering
        dependencies = {task.id: task.dependencies for task in tasks}
        
        # Find tasks with no dependencies (can start immediately)
        ready_tasks = [task for task in tasks if not task.dependencies]
        
        # Create execution phases
        phases = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            current_phase = []
            completed_in_phase = set()
            
            for task in remaining_tasks[:]:
                # Check if all dependencies are satisfied
                if all(dep in completed_in_phase or 
                      any(dep in prev_phase for prev_phase in phases) 
                      for dep in task.dependencies):
                    current_phase.append(task)
                    remaining_tasks.remove(task)
                    completed_in_phase.add(task.id)
            
            if not current_phase:
                break  # Circular dependency or error
            
            phases.append([task.id for task in current_phase])
        
        return {
            "total_phases": len(phases),
            "execution_phases": phases,
            "estimated_sequential_hours": sum(task.estimated_hours for task in tasks),
            "estimated_parallel_hours": max(
                sum(next(t.estimated_hours for t in tasks if t.id == task_id) 
                    for task_id in phase)
                for phase in phases
            ) if phases else 0,
            "recommended_agents": min(num_agents, max(len(phase) for phase in phases) if phases else 1)
        }

def main():
    parser = argparse.ArgumentParser(description="Decompose features into atomic tasks")
    parser.add_argument("--feature", required=True, help="Feature description to decompose")
    parser.add_argument("--max-hours", type=float, default=2.0, help="Maximum hours per task")
    parser.add_argument("--validate", action="store_true", help="Validate atomicity")
    parser.add_argument("--optimize", action="store_true", help="Optimize for parallelization")
    parser.add_argument("--execution-plan", type=int, metavar="AGENTS", 
                       help="Generate execution plan for N agents")
    parser.add_argument("--output", help="Output file for task contracts")
    
    args = parser.parse_args()
    
    decomposer = AtomicTaskDecomposer()
    decomposer.max_hours = args.max_hours
    
    # Decompose feature
    tasks = decomposer.decompose_feature(args.feature)
    
    if args.optimize:
        tasks = decomposer.optimize_for_parallelization(tasks)
    
    # Validation
    if args.validate:
        report = decomposer.validate_decomposition(tasks)
        print(f"\n📊 Decomposition Validation Report")
        print(f"Total tasks: {report['total_tasks']}")
        print(f"Atomic tasks: {report['atomic_tasks']}")
        print(f"Violations: {len(report['violations'])}")
        print(f"Parallel efficiency: {report['parallel_efficiency']:.1%}")
        print(f"Estimated total hours: {report['estimated_total_hours']:.1f}")
        
        if report['violations']:
            print("\n⚠️ Atomicity Violations:")
            for violation in report['violations']:
                print(f"  {violation['task_name']}:")
                for v in violation['violations']:
                    print(f"    - {v}")
    
    # Execution plan
    if args.execution_plan:
        plan = decomposer.generate_execution_plan(tasks, args.execution_plan)
        print(f"\n🚀 Execution Plan for {args.execution_plan} agents")
        print(f"Phases: {plan['total_phases']}")
        print(f"Sequential time: {plan['estimated_sequential_hours']:.1f}h")
        print(f"Parallel time: {plan['estimated_parallel_hours']:.1f}h")
        print(f"Speedup: {plan['estimated_sequential_hours']/plan['estimated_parallel_hours']:.1f}x")
        
        for i, phase in enumerate(plan['execution_phases'], 1):
            print(f"  Phase {i}: {', '.join(phase)}")
    
    # Output
    if args.output:
        task_data = [asdict(task) for task in tasks]
        with open(args.output, 'w') as f:
            json.dump(task_data, f, indent=2, default=str)
        print(f"\n✅ {len(tasks)} atomic tasks saved to {args.output}")
    else:
        print(f"\n✅ Generated {len(tasks)} atomic tasks:")
        for task in tasks:
            print(f"  - {task.name} ({task.estimated_hours}h)")

if __name__ == "__main__":
    main()