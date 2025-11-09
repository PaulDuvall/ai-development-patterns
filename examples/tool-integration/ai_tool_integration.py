#!/usr/bin/env python3
"""
AI Tool Integration - Complete Implementation
===========================================

This is the full implementation of the AI Tool Integration pattern demonstrating
how to connect AI systems to external data sources, APIs, and tools for enhanced
capabilities beyond prompt-only interactions.

For pattern documentation, see: 
https://github.com/PaulDuvall/ai-development-patterns#ai-tool-integration
"""

import os
import json
import sqlite3
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional


class ToolAugmentedAI:
    """AI system with integrated tool access for enhanced capabilities"""
    
    def __init__(self, config_path: str = ".ai/tools.json"):
        self.config = self._load_tool_config(config_path)
        self.db_connection = self._setup_database()
        self.available_tools = {
            "database_query": self._query_database,
            "file_operations": self._file_operations,
            "api_requests": self._api_requests,
            "system_info": self._system_info
        }
    
    def _load_tool_config(self, config_path: str) -> Dict[str, Any]:
        """Load tool configuration securely"""
        config_file = Path(config_path)
        if config_file.exists():
            return json.loads(config_file.read_text())
        return {
            "database_url": "sqlite:///app_data.db",
            "allowed_apis": ["api.github.com", "api.openweathermap.org"],
            "file_access_paths": ["./data/", "./logs/"],
            "max_query_results": 100
        }
    
    def _setup_database(self) -> sqlite3.Connection:
        """Initialize database connection with read-only access"""
        conn = sqlite3.connect("app_data.db")
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def _query_database(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute database queries safely"""
        # Whitelist allowed operations (read-only)
        allowed_operations = ["SELECT", "WITH"]
        query_upper = query.strip().upper()
        
        if not any(query_upper.startswith(op) for op in allowed_operations):
            raise ValueError("Only SELECT queries allowed")
        
        cursor = self.db_connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchmany(self.config["max_query_results"])
        return [dict(row) for row in results]
    
    def _file_operations(self, operation: str, path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """Safe file operations within allowed paths"""
        file_path = Path(path)
        
        # Verify path is within allowed directories
        allowed = any(str(file_path).startswith(allowed_path) 
                     for allowed_path in self.config["file_access_paths"])
        if not allowed:
            raise ValueError(f"File access denied: {path}")
        
        if operation == "read":
            if file_path.exists():
                return {"content": file_path.read_text(), "size": file_path.stat().st_size}
            return {"error": "File not found"}
        
        elif operation == "write":
            if content is None:
                return {"error": "Content required for write operation"}
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return {"status": "written", "path": str(file_path)}
        
        elif operation == "list":
            if file_path.is_dir():
                files = [str(f) for f in file_path.iterdir()]
                return {"files": files, "count": len(files)}
            return {"error": "Not a directory"}
        
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _api_requests(self, url: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP requests to allowed APIs"""
        from urllib.parse import urlparse
        
        # Verify API is in allowlist
        parsed_url = urlparse(url)
        if parsed_url.netloc not in self.config["allowed_apis"]:
            raise ValueError(f"API not allowed: {parsed_url.netloc}")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                raise ValueError("Only GET and POST methods allowed")
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "headers": dict(response.headers)
            }
        except requests.RequestException as e:
            return {"error": str(e), "status": "failed"}
    
    def _system_info(self) -> Dict[str, Any]:
        """Get safe system information"""
        return {
            "timestamp": datetime.now().isoformat(),
            "working_directory": os.getcwd(),
            "environment": os.environ.get("NODE_ENV", "development"),
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            "available_tools": list(self.available_tools.keys())
        }
    
    def execute_with_tools(self, ai_request: str, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute AI request with tool augmentation"""
        results = {
            "request": ai_request,
            "tool_results": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool")
            tool_args = tool_call.get("args", {})
            
            if tool_name in self.available_tools:
                try:
                    result = self.available_tools[tool_name](**tool_args)
                    results["tool_results"].append({
                        "tool": tool_name,
                        "status": "success",
                        "result": result
                    })
                except Exception as e:
                    results["tool_results"].append({
                        "tool": tool_name,
                        "status": "error",
                        "error": str(e)
                    })
            else:
                results["tool_results"].append({
                    "tool": tool_name,
                    "status": "not_found",
                    "error": f"Tool {tool_name} not available"
                })
        
        return results


def main():
    """Example usage demonstrating AI with Enhanced Capabilities"""
    
    # Initialize tool-augmented AI system
    ai_system = ToolAugmentedAI()
    
    # Example: AI analyzing user behavior with real data
    tool_calls = [
        {
            "tool": "database_query",
            "args": {
                "query": "SELECT user_id, last_login, feature_usage FROM users WHERE last_login > date('now', '-7 days')",
                "params": ()
            }
        },
        {
            "tool": "file_operations",
            "args": {
                "operation": "read",
                "path": "./logs/user_activity.log"
            }
        },
        {
            "tool": "api_requests",
            "args": {
                "url": "https://api.github.com/repos/myorg/myapp/issues",
                "method": "GET"
            }
        },
        {
            "tool": "system_info",
            "args": {}
        }
    ]
    
    # AI can now provide insights based on actual data, not just training knowledge
    results = ai_system.execute_with_tools(
        "Analyze user engagement patterns and suggest improvements",
        tool_calls
    )
    
    print("AI System with Tool Integration Results:")
    print(json.dumps(results, indent=2))
    
    # Demonstrate individual tool usage
    print("\n" + "="*50)
    print("Individual Tool Examples:")
    print("="*50)
    
    # Database query example
    try:
        db_results = ai_system._query_database(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        print(f"Database tables: {db_results}")
    except Exception as e:
        print(f"Database query failed: {e}")
    
    # File operations example
    try:
        # Create a test file
        file_result = ai_system._file_operations(
            "write", 
            "./data/test_output.txt", 
            "AI-generated content with timestamp: " + datetime.now().isoformat()
        )
        print(f"File write result: {file_result}")
        
        # Read it back
        read_result = ai_system._file_operations("read", "./data/test_output.txt")
        print(f"File read result: {read_result}")
    except Exception as e:
        print(f"File operations failed: {e}")
    
    # System info example
    sys_info = ai_system._system_info()
    print(f"System info: {sys_info}")


if __name__ == "__main__":
    main()