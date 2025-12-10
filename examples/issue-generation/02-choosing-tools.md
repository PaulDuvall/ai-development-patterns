# Choosing Your Issue Tracking Tool

Decision framework for selecting between Beads, GitHub Issues, JIRA, and Linear for AI-assisted development.

## Quick Decision Tree

```
Are you primarily using AI coding agents (Claude Code, Cursor, etc.)?
├─ YES → Do you work offline frequently or want git-native issues?
│   ├─ YES → Use Beads (see beads-guide.md)
│   └─ NO → Do you have non-technical stakeholders who need issue access?
│       ├─ YES → Use GitHub/JIRA/Linear (see below)
│       └─ NO → Use Beads (faster for AI agents)
└─ NO → Do you have enterprise requirements (SSO, audit trails)?
    ├─ YES → Use JIRA
    └─ NO → Use GitHub Issues or Linear
```

## Comparison Table

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

## When to Use Beads

### ✅ Perfect For:

**Solo developers or small technical teams**
- Everyone comfortable with CLI and git
- No need for web UI access
- Want maximum speed for AI agents

**AI-first development workflows**
- Using Claude Code, Cursor, or similar AI tools daily
- AI agents need to query/update issues automatically
- Want issues to have persistent memory across sessions

**Git-native workflows**
- Want issues versioned with code in the same repository
- Need to see issue history in git log
- Want to branch issues with code changes

**Offline or distributed work**
- Frequent travel with limited connectivity
- Work on planes, trains, or in areas with poor internet
- Want zero dependency on external services

**Example Use Case:**
```bash
# AI agent workflow with Beads
bd create --title "Add JWT token validation" \
  --body "RED: Write failing test
GREEN: Implement validation
REFACTOR: Extract key management"

# AI agent queries ready work
bd ready  # <50ms response
# bd-a1b2: Add JWT token validation

# Work on task
bd update bd-a1b2 --status in_progress
ai "implement JWT validation following RED/GREEN/REFACTOR"

# Complete and sync
bd update bd-a1b2 --status done
git add .beads/ && git commit -m "beads: complete JWT validation"
git push
```

### ❌ Not Ideal For:

- Teams with non-technical stakeholders (PMs, designers, executives)
- Open source projects needing external contributor visibility
- Teams requiring rich collaboration (comments, mentions, attachments)
- Need for extensive integrations (Slack, Zapier, analytics tools)

## When to Use GitHub Issues

### ✅ Perfect For:

**Teams with mixed technical levels**
- Developers, PMs, designers all need access
- Web UI more accessible than CLI
- Need comments, mentions, reactions

**Open source projects**
- External contributors discover issues via github.com
- Community engagement and discussions
- Public visibility and discoverability

**GitHub-centric workflows**
- Already using GitHub for code hosting
- Want PR auto-linking (`closes #123`)
- Using GitHub Actions for CI/CD
- Project boards for planning

**Example Use Case:**
```yaml
# PR auto-closes issue
git commit -m "feat: add JWT validation

Implements token validation with exp/iat checks.
Tests included with 98% coverage.

Closes #42"

# GitHub automatically:
# - Links PR to issue
# - Closes issue when PR merges
# - Notifies stakeholders
```

### ❌ Not Ideal For:

- Pure AI agent workflows (API slower than Beads CLI)
- Offline work (requires internet connection)
- Git-native issue versioning (issues separate from code)

## When to Use JIRA

### ✅ Perfect For:

**Enterprise requirements**
- SSO integration (SAML, LDAP)
- Audit trails and compliance
- Complex approval workflows (10+ states)
- Security and governance needs

**Agile ceremonies**
- Sprint planning with story points
- Burndown charts and velocity tracking
- Time tracking for billing/resource planning
- Retrospective and estimation tools

**Large organizations**
- Multiple teams with different workflows
- Custom fields and issue types
- Advanced JQL queries
- Hierarchical epic/story/subtask structures

**Example Use Case:**
```jql
# Complex query across projects
project in (AUTH, INFRA) AND
  sprint = "Sprint 42" AND
  status changed from "In Progress" to "Done"
  DURING (startOfWeek(), endOfWeek()) AND
  assignee in membersOf("Backend Team")
ORDER BY priority DESC
```

### ❌ Not Ideal For:

- Small teams (overhead too high)
- AI-first workflows (complex API, slow queries)
- Startups wanting speed over process
- Teams who find JIRA's complexity frustrating

## When to Use Linear

### ✅ Perfect For:

**Fast-moving startups**
- Want speed and beauty over enterprise features
- Engineering teams that hate JIRA
- Product teams collaborating closely with engineers

**Keyboard-first users**
- Lightning-fast keyboard shortcuts
- Minimal clicks to create/update issues
- Modern, responsive UI

**Roadmap visibility**
- Cycles (2-week iterations)
- Roadmap views for stakeholders
- Progress tracking across teams

**Modern integrations**
- Slack, Discord, Figma
- GitHub PR linking
- API-first architecture

**Example Use Case:**
```bash
# Create issue with keyboard
Cmd+K → "Create issue" →
  Title: "Add JWT validation"
  Project: Auth
  Cycle: Current
  Estimate: <1 hour
  → Enter

# Total time: <10 seconds
```

### ❌ Not Ideal For:

- Enterprise requirements (no SSO on lower tiers)
- Complex multi-stage workflows
- Teams needing extensive customization
- AI agent workflows (API better than JIRA, slower than Beads)

## Hybrid Approach

You can use multiple tools for different purposes:

### Pattern 1: Beads + GitHub Issues

```bash
# Internal tech work: Beads
bd create "Refactor authentication module"
bd create "Extract key management service"
bd create "Add integration tests for auth flow"

# User-facing work: GitHub Issues
gh issue create --title "Password reset not working on mobile"
gh issue create --title "Feature request: Social login"

# Benefits:
# - AI agents use Beads (fast CLI)
# - Users/stakeholders use GitHub (web UI)
# - Clear separation of internal vs external work
```

### Pattern 2: Beads with Sync (Experimental)

```bash
# Work locally with Beads
bd create "Add JWT validation"
bd update issue-generation-7c9.1 --status done

# Sync to external system for visibility
bd sync --to linear  # Experimental feature
bd sync --to github  # Experimental feature

# Benefits:
# - Speed of Beads for development
# - Visibility in traditional tools for stakeholders
```

## Real-World Scenarios

### Scenario 1: Solo Developer with AI Agent
**Recommendation**: Beads
- Fastest for AI queries (<50ms)
- No external dependencies
- Git-native workflow
- Offline capable

### Scenario 2: 5-Person Startup (All Developers)
**Recommendation**: Beads or Linear
- Beads if everyone likes CLI and AI-first
- Linear if team wants modern web UI
- Both fast enough for small teams

### Scenario 3: 10-Person Team (Devs + PM + Designer)
**Recommendation**: GitHub Issues or Linear
- PM and designer need web access
- Linear if budget allows (better UX)
- GitHub if already on GitHub

### Scenario 4: 50-Person Engineering Org
**Recommendation**: JIRA or Linear
- JIRA for enterprise features, compliance
- Linear for speed, modern UX
- Consider GitHub for open source projects

### Scenario 5: Open Source Project
**Recommendation**: GitHub Issues
- Public visibility for contributors
- Community engagement features
- PR auto-linking
- Free for public repos

## Migration Considerations

### Moving from JIRA to Beads
```bash
# Export JIRA issues
jira export --project AUTH --format json > jira-issues.json

# Import to Beads (script)
python import-to-beads.py jira-issues.json

# Benefits:
# - Escape JIRA complexity
# - Faster AI agent access
# - Git-native workflow
```

### Moving from Beads to GitHub
```bash
# Beads has experimental sync
bd sync --to github

# Or manual export
bd list --json | gh-import-tool

# When to do this:
# - Adding non-technical team members
# - Open sourcing the project
# - Need for richer collaboration
```

## Summary Recommendations

### Choose Beads If:
1. AI-assisted development is your primary workflow
2. You're solo or small technical team
3. You want git-native issues
4. You work offline frequently
5. You want <50ms query speed

### Choose GitHub Issues If:
1. Team includes non-technical members
2. Open source project
3. Already GitHub-centric
4. Want PR auto-linking
5. Need community engagement

### Choose JIRA If:
1. Enterprise requirements (SSO, compliance)
2. Complex workflows
3. Agile ceremonies and reporting
4. Time tracking critical
5. Large organization (50+ people)

### Choose Linear If:
1. Fast-moving startup
2. Dislike JIRA complexity
3. Want modern, beautiful UI
4. Keyboard-first users
5. Product/engineering collaboration

## Next Steps

**If you chose Beads**: See [beads-guide.md](beads-guide.md) for setup and usage

**If you chose traditional tools**: See [03-ai-prompts.md](03-ai-prompts.md) for AI prompt templates that work across all platforms

**Learn more**: [01-getting-started.md](01-getting-started.md) for core concepts
