# Parallelized AI Coding Agents - Example Implementation

This directory contains a complete, practical implementation of the Parallelized AI Coding Agents pattern. The example demonstrates how to run multiple AI agents concurrently to build a Task Management SaaS application.

## 🎯 Overview

This example shows how to:
- Run 4 AI agents in parallel working on different parts of a codebase
- Use container isolation to prevent conflicts
- Implement shared memory for agent collaboration
- Automatically merge parallel work streams
- Handle conflicts intelligently

## 📁 Directory Structure

```
parallelized-ai-agents/
├── config/
│   └── tasks.yaml           # Task definitions for agents
├── docker/
│   └── Dockerfile.ai-agent  # AI agent container image
├── scripts/
│   ├── agent_runner.py      # Main agent execution script
│   ├── coordinator.py       # Coordinator service
│   ├── merge-parallel-work.sh # Automated merge script
│   └── shared_memory.py     # Shared memory implementation
├── shared-memory/           # Shared knowledge between agents
├── workspace/               # Agent working directories
│   ├── frontend/           # Frontend agent workspace
│   ├── backend/            # Backend agent workspace
│   ├── database/           # Database agent workspace
│   └── tests/              # Testing agent workspace
├── reports/                # Progress and merge reports
└── docker-compose.parallel-agents.yml
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git (for worktree examples)
- Python 3.8+
- API keys for your AI provider (Claude, OpenAI, etc.)

### 1. Initial Setup

```bash
# Clone the repository
git clone <your-repo>
cd examples/parallelized-ai-agents

# Create necessary directories
mkdir -p workspace/{frontend,backend,database,tests}
mkdir -p shared-memory reports

# Set up environment variables
cp .env.example .env
# Edit .env with your AI API keys
```

### 2. Build the AI Agent Container

First, create the Dockerfile for the AI agents:

```bash
# Create the Dockerfile
cat > docker/Dockerfile.ai-agent <<'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for JavaScript/TypeScript support
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create working directory
WORKDIR /workspace

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Copy scripts
COPY scripts/ /scripts/
RUN chmod +x /scripts/*.py

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=development

# Default command
CMD ["python", "/scripts/agent_runner.py"]
EOF

# Create requirements.txt
cat > docker/requirements.txt <<'EOF'
anthropic>=0.18.0
openai>=1.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
rich>=13.0.0
click>=8.0.0
watchdog>=3.0.0
aiofiles>=23.0.0
EOF

# Build the image
docker build -t ai-agent:latest docker/
```

### 3. Create Agent Runner Script

```bash
cat > scripts/agent_runner.py <<'EOF'
#!/usr/bin/env python3
"""
AI Agent Runner - Executes tasks from task configuration
"""
import os
import sys
import yaml
import json
import asyncio
from pathlib import Path
from datetime import datetime
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import your AI library (anthropic, openai, etc.)
# This is a mock implementation - replace with actual AI calls

console = Console()

class AIAgent:
    def __init__(self, agent_id: str, task_id: str):
        self.agent_id = agent_id
        self.task_id = task_id
        self.workspace = Path("/workspace")
        self.shared_memory_path = Path(os.environ.get("SHARED_MEMORY_PATH", "/shared/agent_memory.json"))
        
    async def load_task(self, task_file: str) -> dict:
        """Load task configuration"""
        with open(task_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Find our specific task
        for task in config['tasks']:
            if task['id'] == self.task_id:
                return task
        
        raise ValueError(f"Task {self.task_id} not found")
    
    async def execute_task(self, task: dict):
        """Execute the assigned task"""
        console.print(f"[bold blue]Agent {self.agent_id} starting task: {task['id']}[/bold blue]")
        
        # Record start in shared memory
        await self.update_shared_memory("status", "started")
        
        # This is where you would integrate with your AI provider
        # For demo purposes, we'll create some mock files
        
        instructions = task['instructions']
        console.print(f"[yellow]Instructions:[/yellow]\n{instructions[:200]}...")
        
        # Simulate work based on task type
        if self.task_id == "frontend-components":
            await self.create_frontend_components()
        elif self.task_id == "backend-api":
            await self.create_backend_api()
        elif self.task_id == "database-schema":
            await self.create_database_schema()
        elif self.task_id == "test-suite":
            await self.create_test_suite()
        
        # Record completion
        await self.update_shared_memory("status", "completed")
        console.print(f"[bold green]Agent {self.agent_id} completed task: {task['id']}[/bold green]")
    
    async def create_frontend_components(self):
        """Mock implementation for frontend components"""
        components = [
            ("TaskList.tsx", "React component for task list with Kanban board"),
            ("TaskDetail.tsx", "React component for task details"),
            ("TeamView.tsx", "React component for team management")
        ]
        
        for filename, description in components:
            filepath = self.workspace / "components" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # In real implementation, this would be AI-generated code
            content = f"""// {description}
// Generated by Agent: {self.agent_id}

import React from 'react';

export const {filename.replace('.tsx', '')} = () => {{
    return <div>AI-generated component</div>;
}};
"""
            filepath.write_text(content)
            
            # Record discovery
            await self.update_shared_memory(
                f"component_{filename}", 
                {"path": str(filepath), "description": description}
            )
    
    async def create_backend_api(self):
        """Mock implementation for backend API"""
        # Similar implementation for backend
        pass
    
    async def create_database_schema(self):
        """Mock implementation for database schema"""
        schema_file = self.workspace / "schema.prisma"
        schema_file.parent.mkdir(parents=True, exist_ok=True)
        
        schema_content = """// Generated by Agent: database
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  tasks     Task[]
  createdAt DateTime @default(now())
}

model Task {
  id          String   @id @default(cuid())
  title       String
  description String?
  status      Status   @default(TODO)
  userId      String
  user        User     @relation(fields: [userId], references: [id])
  createdAt   DateTime @default(now())
}

enum Status {
  TODO
  IN_PROGRESS
  DONE
}
"""
        schema_file.write_text(schema_content)
        
        # Share schema info with other agents
        await self.update_shared_memory("database_schema", {
            "path": str(schema_file),
            "tables": ["User", "Task"],
            "ready": True
        })
    
    async def create_test_suite(self):
        """Mock implementation for test suite"""
        # Wait for other agents to share their work
        await asyncio.sleep(2)
        
        # Read shared memory to understand what to test
        shared_data = await self.read_shared_memory()
        console.print(f"[cyan]Test agent found {len(shared_data.get('discoveries', {}))} items to test[/cyan]")
    
    async def update_shared_memory(self, key: str, value: any):
        """Update shared memory with discoveries"""
        # This would use the shared_memory.py module in production
        console.print(f"[dim]Agent {self.agent_id} sharing: {key}[/dim]")
    
    async def read_shared_memory(self) -> dict:
        """Read current shared memory state"""
        if self.shared_memory_path.exists():
            with open(self.shared_memory_path, 'r') as f:
                return json.load(f)
        return {}

@click.command()
@click.option('--task-file', required=True, help='Path to tasks.yaml')
@click.option('--task-id', required=True, help='Task ID to execute')
def main(task_file: str, task_id: str):
    """Run an AI agent for a specific task"""
    agent_id = os.environ.get('AGENT_ID', 'unknown')
    agent = AIAgent(agent_id, task_id)
    
    # Run the task
    asyncio.run(agent.execute_task(asyncio.run(agent.load_task(task_file))))

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/agent_runner.py
```

### 4. Create Coordinator Script

```bash
cat > scripts/coordinator.py <<'EOF'
#!/usr/bin/env python3
"""
Coordinator service to monitor agent progress
"""
import os
import json
import time
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
import click

console = Console()

class Coordinator:
    def __init__(self, watch_dir: str, report_dir: str):
        self.watch_dir = Path(watch_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
    def get_agent_status(self) -> dict:
        """Check status of all agent workspaces"""
        status = {}
        
        for workspace in self.watch_dir.iterdir():
            if workspace.is_dir():
                agent_name = workspace.name
                file_count = sum(1 for _ in workspace.rglob("*") if _.is_file())
                last_modified = max(
                    (f.stat().st_mtime for f in workspace.rglob("*") if f.is_file()),
                    default=0
                )
                
                status[agent_name] = {
                    "files": file_count,
                    "last_activity": datetime.fromtimestamp(last_modified).strftime("%H:%M:%S") if last_modified else "No activity",
                    "status": "Active" if time.time() - last_modified < 60 else "Idle"
                }
        
        return status
    
    def create_status_table(self, status: dict) -> Table:
        """Create a rich table showing agent status"""
        table = Table(title="Parallel Agent Status")
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Files", style="magenta")
        table.add_column("Last Activity", style="yellow")
        table.add_column("Status", style="green")
        
        for agent, info in status.items():
            table.add_row(
                agent,
                str(info["files"]),
                info["last_activity"],
                info["status"]
            )
        
        return table
    
    def generate_report(self, status: dict):
        """Generate a status report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "agents": status,
            "summary": {
                "total_agents": len(status),
                "active_agents": sum(1 for s in status.values() if s["status"] == "Active"),
                "total_files": sum(s["files"] for s in status.values())
            }
        }
        
        report_file = self.report_dir / f"status_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
    
    def monitor(self):
        """Monitor agent activity"""
        console.print("[bold blue]Starting Coordinator Service[/bold blue]")
        
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                status = self.get_agent_status()
                table = self.create_status_table(status)
                
                # Add summary
                total_files = sum(s["files"] for s in status.values())
                table.caption = f"Total files generated: {total_files}"
                
                live.update(table)
                
                # Generate report every 30 seconds
                if int(time.time()) % 30 == 0:
                    self.generate_report(status)
                
                time.sleep(1)

@click.command()
@click.option('--watch-dir', required=True, help='Directory to watch')
@click.option('--report-dir', required=True, help='Directory for reports')
def main(watch_dir: str, report_dir: str):
    """Run the coordinator service"""
    coordinator = Coordinator(watch_dir, report_dir)
    try:
        coordinator.monitor()
    except KeyboardInterrupt:
        console.print("\n[yellow]Coordinator shutting down...[/yellow]")

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/coordinator.py
```

### 5. Run the Parallel Agents

#### Using Docker Compose (Recommended)

```bash
# Start all agents
docker-compose -f docker-compose.parallel-agents.yml up -d

# Watch the logs
docker-compose -f docker-compose.parallel-agents.yml logs -f

# Check agent status
docker-compose -f docker-compose.parallel-agents.yml ps

# Stop all agents
docker-compose -f docker-compose.parallel-agents.yml down
```

#### Using Git Worktrees

```bash
# Create worktrees for each agent
git worktree add -b agent/frontend ../agent-frontend
git worktree add -b agent/backend ../agent-backend
git worktree add -b agent/database ../agent-database
git worktree add -b agent/tests ../agent-tests

# Run agents in parallel (requires GNU parallel)
parallel --jobs 4 << 'EOF'
cd ../agent-frontend && ai-agent --task frontend-components
cd ../agent-backend && ai-agent --task backend-api  
cd ../agent-database && ai-agent --task database-schema
cd ../agent-tests && ai-agent --task test-suite
EOF
```

### 6. Merge Parallel Work

After agents complete their tasks:

```bash
# Run the merge script
./scripts/merge-parallel-work.sh

# Check merge reports
ls -la reports/

# View the summary
cat reports/merge_summary_*.txt
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
# AI Provider Configuration
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
AGENT_MODEL=claude-3-sonnet

# Agent Configuration
AGENT_BRANCH_PREFIX=agent/
MAIN_BRANCH=main
WORKSPACE_DIR=./workspace
REPORTS_DIR=./reports
SHARED_MEMORY=./shared-memory/agent_memory.json

# Container Configuration
COMPOSE_PROJECT_NAME=parallel-agents
```

### Task Configuration

Edit `config/tasks.yaml` to define your own tasks:

```yaml
tasks:
  - id: your-task-id
    agent_count: 1
    isolation: container  # or 'worktree'
    dependencies: []      # List task IDs that must complete first
    priority: high        # high, medium, low
    estimated_hours: 4
    instructions: |
      Detailed instructions for the AI agent...
    success_criteria:
      - Specific success criteria
      - That can be validated
```

## 📊 Monitoring and Reports

### Real-time Monitoring

The coordinator service provides real-time status updates:

```bash
# View coordinator dashboard
docker-compose -f docker-compose.parallel-agents.yml logs -f coordinator
```

### Generated Reports

- `reports/merge_*.json` - Individual merge reports
- `reports/merge_summary_*.txt` - Summary of all merges
- `reports/status_*.json` - Agent status snapshots
- `shared-memory/agent_memory.json` - Shared discoveries and conflicts

## 🎯 Real-World Example: TaskFlow SaaS

This example implements a complete task management SaaS with:

1. **Frontend Agent**: Creates React components with TypeScript
2. **Backend Agent**: Implements REST API with Node.js/Express
3. **Database Agent**: Designs PostgreSQL schema with Prisma
4. **Test Agent**: Generates comprehensive test suites

The agents work in parallel, share discoveries through shared memory, and their work is automatically merged.

## 🚨 Troubleshooting

### Common Issues

1. **Merge Conflicts**
   ```bash
   # Check conflict details
   cat reports/merge_*.json | jq '.status == "conflict"'
   
   # Manually resolve
   git checkout agent/frontend
   git rebase main
   # Fix conflicts
   git push --force-with-lease
   ```

2. **Agent Failures**
   ```bash
   # Check agent logs
   docker-compose -f docker-compose.parallel-agents.yml logs agent-frontend
   
   # Restart specific agent
   docker-compose -f docker-compose.parallel-agents.yml restart agent-frontend
   ```

3. **Shared Memory Issues**
   ```bash
   # Check shared memory
   cat shared-memory/agent_memory.json | jq .
   
   # Reset if corrupted
   rm shared-memory/agent_memory.json
   docker-compose -f docker-compose.parallel-agents.yml restart
   ```

## 🔐 Security Considerations

1. **API Key Management**: Never commit API keys. Use environment variables or secrets management.
2. **Container Isolation**: Set `internal: true` in docker-compose for complete network isolation.
3. **Code Review**: Always review AI-generated code before merging to production.

## 📚 Additional Resources

- [Pattern Documentation](../../README.md#parallelized-ai-coding-agents)
- [Shared Memory Module](scripts/shared_memory.py)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)

## 🤝 Contributing

To improve this example:

1. Add support for more AI providers
2. Implement better conflict resolution strategies
3. Add metrics and performance monitoring
4. Create language-specific agent templates

---

**Note**: This is a demonstration of the pattern. In production, you would integrate with actual AI APIs and implement proper error handling, retries, and monitoring.