# AI Issue Generation Example

This directory contains a complete implementation of the AI Issue Generation pattern with Kanban-optimized work item creation, GitHub/JIRA integration, and workflow automation.

## Directory Structure

```
ai-issue-generation/
├── README.md                  # This file
├── issue-generator.py         # AI-powered issue generation tool
├── github-integration.py      # GitHub Issues API integration
├── jira-integration.py        # JIRA API integration
├── kanban-templates/          # Issue templates for different work types
│   ├── feature-template.json
│   ├── bug-template.json
│   ├── epic-template.json
│   └── task-template.json
├── examples/                  # Example generated issues
│   ├── password-reset-feature/
│   ├── user-dashboard-epic/
│   └── api-optimization-tasks/
└── workflows/                 # Workflow automation
    ├── github-actions.yml
    └── automation-scripts/
```

## Key Features

- **Kanban-Optimized Work Items**: 4-8 hour tasks for continuous flow
- **Multi-Platform Integration**: GitHub Issues, JIRA, Azure DevOps
- **Template-Based Generation**: Consistent issue formatting
- **Dependency Mapping**: Automatic task dependency detection
- **Cycle Time Tracking**: Measure actual vs estimated completion times
- **Automated Workflows**: CI/CD integration for issue lifecycle

## Quick Start

1. **Generate issues from requirements:**
   ```bash
   python issue-generator.py --input requirements.md --platform github
   ```

2. **Create Kanban epic breakdown:**
   ```bash
   python issue-generator.py --epic "User Dashboard" --break-down
   ```

3. **Integrate with GitHub:**
   ```bash
   python github-integration.py --create-batch issues.json
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

### Epic Decomposition  
```bash
# Input: Large epic
python issue-generator.py \
  --epic "User Analytics Dashboard" \
  --template epic \
  --kanban-optimized \
  --dependencies
```

### Bug Triage
```bash
# Input: Bug report
python issue-generator.py \
  --bug "Login fails with 500 error" \
  --priority high \
  --assign-team backend
```

## Integration

This tool integrates with:
- **GitHub Issues** - Complete API integration with labels, milestones, assignees
- **JIRA** - Story creation with epics, components, and custom fields  
- **Azure DevOps** - Work item creation with area paths and iterations
- **Linear** - Issue creation with teams, projects, and cycles
- **CI/CD Pipelines** - Automated issue creation from failed builds

See individual integration files for setup and configuration details.