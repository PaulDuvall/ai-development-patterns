# Beads: Git-Based Issue Tracking for AI Agents

Beads is a lightweight, git-based issue tracking system designed for AI coding agents. It provides persistent memory across sessions with zero setup.

**Source**: [github.com/steveyegge/beads](https://github.com/steveyegge/beads)

## Quick Start

```bash
# Install
pip install beads-project

# Initialize in your project
cd your-project
bd init

# Create issues
bd create --title "Epic: User Authentication System"
# Output: Created bd-a1b2

bd create --title "Implement JWT token generation" \
  --body "RED: Test JWT.generate()
GREEN: Implement with exp/iat claims
REFACTOR: Extract key management" \
  --parent bd-a1b2
# Output: Created bd-c3d4

# Query ready work
bd ready
# bd-c3d4: Implement JWT token generation

# Start and complete work
bd start bd-c3d4
bd done bd-c3d4

# Sync via git
git add .beads/
git commit -m "beads: add auth tasks"
git push
```

## AI Agent Workflow

```bash
# AI agent discovers new work during implementation
bd create --title "Add JWT key rotation" \
  --body "Discovered need for security - scheduled key rotation" \
  --discovered-from bd-c3d4 \
  --blocks bd-c3d4

# Agent queries what's unblocked and ready
bd ready

# Agent shows epic progress
bd show bd-a1b2 --tree
# bd-a1b2: Epic: User Authentication [open]
#   ├─ bd-c3d4: JWT generation [done]
#   └─ bd-e5f6: Password reset [in progress]
# Progress: 1/2 complete (50%)
```

## Python Integration

```python
import subprocess
import json

def create_beads_issue(title, body, parent=None):
    cmd = ['bd', 'create', '--title', title, '--body', body, '--format', 'json']
    if parent:
        cmd.extend(['--parent', parent])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)['id']

# Generate epic with tasks
epic_id = create_beads_issue("Epic: User Auth", "Complete auth system")
create_beads_issue("Setup database schema", "RED/GREEN/REFACTOR", parent=epic_id)
create_beads_issue("Implement login endpoint", "RED/GREEN/REFACTOR", parent=epic_id)
```

## Why Beads?

Beads is optimized for AI agent workflows with:
- **Native CLI access**: No API tokens or authentication complexity
- **Offline-first**: Create/update without internet, sync via git
- **Git-native**: Issues version with code in `.beads/issues.jsonl`
- **Fast queries**: <50ms (local SQLite) vs 100-500ms API calls
- **Zero dependencies**: No accounts, tokens, or external services

For a detailed comparison with GitHub/JIRA/Linear, see the [comparison table in README.md](README.md#comparison-table).

## Best Practices

**Keep tasks atomic (<1 hour for AI development)**:
```bash
✅ bd create --title "Implement JWT token generation"
❌ bd create --title "Build entire authentication system"
```

**Use dependency types correctly**:
```bash
--blocks    # Must be done before dependent task
--parent    # Organizational hierarchy (epic/subissue)
--related   # Related but not blocking
--discovered-from  # Found during implementation
```

**Commit Beads changes regularly**:
```bash
git add .beads/
git commit -m "beads: add authentication tasks"
git push
```

For more details, see the [Beads documentation](https://github.com/steveyegge/beads).
