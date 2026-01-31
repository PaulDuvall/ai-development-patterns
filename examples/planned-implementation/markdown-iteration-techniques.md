# Markdown Iteration Techniques

This guide provides detailed techniques for iterating on implementation plans using structured markdown documentation, as referenced in the [Planned Implementation](../../README.md#planned-implementation) pattern.

## Overview

Effective plan iteration requires structured refinement cycles using markdown documentation. This approach enables systematic improvement of implementation plans through stakeholder feedback and iterative enhancement.

## 1. Initial Plan Creation

Start with a simple, structured markdown document that captures the essential elements:

```markdown
# Feature: User Authentication
## Initial Plan (Draft 1)
- Add login endpoint
- Store user sessions
- Add logout functionality
```

**Key Principles for Initial Plans:**
- Keep structure simple and scannable
- Focus on major components/endpoints
- Avoid implementation details in first draft
- Use consistent markdown formatting

## 2. Stakeholder Review Cycle

Share the initial plan with team members and gather structured feedback:

```bash
# Share initial plan with team, gather feedback
ai "Review this authentication plan for security gaps and suggest improvements:

[paste initial plan]

Focus on:
- Security best practices
- Integration with existing systems
- Performance considerations
- Testing strategy"
```

**Review Guidelines:**
- Include specific review criteria in prompts
- Focus on one concern area per review cycle
- Document feedback sources and rationale
- Set clear expectations for review depth

## 3. Plan Enhancement Iteration

Incorporate feedback to create enhanced plan versions:

```markdown
# Feature: User Authentication
## Refined Plan (Draft 2)

### Security Considerations (Added from review)
- JWT with refresh tokens for session management
- Rate limiting on login attempts (5 attempts/minute/IP)
- Password hashing with bcrypt (cost factor 12)

### API Design (Enhanced)
- POST /auth/login (returns access + refresh tokens)
- POST /auth/refresh (extends session)
- POST /auth/logout (revokes tokens)

### Integration Points (New section)
- Existing user table schema compatibility
- Current session middleware replacement strategy
- Gradual migration plan for existing sessions

### Performance Requirements (Added)
- Login response time: <200ms
- Token validation: <50ms
- Support for 1000 concurrent logins
```

**Enhancement Best Practices:**
- Add sections rather than completely rewriting
- Maintain version history in git
- Include specific metrics and thresholds
- Document architectural decisions and trade-offs

## 4. Implementation Readiness Check

Validate the refined plan before moving to implementation:

```bash
# Final validation before coding
ai "Validate this refined plan for implementation readiness:

[paste refined plan]

Check:
- All acceptance criteria are testable
- Dependencies are clearly identified
- Rollback strategy is defined
- Time estimates are realistic
- Security requirements are comprehensive"
```

**Readiness Criteria:**
- Every feature has clear acceptance criteria
- All dependencies are identified and available
- Implementation can be broken into <8 hour tasks
- Rollback procedures are documented
- Performance targets are measurable

## 5. Iteration Best Practices

### Version Control Guidelines
```bash
# Track plan evolution in git
git add auth-implementation-plan.md
git commit -m "docs: initial authentication plan (draft 1)"

# After stakeholder review
git add auth-implementation-plan.md
git commit -m "docs: enhance auth plan with security requirements (draft 2)"

# Final version before implementation
git add auth-implementation-plan.md
git commit -m "docs: finalize auth implementation plan (ready for development)"
```

### Optimal Iteration Cycles
- **2-3 iteration cycles maximum**: Avoid over-planning
- **24-48 hours between iterations**: Allow time for thoughtful review
- **Stakeholder sign-off**: Get explicit approval before implementation
- **Plan-to-code traceability**: Reference plan sections in implementation commits

### Stakeholder Coordination
- **Assign specific reviewers**: Security, architecture, operations perspectives
- **Set review deadlines**: Prevent planning paralysis
- **Document decisions**: Capture rationale for plan changes
- **Communicate changes**: Share plan updates with all stakeholders

## Tool-Specific Implementation

### Claude Code
```bash
# Use Plan Mode for initial planning
claude plan "Create authentication implementation plan for SaaS application"

# Use iterative refinement
claude refine "Enhance this plan with security and performance considerations: [plan]"

# Final validation
claude validate "Check this plan for implementation readiness: [refined plan]"
```

### Cursor
```bash
# Use /plan command for structured planning
/plan Authentication implementation with JWT and session migration

# Use @docs for context-aware refinement
/refine authentication plan @docs considering existing architecture

# Validate before implementation
/validate plan readiness for authentication implementation
```

### Other AI Tools
- Use the markdown templates as structured prompts
- Break planning into focused sessions (problem → approach → details)
- Maintain consistent formatting across tools
- Save plan versions for comparison and rollback

## Example: Complete Iteration Cycle

### Draft 1: Initial Plan
```markdown
# User Dashboard Feature
## Components
- User profile display
- Activity timeline
- Settings panel
```

### Draft 2: After Review
```markdown
# User Dashboard Feature
## Components
- User profile display (avatar, name, email, role)
- Activity timeline (last 30 days, paginated)
- Settings panel (preferences, notifications, security)

## Technical Requirements
- Mobile responsive design
- <2 second load time
- Real-time activity updates

## API Endpoints
- GET /api/user/profile
- GET /api/user/activity?page=1&limit=20
- PUT /api/user/settings
```

### Draft 3: Implementation Ready
```markdown
# User Dashboard Feature
## Components
- User profile display (avatar, name, email, role)
  - Avatar upload with 2MB size limit
  - Role-based visibility controls
- Activity timeline (last 30 days, paginated)
  - WebSocket for real-time updates
  - Infinite scroll with 20 items per page
- Settings panel (preferences, notifications, security)
  - Form validation with real-time feedback
  - Two-factor authentication toggle

## Technical Requirements
- Mobile responsive design (320px minimum width)
- <2 second load time (measured at P95)
- Real-time activity updates via WebSocket
- Progressive loading for large activity histories

## API Endpoints
- GET /api/user/profile (includes avatar URL, permissions)
- GET /api/user/activity?page=1&limit=20 (returns total count)
- PUT /api/user/settings (validates before save)
- WebSocket /ws/activity (real-time updates)

## Security Considerations
- Avatar uploads scanned for malware
- Activity data filtered by user permissions
- Settings changes require password confirmation
- Rate limiting on API endpoints (100 requests/minute)

## Testing Strategy
- Unit tests: Component rendering and API logic
- Integration tests: Full dashboard workflow
- Performance tests: Load time with 1000+ activities
- Security tests: Permission boundary validation
```

This complete iteration demonstrates how structured markdown planning evolves from simple concepts to implementation-ready specifications through systematic refinement cycles.
