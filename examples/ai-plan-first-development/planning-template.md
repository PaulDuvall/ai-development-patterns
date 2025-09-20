# AI Plan-First Development Template

Use this template with any AI coding tool to create structured implementation plans before writing code.

## Planning Session Template

### 1. Problem Definition
**Objective**: [What needs to be built in 2-3 sentences]

**Success Criteria**:
- [ ] [Specific measurable outcome]
- [ ] [User experience goal]
- [ ] [Technical requirement]

### 2. Context & Constraints

**Technical Context**:
- Existing systems: [Current architecture, technologies, databases]
- Integration points: [APIs, services, data sources to connect with]
- Performance requirements: [Response times, throughput, scalability needs]

**Business Constraints**:
- Timeline: [Available time for implementation]
- Resources: [Team size, expertise available, budget]
- Compliance: [Security, regulatory, accessibility requirements]

**Technology Constraints**:
- Tech stack: [Required or preferred technologies]
- Compatibility: [Browser support, mobile requirements, legacy system support]
- Infrastructure: [Deployment environment, cloud provider, resource limits]

### 3. Implementation Options Analysis

**Option A**: [Brief approach description]
- **Pros**: [2-3 key advantages]
- **Cons**: [2-3 main limitations]
- **Time Estimate**: [Hours/days for implementation]
- **Risk Level**: [Low/Medium/High with key risks]

**Option B**: [Alternative approach description]
- **Pros**: [2-3 key advantages]
- **Cons**: [2-3 main limitations]
- **Time Estimate**: [Hours/days for implementation]
- **Risk Level**: [Low/Medium/High with key risks]

**Recommended Approach**: [Chosen option with 2-3 sentence justification]

### 4. Detailed Implementation Plan

**Phase 1**: [Phase name] ([Time estimate])
- [ ] Task 1: [Specific action with acceptance criteria]
- [ ] Task 2: [Specific action with acceptance criteria]
- [ ] Task 3: [Specific action with acceptance criteria]

**Phase 2**: [Phase name] ([Time estimate])
- [ ] Task 1: [Specific action with acceptance criteria]
- [ ] Task 2: [Specific action with acceptance criteria]

**Phase 3**: [Phase name] ([Time estimate])
- [ ] Task 1: [Specific action with acceptance criteria]
- [ ] Task 2: [Specific action with acceptance criteria]

### 5. Quality Assurance Strategy

**Testing Approach**:
- [ ] Unit tests: [Coverage goals and key test cases]
- [ ] Integration tests: [System interaction testing]
- [ ] End-to-end tests: [User workflow validation]
- [ ] Performance tests: [Load and stress testing requirements]

**Code Quality**:
- [ ] Code review checklist: [Key review criteria]
- [ ] Static analysis: [Linting, security scanning tools]
- [ ] Documentation: [Code comments, API docs, user guides]

### 6. Risk Mitigation & Rollback

**Identified Risks**:
- **Risk 1**: [Description] → **Mitigation**: [Prevention strategy]
- **Risk 2**: [Description] → **Mitigation**: [Prevention strategy]

**Rollback Plan**:
- [ ] Database backup strategy: [How to revert data changes]
- [ ] Code rollback process: [Version control and deployment rollback]
- [ ] Communication plan: [Who to notify, how to communicate issues]

### 7. Success Validation

**Acceptance Criteria**:
- [ ] Functional requirement 1: [How to verify it works]
- [ ] Functional requirement 2: [How to verify it works]
- [ ] Performance requirement: [Specific metrics to measure]
- [ ] Security requirement: [Security validation steps]

**Deployment Checklist**:
- [ ] Local testing complete
- [ ] Staging environment validation
- [ ] Performance benchmarks met
- [ ] Security review passed
- [ ] Documentation updated
- [ ] Team training completed (if needed)

## Tool-Specific Usage

### Claude Code
Copy this template into Claude Code and request:
```
Please help me fill out this planning template for [your project description].
Use Plan Mode to create a detailed implementation strategy.
```

### Cursor
Use the `/plan` command with this structure:
```
/plan Using this planning template, create a detailed implementation plan for [your project description]
```

### Other AI Tools
Adapt the template format for your tool's planning features:
- Use as a prompt template for structured planning
- Break into multiple planning sessions if needed
- Customize sections based on your tool's capabilities

## Best Practices

1. **Start Simple**: Begin with high-level plan, add details as needed
2. **Be Specific**: Use concrete acceptance criteria and measurable outcomes
3. **Consider Alternatives**: Always evaluate multiple implementation approaches
4. **Plan for Failure**: Include risk mitigation and rollback strategies
5. **Validate Assumptions**: Test key technical assumptions early
6. **Communicate Progress**: Share plan with team and update status regularly
7. **Learn from Execution**: Update planning approach based on implementation experience

## Common Planning Pitfalls

❌ **Too Abstract**: "Implement user authentication" vs. ✅ "Create JWT middleware with 15-minute expiration"
❌ **Missing Dependencies**: Not identifying required external services or data
❌ **Unrealistic Estimates**: Underestimating complexity or available time
❌ **No Rollback Plan**: Not considering how to undo changes if issues arise
❌ **Ignoring Constraints**: Planning without considering technical or business limitations

This template provides a structured approach to AI-assisted planning that works across different tools and project types.