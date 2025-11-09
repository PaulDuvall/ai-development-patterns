# AI Prompts for Epic-Subissue Management

Direct AI instructions for creating and managing epic-subissue relationships across issue tracking systems.

## Epic Creation with Subissue Breakdown

```bash
ai "Create an epic for User Authentication System with the following requirements:

EPIC REQUIREMENTS:
1. Break into tasks that can be deployed in less than a day (4-8 hours max)
2. Each task must be independently deployable
3. Use RED/GREEN/REFACTOR approach for all code tasks
4. Ensure CI/CD pipeline can run for each task
5. Create cross-links between epic and all subissues

EPIC STRUCTURE:
- Epic title: 'Epic: User Authentication System'
- Epic description with success criteria
- List of 4-6 subissues with clear dependencies
- Each subissue references parent epic
- Progress tracking mechanism

OUTPUT FORMAT:
- Epic work item with subissue checklist
- Individual subissue work items with 'epic-123' labels
- Dependency comments in each subissue
- RED/GREEN/REFACTOR acceptance criteria"
```

## Universal Epic Linking

```bash
ai "Generate epic-subissue structure with universal compatibility:

UNIVERSAL REQUIREMENTS:
1. Parent-child references that survive tool migrations
2. Progress calculation: completed subissues / total subissues
3. Dependency chain validation (no circular dependencies)
4. Auto-update epic status when subissues change
5. CI/CD integration points for each subissue

LINKING STRATEGY:
- Use work item references for cross-linking
- Include epic ID in subissue titles or descriptions
- Use labels/tags for epic grouping (epic-auth-system)
- Status propagation rules (epic done when all subissues done)

Create: Epic + 5 subissues with proper cross-references"
```

## RED/GREEN/REFACTOR Task Structure

```bash
ai "Break down this feature using RED/GREEN/REFACTOR approach:

FEATURE: Password validation service

RED/GREEN/REFACTOR BREAKDOWN:
1. RED: Write failing tests for password validation
   - Deploy target: Test suite with failing tests
   - CI/CD: Tests run and fail as expected
   - Independent: Can deploy without breaking existing code

2. GREEN: Implement minimum code to pass tests
   - Deploy target: Working password validation
   - CI/CD: All tests pass, feature flags control activation
   - Independent: Behind feature flag, safe to deploy

3. REFACTOR: Optimize and clean implementation
   - Deploy target: Improved performance/maintainability
   - CI/CD: No functional changes, all tests still pass
   - Independent: Pure refactor, no user-facing changes

Each phase must:
- Be deployable within same day
- Have clear acceptance criteria
- Pass through CI/CD pipeline
- Link back to parent epic"
```

## Automated Progress Tracking Prompts

```bash
ai "Create progress tracking for epic AUTH-001 with these subissues:

SUBISSUES STATUS:
- AUTH-002 (Password validation): Completed
- AUTH-003 (JWT service): In Progress (60% done)
- AUTH-004 (Registration API): Not Started
- AUTH-005 (Integration tests): Blocked by AUTH-002, AUTH-003

GENERATE:
1. Epic progress summary (% complete)
2. Updated epic description with current status
3. Next action recommendations
4. Risk assessment for blocked items
5. Stakeholder communication text

UPDATE EPIC with:
- Progress: X% (N/M subissues completed)
- Status: [Not Started/In Progress/Completed]
- Next Actions: Specific next steps
- Blockers: List of blocking issues with mitigation"
```

## CI/CD Integration Instructions

```bash
ai "Generate CI/CD pipeline requirements for epic subissues:

PIPELINE REQUIREMENTS per subissue:
1. Automated testing (unit, integration, security)
2. Code quality gates (linting, coverage >90%)
3. Deployment automation (staging → production)
4. Rollback capability for each deployment
5. Epic progress notification on completion

Create CI/CD workflows that include:
- Workflow trigger: subissue completion
- Epic progress update job
- Dependency unblocking automation
- Stakeholder notification on epic completion

Output: Workflow configuration that handles epic lifecycle automation"
```

## Dependency Management Prompts

```bash
ai "Validate and optimize dependencies for User Dashboard epic:

CURRENT DEPENDENCIES:
- Database schema → API endpoints → Frontend components
- Each layer depends on previous layer completion

OPTIMIZATION REQUIREMENTS:
1. Identify parallel work opportunities
2. Eliminate unnecessary dependencies
3. Validate no circular dependencies exist
4. Minimize critical path length
5. Enable maximum team parallelization

CHECK FOR:
- Can database and API work happen in parallel?
- Can frontend use mock data initially?
- Are all dependencies truly necessary?
- What's the minimum viable epic (MVE)?

OUTPUT:
- Optimized dependency graph
- Parallel execution plan
- Risk mitigation for critical path
- Reduced epic completion time estimate"
```

## Simple Epic Status Automation

```bash
ai "Create automatic epic status updates using simple rules:

AUTOMATION RULES:
1. When subissue closed → update epic progress
2. When all subissues closed → mark epic complete
3. When epic >50% complete → notify stakeholders
4. When subissue blocked >2 days → escalate

IMPLEMENTATION:
- Use webhooks/automation rules
- Simple percentage calculation
- Comment-based progress updates
- Label-based status tracking

Generate automation rules that maintain epic-subissue relationships with minimal manual intervention"
```

These prompts focus on **direct AI instructions** rather than complex tooling, emphasizing the core principles: <1 day deployment, independent tasks, cross-linking, RED/GREEN/REFACTOR, and CI/CD integration.