# Claude Code Plan Mode Example

This example demonstrates how to use Claude Code's Plan Mode to implement user authentication for a Node.js application.

## Scenario
Adding JWT-based authentication to an existing Express.js API with user registration, login, and password reset functionality.

## Step 1: Enter Plan Mode

In Claude Code, activate Plan Mode before starting implementation:

```
I need to add user authentication to my Express.js API. The requirements are:
- User registration with email validation
- JWT-based login system
- Password reset functionality
- Rate limiting for auth endpoints
- Integration with existing user database

Please create a plan before we start implementing.
```

## Step 2: Generated Plan Example

**Claude Code Plan Output:**

```markdown
# User Authentication Implementation Plan

## Overview
Add complete JWT authentication system to existing Express.js API with security best practices.

## Implementation Steps

### 1. Database Schema Updates
- Add authentication fields to users table
- Create password_resets table for reset tokens
- Add indexes for performance

### 2. Authentication Middleware
- JWT token validation middleware
- Rate limiting middleware for auth endpoints
- Input validation and sanitization

### 3. API Endpoints
- POST /auth/register - User registration
- POST /auth/login - User login
- POST /auth/forgot-password - Password reset request
- POST /auth/reset-password - Password reset completion
- GET /auth/profile - Protected user profile

### 4. Security Implementation
- Password hashing with bcrypt
- JWT token generation and validation
- Rate limiting (5 attempts per 15 minutes)
- Email validation and verification

### 5. Testing Strategy
- Unit tests for auth functions
- Integration tests for endpoints
- Security testing for common attacks

## Files to Create/Modify
- `models/User.js` - Update user model
- `middleware/auth.js` - Authentication middleware
- `routes/auth.js` - Authentication routes
- `services/auth.js` - Authentication business logic
- `tests/auth.test.js` - Test suite

## Estimated Time: 4-6 hours
```

## Step 3: Plan Review and Iteration

Review the plan and request modifications:

```
The plan looks good, but I need to make two changes:
1. We're using PostgreSQL, not the default database assumptions
2. Add OAuth integration preparation for future Google/GitHub login
3. Ensure compatibility with existing user table schema

Please update the plan accordingly.
```

## Step 4: Execute Plan

Exit Plan Mode and begin implementation:

```
Great! Let's implement this plan. Start with Step 1 - the database schema updates for PostgreSQL.
```

Claude Code then executes the implementation following the approved plan, with references back to specific plan steps.

## Benefits Demonstrated

1. **Clear Requirements Validation**: Plan Mode caught missing PostgreSQL specification
2. **Scope Management**: Plan prevented feature creep by defining boundaries
3. **Time Estimation**: Realistic 4-6 hour estimate helps with scheduling
4. **Implementation Order**: Logical sequence from database to endpoints to tests
5. **Collaboration Ready**: Plan can be shared with team for review

## Plan Validation During Implementation

```bash
# Step 1 Complete ✓
echo "✓ Database schema updated with auth fields"

# Step 2 In Progress
echo "→ Creating JWT middleware (matches plan step 2)"

# Plan Deviation
echo "⚠ Using express-rate-limit instead of custom solution (documented)"
```

This example shows how Claude Code's Plan Mode creates a structured approach to feature development, reducing iterations and improving code quality.