# Test Generation Prompt Templates

## Unit Test Generation
```
Generate comprehensive unit tests for [function/class_name]:

Test requirements:
- Use pytest framework
- Include fixtures for test data
- Test happy path and edge cases
- Test error conditions and exceptions
- Achieve >90% code coverage
- Mock external dependencies

Test structure:
- Arrange: Set up test data and mocks
- Act: Execute the function under test
- Assert: Verify expected outcomes

Include tests for:
- Valid inputs with expected outputs
- Invalid inputs with proper error handling
- Boundary conditions (empty, null, max values)
- Error conditions with appropriate exceptions
- Integration with mocked dependencies

Use descriptive test names that explain:
- What is being tested
- Under what conditions
- What the expected outcome is
```

## Integration Test Generation
```
Create integration tests for [API endpoint/service]:

Test scope:
- End-to-end request/response flow
- Database interactions
- External service integrations
- Authentication and authorization
- Error handling across system boundaries

Test data management:
- Use test database with clean fixtures
- Create test users with appropriate permissions
- Mock external services consistently
- Clean up test data after each test

Test scenarios:
- Successful operations with valid data
- Authentication failures
- Authorization violations
- Invalid input data
- External service failures
- Database constraint violations
- Rate limiting behavior

Response validation:
- Correct HTTP status codes
- Expected response structure
- Proper error message format
- Security headers present
```

## Acceptance Test Generation
```
Generate acceptance tests in Gherkin format for [feature]:

Feature structure:
```gherkin
Feature: [Feature Name]
  As a [user type]
  I want to [goal]
  So that [benefit]

  Scenario: [Scenario name]
    Given [initial context]
    When [action performed]
    Then [expected outcome]
    And [additional verification]
```

Include scenarios for:
- Happy path user journeys
- Error conditions and recovery
- Edge cases and boundary conditions
- Different user roles and permissions
- Mobile and desktop experiences

Step definitions should:
- Be reusable across scenarios
- Include data validation
- Handle asynchronous operations
- Provide clear error messages
- Support parallel test execution
```