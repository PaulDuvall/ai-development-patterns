# Getting Started with AI Issue Generation

Learn how to generate Kanban-optimized issues for AI-assisted development workflows.

## What Are Kanban-Optimized Issues?

Kanban-optimized issues are work items designed for continuous flow rather than batched delivery. In AI-assisted development, this means:

- **Small, focused tasks**: <1 hour to complete
- **Independently deployable**: Each task can ship without waiting for others
- **Continuous feedback**: Deploy and validate multiple times per day
- **Reduced work-in-progress**: Finish tasks quickly, don't accumulate partially-done work

## Why <1 Hour Tasks for AI Development?

AI fundamentally changes development velocity. What used to take hours now takes minutes:

### Traditional Manual Coding (4-8 hour tasks)
```
Planning (30 min) → Coding (6 hours) → Testing (1 hour) → Review (30 min) = 8 hours
```

### AI-Assisted Development (<1 hour tasks)
```
Planning (5 min) → AI prompting (10 min) → Review/refine (20 min) → Testing (15 min) → Deploy (10 min) = 60 min
```

### Key Differences

| Aspect | Manual Coding | AI-Assisted |
|--------|---------------|-------------|
| **Code generation** | Hours of typing | Minutes of prompting |
| **Iteration cycle** | Hours per change | 5-15 minutes per iteration |
| **Testing** | Manual, sequential | Automated, parallel |
| **Deployment** | 1-2x per day | Multiple times per hour |
| **Feedback loop** | End of day | Immediate |

### Real-World AI Development Cycle Times

Based on AI-assisted development:
- **JWT token generation**: 30-45 minutes (not 8 hours)
- **API endpoint**: 30-40 minutes (not 6 hours)
- **Database migration**: 15-25 minutes (not 3 hours)
- **Email template**: 15-20 minutes (not 4 hours)
- **Password reset form**: 20-30 minutes (not 4 hours)

## Core Principles

### 1. Flow Over Estimates

Don't spend time estimating 4, 8, or 13 story points. Instead:
- **Split work** until each task is <1 hour
- **Measure actual cycle time** from start to production
- **Optimize for throughput**, not utilization

```bash
❌ "This epic is 40 story points"
✅ "This epic has 12 tasks, each <1 hour"
```

### 2. Independent Deployment

Every task should be deployable without waiting for other tasks:

```bash
✅ "Add JWT token generation function"
   → Can deploy with feature flag
   → Doesn't break existing code
   → Tests pass independently

❌ "Implement complete authentication system"
   → Can't deploy until entire system is done
   → High risk, long feedback cycle
```

### 3. RED/GREEN/REFACTOR Development Cycle

Break even small tasks into three phases:

```bash
# Task: "Add JWT token validation middleware" (<1 hour total)

## RED (15 minutes)
- Write failing test for middleware
- Define expected behavior
- Deploy test suite (CI runs, test fails as expected)

## GREEN (25 minutes)
- AI generates minimum implementation
- Make test pass
- Deploy behind feature flag

## REFACTOR (20 minutes)
- Clean up generated code
- Extract key management
- Add documentation
- Deploy refactored version
```

### 4. CI/CD for Every Task

Each task should trigger and pass through your CI/CD pipeline:

```yaml
Task: "Add password reset endpoint"
  ↓
Commit → CI Pipeline:
  - Lint check ✓
  - Unit tests ✓
  - Integration tests ✓
  - Security scan ✓
  - Deploy to dev ✓
  ↓
Production (with feature flag)
```

## Task Splitting Examples

### Too Large (>1 Hour)
```markdown
❌ "Implement user authentication system"
   - Too many components
   - Can't deploy incrementally
   - High risk
```

### Right Size (<1 Hour Each)
```markdown
✅ "Add JWT token generation function"
✅ "Add token validation middleware"
✅ "Create /auth/login endpoint"
✅ "Add password hashing utility"
✅ "Write integration tests for auth flow"
✅ "Add rate limiting to login"
✅ "Create session management middleware"
```

### AI-Assisted Splitting Prompt
```bash
ai "Split this feature into <1 hour tasks for AI-assisted development:

Feature: User password reset via email

Requirements:
- Each task <1 hour with AI assistance
- Independently deployable
- Include RED/GREEN/REFACTOR phases
- Specify CI/CD requirements"
```

## Getting Started Workflow

### Step 1: Choose Your Tools

See [02-choosing-tools.md](02-choosing-tools.md) to decide between:
- **Beads**: Git-native, CLI-first, offline-capable (ideal for AI agents)
- **GitHub/JIRA/Linear**: Web UI, team collaboration, enterprise features

### Step 2: Learn AI Prompts

See [03-ai-prompts.md](03-ai-prompts.md) for templates to:
- Break down epics into <1 hour tasks
- Generate RED/GREEN/REFACTOR acceptance criteria
- Create dependency chains
- Track progress automatically

### Step 3: Understand Workflows

See [04-workflow-examples.md](04-workflow-examples.md) for:
- Epic breakdown examples
- Relationship management patterns
- Progress tracking strategies
- Dependency validation

### Step 4: Integrate CI/CD

See [05-ci-integration.md](05-ci-integration.md) for:
- Traceability patterns
- File change validation
- Coverage enforcement
- Automated reporting

## Quick Start Example

```bash
# 1. Create an epic
ai "Create epic: User Dashboard with Analytics
Break into <1 hour tasks, each independently deployable"

# 2. AI generates 8 tasks:
- Create analytics_events table (25 min)
- Add /api/analytics/events endpoint (35 min)
- Create dashboard data aggregation service (45 min)
- Add GET /api/dashboard/stats endpoint (30 min)
- Create DashboardCard React component (40 min)
- Add chart visualization component (50 min)
- Write integration tests for analytics flow (45 min)
- Add real-time updates with WebSocket (55 min)

# 3. Work on first task
git checkout -b analytics-events-table
ai "Implement analytics_events table migration following RED/GREEN/REFACTOR"
git add . && git commit -m "feat: add analytics events table"
git push && create-pr

# 4. CI runs automatically
- Tests pass ✓
- Deploy to dev ✓
- Merge to main ✓

# 5. Repeat for next task (all done in <8 hours total)
```

## Common Mistakes

### ❌ Mistake 1: Using Manual Coding Time Estimates
```bash
"This will take 4-8 hours"
→ AI can do it in 30-45 minutes
```

### ❌ Mistake 2: Not Splitting Tasks Small Enough
```bash
"Implement authentication" (4-6 hours even with AI)
→ Split into 8 tasks of <1 hour each
```

### ❌ Mistake 3: Batching Deployments
```bash
"Let's finish all 8 tasks then deploy"
→ Deploy each task as soon as it's done
```

### ❌ Mistake 4: Skipping RED/GREEN/REFACTOR
```bash
ai "Write complete auth system with tests"
→ Break into RED (tests) → GREEN (impl) → REFACTOR (clean)
```

## Benefits of <1 Hour Tasks

1. **Faster feedback**: Find problems in minutes, not days
2. **Reduced risk**: Smaller changes = easier debugging
3. **Better flow**: No tasks stuck "in progress" for hours
4. **Higher quality**: More frequent testing and validation
5. **Team visibility**: Clear progress throughout the day
6. **AI advantage**: Leverages AI speed, not constrained by typing

## Next Steps

1. **Choose your tools**: [02-choosing-tools.md](02-choosing-tools.md)
2. **Learn AI prompts**: [03-ai-prompts.md](03-ai-prompts.md)
3. **See examples**: [04-workflow-examples.md](04-workflow-examples.md)
4. **Integrate CI/CD**: [05-ci-integration.md](05-ci-integration.md)

## Quick Reference

```bash
# Task sizing rule
Target: <1 hour
Maximum: 2 hours (if longer, split it)
Optimal: 15-45 minutes

# Task checklist
□ <1 hour with AI assistance?
□ Independently deployable?
□ Includes tests?
□ Passes through CI/CD?
□ RED/GREEN/REFACTOR phases defined?

# Daily goal
8-10 tasks per developer per day
(not 1-2 large tasks)
```

---

**Remember**: AI changes everything. Don't use manual coding timeframes. Embrace <1 hour tasks for maximum velocity and feedback.
