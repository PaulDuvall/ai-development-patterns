# Test Failure Error Example

This example demonstrates how to use the Error Resolution pattern for debugging test failures.

## Error Scenario

```
FAILED tests/test_user_service.py::test_user_creation - AssertionError
FAILED tests/test_user_service.py::test_user_update - AttributeError: 'NoneType' object has no attribute 'id'
```

## Error Context Collection

```bash
cat > .error-context.md << 'EOF'
# Test Failure Analysis

## Error Output
```
============================= FAILURES =============================
______________________ test_user_creation _______________________

    def test_user_creation():
        user = create_user(email="test@example.com", name="Test User")
>       assert user.id is not None
E       AssertionError: assert None is not None
E        +  where None = <User(email='test@example.com', name='Test User')>.id

tests/test_user_service.py:15: AssertionError

______________________ test_user_update _______________________

    def test_user_update():
        user = get_user(1)
>       user.name = "Updated Name"
E       AttributeError: 'NoneType' object has no attribute 'name'

tests/test_user_service.py:25: AttributeError
====================== short test summary ======================
FAILED tests/test_user_service.py::test_user_creation - AssertionError
FAILED tests/test_user_service.py::test_user_update - AttributeError
=================== 2 failed, 5 passed in 0.45s ================
```

## Test File (tests/test_user_service.py)
```python
import pytest
from app.services.user_service import create_user, get_user, update_user

def test_user_creation():
    """Test that creating a user assigns an ID"""
    user = create_user(email="test@example.com", name="Test User")
    assert user.id is not None  # Line 15 - FAILING
    assert user.email == "test@example.com"
    assert user.name == "Test User"

def test_user_update():
    """Test that updating a user works"""
    user = get_user(1)  # Returns None
    user.name = "Updated Name"  # Line 25 - FAILING
    updated = update_user(user)
    assert updated.name == "Updated Name"
```

## Source Code (app/services/user_service.py)
```python
from app.models import User
from app.database import db

def create_user(email, name):
    """Create a new user"""
    user = User(email=email, name=name)
    # Missing: db.session.add(user)
    # Missing: db.session.commit()
    return user

def get_user(user_id):
    """Get user by ID"""
    return User.query.filter_by(id=user_id).first()
    # Returns None if user doesn't exist

def update_user(user):
    """Update existing user"""
    db.session.commit()
    return user
```

## Recent Changes
```
git log --oneline -5 app/services/
abc123 Refactor user service to remove redundant code
def456 Add user update functionality
ghi789 Initial user service implementation
```

## Git Diff
```diff
diff --git a/app/services/user_service.py b/app/services/user_service.py
@@ -3,8 +3,6 @@
 def create_user(email, name):
     """Create a new user"""
     user = User(email=email, name=name)
-    db.session.add(user)
-    db.session.commit()
     return user
```

## Environment
- Python: 3.11.5
- pytest: 7.4.2
- SQLAlchemy: 2.0.21
- Database: SQLite (in-memory for tests)

EOF
```

## AI Diagnosis

```bash
ai "Diagnose these test failures:

$(cat .error-context.md)

Provide:
1. Root cause of each failure
2. Why tests worked before recent change
3. Fix for the code (not the tests)
4. How to prevent regression"
```

## Expected AI Response

### Root Cause Analysis

**Test 1: test_user_creation**
- **Issue**: `create_user()` returns User object without committing to database
- **Why**: Recent refactoring removed `db.session.add()` and `db.session.commit()`
- **Result**: User object created but not persisted, so `id` field remains `None`
- **Impact**: User creation appears to work but doesn't save to database

**Test 2: test_user_update**
- **Issue**: `get_user(1)` returns `None` because no user exists in database
- **Why**: Previous test (`test_user_creation`) doesn't actually create users anymore
- **Result**: Attempting to access `.name` on `None` raises AttributeError
- **Impact**: All tests depending on database state are broken

**Root Problem**: The refactoring in commit `abc123` removed critical database operations, breaking test isolation and data persistence.

### Immediate Fixes

```python
# Fix 1: Restore database commit in create_user
# File: app/services/user_service.py

def create_user(email, name):
    """Create a new user"""
    user = User(email=email, name=name)
    db.session.add(user)  # ← Restore this line
    db.session.commit()   # ← Restore this line
    return user

# Fix 2: Add null check in test (defensive)
# File: tests/test_user_service.py

def test_user_update():
    """Test that updating a user works"""
    # First, create a user to update
    user = create_user(email="test@example.com", name="Test User")
    assert user.id is not None, "User creation failed"

    # Now test update
    fetched_user = get_user(user.id)
    assert fetched_user is not None, f"User {user.id} not found"

    fetched_user.name = "Updated Name"
    updated = update_user(fetched_user)
    assert updated.name == "Updated Name"
```

### Complete Fix

```bash
# Apply fixes
cat > app/services/user_service.py << 'PYTHON'
from app.models import User
from app.database import db

def create_user(email, name):
    """Create a new user in the database"""
    user = User(email=email, name=name)
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)  # Ensure ID is populated
    return user

def get_user(user_id):
    """Get user by ID, returns None if not found"""
    return User.query.filter_by(id=user_id).first()

def update_user(user):
    """Update existing user in database"""
    if user is None:
        raise ValueError("Cannot update None user")
    db.session.commit()
    return user
PYTHON

# Improve tests with better setup
cat > tests/test_user_service.py << 'PYTHON'
import pytest
from app.services.user_service import create_user, get_user, update_user
from app.database import db

@pytest.fixture(autouse=True)
def setup_database():
    """Set up test database before each test"""
    db.create_all()
    yield
    db.session.remove()
    db.drop_all()

def test_user_creation():
    """Test that creating a user assigns an ID and persists to database"""
    user = create_user(email="test@example.com", name="Test User")

    # Verify object properties
    assert user.id is not None, "User ID should be assigned"
    assert user.email == "test@example.com"
    assert user.name == "Test User"

    # Verify persistence by fetching from database
    fetched_user = get_user(user.id)
    assert fetched_user is not None, "User should be retrievable from database"
    assert fetched_user.email == user.email

def test_user_update():
    """Test that updating a user works"""
    # Setup: Create user first
    user = create_user(email="test@example.com", name="Test User")
    assert user.id is not None, "Setup failed: user not created"

    # Test: Update user
    user.name = "Updated Name"
    updated = update_user(user)

    # Verify
    assert updated.name == "Updated Name"

    # Verify persistence
    fetched_user = get_user(user.id)
    assert fetched_user.name == "Updated Name", "Update not persisted"

def test_get_nonexistent_user():
    """Test that getting nonexistent user returns None"""
    user = get_user(99999)
    assert user is None, "Should return None for nonexistent user"

def test_update_none_user_raises_error():
    """Test that updating None raises appropriate error"""
    with pytest.raises(ValueError, match="Cannot update None user"):
        update_user(None)
PYTHON
```

### Validation

```bash
# Run tests to verify fixes
pytest tests/test_user_service.py -v

# Expected output:
# tests/test_user_service.py::test_user_creation PASSED
# tests/test_user_service.py::test_user_update PASSED
# tests/test_user_service.py::test_get_nonexistent_user PASSED
# tests/test_user_service.py::test_update_none_user_raises_error PASSED
# =================== 4 passed in 0.23s ===================

# Run full test suite to check for other impacts
pytest tests/ -v

# Check code coverage
pytest tests/test_user_service.py --cov=app.services.user_service --cov-report=term-missing
```

### Prevention Strategy

**1. Add Integration Test for Database Operations**

```python
# tests/integration/test_user_persistence.py
def test_user_persistence_across_sessions():
    """Verify users persist across database sessions"""
    # Create user in one session
    user = create_user(email="persist@example.com", name="Persist User")
    user_id = user.id

    # Close session
    db.session.remove()

    # Fetch in new session
    fetched_user = get_user(user_id)
    assert fetched_user is not None
    assert fetched_user.email == "persist@example.com"
```

**2. Add Pre-commit Hook for Test Execution**

```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "Running tests before commit..."
pytest tests/ --maxfail=1 --tb=short -q || {
    echo "❌ Tests failed - commit blocked"
    echo "Fix tests or use --no-verify to skip (not recommended)"
    exit 1
}
echo "✓ All tests passed"
```

**3. Add CI Check for Test Coverage**

```yaml
# .github/workflows/tests.yml
- name: Run tests with coverage
  run: |
    pytest tests/ \
      --cov=app \
      --cov-fail-under=80 \
      --cov-report=term-missing
```

**4. Add Database Operation Assertions**

```python
# tests/conftest.py
import pytest

@pytest.fixture
def assert_db_commit():
    """Helper to verify database commits happened"""
    def _assert_commit(func, *args, **kwargs):
        before_count = db.session.query(User).count()
        result = func(*args, **kwargs)
        after_count = db.session.query(User).count()
        assert after_count > before_count, f"{func.__name__} didn't commit to database"
        return result
    return _assert_commit

# Usage in tests:
def test_user_creation(assert_db_commit):
    user = assert_db_commit(create_user, email="test@example.com", name="Test")
```

**5. Code Review Checklist**

Add to `.github/pull_request_template.md`:
```markdown
## Testing Checklist

- [ ] All tests pass locally
- [ ] New/modified code has test coverage
- [ ] Database operations include commit/rollback
- [ ] Tests check for both positive and negative cases
- [ ] No test fixtures depend on implicit state
```

## Common Test Failure Patterns

### Shared State Between Tests
```python
# ❌ Bad: Tests affect each other
shared_user = None

def test_create():
    global shared_user
    shared_user = create_user(...)

def test_update():
    # Fails if test_create didn't run first
    shared_user.name = "Updated"

# ✅ Good: Isolated tests
@pytest.fixture
def user():
    return create_user(...)

def test_create(user):
    assert user.id is not None

def test_update(user):
    user.name = "Updated"
```

### Missing Test Setup
```python
# ❌ Bad: Assumes database state
def test_get_user():
    user = get_user(1)  # Assumes user 1 exists

# ✅ Good: Create needed state
def test_get_user():
    created = create_user(...)
    user = get_user(created.id)
```

### Assertion Without Context
```python
# ❌ Bad: Unclear failure
assert user.id is not None

# ✅ Good: Clear failure message
assert user.id is not None, "User ID should be assigned after creation"
```

## Key Takeaways

- **Read error messages carefully**: They often point directly to the problem
- **Check recent changes**: Use `git diff` to see what changed
- **Verify database operations**: Ensure commits/rollbacks happen
- **Isolate tests**: Each test should set up its own state
- **Add assertions with messages**: Make failures self-explanatory
- **Run tests before committing**: Catch issues early
- **Test coverage matters**: But quality > quantity
