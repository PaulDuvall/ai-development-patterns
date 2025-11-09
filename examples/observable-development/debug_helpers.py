#!/usr/bin/env python3
"""
Debug helpers for AI-friendly log analysis and troubleshooting
"""

import json
import argparse
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
import sys

def extract_log_entries(log_file: str, time_range: Optional[str] = None) -> List[Dict]:
    """Extract structured log entries from log file"""
    entries = []
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if time_range and not is_within_time_range(entry.get('timestamp'), time_range):
                        continue
                    entries.append(entry)
                except json.JSONDecodeError:
                    # Skip non-JSON log lines
                    continue
    except FileNotFoundError:
        print(f"Log file {log_file} not found", file=sys.stderr)
        return []
    
    return entries

def is_within_time_range(timestamp_str: str, time_range: str) -> bool:
    """Check if timestamp is within specified time range"""
    if not timestamp_str:
        return True
    
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.utcnow()
        
        if time_range == "last hour":
            return timestamp > now - timedelta(hours=1)
        elif time_range == "last 2 hours":
            return timestamp > now - timedelta(hours=2)
        elif time_range == "last day":
            return timestamp > now - timedelta(days=1)
        else:
            return True
    except ValueError:
        return True

def analyze_errors(entries: List[Dict]) -> Dict[str, Any]:
    """Analyze error patterns in log entries"""
    error_entries = [e for e in entries if 'error' in e.get('operation', '')]
    
    if not error_entries:
        return {"message": "No errors found in log entries"}
    
    # Group errors by type
    error_types = Counter()
    error_operations = Counter()
    error_contexts = defaultdict(list)
    
    for entry in error_entries:
        operation = entry.get('operation', 'unknown')
        context = entry.get('context', {})
        
        error_type = context.get('error_type', 'unknown')
        error_types[error_type] += 1
        error_operations[operation] += 1
        error_contexts[error_type].append({
            'timestamp': entry.get('timestamp'),
            'operation': operation,
            'error_message': context.get('error_message', ''),
            'context': context
        })
    
    return {
        "total_errors": len(error_entries),
        "error_types": dict(error_types.most_common()),
        "error_operations": dict(error_operations.most_common()),
        "error_details": dict(error_contexts)
    }

def analyze_performance(entries: List[Dict], threshold_ms: float = 500) -> Dict[str, Any]:
    """Analyze performance issues in log entries"""
    perf_entries = [e for e in entries if 'performance' in e.get('operation', '')]
    
    if not perf_entries:
        return {"message": "No performance data found in log entries"}
    
    slow_operations = []
    operation_stats = defaultdict(list)
    
    for entry in perf_entries:
        context = entry.get('context', {})
        duration = context.get('duration_ms', 0)
        operation = entry.get('operation', '').replace('_performance', '')
        
        operation_stats[operation].append(duration)
        
        if duration > threshold_ms:
            slow_operations.append({
                'timestamp': entry.get('timestamp'),
                'operation': operation,
                'duration_ms': duration,
                'context': context
            })
    
    # Calculate stats for each operation
    stats_summary = {}
    for op, durations in operation_stats.items():
        stats_summary[op] = {
            'count': len(durations),
            'avg_ms': sum(durations) / len(durations),
            'max_ms': max(durations),
            'min_ms': min(durations),
            'slow_count': len([d for d in durations if d > threshold_ms])
        }
    
    return {
        "threshold_ms": threshold_ms,
        "slow_operations": slow_operations,
        "operation_stats": stats_summary,
        "performance_summary": {
            "total_operations": len(perf_entries),
            "slow_operations_count": len(slow_operations),
            "slowest_operation": max(slow_operations, key=lambda x: x['duration_ms']) if slow_operations else None
        }
    }

def generate_ai_debugging_prompt(entries: List[Dict], error_type: Optional[str] = None) -> str:
    """Generate AI-friendly debugging prompt from log entries"""
    
    if error_type:
        entries = [e for e in entries if error_type in e.get('operation', '') or 
                  error_type in str(e.get('context', {}))]
    
    # Recent errors
    error_analysis = analyze_errors(entries)
    
    # Performance issues
    perf_analysis = analyze_performance(entries)
    
    # Correlation patterns
    correlation_ids = Counter()
    for entry in entries:
        corr_id = entry.get('correlation_id')
        if corr_id:
            correlation_ids[corr_id] += 1
    
    prompt = f"""
# AI Debugging Session

## System Overview
- Log entries analyzed: {len(entries)}
- Time range: Recent operations
- Focus: {'Error type: ' + error_type if error_type else 'General system analysis'}

## Error Analysis
{json.dumps(error_analysis, indent=2)}

## Performance Analysis  
{json.dumps(perf_analysis, indent=2)}

## Request Correlation
Most active correlation IDs: {dict(correlation_ids.most_common(5))}

## AI Analysis Request
Please analyze the above log data and provide:

1. **Root Cause Analysis**: What are the primary issues based on the error patterns?
2. **Performance Bottlenecks**: Which operations are consistently slow?
3. **Correlation Insights**: Are there patterns in the correlation data?
4. **Recommended Actions**: What specific steps should be taken to resolve issues?
5. **Monitoring Improvements**: What additional observability would help?

## Raw Log Sample
```json
{json.dumps(entries[-10:], indent=2)}
```

Focus on actionable insights and specific implementation recommendations.
"""
    
    return prompt

def extract_ai_friendly_errors(log_file: str, time_range: str = "last hour") -> str:
    """Extract error information in AI-friendly format (equivalent to bash command)"""
    entries = extract_log_entries(log_file, time_range)
    error_entries = [e for e in entries if 'error' in e.get('operation', '')]
    
    if not error_entries:
        return "No errors found in the specified time range"
    
    # Format similar to grep -A5 -B5 but with structured data
    output_lines = []
    for entry in error_entries[-20:]:  # Last 20 errors like tail -20
        output_lines.append(f"=== ERROR: {entry.get('operation')} ===")
        output_lines.append(f"Timestamp: {entry.get('timestamp')}")
        output_lines.append(f"Correlation ID: {entry.get('correlation_id')}")
        
        context = entry.get('context', {})
        if context:
            output_lines.append("Context:")
            for key, value in context.items():
                output_lines.append(f"  {key}: {value}")
        
        output_lines.append("")  # Empty line separator
    
    return "\n".join(output_lines)

def main():
    parser = argparse.ArgumentParser(description="AI-friendly log analysis and debugging")
    parser.add_argument("--log-file", default="app.log", help="Log file to analyze")
    parser.add_argument("--analyze-errors", action="store_true", help="Analyze error patterns")
    parser.add_argument("--performance-issues", action="store_true", help="Analyze performance issues")
    parser.add_argument("--threshold", type=float, default=500, help="Performance threshold in ms")
    parser.add_argument("--ai-prompt", action="store_true", help="Generate AI debugging prompt")
    parser.add_argument("--error-type", help="Focus on specific error type")
    parser.add_argument("--time-range", default="last hour", help="Time range: 'last hour', 'last 2 hours', 'last day'")
    parser.add_argument("--extract-errors", action="store_true", help="Extract errors like grep command")
    
    args = parser.parse_args()
    
    entries = extract_log_entries(args.log_file, args.time_range)
    
    if not entries:
        print("No log entries found or file not accessible")
        return
    
    if args.analyze_errors:
        analysis = analyze_errors(entries)
        print("=== ERROR ANALYSIS ===")
        print(json.dumps(analysis, indent=2))
    
    if args.performance_issues:
        analysis = analyze_performance(entries, args.threshold)
        print("=== PERFORMANCE ANALYSIS ===")
        print(json.dumps(analysis, indent=2))
    
    if args.ai_prompt:
        prompt = generate_ai_debugging_prompt(entries, args.error_type)
        print("=== AI DEBUGGING PROMPT ===")
        print(prompt)
    
    if args.extract_errors:
        errors = extract_ai_friendly_errors(args.log_file, args.time_range)
        print("=== EXTRACTED ERRORS ===")
        print(errors)

if __name__ == "__main__":
    main()