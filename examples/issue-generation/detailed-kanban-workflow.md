# Detailed Kanban Workflow Examples

This document provides comprehensive examples for implementing the AI Issue Generation pattern with detailed Kanban workflows, epic management, and CI integration.

## Kanban Epic Breakdown Example

### Input: High-Level Epic
```markdown
## Epic: User Dashboard with Analytics
Provide users with a comprehensive dashboard showing usage analytics, performance metrics, and actionable insights.
```

### AI Prompt for Epic Breakdown
```bash
ai "Break down this epic for optimal Kanban flow:

Epic: User Dashboard with Analytics

Kanban task requirements:
- Maximum <1 hour per task (AI-assisted development)
- If a task would take longer, split it
- Each task independently deployable
- Focus on flow over estimates

Break down into:
- Database migrations (each table/index separately)
- Individual API endpoints (one endpoint per task)
- UI components (one component per task)
- Test suites (by feature area)
- Security checks (per component)
- Performance optimizations (targeted improvements)

Goal: Continuous flow with rapid feedback cycles."
```

### Generated Work Items
```json
[
  {
    "id": "DASH-001",
    "title": "Create analytics_events table migration",
    "description": "Database migration for storing user interaction events",
    "acceptance_criteria": [
      "Create analytics_events table with proper indexes",
      "Include user_id, event_type, timestamp, metadata columns",
      "Add appropriate constraints and foreign keys"
    ],
    "cycle_time_target": "<1 hour",
    "labels": ["backend", "database", "kanban-ready"],
    "dependencies": []
  },
  {
    "id": "DASH-002",
    "title": "Analytics data collection API endpoint",
    "description": "REST endpoint to receive and store analytics events",
    "acceptance_criteria": [
      "POST /api/analytics/events endpoint",
      "Validate event payload structure",
      "Store events in analytics_events table",
      "Return appropriate status codes"
    ],
    "cycle_time_target": "6 hours",
    "labels": ["backend", "api", "kanban-ready"],
    "dependencies": ["DASH-001"]
  }
]
```

## Epic-Subissue Relationship Management

### AI-Driven Cross-Linking Strategy
```bash
ai "Generate epic-subissue relationships for:
Epic: User Authentication System

Requirements:
- Create parent-child references in both directions
- Establish dependency chains between subissues
- Include progress tracking mechanisms
- Generate status rollup criteria
- Add completion validation rules

Output universal relationship structure:
- Reference IDs for linking
- Status propagation rules
- Dependency validation
- Progress calculation logic"
```

### Generated Relationship Structure
```json
{
  "epic": {
    "id": "AUTH-001",
    "title": "Epic: User Authentication System",
    "subissues": ["AUTH-002", "AUTH-003", "AUTH-004", "AUTH-005"],
    "completion_criteria": "all_subissues_closed",
    "status_calculation": "percentage_complete"
  },
  "subissues": [
    {
      "id": "AUTH-002",
      "title": "Password validation service",
      "parent_epic": "AUTH-001",
      "blocks": [],
      "blocked_by": [],
      "completion_updates_epic": true
    },
    {
      "id": "AUTH-003",
      "title": "Email verification workflow",
      "parent_epic": "AUTH-001",
      "blocks": [],
      "blocked_by": [],
      "completion_updates_epic": true
    },
    {
      "id": "AUTH-004",
      "title": "Session management middleware",
      "parent_epic": "AUTH-001",
      "blocks": [],
      "blocked_by": [],
      "completion_updates_epic": true
    },
    {
      "id": "AUTH-005",
      "title": "Frontend login form integration",
      "parent_epic": "AUTH-001",
      "blocks": [],
      "blocked_by": ["AUTH-002", "AUTH-003", "AUTH-004"],
      "completion_updates_epic": true
    }
  ],
  "relationships": {
    "AUTH-002": {"depends_on": [], "enables": ["AUTH-005"]},
    "AUTH-003": {"depends_on": [], "enables": ["AUTH-005"]},
    "AUTH-004": {"depends_on": [], "enables": ["AUTH-005"]},
    "AUTH-005": {"depends_on": ["AUTH-002", "AUTH-003", "AUTH-004"], "enables": []}
  }
}
```

## Automated Progress Tracking

### Progress Monitoring AI Prompts
```bash
# AI-generated progress monitoring
ai "Create progress tracking for epic AUTH-001:

Monitor subissue completion and update epic status:
- Calculate completion percentage
- Identify blocking dependencies
- Update epic description with progress
- Generate status reports
- Alert on timeline risks

Track these metrics:
- Subissues completed vs total
- Cycle time per subissue
- Dependency chain health
- Epic velocity trends"
```

### Dynamic Epic Status Management
```bash
ai "Update epic AUTH-001 status based on subissue changes:

Current state:
- AUTH-002: Completed
- AUTH-003: In Progress (60% done)
- AUTH-004: Not Started
- AUTH-005: Blocked (waiting for AUTH-002, AUTH-003, AUTH-004)

Generate:
- Epic progress summary
- Updated epic description
- Risk assessment
- Next action recommendations
- Stakeholder communication"
```

## Universal Linking Implementation

### Cross-Platform Relationship Strategy
```bash
ai "Generate relationship linking strategy:

Common platform capabilities to leverage:
- Reference linking between work items
- Custom fields for parent/child relationships
- Labels for epic grouping
- Milestones for epic tracking
- Comments for progress updates

Create linking strategy that:
1. Works with platform limitations
2. Maintains bidirectional references
3. Survives tool migrations
4. Enables automated reporting"
```

### Work Item Integration Pattern
```bash
# Epic-aware work item creation
ai "Create linked work items maintaining epic relationships"

# Universal linking approach
epic_id="EPIC-123"
parent_reference="Relates to: ${epic_id}"

# Standard relationship format
item_description="$original_description\n\n## Epic Relationship\nParent Epic: $epic_id\nDependencies: [see epic for full context]\nProgress contributes to: Epic completion"
```

## Dependency Chain Validation

### Validation AI Prompts
```bash
ai "Validate dependency relationships for epic AUTH-001:

Check for:
- Circular dependencies
- Missing prerequisite work
- Parallel work opportunities
- Critical path identification
- Resource contention

Output:
- Dependency graph validation
- Suggested scheduling optimizations
- Risk mitigation recommendations
- Parallel execution opportunities"
```

### Historical Cycle Time Integration
```bash
ai "Apply Kanban principles to split these work items:

Kanban splitting rules:
- Maximum cycle time: <1 hour (AI-assisted development)
- If >1 hour, must split into smaller items
- Each item independently deployable
- Measure actual cycle time, not estimates

Historical cycle times for AI-assisted reference:
- Authentication token generation: 30-45 minutes
- Email template setup: 15-20 minutes
- Password reset form: 20-30 minutes
- API endpoint creation: 30-40 minutes
- Database migration: 15-25 minutes per table

For each task:
1. Can it be completed in <1 hour with AI assistance?
2. If no, how to split it?
3. What's the smallest valuable increment?

Remember: Flow over estimates, rapid feedback over perfect planning."
```

## CI Integration Examples

See [ci-integration-examples.md](ci-integration-examples.md) for detailed examples of how to integrate AI-generated issues with CI workflows, including commit message formats, traceability, and automated reporting.