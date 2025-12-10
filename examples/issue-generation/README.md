# AI Issue Generation Example

This directory demonstrates the AI Issue Generation pattern focusing on practical AI prompts for creating Kanban-optimized work items with proper epic-subissue relationships.

## Directory Structure

```
ai-issue-generation/
├── README.md                           # This file
├── issue-generator.py                  # Basic issue generation example
├── ai-prompts-for-epic-management.md  # Practical AI prompts for epic-subissue management
├── beads-example.md                    # Git-based issue tracking for AI agents with persistent memory
├── ci-integration-examples.md          # CI/CD integration patterns
└── detailed-kanban-workflow.md         # Kanban workflow optimization
```

## Key Features

- **Kanban-Optimized Work Items**: 4-8 hour tasks for continuous flow
- **Epic-Subissue Relationship Management**: Bidirectional linking and progress tracking
- **Multi-Platform Integration**: GitHub Issues, JIRA, Azure DevOps with native relationship support
- **Template-Based Generation**: Consistent issue formatting with relationship metadata
- **Dependency Mapping**: Automatic task dependency detection and validation
- **Automated Progress Tracking**: Real-time epic status updates based on subissue completion
- **Workflow Automation**: CI/CD integration for epic lifecycle management
- **Cross-Platform Compatibility**: Universal linking strategies that work across tools

## Quick Start

The most effective approach is using AI prompts directly with your issue tracking system. See `ai-prompts-for-epic-management.md` for comprehensive prompt templates that ensure:
- Tasks deployable in <1 day (4-8 hours max)
- Independent deployment capability
- Epic-subissue cross-linking
- RED/GREEN/REFACTOR development cycle
- CI/CD integration for each task

Example:
```bash
ai "Create epic for User Authentication with subissues that are:
1. Deployable in <8 hours each
2. Independently deployable
3. Cross-linked to parent epic
4. Include RED/GREEN/REFACTOR acceptance criteria
5. Have CI/CD pipeline hooks"
```

## Usage Examples

### Feature Breakdown
```bash
# Input: High-level feature request
python issue-generator.py \
  --feature "Password reset via email" \
  --platform github \
  --max-hours 8 \
  --output password-reset-issues.json
```

### Epic Decomposition with Relationship Management

Use AI prompts to create properly structured epics:

```bash
ai "Break down 'User Dashboard' epic following these rules:
- Each subissue must be deployable same day (4-8 hours)
- Create bidirectional epic-subissue links
- Use RED/GREEN/REFACTOR for development tasks
- Include CI/CD pipeline triggers for each subissue
- Auto-update epic progress when subissues complete"
```

See `ai-prompts-for-epic-management.md` for complete prompt templates.

### Bug Triage
```bash
# Input: Bug report
python issue-generator.py \
  --bug "Login fails with 500 error" \
  --priority high \
  --assign-team backend
```

## Integration Philosophy

Rather than complex API scripts, use AI prompts that work with your existing issue tracking tools:

- **Direct AI Interface**: Let AI tools create issues directly through their integrations
- **Platform-Agnostic Prompts**: Same prompt structure works across GitHub, JIRA, Azure DevOps
- **Focus on Requirements**: Specify what you need (timing, dependencies, CI/CD), not how to implement
- **Automation Through Simplicity**: Use platform's built-in automation rather than custom scripts
- **Git-Native Option**: For AI-first workflows, consider Beads for CLI-native, offline-capable issue tracking (see `beads-example.md`)

The key is providing clear, specific instructions to AI that result in properly structured, deployable work items.

### When to Use Beads vs Traditional Tools

**Use Beads** (`beads-example.md`) when:
- AI-assisted development is core to your workflow (Claude Code, Cursor, etc.)
- You're a solo developer or small technical team
- You want issues versioned with code in the same git repository
- You work offline frequently or want zero external dependencies

**Use GitHub/JIRA/Linear** when:
- Your team includes non-technical stakeholders (PMs, designers)
- You need rich collaboration features (comments, mentions, web UI)
- Open source project requiring external contributor visibility
- Enterprise requirements (SSO, audit trails, complex workflows)

### Comparison Table

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

**Key Insights**:
- **Beads excels** for AI agent workflows, offline development, and git-native issue tracking
- **GitHub/JIRA/Linear excel** for team collaboration, rich features, and stakeholder visibility
- **Consider a hybrid approach**: Use Beads for internal tech work, traditional tools for external visibility