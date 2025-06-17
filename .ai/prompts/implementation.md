# Implementation Prompt Templates

## Feature Implementation
```
Implement [feature_name] following our architecture patterns:

Requirements:
- Follow security standards in .ai/rules/security.md
- Adhere to code style in .ai/rules/style.md
- Use approved libraries from .ai/rules/architecture.md
- Include comprehensive error handling
- Add appropriate logging for observability

Implementation guidelines:
- Keep functions under 20 lines
- Use type hints for all parameters
- Include docstrings with examples
- Write unit tests with >90% coverage
- Handle edge cases and error conditions

Constraints:
- Maximum complexity: [specify limit]
- Dependencies: [list approved dependencies only]
- Performance: [specify requirements]
```

## API Endpoint Creation
```
Create REST API endpoint for [endpoint_purpose]:

Specifications:
- Method: [GET/POST/PUT/DELETE]
- Path: [/api/v1/resource]
- Authentication: JWT required
- Rate limiting: [requests per minute]
- Request validation: Use Pydantic models
- Response format: JSON with consistent error structure

Security requirements:
- Input validation against SQL injection
- Authorization check for user permissions
- Audit logging of all operations
- Return appropriate HTTP status codes

Testing requirements:
- Unit tests for business logic
- Integration tests for endpoint
- Security tests for edge cases
- Performance tests for expected load
```

## Database Schema Design
```
Design database schema for [entity_name]:

Requirements:
- Use PostgreSQL with proper indexing
- Include audit fields (created_at, updated_at, created_by)
- Implement soft deletes where appropriate
- Use foreign keys for referential integrity
- Include check constraints for data validation

Migration guidelines:
- Use Alembic for version control
- Include rollback procedures
- Test migration on sample data
- Document breaking changes
- Ensure zero-downtime deployment compatibility
```