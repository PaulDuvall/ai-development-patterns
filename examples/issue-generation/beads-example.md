# Beads: AI Agent Memory for Issue Tracking

Beads is a lightweight, git-based issue tracking system that gives AI coding agents persistent memory across sessions. Unlike traditional issue trackers, Beads is designed specifically for AI agents to maintain organized work queues with dependency tracking.

**Source**: [github.com/steveyegge/beads](https://github.com/steveyegge/beads)

## Why Beads for Issue Generation?

Traditional issue tracking systems require web interfaces or complex APIs. Beads provides:

- **Zero-setup initialization**: `bd init` creates a local git-backed database
- **CLI-first design**: Perfect for AI agent automation
- **Automatic dependency tracking**: Four relationship types (blocks, related, parent-child, discovered-from)
- **Ready work detection**: Automatically identifies unblocked tasks
- **Git-based distribution**: JSONL files sync across machines and agents
- **Collision-resistant IDs**: Hash-based identifiers enable multi-agent workflows
- **Persistent memory**: Agents can resume complex tasks across sessions

## Installation

```bash
# Install Beads
pip install beads-project

# Verify installation
bd --version
```

## Quick Start

### Initialize Project

```bash
# Navigate to your project
cd your-project

# Initialize Beads
bd init
# Creates .beads/ directory with SQLite cache and JSONL source files

# Commit to git for distribution
git add .beads/
git commit -m "Initialize Beads issue tracking"
```

### Create Your First Issues

```bash
# Create parent issue for feature epic
bd create --title "Epic: User Authentication System" \
  --body "Complete user authentication with JWT, password reset, and session management"

# Output: Created bd-a1b2

# Create dependent subissues (4-8 hour tasks)
bd create --title "Implement JWT token generation" \
  --body "RED: Write failing test for JWT.generate()
GREEN: Implement token generation with exp and iat claims
REFACTOR: Extract key management to config" \
  --parent bd-a1b2

# Output: Created bd-c3d4

bd create --title "Add password reset endpoint" \
  --body "RED: Write test for POST /auth/reset-password
GREEN: Implement reset with email notification
REFACTOR: Extract email service" \
  --parent bd-a1b2 \
  --blocks bd-c3d4

# Output: Created bd-e5f6
```

## AI Agent Integration

### Automatic Issue Discovery During Development

```bash
# AI agent encounters new work during implementation
ai_agent_workflow() {
  # Agent working on bd-c3d4 discovers need for key rotation
  bd create --title "Implement JWT key rotation" \
    --body "Discovered during JWT implementation - need scheduled key rotation for security" \
    --discovered-from bd-c3d4 \
    --blocks bd-c3d4

  # Agent files this for future work and continues
}
```

### Query Ready Work

```bash
# Agent starts new session - what can I work on?
bd ready

# Output shows tasks with no open blockers:
# bd-c3d4: Implement JWT token generation
# bd-g7h8: Add input validation middleware

# Agent picks first task
bd show bd-c3d4

# Output:
# ID: bd-c3d4
# Title: Implement JWT token generation
# Status: open
# Parent: bd-a1b2 (Epic: User Authentication System)
# Blocks: bd-e5f6 (Add password reset endpoint)
# Body:
#   RED: Write failing test for JWT.generate()
#   GREEN: Implement token generation with exp and iat claims
#   REFACTOR: Extract key management to config
```

### Update Status as Work Progresses

```bash
# Agent starts work
bd start bd-c3d4

# Agent completes work
bd done bd-c3d4

# Check what's ready now (password reset is unblocked)
bd ready
# bd-e5f6: Add password reset endpoint
# bd-g7h8: Add input validation middleware
```

## Advanced Workflows

### Complex Dependency Chains

```bash
# Create foundation tasks
bd create --title "Setup Redis session store" --body "Foundation for auth system"
# bd-j1k2

bd create --title "Add CORS middleware" --body "Required before authentication endpoints"
# bd-l3m4

# Create dependent feature with multiple blockers
bd create --title "Protected API endpoints" \
  --body "Add authentication middleware to protect /api/* routes" \
  --blocks bd-j1k2,bd-l3m4,bd-c3d4

# bd-n5o6 won't show in 'bd ready' until all three blockers are done
```

### Epic Progress Tracking

```bash
# Show epic with all child tasks
bd show bd-a1b2 --tree

# Output:
# bd-a1b2: Epic: User Authentication System [open]
#   ├─ bd-c3d4: Implement JWT token generation [done]
#   ├─ bd-e5f6: Add password reset endpoint [in progress]
#   ├─ bd-i9j0: Implement JWT key rotation [open]
#   └─ bd-n5o6: Protected API endpoints [blocked]
#
# Progress: 1/4 complete (25%)

# List all children of epic
bd children bd-a1b2
```

### Multi-Agent Coordination

```bash
# Agent 1 creates work and pushes
bd create --title "Write API documentation" --body "Document all auth endpoints"
git add .beads/
git commit -m "Add API documentation task"
git push

# Agent 2 pulls and sees new work
git pull
# Beads auto-imports new JSONL records to local SQLite

bd ready
# bd-p7q8: Write API documentation
```

## Integration with AI Prompts

### AI Prompt: Break Down Feature into Beads Issues

```bash
ai "Analyze the 'User Profile Management' feature and create Beads issues:

REQUIREMENTS:
1. Break into 4-8 hour tasks following RED/GREEN/REFACTOR
2. Create parent issue for epic tracking
3. Establish dependency chains (use --blocks for blockers)
4. Each task must be independently deployable
5. Use 'bd create' commands I can execute directly

OUTPUT:
- One parent epic issue
- 4-6 child issues with proper dependencies
- Ready work clearly identified
- Commands formatted for copy-paste execution"
```

### AI Prompt: Agent Session Resume

```bash
ai "I'm resuming work on this project. Query Beads and tell me:

1. What tasks are ready to work on? (bd ready)
2. What was I last working on? (bd status --mine)
3. What's blocking the most tasks? (bd blockers)
4. Show me the critical path to completion

Analyze the output and recommend which task I should start next and why."
```

### AI Prompt: Discovered Work During Implementation

```bash
ai "While implementing bd-c3d4, I discovered we need input validation middleware.

Create a Beads issue for this discovered work:
- Link to the issue where I discovered it (--discovered-from bd-c3d4)
- Make it block bd-c3d4 if it should be done first
- Keep scope to 4-8 hours
- Include RED/GREEN/REFACTOR criteria"
```

## Beads vs Traditional Issue Tracking

### Where Beads Wins

#### 1. AI Agent Integration

**Beads**: Claude Code can query/update issues via simple CLI commands in the same context as code

```bash
bd list --status open --json | jq '.[] | select(.priority == 0)'
bd update issue-123 --status in_progress
```

**GitHub/JIRA/Linear**: Requires API tokens, rate limits, web requests, context switching
- More complex for AI agents to orchestrate
- Need to manage authentication separately
- Network dependency

#### 2. Offline-First

**Beads**: Create/update/query issues without internet - syncs later via git push

**GitHub/JIRA/Linear**: Requires live connection to their servers
- Can't work on issues during flight/train/outage
- Every update hits their API

#### 3. Git-Native Workflow

**Beads**: Issues live in `.beads/issues.jsonl` - same repo, same branch workflow

```bash
git log -p .beads/issues.jsonl  # See issue history
git diff HEAD~1 .beads/issues.jsonl  # What issues changed?
```

**GitHub/JIRA/Linear**: Separate system with separate history
- Can't see issue changes in git log
- Code review doesn't show related issue updates
- No way to branch issues with code

#### 4. Zero External Dependencies

**Beads**: Just a CLI tool + local SQLite + JSONL files
- No account required
- No pricing tiers
- No service outages
- No vendor lock-in

**GitHub/JIRA/Linear**: Requires account, potential costs, service availability

#### 5. Speed

**Beads**: Daemon + local DB = instant queries

```bash
bd list  # <50ms (local SQLite)
```

**GitHub/JIRA/Linear**: API round-trip latency (100-500ms typical)

### Where GitHub/JIRA/Linear Win

#### 1. Team Collaboration & Visibility

**GitHub/JIRA/Linear**:
- Web UI accessible to PMs, designers, stakeholders (non-technical users)
- Comments, mentions, notifications
- Rich formatting, attachments, screenshots
- Easier for non-developers to participate

**Beads**:
- CLI-first (non-technical users struggle)
- Everyone needs git access
- Less discoverability ("what issues exist?")

#### 2. Rich Features

**GitHub Issues**:
- PR auto-linking (`closes #123`)
- GitHub Actions integration
- Project boards
- Milestones, releases

**JIRA**:
- Custom workflows
- Time tracking, sprint planning
- Advanced JQL queries
- Agile boards, burndown charts

**Linear**:
- Keyboard shortcuts, fast UI
- Cycles, roadmaps
- Slack/Discord integration
- Beautiful design

**Beads**:
- Basic fields (title, description, status, priority)
- Simple dependencies
- Limited querying (no complex JQL equivalent)

#### 3. Integrations

**GitHub/JIRA/Linear**: Hundreds of integrations
- Slack, Discord, email notifications
- Zapier, webhooks
- CI/CD pipelines
- Analytics tools

**Beads**: Minimal integrations (experimental JIRA/Linear/GitHub sync)

#### 4. Search & Discoverability

**GitHub/JIRA/Linear**:
- Full-text search across all issues
- Advanced filters, saved searches
- Global search across repos/projects

**Beads**:
- SQLite queries or grep through JSONL
- Less powerful search
- No global search across repos

#### 5. Reporting & Analytics

**JIRA/Linear**:
- Burndown charts
- Velocity tracking
- Custom dashboards
- Time in status reports

**Beads**:
- Raw data in JSONL/DB
- Need to build your own analytics

### When to Use Each Tool

#### Use Beads When:

✅ You're a solo developer or small technical team (everyone comfortable with CLI/git)
✅ AI-assisted development is core to your workflow (Claude Code, Cursor, etc.)
✅ You want issues versioned with code (same branches, same history)
✅ You work offline frequently (travel, poor connectivity)
✅ You want zero external dependencies (no accounts, no API tokens, no costs)
✅ Your issues are technical/code-centric (refactoring tasks, bug tracking)

#### Use GitHub Issues When:

✅ Your team includes non-technical members (PMs, designers, stakeholders)
✅ You're already deeply integrated with GitHub (PRs, Actions, Projects)
✅ You want PR auto-linking (`fixes #123` closes issues automatically)
✅ Open source project with external contributors (discoverable via github.com)
✅ You need community engagement (triaging, discussions, reactions)

#### Use JIRA When:

✅ Enterprise requirements (compliance, audit trails, SSO)
✅ Complex workflows (10+ states, custom transitions, approval gates)
✅ Agile ceremonies (sprint planning, burndown charts, velocity tracking)
✅ Time tracking is critical (billing, resource planning)
✅ Non-technical stakeholders need extensive visibility

#### Use Linear When:

✅ Fast-moving startups that want speed + beauty
✅ Engineering teams that dislike JIRA complexity
✅ Keyboard-first users who want fastest possible issue management
✅ Product teams collaborating closely with engineering
✅ Roadmap visibility is important for stakeholders

### Hybrid Approach

You can combine tools for different purposes:

```bash
# Local development with Beads (fast, AI-friendly)
bd create "Refactor phase2_director.py"
bd update screencast-optimizer-rva.3 --status in_progress

# Sync to Linear/JIRA/GitHub for visibility (experimental feature)
bd sync --to linear  # Pushes to Linear API
```

Beads has experimental bi-directional sync with Linear/JIRA/GitHub. This allows you to:
- Keep using Beads for internal development tracking (refactoring, tech debt)
- Use GitHub Issues for user-facing features/bugs (discoverable, external contributions)
- Get the best of both worlds

### Quick Comparison Table

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

## Integration with Development Patterns

### With CI/CD Pipelines

```bash
# Add CI integration to issue body
bd create --title "Add health check endpoint" \
  --body "RED: Write test for GET /health
GREEN: Return 200 with system status
REFACTOR: Extract status checks to service

CI/CD HOOKS:
- Trigger: On PR creation for this issue
- Tests: pytest tests/test_health.py
- Deploy: Auto-deploy to dev on green"
```

### With Epic Management

```bash
# Query epic progress in CI
bd show bd-a1b2 --tree | grep "Progress:"
# Progress: 3/4 complete (75%)

# Auto-close epic when all children done
if bd children bd-a1b2 --status open | wc -l == 0; then
  bd done bd-a1b2
  bd create --title "Epic: User Authorization System" --body "Next phase"
fi
```

### With Issue Generator Script

```python
#!/usr/bin/env python3
"""
Integrate Beads with AI issue generation
"""
import subprocess
import json

def create_beads_issue(title, body, parent=None, blocks=None):
    """Create Beads issue via subprocess"""
    cmd = ['bd', 'create', '--title', title, '--body', body, '--format', 'json']

    if parent:
        cmd.extend(['--parent', parent])
    if blocks:
        cmd.extend(['--blocks', blocks])

    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)['id']

def generate_feature_issues(feature_name, task_descriptions):
    """Generate epic with child tasks"""
    # Create parent epic
    epic_id = create_beads_issue(
        title=f"Epic: {feature_name}",
        body=f"Complete implementation of {feature_name}"
    )

    # Create child tasks with dependencies
    previous_task = None
    for task in task_descriptions:
        task_id = create_beads_issue(
            title=task['title'],
            body=task['body'],
            parent=epic_id,
            blocks=previous_task if task.get('sequential') else None
        )
        if task.get('sequential'):
            previous_task = task_id

    return epic_id

# Example usage
if __name__ == '__main__':
    epic_id = generate_feature_issues(
        "User Authentication",
        [
            {
                'title': 'Setup database schema',
                'body': 'RED: Write migration test\nGREEN: Create users table\nREFACTOR: Add indexes',
                'sequential': True
            },
            {
                'title': 'Implement login endpoint',
                'body': 'RED: Test POST /auth/login\nGREEN: Validate credentials\nREFACTOR: Extract validation',
                'sequential': True
            }
        ]
    )
    print(f"Created epic {epic_id}")
```

## Best Practices

### 1. Commit Beads Changes Regularly

```bash
# After creating issues
git add .beads/
git commit -m "beads: add authentication feature tasks"
git push

# Enable auto-commit with git hooks
cat > .git/hooks/post-beads <<'EOF'
#!/bin/bash
git add .beads/
git commit -m "beads: auto-commit issue changes"
EOF
chmod +x .git/hooks/post-beads
```

### 2. Use Descriptive Issue IDs

```bash
# Beads generates hash-based IDs, but you can add custom prefixes
bd create --title "AUTH-001: JWT Implementation" \
  --body "First task in authentication epic"

# Reference in commit messages
git commit -m "feat(auth): implement JWT generation (bd-c3d4, AUTH-001)"
```

### 3. Keep Tasks Atomic (4-8 Hours)

```bash
# Too large - break it down
❌ bd create --title "Build entire authentication system"

# Right size for AI agent
✅ bd create --title "Implement JWT token generation"
✅ bd create --title "Add token refresh endpoint"
✅ bd create --title "Write JWT integration tests"
```

### 4. Use Dependency Types Correctly

```bash
# --blocks: This must be done before dependent task can start
bd create --title "Task B" --blocks bd-a1b2

# --parent: Organizational hierarchy (epic/subissue)
bd create --title "Subissue" --parent bd-epic1

# --related: Related but not blocking
bd create --title "Documentation" --related bd-a1b2

# --discovered-from: Found during implementation
bd create --title "Bug fix" --discovered-from bd-a1b2
```

### 5. Query Work Strategically

```bash
# What can I work on now?
bd ready

# What's preventing progress?
bd blockers

# What's the critical path?
bd critical

# Show my assigned work
bd list --assignee me --status open

# Epic overview
bd show epic-id --tree
```

## Real-World Example: Full Feature Development

```bash
# 1. Agent starts new feature
bd create --title "Epic: Two-Factor Authentication" \
  --body "Add 2FA support with TOTP and backup codes"
# bd-2fa1

# 2. Agent breaks down into tasks
bd create --title "Add TOTP library dependency" \
  --body "RED: Test TOTP.generate()\nGREEN: Install pyotp\nREFACTOR: Version pin" \
  --parent bd-2fa1
# bd-2fa2

bd create --title "Create 2FA settings table" \
  --body "RED: Test migration\nGREEN: Add user_2fa_settings table\nREFACTOR: Add indexes" \
  --parent bd-2fa1
# bd-2fa3

bd create --title "Implement TOTP enrollment endpoint" \
  --body "RED: Test POST /auth/2fa/enroll\nGREEN: Generate QR code\nREFACTOR: Extract QR service" \
  --parent bd-2fa1 \
  --blocks bd-2fa2,bd-2fa3
# bd-2fa4

bd create --title "Add 2FA verification to login" \
  --body "RED: Test login with 2FA\nGREEN: Verify TOTP code\nREFACTOR: Add rate limiting" \
  --parent bd-2fa1 \
  --blocks bd-2fa4
# bd-2fa5

# 3. Agent checks ready work
bd ready
# bd-2fa2: Add TOTP library dependency
# bd-2fa3: Create 2FA settings table

# 4. Agent works in parallel on independent tasks
bd start bd-2fa2
# ... implement ...
bd done bd-2fa2

bd start bd-2fa3
# ... implement ...
bd done bd-2fa3

# 5. Next task automatically becomes ready
bd ready
# bd-2fa4: Implement TOTP enrollment endpoint

# 6. Agent discovers missing work during implementation
bd create --title "Add backup codes generation" \
  --body "User needs backup codes when TOTP device unavailable" \
  --discovered-from bd-2fa4 \
  --parent bd-2fa1 \
  --blocks bd-2fa5
# bd-2fa6

# 7. Complete feature
bd done bd-2fa4
bd start bd-2fa6
# ... implement ...
bd done bd-2fa6
bd done bd-2fa5

# 8. Check epic completion
bd show bd-2fa1 --tree
# bd-2fa1: Epic: Two-Factor Authentication [open]
#   ├─ bd-2fa2: Add TOTP library dependency [done]
#   ├─ bd-2fa3: Create 2FA settings table [done]
#   ├─ bd-2fa4: Implement TOTP enrollment endpoint [done]
#   ├─ bd-2fa5: Add 2FA verification to login [done]
#   └─ bd-2fa6: Add backup codes generation [done]
# Progress: 5/5 complete (100%)

bd done bd-2fa1

# 9. Sync with team
git add .beads/
git commit -m "beads: complete 2FA epic (bd-2fa1)"
git push
```

## Troubleshooting

### Sync Issues

```bash
# Force reimport from JSONL
bd sync

# Check for conflicts
bd status --conflicts

# View sync log
cat .beads/sync.log
```

### Database Corruption

```bash
# Rebuild from JSONL source of truth
rm .beads/beads.db
bd sync
```

### Viewing Raw Data

```bash
# JSONL source files
cat .beads/issues/*.jsonl | jq .

# SQLite database
sqlite3 .beads/beads.db "SELECT * FROM issues WHERE status='open';"
```

## Summary

Beads provides AI agents with persistent memory for issue tracking through:

- **Git-based distribution**: JSONL files sync via normal git workflows
- **Automatic dependency tracking**: Built-in relationship types keep work organized
- **Ready work detection**: Agents instantly know what they can work on
- **Zero-setup initialization**: No servers, no configuration files
- **CLI-first design**: Perfect for AI agent automation
- **Multi-agent coordination**: Hash-based IDs prevent conflicts

This makes Beads ideal for AI-driven development workflows where agents need to:
- Resume complex tasks across sessions
- Track dependencies automatically
- Coordinate work across multiple agents
- Maintain persistent memory in a git-based workflow
- Query ready work without complex APIs

For more details, see the [Beads documentation](https://github.com/steveyegge/beads).
