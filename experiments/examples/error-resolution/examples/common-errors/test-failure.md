# Test Failure Error Example

Example of using the Error Resolution pattern with pytest test failures.

## Step 1: Error Output

```
FAILED tests/test_user_service.py::test_user_creation - AssertionError: assert None is not None
FAILED tests/test_user_service.py::test_user_update - AttributeError: 'NoneType' object has no attribute 'name'
=================== 2 failed, 5 passed in 0.45s ================
```

## Step 2: Collect Context

```bash
cat > .error-context.md << 'EOF'
## Error
- test_user_creation: user.id is None after creation
- test_user_update: get_user(1) returns None

## Recent Changes
$(git log --oneline -3 app/services/)

## Source Code
```python
# app/services/user_service.py
def create_user(email, name):
    user = User(email=email, name=name)
    # Missing: db.session.add(user)
    # Missing: db.session.commit()
    return user
```

## Test Code
```python
# tests/test_user_service.py:15
def test_user_creation():
    user = create_user(email="test@example.com", name="Test User")
    assert user.id is not None  # FAILING
```
EOF
```

## Step 3: AI Diagnosis

```bash
ai "Fix these test failures:

$(cat .error-context.md)

Provide:
1. Root cause
2. Fix commands
3. Prevention (one method)"
```

## Step 4: Apply Fix

```bash
# Root cause: create_user() doesn't commit to database

# Fix the code
cat > app/services/user_service.py << 'PYTHON'
from app.models import User
from app.database import db

def create_user(email, name):
    user = User(email=email, name=name)
    db.session.add(user)
    db.session.commit()
    return user

def get_user(user_id):
    return User.query.filter_by(id=user_id).first()
PYTHON

# Verify fix
pytest tests/test_user_service.py -v

# Commit
git add -A
git commit -m "fix: restore database commit in create_user"
git push
```

## Prevention

Add pre-commit hook to run tests:

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/ --maxfail=1 -q || {
    echo "❌ Tests failed - commit blocked"
    exit 1
}
```

Make executable: `chmod +x .git/hooks/pre-commit`
