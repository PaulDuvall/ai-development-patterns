# AI Issue Generation Examples

Learn how to generate Kanban-optimized issues for AI-assisted development with <1 hour cycle times.

## 🚀 Quick Start

**New to AI issue generation?** Follow this learning path:

1. **[Getting Started](01-getting-started.md)** - Core concepts, why <1 hour tasks, AI development velocity
2. **[Choosing Tools](02-choosing-tools.md)** - Decision framework: Beads vs GitHub/JIRA/Linear
3. **[AI Prompts](03-ai-prompts.md)** - Templates for epic breakdown, progress tracking, dependencies
4. **[Workflow Examples](04-workflow-examples.md)** - Real-world epic management and relationship patterns
5. **[CI Integration](05-ci-integration.md)** - Traceability, file validation, automated reporting

**For Beads users**: See [beads-guide.md](beads-guide.md) for git-native, AI-first issue tracking

## Directory Structure

```
├── README.md                      # You are here - navigation hub
├── 01-getting-started.md          # Core concepts and AI-first principles
├── 02-choosing-tools.md           # Tool comparison and decision framework
├── 03-ai-prompts.md               # AI prompt templates for issue generation
├── 04-workflow-examples.md        # Epic breakdown and relationship patterns
├── 05-ci-integration.md           # CI/CD integration and traceability
├── beads-guide.md                 # Beads setup and usage guide
└── issue-generator.py             # Python script for automated generation
```

## Key Concepts

### Why <1 Hour Tasks?

AI-assisted development is fundamentally faster than manual coding:

| Activity | Manual | AI-Assisted |
|----------|--------|-------------|
| Code generation | Hours | Minutes |
| Iteration cycle | Hours | 5-15 minutes |
| Deployment | 1-2x/day | Multiple times/hour |
| **Total task time** | **4-8 hours** | **<1 hour** |

**Traditional**: `Planning (30min) + Coding (6hrs) + Testing (1hr) + Review (30min) = 8 hours`

**AI-Assisted**: `Planning (5min) + AI prompting (10min) + Review (20min) + Testing (15min) = 50 minutes`

See [01-getting-started.md](01-getting-started.md) for detailed velocity comparisons.

### Core Principles

1. **Flow over estimates**: Split work until each task is <1 hour
2. **Independent deployment**: Every task ships without waiting
3. **RED/GREEN/REFACTOR**: Test-first, minimal implementation, then clean
4. **CI/CD always**: Every task runs through the pipeline

## Tool Decision Framework

### Choose Beads if:
- AI-assisted development is your primary workflow
- Solo developer or small technical team
- Want git-native issues versioned with code
- Work offline frequently
- Need <50ms query speed for AI agents

### Choose GitHub/JIRA/Linear if:
- Team includes non-technical stakeholders
- Need rich collaboration (comments, mentions, web UI)
- Open source with external contributors
- Enterprise requirements (SSO, compliance)

See [02-choosing-tools.md](02-choosing-tools.md) for complete comparison and decision tree.

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

**Key Insights**:
- **Beads excels** for AI agent workflows, offline development, and git-native issue tracking
- **GitHub/JIRA/Linear excel** for team collaboration, rich features, and stakeholder visibility
- **Consider a hybrid approach**: Use Beads for internal tech work, traditional tools for external visibility

## Quick Examples

### Create Epic with <1 Hour Tasks

```bash
ai "Create epic for User Authentication with subissues that are:
1. Deployable in <1 hour each (AI-assisted development)
2. Independently deployable
3. Cross-linked to parent epic
4. Include RED/GREEN/REFACTOR acceptance criteria
5. Have CI/CD pipeline hooks"
```

### Break Down Feature

```bash
ai "Break down 'User Dashboard' epic following these rules:
- Each subissue must be deployable in <1 hour (AI-assisted development)
- Create bidirectional epic-subissue links
- Use RED/GREEN/REFACTOR for development tasks
- Include CI/CD pipeline triggers for each subissue
- Auto-update epic progress when subissues complete"
```

See [03-ai-prompts.md](03-ai-prompts.md) for complete prompt library.

### Beads Workflow (CLI)

```bash
# Create epic
bd create --title "Epic: User Auth System"

# Create subtask with RED/GREEN/REFACTOR
bd create --title "Add JWT validation" \
  --body "RED: Write failing test
GREEN: Implement validation
REFACTOR: Extract key management" \
  --parent issue-generation-7c9

# Query ready work (<50ms)
bd ready

# Update status
bd update issue-generation-7c9.1 --status done

# Sync via git
git add .beads/ && git commit -m "beads: complete JWT validation"
```

See [beads-guide.md](beads-guide.md) for complete Beads tutorial.

## Integration Philosophy

Rather than complex API scripts, use AI prompts that work with your existing issue tracking tools:

- **Direct AI Interface**: Let AI tools create issues directly through their integrations
- **Platform-Agnostic Prompts**: Same prompt structure works across GitHub, JIRA, Azure DevOps
- **Focus on Requirements**: Specify what you need (timing, dependencies, CI/CD), not how to implement
- **Automation Through Simplicity**: Use platform's built-in automation rather than custom scripts
- **Git-Native Option**: For AI-first workflows, consider Beads for CLI-native, offline-capable issue tracking

## Learning Path

### Beginners
1. Start: [01-getting-started.md](01-getting-started.md)
2. Choose: [02-choosing-tools.md](02-choosing-tools.md)
3. Try: Pick one AI prompt from [03-ai-prompts.md](03-ai-prompts.md)

### Intermediate
1. Review: [04-workflow-examples.md](04-workflow-examples.md)
2. Implement: [05-ci-integration.md](05-ci-integration.md)
3. Automate: Use [issue-generator.py](issue-generator.py)

### Advanced
1. Customize: Modify prompts for your workflow
2. Integrate: Build CI/CD automation
3. Scale: Implement hybrid Beads + traditional tools

## Common Questions

**Q: Why <1 hour instead of 4-8 hours?**
A: AI generates code in minutes, not hours. See [01-getting-started.md#why-1-hour-tasks](01-getting-started.md#why-1-hour-tasks-for-ai-development)

**Q: Which tool should I use?**
A: See the decision tree in [02-choosing-tools.md#quick-decision-tree](02-choosing-tools.md#quick-decision-tree)

**Q: How do I break down large epics?**
A: Use AI prompts from [03-ai-prompts.md#epic-creation](03-ai-prompts.md#epic-creation-with-subissue-breakdown)

**Q: Can I use Beads with GitHub?**
A: Yes! See hybrid approach in [02-choosing-tools.md#hybrid-approach](02-choosing-tools.md#hybrid-approach)

## Resources

- **Python Script**: [issue-generator.py](issue-generator.py) - Automated issue generation
- **Main Pattern**: [../../README.md#issue-generation](../../README.md#issue-generation) - Pattern documentation

## Getting Help

- **Beads Issues**: [GitHub - steveyegge/beads](https://github.com/steveyegge/beads)
- **Pattern Issues**: [GitHub - PaulDuvall/ai-development-patterns](https://github.com/PaulDuvall/ai-development-patterns)

---

**Start here**: [01-getting-started.md](01-getting-started.md) to learn AI-first issue generation principles.
