# Code Style Guide for AI Development

## General Principles
- Favor explicit over implicit code
- Use descriptive names for variables and functions
- Keep functions under 20 lines (excluding docstrings)
- Maximum cyclomatic complexity of 10 per function
- One class per file unless tightly coupled

## Naming Conventions
- Variables: snake_case for Python, camelCase for JavaScript
- Functions: snake_case for Python, camelCase for JavaScript
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE
- Files: lowercase with hyphens for separation

## Documentation
- All public functions must have docstrings
- Use type hints for all function parameters and return values
- Include examples in docstrings for complex functions
- Document any non-obvious business logic
- Keep comments focused on "why" not "what"

## Error Handling
- Use specific exception types, not generic Exception
- Include context in error messages
- Log errors with appropriate severity levels
- Clean up resources in finally blocks
- Fail fast with clear error messages

## Performance Guidelines
- Use list comprehensions over loops when appropriate
- Cache expensive computations
- Use lazy loading for large datasets
- Profile before optimizing
- Measure actual performance impact of changes