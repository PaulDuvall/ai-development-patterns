# Code Review Prompt Templates

## Security Review
```
Review this code for security vulnerabilities:

Security checklist:
- [ ] No hardcoded secrets or credentials
- [ ] Input validation prevents injection attacks
- [ ] Authentication and authorization properly implemented
- [ ] Error messages don't expose internal details
- [ ] Sensitive data is properly encrypted
- [ ] Rate limiting implemented where needed
- [ ] Audit logging captures security events

Focus areas:
- Authentication flows
- Data validation logic
- External API integrations
- Database query construction
- Error handling patterns

Report any findings with:
- Severity level (Critical/High/Medium/Low)
- Specific location in code
- Recommended remediation
- Example of secure implementation
```

## Code Quality Review
```
Analyze this code for quality and maintainability:

Quality metrics:
- [ ] Functions under 20 lines
- [ ] Cyclomatic complexity ≤ 10
- [ ] Proper error handling
- [ ] Comprehensive test coverage
- [ ] Clear variable and function names
- [ ] Appropriate comments and documentation

Architecture review:
- [ ] Follows established patterns
- [ ] Proper separation of concerns
- [ ] Dependencies are minimal and justified
- [ ] Performance considerations addressed
- [ ] Scalability implications considered

Provide specific recommendations for:
- Code simplification opportunities
- Performance improvements
- Maintainability enhancements
- Test coverage gaps
```

## AI-Generated Code Review
```
Review AI-generated code for accuracy and completeness:

AI-specific checks:
- [ ] Code actually solves the stated problem
- [ ] Edge cases are properly handled
- [ ] No hallucinated functions or APIs
- [ ] Dependencies exist and are used correctly
- [ ] Generated tests actually test the implementation
- [ ] Documentation matches actual behavior

Common AI pitfalls to check:
- Outdated API usage
- Incorrect import statements
- Missing error handling
- Incomplete implementations
- Over-engineered solutions
- Inconsistent coding patterns

Validation steps:
1. Run the code to verify it executes
2. Test with edge case inputs
3. Verify external dependencies work
4. Check generated tests pass
5. Confirm code meets requirements
```