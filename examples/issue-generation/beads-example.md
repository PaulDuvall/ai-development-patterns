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

## Beads vs Traditional Tools

### Where Beads Wins

**AI Agent Integration**: Native CLI vs API tokens
```bash
bd list --status open --json | jq '.[] | select(.priority == 0)'
```

**Offline-First**: Create/update without internet, sync via git later

**Git-Native**: Issues version with code
```bash
git log -p .beads/issues.jsonl  # See issue history
git diff HEAD~1 .beads/issues.jsonl  # What changed?
```

**Speed**: <50ms queries (local SQLite) vs 100-500ms API calls

**Zero Dependencies**: No accounts, tokens, or costs

### Where GitHub/JIRA/Linear Win

**Team Collaboration**: Web UI for non-technical users (PMs, designers)

**Rich Features**:
- GitHub: PR auto-linking (`closes #123`), Actions, project boards
- JIRA: Custom workflows, time tracking, sprint planning, burndown charts
- Linear: Fast UI, cycles, roadmaps, beautiful design

**Integrations**: Slack, webhooks, Zapier, analytics tools

**Search**: Full-text search, advanced filters, saved queries

**Reporting**: Burndown charts, velocity tracking, dashboards

### Quick Comparison

| Feature | Beads | GitHub Issues | JIRA | Linear |
|---------|-------|---------------|------|--------|
| **AI Agent Access** | ✅ Native CLI | ⚠️ API + token | ⚠️ Complex API | ⚠️ API + token |
| **Offline Work** | ✅ Full | ❌ Limited | ❌ None | ❌ None |
| **Git Integration** | ✅ Native | ⚠️ External | ❌ Separate | ❌ Separate |
| **Setup Time** | ✅ Instant | ⚠️ Minutes | ❌ Hours/Days | ⚠️ Minutes |
| **Query Speed** | ✅ <50ms | ⚠️ 100-500ms | ⚠️ 200-1000ms | ⚠️ 100-300ms |
| **Non-tech Users** | ❌ CLI only | ✅ Web UI | ✅ Web UI | ✅ Web UI |
| **Collaboration** | ⚠️ Basic | ✅ Rich | ✅ Enterprise | ✅ Modern |
| **Integrations** | ❌ Minimal | ✅ Extensive | ✅ Enterprise | ✅ Modern |
| **Cost** | ✅ Free | ✅ Free | ❌ Paid | ⚠️ Paid |

### When to Use Each

**Use Beads When:**
- ✅ AI-assisted development is core to your workflow
- ✅ Solo developer or small technical team
- ✅ You want issues versioned with code
- ✅ You work offline frequently

**Use GitHub/JIRA/Linear When:**
- ✅ Team includes non-technical stakeholders
- ✅ Need rich collaboration (comments, mentions, web UI)
- ✅ Open source with external contributors
- ✅ Enterprise requirements (SSO, audit trails)

### Hybrid Approach

Combine both for different purposes:

```bash
# Use Beads for internal tech tasks (refactoring, tech debt)
bd create "Refactor authentication module"

# Sync to GitHub/Linear for stakeholder visibility
bd sync --to linear  # Experimental feature

# Or keep them separate:
# - Beads: AI agent work tracking
# - GitHub Issues: User-facing features/bugs
```

## Best Practices

**Keep tasks atomic (4-8 hours)**:
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
