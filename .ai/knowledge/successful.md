# Successful AI Development Patterns

## Authentication Implementation

### JWT with RS256 - 95% Success Rate
**Prompt that works reliably:**
```
Implement JWT authentication:
- Use RS256 algorithm (never HS256)
- 15 minute access token expiration
- 7 day refresh token in httpOnly cookie
- Include user.id and role in payload
- Implement token refresh endpoint
- Add middleware for route protection
```

**Why this works:**
- Specific algorithm prevents AI from defaulting to insecure HS256
- Clear expiration times prevent indefinite token lifetimes
- httpOnly cookie specification prevents XSS attacks
- Specific payload requirements ensure consistent token structure

### Database Connection Pooling - 90% Success Rate
**Proven prompt:**
```
Set up PostgreSQL connection pool:
- Use SQLAlchemy with connection pooling
- Pool size: 10 connections
- Overflow: 20 additional connections
- Recycle connections every 3600 seconds
- Include health check queries
- Handle connection failures gracefully
```

## API Development

### FastAPI Endpoint Creation - 85% Success Rate
**Reliable pattern:**
```
Create FastAPI endpoint with:
- Pydantic models for request/response validation
- Dependency injection for database session
- Proper HTTP status codes (200, 201, 400, 404, 500)
- OpenAPI documentation with examples
- Error handling with consistent response format
- Rate limiting using slowapi
```

### Error Response Standardization - 90% Success Rate
**Consistent error handling:**
```
Implement standardized error responses:
- Use Pydantic BaseModel for error structure
- Include error code, message, and details
- Map exceptions to appropriate HTTP status codes
- Log errors with correlation IDs
- Never expose internal system details
```

## Frontend Development

### React Component with TypeScript - 80% Success Rate
**Effective approach:**
```
Create React component with:
- TypeScript interfaces for all props
- React.memo for performance optimization
- Custom hooks for state management
- Error boundaries for error handling
- Accessible HTML with ARIA labels
- Responsive design using CSS modules
```

### State Management with Zustand - 85% Success Rate
**Clean state pattern:**
```
Implement Zustand store with:
- TypeScript interfaces for state shape
- Actions for state mutations
- Selectors for derived state
- Middleware for persistence
- DevTools integration for debugging
```

## Testing Strategies

### Unit Test Generation - 75% Success Rate
**High-coverage test prompt:**
```
Generate pytest unit tests with:
- Fixtures for test data setup
- Parametrized tests for multiple inputs
- Mock external dependencies
- Test happy path and error conditions
- Achieve >90% branch coverage
- Use descriptive test names
```

### Integration Test Setup - 70% Success Rate
**Reliable integration testing:**
```
Create integration tests with:
- Test database with fixtures
- Real HTTP requests using httpx
- Authentication with test users
- Cleanup after each test
- Parallel test execution support
```

## Deployment and Operations

### Docker Configuration - 90% Success Rate
**Production-ready Docker:**
```
Create Dockerfile with:
- Multi-stage build for size optimization
- Non-root user for security
- Health check endpoint
- Proper signal handling
- Environment variable configuration
- Security scanning integration
```

### CI/CD Pipeline - 85% Success Rate
**GitHub Actions workflow:**
```
Implement CI/CD with:
- Dependency caching for speed
- Parallel test execution
- Security scanning with Snyk
- Build artifacts with versioning
- Automated deployment on merge
- Rollback capability
```

## Performance Optimization

### Database Query Optimization - 80% Success Rate
**Efficient query patterns:**
```
Optimize database queries with:
- Proper indexing strategy
- Query result pagination
- Eager loading for relationships
- Connection pooling
- Query performance monitoring
- Avoid N+1 query patterns
```

### Caching Implementation - 75% Success Rate
**Redis caching strategy:**
```
Implement Redis caching with:
- TTL-based expiration
- Cache key naming convention
- Cache invalidation strategy
- Fallback to database on cache miss
- Monitoring cache hit rates
```