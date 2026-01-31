# Tool Integration - Complete Implementation

This directory contains the full implementation of the **Tool Integration** pattern, demonstrating how to connect AI systems to external data sources, APIs, and tools for enhanced capabilities beyond prompt-only interactions.

## Pattern Overview

The Tool Integration pattern enables the architectural shift from isolated prompt-only AI to connected AI systems that can interact with real-world data and services. This includes database queries, file operations, API calls, and system information access.

For complete pattern documentation, see: [Tool Integration](../../README.md#tool-integration)

## Files in This Directory

### Core Implementation
- **`ai_tool_integration.py`** - Complete Python implementation with security controls
- **`tools.json`** - Configuration file with security settings and tool access rules

### Key Features

- **Database Integration**: Read-only SQL queries with operation whitelisting
- **File System Access**: Controlled file operations within specified paths
- **API Integration**: HTTP requests to allowlisted external services  
- **System Information**: Safe access to environment and system state
- **Security Controls**: Path restrictions, operation limits, timeout handling

## Usage Examples

### Basic Usage

```python
from ai_tool_integration import ToolAugmentedAI

# Initialize with configuration
ai_system = ToolAugmentedAI("tools.json")

# Execute AI request with tool access
tool_calls = [
    {
        "tool": "database_query",
        "args": {
            "query": "SELECT COUNT(*) as user_count FROM users",
            "params": ()
        }
    }
]

results = ai_system.execute_with_tools(
    "How many users are in the system?",
    tool_calls
)
```

### Model Context Protocol (MCP) Integration

This pattern can be implemented using the Model Context Protocol (MCP) for standardized tool integration:

```json
{
  "mcp_servers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "./data"]
    },
    "sqlite": {
      "command": "npx", 
      "args": ["@modelcontextprotocol/server-sqlite", "app_data.db"]
    }
  }
}
```

MCP provides a standardized way to implement this pattern across different AI tools and platforms.

## Security Integration

The implementation includes multiple security layers:

- **Path Restrictions**: File access limited to configured directories
- **Operation Whitelisting**: Only safe database operations allowed
- **API Allowlisting**: Network requests restricted to approved domains
- **Timeout Controls**: Prevents hanging requests and resource exhaustion
- **Error Handling**: Graceful failure without exposing system details

### Security Sandbox Integration

When deployed with the [Security Sandbox](../security-sandbox/), tool access remains secure:

```yaml
services:
  ai-with-tools:
    network_mode: none  # No external network access
    volumes:
      - ./data:/workspace/data:ro
      - ./generated:/workspace/output:rw
```

## Running the Example

1. **Install dependencies:**
   ```bash
   pip install requests
   ```

2. **Set up data directory:**
   ```bash
   mkdir -p data logs generated
   ```

3. **Run the example:**
   ```bash
   python ai_tool_integration.py
   ```

## What This Enables

- **Real-time data access**: AI queries current database state, not training data
- **File system interaction**: Read logs, write generated code, manage project files  
- **API integration**: Fetch live data from external services
- **System awareness**: Access to current environment state and configuration
- **Enhanced context**: AI decisions based on actual system state, not assumptions

## Anti-Pattern: Prompt-Only Development

This pattern solves the limitations of prompt-only AI development:

❌ **Prompt-Only Approach:**
```
AI: "Based on my training data, I think your database might have around 1000 users..."
```

✅ **Tool-Augmented Approach:**
```
AI: "I queried your database and found exactly 1,247 active users as of 2024-06-29 14:23:15"
```

The tool-augmented approach provides accurate, current information instead of educated guesses based on training data.

## Integration with Other Patterns

This pattern enables and enhances:
- [Spec-Driven Development](../../README.md#spec-driven-development) - AI can validate against actual system state
- [Observable Development](../../README.md#observable-development) - AI can read logs and monitoring data
- [Workflow Orchestration](../../experiments/README.md#workflow-orchestration) - Enables data-driven workflow decisions
- [Baseline Management](../../README.md#baseline-management) - AI can analyze actual performance metrics

## Further Reading

- [Model Context Protocol (MCP) Documentation](https://www.anthropic.com/news/model-context-protocol)
- [AI Development Patterns Collection](../../README.md)
- [Security Sandbox Example](../security-sandbox/)
