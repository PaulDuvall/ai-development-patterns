# Python Development Rules

Language-specific rules for Python projects.

## Code Style

### Formatting
- **Tool**: Black (line length: 88 characters)
- **Import sorting**: isort with Black-compatible settings
- **Linting**: Ruff (replaces flake8, pylint, pyupgrade)

```bash
# Auto-format before commit
black .
isort .
ruff check --fix .
```

### Type Hints
- ✅ Required for all functions (parameters and return types)
- ✅ Use `typing` module for complex types
- ✅ Type check with mypy before committing

```python
# CORRECT
def process_payment(user_id: int, amount: Decimal) -> PaymentResult:
    ...

# WRONG - no type hints
def process_payment(user_id, amount):
    ...
```

### Docstrings
- Use Google-style docstrings
- Required for: all public functions, classes, modules
- Optional for: private functions, simple getters/setters

```python
def calculate_tax(amount: Decimal, rate: Decimal) -> Decimal:
    """Calculate tax amount for a transaction.

    Args:
        amount: Pre-tax transaction amount in USD
        rate: Tax rate as decimal (0.07 = 7%)

    Returns:
        Tax amount rounded to 2 decimal places

    Raises:
        ValueError: If amount or rate is negative
    """
    if amount < 0 or rate < 0:
        raise ValueError("Amount and rate must be non-negative")
    return round(amount * rate, 2)
```

## Project Structure

### Standard Layout
```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── api/          # API routes
│       ├── models/       # Data models
│       ├── services/     # Business logic
│       └── utils/        # Utilities
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py       # Pytest fixtures
├── pyproject.toml        # Dependencies & config
└── README.md
```

### Dependencies
- **File**: `pyproject.toml` (preferred) or `requirements.txt`
- **Pinning**: Pin all versions in production
- **Dev deps**: Separate from production (`[tool.poetry.dev-dependencies]`)

```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "0.104.1"  # Pin exact version
pydantic = "^2.5"    # Allow minor updates

[tool.poetry.dev-dependencies]
pytest = "^7.4"
black = "^23.11"
mypy = "^1.7"
```

## Testing

### Framework
- **Primary**: pytest
- **Coverage**: pytest-cov (minimum 80%)
- **Fixtures**: Define in `tests/conftest.py`

### Test Structure
```python
# tests/test_payments.py
import pytest
from myapp.services.payment import PaymentService

class TestPaymentService:
    """Test suite for payment processing."""

    @pytest.fixture
    def payment_service(self, db_session):
        """Create payment service with test database."""
        return PaymentService(db_session)

    def test_successful_payment(self, payment_service):
        """Process payment successfully with valid card."""
        # Arrange
        payment_data = {"amount": 100, "card": "4242424242424242"}

        # Act
        result = payment_service.process(payment_data)

        # Assert
        assert result.success is True
        assert result.transaction_id is not None

    def test_payment_idempotency(self, payment_service):
        """Prevent duplicate charges for same transaction ID."""
        payment_id = "txn_123"
        payment_service.process({"id": payment_id, "amount": 100})

        with pytest.raises(DuplicateTransactionError):
            payment_service.process({"id": payment_id, "amount": 100})
```

### Coverage Requirements
```bash
# Run tests with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Generate HTML report
pytest --cov=src --cov-report=html
```

## Common Patterns

### Error Handling
```python
# CORRECT - Specific exceptions
try:
    user = get_user_by_id(user_id)
except UserNotFoundError as e:
    logger.error(f"User {user_id} not found: {e}")
    raise HTTPException(status_code=404, detail="User not found")
except DatabaseError as e:
    logger.error(f"Database error fetching user {user_id}: {e}")
    raise HTTPException(status_code=500, detail="Database error")

# WRONG - Bare except
try:
    user = get_user_by_id(user_id)
except:  # Too broad!
    pass
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# CORRECT - Structured logging with context
logger.info(
    "Payment processed",
    extra={
        "user_id": user_id,
        "amount": amount,
        "transaction_id": txn_id,
        "duration_ms": duration
    }
)

# WRONG - Unstructured strings
logger.info(f"Payment of {amount} processed for user {user_id}")
```

### Configuration
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration from environment."""

    database_url: str
    secret_key: str
    api_timeout: int = 30

    class Config:
        env_file = ".env"

# Load config once at startup
settings = Settings()
```

## Security

### Input Validation
- Use Pydantic models for all API inputs
- Validate ranges, formats, and business rules
- Never trust user input

```python
from pydantic import BaseModel, Field, validator

class CreateUserRequest(BaseModel):
    email: str = Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(..., ge=18, le=120)

    @validator('email')
    def email_must_be_lowercase(cls, v):
        return v.lower()
```

### SQL Injection Prevention
```python
# CORRECT - Parameterized query
cursor.execute(
    "SELECT * FROM users WHERE email = %s",
    (email,)  # Tuple of parameters
)

# WRONG - String interpolation
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")  # SQL INJECTION!
```

## Performance

### Async/Await
- Use async for I/O-bound operations (database, HTTP calls)
- Don't use async for CPU-bound tasks

```python
async def fetch_user_data(user_id: int) -> UserData:
    """Fetch user from database asynchronously."""
    async with db.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            user_id
        )
```

### Database Queries
- Use connection pooling
- Eager load relationships (avoid N+1 queries)
- Index frequently queried columns

## Tools & Commands

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type check
mypy src/

# Lint
ruff check src/ tests/

# Test
pytest -v --cov=src

# Security scan
bandit -r src/
safety check
```

## Version Requirements

- **Minimum Python version**: 3.11
- **Package manager**: Poetry (preferred) or pip
- **Virtual environments**: Required for all projects
