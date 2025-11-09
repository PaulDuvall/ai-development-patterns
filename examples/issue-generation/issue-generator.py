#!/usr/bin/env python3
"""
AI Issue Generation Tool

Generates Kanban-optimized work items from high-level requirements using AI assistance.
Focuses on 4-8 hour tasks for continuous flow and rapid feedback cycles.
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class KanbanIssueGenerator:
    def __init__(self):
        self.max_task_hours = 8
        self.min_task_hours = 2
        self.templates_dir = Path("kanban-templates")
        
    def generate_feature_issues(self, feature_description: str, platform: str = "github") -> List[Dict[str, Any]]:
        """
        Generate Kanban-ready issues for a feature request.
        
        Args:
            feature_description: High-level feature description
            platform: Target platform (github, jira, azure)
            
        Returns:
            List of issue dictionaries ready for API submission
        """
        print(f"🎯 Generating Kanban issues for: {feature_description}")
        
        # In a real implementation, this would call an AI service
        # For this example, we'll use templated logic
        
        issues = []
        
        # Epic level issue
        epic = self._create_epic_issue(feature_description, platform)
        issues.append(epic)
        
        # Break down into Kanban-sized stories
        stories = self._break_down_feature(feature_description, platform)
        issues.extend(stories)
        
        # Add technical tasks
        tech_tasks = self._generate_technical_tasks(feature_description, platform)
        issues.extend(tech_tasks)
        
        return issues
    
    def _create_epic_issue(self, feature_description: str, platform: str) -> Dict[str, Any]:
        """Create an epic-level issue for the feature."""
        template = self._load_template("epic", platform)
        
        epic = {
            "title": f"Epic: {feature_description}",
            "body": f"""## Epic Overview
{feature_description}

## Success Criteria
- [ ] All user stories completed
- [ ] Acceptance criteria satisfied
- [ ] Integration tests passing
- [ ] Performance requirements met

## Definition of Done
- [ ] Code reviewed and approved
- [ ] Tests written and passing (>90% coverage)
- [ ] Documentation updated
- [ ] Deployed to production

## Estimated Cycle Time
Target: 2-3 weeks with 4-6 parallel stories

Generated: {datetime.now().isoformat()}
            """,
            "labels": ["epic", "feature", "kanban"],
            "milestone": "Sprint Planning",
            "type": "epic"
        }
        
        return self._apply_platform_format(epic, platform)
    
    def _break_down_feature(self, feature_description: str, platform: str) -> List[Dict[str, Any]]:
        """Break down feature into Kanban-optimized stories (4-8 hours each)."""
        
        # Example breakdown for "Password reset via email"
        if "password reset" in feature_description.lower():
            return self._password_reset_breakdown(platform)
        elif "dashboard" in feature_description.lower():
            return self._dashboard_breakdown(platform)
        else:
            return self._generic_breakdown(feature_description, platform)
    
    def _password_reset_breakdown(self, platform: str) -> List[Dict[str, Any]]:
        """Specific breakdown for password reset feature."""
        stories = [
            {
                "title": "Backend: Password reset token generation",
                "body": """## Acceptance Criteria
- [ ] Generate secure reset tokens (UUID4 + timestamp)
- [ ] Set 15-minute expiration time
- [ ] Store tokens in Redis with TTL
- [ ] Handle token collision edge cases

## Technical Notes
- Use `secrets.token_urlsafe()` for cryptographically secure tokens
- Implement rate limiting: max 3 requests per email per hour
- Clean up expired tokens automatically

## Cycle Time Target
6-8 hours (includes testing)

## Dependencies
None - can start immediately
                """,
                "labels": ["backend", "security", "kanban-ready"],
                "estimate": "8 hours",
                "priority": "high"
            },
            {
                "title": "Backend: Email service integration",
                "body": """## Acceptance Criteria
- [ ] Integrate with SendGrid/AWS SES
- [ ] Create password reset email template
- [ ] Handle email delivery failures gracefully
- [ ] Log email sending events for debugging

## Technical Notes
- Use environment variables for API keys
- Implement retry logic with exponential backoff
- Track email delivery status

## Cycle Time Target
4-6 hours

## Dependencies
None - parallel with token generation
                """,
                "labels": ["backend", "email", "kanban-ready"],
                "estimate": "6 hours",
                "priority": "high"
            },
            {
                "title": "Frontend: Password reset form",
                "body": """## Acceptance Criteria
- [ ] Create responsive reset request form
- [ ] Add email validation
- [ ] Show success/error messages
- [ ] Implement loading states

## Technical Notes
- Use existing form components
- Add client-side validation
- Follow design system guidelines

## Cycle Time Target
4-5 hours

## Dependencies
None - can develop independently
                """,
                "labels": ["frontend", "ui", "kanban-ready"],
                "estimate": "5 hours",
                "priority": "medium"
            },
            {
                "title": "Integration: Complete password reset flow",
                "body": """## Acceptance Criteria
- [ ] Connect frontend form to backend API
- [ ] Test complete user journey
- [ ] Add error handling for edge cases
- [ ] Verify email delivery end-to-end

## Technical Notes
- Integration testing required
- Cross-browser compatibility check
- Performance testing with realistic load

## Cycle Time Target
3-4 hours

## Dependencies
- Backend token generation complete
- Email service integration complete
- Frontend form complete
                """,
                "labels": ["integration", "testing", "kanban-ready"],
                "estimate": "4 hours",
                "priority": "high"
            }
        ]
        
        return [self._apply_platform_format(story, platform) for story in stories]
    
    def _dashboard_breakdown(self, platform: str) -> List[Dict[str, Any]]:
        """Breakdown for dashboard features."""
        stories = [
            {
                "title": "Backend: User metrics API endpoint",
                "body": """## Acceptance Criteria
- [ ] Create /api/users/metrics endpoint
- [ ] Return user activity data (last 30 days)
- [ ] Implement pagination (limit 100 records)
- [ ] Add response caching (5-minute TTL)

## Cycle Time Target
6-7 hours

## Dependencies
None
                """,
                "labels": ["backend", "api", "kanban-ready"],
                "estimate": "7 hours",
                "priority": "high"
            },
            {
                "title": "Frontend: Metrics dashboard component",
                "body": """## Acceptance Criteria
- [ ] Create reusable dashboard grid component
- [ ] Add chart visualization (using Chart.js)
- [ ] Implement responsive design
- [ ] Add loading and error states

## Cycle Time Target
8 hours

## Dependencies
None - can use mock data initially
                """,
                "labels": ["frontend", "dashboard", "kanban-ready"],
                "estimate": "8 hours",
                "priority": "medium"
            }
        ]
        
        return [self._apply_platform_format(story, platform) for story in stories]
    
    def _generic_breakdown(self, feature_description: str, platform: str) -> List[Dict[str, Any]]:
        """Generic breakdown for unknown features."""
        stories = [
            {
                "title": f"Backend: Core logic for {feature_description}",
                "body": f"""## Acceptance Criteria
- [ ] Implement main business logic
- [ ] Add input validation
- [ ] Create unit tests (>90% coverage)
- [ ] Add error handling

## Feature Context
{feature_description}

## Cycle Time Target
6-8 hours

## Dependencies
To be determined during planning
                """,
                "labels": ["backend", "feature", "kanban-ready"],
                "estimate": "8 hours",
                "priority": "high"
            },
            {
                "title": f"Frontend: UI for {feature_description}",
                "body": f"""## Acceptance Criteria
- [ ] Create user interface components
- [ ] Implement user interactions
- [ ] Add responsive design
- [ ] Test across browsers

## Feature Context
{feature_description}

## Cycle Time Target
6-8 hours

## Dependencies
Backend API completion recommended
                """,
                "labels": ["frontend", "ui", "kanban-ready"],
                "estimate": "8 hours",
                "priority": "medium"
            }
        ]
        
        return [self._apply_platform_format(story, platform) for story in stories]
    
    def _generate_technical_tasks(self, feature_description: str, platform: str) -> List[Dict[str, Any]]:
        """Generate supporting technical tasks."""
        tasks = [
            {
                "title": "Testing: Integration test suite",
                "body": f"""## Acceptance Criteria
- [ ] End-to-end test scenarios
- [ ] API integration tests
- [ ] Performance test baseline
- [ ] Security test cases

## Feature Context
{feature_description}

## Cycle Time Target
4-6 hours

## Dependencies
All feature development complete
                """,
                "labels": ["testing", "qa", "kanban-ready"],
                "estimate": "6 hours",
                "priority": "medium"
            },
            {
                "title": "Documentation: Feature documentation",
                "body": f"""## Acceptance Criteria
- [ ] API documentation updated
- [ ] User guide sections added
- [ ] Architecture decision records
- [ ] Deployment notes

## Feature Context
{feature_description}

## Cycle Time Target
2-3 hours

## Dependencies
Feature implementation complete
                """,
                "labels": ["documentation", "kanban-ready"],
                "estimate": "3 hours",
                "priority": "low"
            }
        ]
        
        return [self._apply_platform_format(task, platform) for task in tasks]
    
    def _apply_platform_format(self, issue: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Apply platform-specific formatting."""
        if platform == "github":
            return self._format_for_github(issue)
        elif platform == "jira":
            return self._format_for_jira(issue)
        elif platform == "azure":
            return self._format_for_azure(issue)
        else:
            return issue
    
    def _format_for_github(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Format issue for GitHub Issues API."""
        github_issue = {
            "title": issue["title"],
            "body": issue["body"],
            "labels": issue.get("labels", []),
            "milestone": issue.get("milestone"),
            "assignees": issue.get("assignees", [])
        }
        
        # Add cycle time estimate to body
        if "estimate" in issue:
            github_issue["body"] += f"\n\n**Estimate**: {issue['estimate']}"
        
        return github_issue
    
    def _format_for_jira(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Format issue for JIRA API."""
        return {
            "fields": {
                "project": {"key": "PROJ"},
                "summary": issue["title"],
                "description": issue["body"],
                "issuetype": {"name": issue.get("type", "Story")},
                "priority": {"name": issue.get("priority", "Medium")},
                "labels": issue.get("labels", []),
                "timetracking": {
                    "originalEstimate": issue.get("estimate", "8h")
                }
            }
        }
    
    def _format_for_azure(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Format issue for Azure DevOps API."""
        return {
            "op": "add",
            "path": "/fields/System.Title",
            "value": issue["title"],
            "fields": {
                "System.Description": issue["body"],
                "System.Tags": "; ".join(issue.get("labels", [])),
                "Microsoft.VSTS.Scheduling.OriginalEstimate": 
                    issue.get("estimate", "8").split()[0]  # Extract number
            }
        }
    
    def _load_template(self, template_type: str, platform: str) -> Dict[str, Any]:
        """Load issue template from file."""
        template_file = self.templates_dir / f"{template_type}-template.json"
        if template_file.exists():
            with open(template_file) as f:
                return json.load(f)
        return {}
    
    def validate_kanban_readiness(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Validate that issues meet Kanban flow criteria."""
        warnings = []
        
        for i, issue in enumerate(issues):
            # Check cycle time estimates
            if "estimate" in issue:
                try:
                    hours = int(issue["estimate"].split()[0])
                    if hours > self.max_task_hours:
                        warnings.append(f"Issue {i+1}: Estimate {hours}h exceeds max {self.max_task_hours}h")
                    elif hours < self.min_task_hours:
                        warnings.append(f"Issue {i+1}: Estimate {hours}h below min {self.min_task_hours}h")
                except ValueError:
                    warnings.append(f"Issue {i+1}: Invalid time estimate format")
            
            # Check for clear acceptance criteria
            if "body" in issue and "Acceptance Criteria" not in issue["body"]:
                warnings.append(f"Issue {i+1}: Missing acceptance criteria")
            
            # Check for dependencies documentation
            if "body" in issue and "Dependencies" not in issue["body"]:
                warnings.append(f"Issue {i+1}: Dependencies not documented")
        
        return warnings

def main():
    parser = argparse.ArgumentParser(description="Generate Kanban-optimized work items using AI")
    parser.add_argument("--feature", help="Feature description to break down")
    parser.add_argument("--epic", help="Epic to decompose into stories")
    parser.add_argument("--bug", help="Bug report to create issues for")
    parser.add_argument("--platform", choices=["github", "jira", "azure"], 
                       default="github", help="Target platform")
    parser.add_argument("--max-hours", type=int, default=8, 
                       help="Maximum hours per task")
    parser.add_argument("--output", help="Output file for generated issues")
    parser.add_argument("--validate", action="store_true", 
                       help="Validate Kanban readiness")
    
    args = parser.parse_args()
    
    if not any([args.feature, args.epic, args.bug]):
        print("Error: Must specify --feature, --epic, or --bug")
        sys.exit(1)
    
    generator = KanbanIssueGenerator()
    generator.max_task_hours = args.max_hours
    
    # Generate issues based on input type
    if args.feature:
        issues = generator.generate_feature_issues(args.feature, args.platform)
    elif args.epic:
        issues = generator.generate_feature_issues(args.epic, args.platform)
    elif args.bug:
        # Bug handling would be implemented here
        print("Bug issue generation not yet implemented")
        sys.exit(1)
    
    # Validate Kanban readiness
    if args.validate:
        warnings = generator.validate_kanban_readiness(issues)
        if warnings:
            print("⚠️ Kanban Readiness Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
            print()
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(issues, f, indent=2)
        print(f"✅ Generated {len(issues)} issues saved to {args.output}")
    else:
        print(f"✅ Generated {len(issues)} Kanban-ready issues:")
        for i, issue in enumerate(issues, 1):
            print(f"\n{i}. {issue['title']}")
            if 'estimate' in issue:
                print(f"   Estimate: {issue.get('estimate', 'TBD')}")
            print(f"   Labels: {', '.join(issue.get('labels', []))}")

if __name__ == "__main__":
    main()