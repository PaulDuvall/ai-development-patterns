# DEVELOPMENT_RULES - Automated Test-Driven Development

## 30-SECOND VERSION

1. **Spec → Test → Code → Automate** (in that order, always)
2. **No manual commands twice** - Script it, then GitHub Action it
3. **Tests pass locally before push** - Pre-commit hook enforces
4. **Everything traces:** Spec ID → Test → Code → Automation
5. **Tasks ≤ 3 hours** - Break larger work into atomic pieces

---

## 5-MINUTE CORE WORKFLOW

### New Feature?
```bash
# 1. Spec (2 min)
echo "FEAT-001: Login returns 200 for valid creds" > specs/FEAT-001-auth.md

# 2. Test (5 min)
cat > tests/test_auth.py << 'EOF'
def test_valid_login():
    """Implements: specs/FEAT-001-auth.md#AC-001"""
    assert login("user", "pass").status == 200
EOF
pytest tests/test_auth.py  # Should FAIL

# 3. Code (10 min)
cat > src/auth.py << 'EOF'
def login(user, pw):
    """Implements: FEAT-001#AC-001"""
    return Response(200) if valid(user, pw) else Response(401)
EOF
pytest tests/test_auth.py  # Should PASS

# 4. Automate (already done - see .github/workflows/test-and-deploy.yml)
git commit -m "feat(FEAT-001): add login" && git push
```

### Repeating Command?
```bash
# 1. Script it
echo '#!/bin/bash\npsql -c "DELETE FROM logs WHERE age > 90"' > scripts/cleanup-logs.sh
chmod +x scripts/cleanup-logs.sh

# 2. Automate it
cat > .github/workflows/cleanup-logs.yml << 'EOF'
on:
  schedule: [cron: '0 2 * * 0']
jobs:
  cleanup: {runs-on: ubuntu-latest, steps: [{run: ./scripts/cleanup-logs.sh}]}
EOF
```

---

## COMPREHENSIVE DECISION TREE

```
USER REQUEST
│
├─ NEW FEATURE/CHANGE
│  │
│  ├─ Has spec? NO → Create specs/FEAT-XXX.md ━━━━━━━━┓
│  │                  - Unique ID, acceptance criteria │
│  │                  - Test scenarios, task breakdown │ STOP
│  │                  - Size tasks: 1-3h each          │
│  │                                                    ┛
│  ├─ Has tests? NO → Write failing tests first ━━━━━━┓
│  │                   - Reference spec in docstring   │
│  │                   - Verify test fails initially   │ STOP
│  │                   - Commit: "test: FEAT-XXX"      │
│  │                                                    ┛
│  ├─ Tests pass locally? NO → Implement minimal code ┓
│  │                            - Just enough to pass  │
│  │                            - Add spec references  │ STOP
│  │                            - Re-run tests         │
│  │                                                    ┛
│  └─ Tests pass? YES → Proceed to automation check
│
├─ COMMAND/SCRIPT
│  │
│  ├─ First time? → Create script in scripts/ ━━━━━━━━┓
│  │                - Make executable                  │
│  │                - Add --help flag                  │ STOP
│  │                - Add error handling               │
│  │                                                    ┛
│  ├─ Scheduled? → Create GitHub Action FIRST ━━━━━━━━┓
│  │               - Use cron trigger                  │
│  │               - Add workflow_dispatch             │ THEN RUN
│  │               - Test with workflow_dispatch       │
│  │                                                    ┛
│  ├─ Triggered by code? → Add to existing workflow ━━┓
│  │                        - On push/PR trigger       │
│  │                        - Runs automatically       │ STOP
│  │                                                    ┛
│  └─ Truly one-off? → Document in RUNBOOK.md ━━━━━━━━┓
│                      - Why it was one-off            │
│                      - Context for future            │ OK
│                                                       ┛
├─ BUG FIX
│  │
│  ├─ Has repro test? NO → Write failing test first ━━┓
│  │                       - Reproduces the bug        │
│  │                       - Links to issue/spec       │ STOP
│  │                                                    ┛
│  └─ Has test? YES → Fix & verify test passes ━━━━━━━┓
│                      - Minimal fix                   │
│                      - Check no regressions          │ CONTINUE
│                                                       ┛
├─ REFACTOR
│  │
│  ├─ Tests exist? NO → Write characterization tests ━┓
│  │                    - Document current behavior    │
│  │                    - 100% coverage of refactor    │ STOP
│  │                                                    ┛
│  └─ Tests exist? YES → Refactor & keep tests green ━┓
│                        - Tests define correctness    │
│                        - No behavior changes         │ CONTINUE
│                                                       ┛
├─ INFRASTRUCTURE/CONFIG
│  │
│  ├─ Manual change? → Script it as code ━━━━━━━━━━━━━┓
│  │                   - Terraform/CloudFormation      │
│  │                   - Docker/K8s manifests          │ STOP
│  │                   - Version control it            │
│  │                                                    ┛
│  └─ Environment-specific? → Parameterize ━━━━━━━━━━━┓
│                             - Use env vars           │
│                             - Separate configs       │ CONTINUE
│                                                       ┛
├─ DEPENDENCY UPDATE
│  │
│  ├─ Breaking change? → Spec + test + code workflow ━┓
│  │                     - Document breaking changes   │
│  │                     - Update tests first          │ STOP
│  │                                                    ┛
│  └─ Non-breaking? → Update & test ━━━━━━━━━━━━━━━━━━┓
│                     - Run full test suite            │
│                     - Check for deprecations         │ CONTINUE
│                                                       ┛
├─ HOTFIX (Production Down)
│  │
│  ├─ P0 Outage? → FIX FIRST, follow up after ━━━━━━━━┓
│  │               - Fix immediately                   │
│  │               - Document what was done            │ HOTFIX OK
│  │               - Create issue for proper fix       │ THEN
│  │               - Follow normal workflow for issue  │ STOP
│  │                                                    ┛
│  └─ Not P0? → Follow normal workflow ━━━━━━━━━━━━━━━┛
│
├─ DOCUMENTATION
│  │
│  └─ Code change? NO → Update docs directly ━━━━━━━━━┓
│     Code change? YES → Update in same commit ━━━━━━━┫ CONTINUE
│                                                       ┛
└─ QUESTION/EXPLANATION
   │
   └─ Answer directly (no automation needed)
```

---

## WORKFLOW DETAILS

### 1. SPECIFICATION TEMPLATE

```markdown
# specs/FEAT-001-user-authentication.md
**Feature ID:** FEAT-001
**Status:** Draft → Ready → In Progress → Done
**Owner:** @username
**Created:** 2025-01-15

## User Story
As a **registered user**
I want to **log in with email and password**
So that **I can access my account securely**

## Acceptance Criteria
- **AC-001:** Returns 200 + JWT for valid credentials
- **AC-002:** Returns 401 for invalid credentials
- **AC-003:** Returns 429 after 5 failed attempts in 1 minute
- **AC-004:** Logs security events (success/failure)

## Test Scenarios
| Scenario | Test Location | Status |
|----------|---------------|--------|
| Valid login | `tests/test_auth.py::test_valid_login` | ✅ Pass |
| Invalid password | `tests/test_auth.py::test_invalid_password` | ✅ Pass |
| Rate limiting | `tests/test_auth.py::test_rate_limit` | 🚧 In Progress |
| Security logging | `tests/test_auth.py::test_security_logs` | ❌ Not Started |

## Task Breakdown (Atomic: 1-3 hours each)
- [ ] **TASK-001** (2h): Write all test cases
- [ ] **TASK-002** (2h): Implement basic auth endpoint
- [ ] **TASK-003** (2h): Add rate limiting
- [ ] **TASK-004** (1h): Add security logging
- [ ] **TASK-005** (1h): Update API documentation

## Dependencies
- Database: Users table with hashed passwords
- External: Redis for rate limiting
- Config: JWT secret in environment

## Risks
- Rate limiting requires Redis (not in local dev by default)
- JWT secret rotation strategy needed

## Rollback Plan
- Feature flag: `FEATURE_NEW_AUTH=false`
- Old auth endpoint remains at `/auth/legacy`
- Remove after 2 weeks of monitoring
```

### 2. TEST-FIRST IMPLEMENTATION

```python
# tests/test_auth.py
"""Authentication tests
Implements: specs/FEAT-001-user-authentication.md
"""
import pytest
from src.auth import login, AuthService
from src.models import User

class TestAuthentication:
    """Test suite for FEAT-001"""

    @pytest.fixture
    def auth_service(self):
        """Implements: FEAT-001 test setup"""
        return AuthService()

    @pytest.fixture
    def valid_user(self, db):
        """Implements: FEAT-001 test data"""
        return User.create(
            email="test@example.com",
            password_hash=hash_password("ValidPass123!")
        )

    def test_valid_login(self, auth_service, valid_user):
        """Implements: specs/FEAT-001-user-authentication.md#AC-001

        Given a registered user with valid credentials
        When they attempt to login
        Then they receive a 200 response with a JWT token
        """
        response = auth_service.login(
            email="test@example.com",
            password="ValidPass123!"
        )

        assert response.status_code == 200
        assert "token" in response.json()
        assert jwt.decode(response.json()["token"]).get("user_id") == valid_user.id

    def test_invalid_password(self, auth_service, valid_user):
        """Implements: specs/FEAT-001-user-authentication.md#AC-002

        Given a registered user
        When they attempt to login with wrong password
        Then they receive a 401 response
        """
        response = auth_service.login(
            email="test@example.com",
            password="WrongPassword"
        )

        assert response.status_code == 401
        assert response.json()["error"] == "Invalid credentials"

    def test_rate_limiting(self, auth_service, valid_user):
        """Implements: specs/FEAT-001-user-authentication.md#AC-003

        Given a user has failed 5 login attempts in under 1 minute
        When they attempt to login again
        Then they receive a 429 response
        """
        # Make 5 failed attempts
        for _ in range(5):
            auth_service.login("test@example.com", "wrong")

        # 6th attempt should be rate limited
        response = auth_service.login("test@example.com", "wrong")

        assert response.status_code == 429
        assert "retry_after" in response.json()

    def test_security_logging(self, auth_service, valid_user, mock_logger):
        """Implements: specs/FEAT-001-user-authentication.md#AC-004

        Given any login attempt
        When the attempt is made
        Then a security event is logged
        """
        auth_service.login("test@example.com", "ValidPass123!")

        mock_logger.assert_called_with(
            event="login_success",
            user_id=valid_user.id,
            ip_address=ANY,
            timestamp=ANY
        )

    def test_nonexistent_user(self, auth_service):
        """Edge case: User doesn't exist

        Given an email not in the system
        When login attempted
        Then 401 returned (same as invalid password to prevent enumeration)
        """
        response = auth_service.login("nonexistent@example.com", "password")

        assert response.status_code == 401
        assert response.json()["error"] == "Invalid credentials"

# Run and verify FAILS
# $ pytest tests/test_auth.py -v
# FAILED tests/test_auth.py::TestAuthentication::test_valid_login
# FAILED tests/test_auth.py::TestAuthentication::test_invalid_password
# ...all should fail initially
```

### 3. MINIMAL IMPLEMENTATION

```python
# src/auth.py
"""Authentication service
Implements: specs/FEAT-001-user-authentication.md
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
import redis
from .models import User
from .logging import security_logger

class AuthService:
    """Implements: FEAT-001 - User Authentication

    Tests: tests/test_auth.py::TestAuthentication
    """

    def __init__(self, redis_client: redis.Redis = None):
        self.redis = redis_client or redis.from_url(settings.REDIS_URL)
        self.jwt_secret = settings.JWT_SECRET

    def login(self, email: str, password: str) -> Response:
        """Authenticate user and return JWT

        Implements:
            - FEAT-001#AC-001: Valid credentials → 200 + JWT
            - FEAT-001#AC-002: Invalid credentials → 401
            - FEAT-001#AC-003: Rate limiting
            - FEAT-001#AC-004: Security logging

        Tests:
            - tests/test_auth.py::test_valid_login
            - tests/test_auth.py::test_invalid_password
            - tests/test_auth.py::test_rate_limiting
            - tests/test_auth.py::test_security_logging
        """
        # AC-003: Check rate limit first
        if self._is_rate_limited(email):
            self._log_security_event("login_rate_limited", email)
            return Response(429, {"error": "Too many attempts", "retry_after": 60})

        # AC-001, AC-002: Validate credentials
        user = self._authenticate(email, password)

        if user is None:
            self._increment_failed_attempts(email)
            self._log_security_event("login_failed", email)  # AC-004
            return Response(401, {"error": "Invalid credentials"})

        # AC-001: Generate JWT
        token = self._generate_jwt(user)
        self._reset_failed_attempts(email)
        self._log_security_event("login_success", email, user.id)  # AC-004

        return Response(200, {"token": token, "user_id": user.id})

    def _authenticate(self, email: str, password: str) -> Optional[User]:
        """Verify credentials against database"""
        user = User.find_by_email(email)
        if user and user.verify_password(password):
            return user
        return None

    def _is_rate_limited(self, email: str) -> bool:
        """Implements: FEAT-001#AC-003"""
        key = f"login_attempts:{email}"
        attempts = self.redis.get(key)
        return attempts and int(attempts) >= 5

    def _increment_failed_attempts(self, email: str):
        """Implements: FEAT-001#AC-003"""
        key = f"login_attempts:{email}"
        self.redis.incr(key)
        self.redis.expire(key, 60)  # 1 minute window

    def _reset_failed_attempts(self, email: str):
        """Implements: FEAT-001#AC-003"""
        self.redis.delete(f"login_attempts:{email}")

    def _generate_jwt(self, user: User) -> str:
        """Implements: FEAT-001#AC-001"""
        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def _log_security_event(self, event: str, email: str, user_id: int = None):
        """Implements: FEAT-001#AC-004"""
        security_logger.info({
            "event": event,
            "email": email,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip_address": get_request_ip()
        })
```

### 4. AUTOMATION (GitHub Actions)

```yaml
# .github/workflows/test-and-deploy.yml
name: Test, Build, Deploy
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:  # Manual trigger

env:
  PYTHON_VERSION: '3.11'
  MIN_COVERAGE: 80

jobs:
  validate:
    name: Validate Code Quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint code
        run: |
          ruff check src/ tests/
          black --check src/ tests/
          mypy src/

      - name: Check traceability
        run: ./scripts/check_traceability.sh

  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: validate

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run unit tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test
          REDIS_URL: redis://localhost:6379
        run: |
          pytest tests/unit/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=term \
            --cov-fail-under=${{ env.MIN_COVERAGE }} \
            -v

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test
          REDIS_URL: redis://localhost:6379
        run: |
          pytest tests/integration/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: validate
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.example.com

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to staging
        run: ./scripts/deploy.sh staging
        env:
          DEPLOY_KEY: ${{ secrets.STAGING_DEPLOY_KEY }}
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}

      - name: Run smoke tests
        run: ./scripts/smoke-test.sh https://staging.example.com

      - name: Notify deployment
        if: always()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Staging deployment ${{ job.status }}",
              "commit": "${{ github.sha }}",
              "author": "${{ github.actor }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://example.com

    steps:
      - uses: actions/checkout@v4

      - name: Create deployment
        id: deployment
        uses: chrnorm/deployment-action@v2
        with:
          token: ${{ github.token }}
          environment: production

      - name: Deploy to production
        run: ./scripts/deploy.sh production
        env:
          DEPLOY_KEY: ${{ secrets.PROD_DEPLOY_KEY }}
          DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}

      - name: Run smoke tests
        run: ./scripts/smoke-test.sh https://example.com

      - name: Update deployment status (success)
        if: success()
        uses: chrnorm/deployment-status@v2
        with:
          token: ${{ github.token }}
          deployment-id: ${{ steps.deployment.outputs.deployment_id }}
          state: 'success'

      - name: Update deployment status (failure)
        if: failure()
        uses: chrnorm/deployment-status@v2
        with:
          token: ${{ github.token }}
          deployment-id: ${{ steps.deployment.outputs.deployment_id }}
          state: 'failure'

      - name: Rollback on failure
        if: failure()
        run: ./scripts/rollback.sh production

      - name: Notify deployment
        if: always()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Production deployment ${{ job.status }}",
              "commit": "${{ github.sha }}",
              "author": "${{ github.actor }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## FILE STRUCTURE (Complete)

```
project/
│
├── specs/                              # ← Start here (Step 1)
│   ├── FEAT-001-authentication.md     # Specs with IDs, ACs, test refs
│   ├── FEAT-002-user-profile.md
│   ├── ARCH-001-api-design.md         # Architecture decisions
│   ├── traceability.md                # Spec↔Test↔Code matrix
│   └── README.md                      # Spec index and status
│
├── tests/                              # ← Write second (Step 2)
│   ├── unit/                          # Fast, isolated tests
│   │   ├── test_auth.py              # """Implements: specs/FEAT-001#AC-001"""
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── integration/                   # Tests with DB/external services
│   │   ├── test_api_endpoints.py
│   │   └── test_database.py
│   ├── e2e/                           # End-to-end tests
│   │   └── test_user_flows.py
│   ├── fixtures/                      # Test data
│   │   ├── users.json
│   │   └── factories.py
│   ├── conftest.py                    # Pytest configuration
│   └── README.md                      # How to run tests
│
├── src/                                # ← Implement third (Step 3)
│   ├── auth.py                        # # Implements: FEAT-001
│   ├── models/
│   ├── services/
│   ├── api/
│   └── utils/
│
├── scripts/                            # ← Automate fourth (Step 4)
│   ├── deploy.sh                      # Deployment script
│   ├── rollback.sh                    # Rollback script
│   ├── smoke-test.sh                  # Post-deploy validation
│   ├── cleanup-old-data.sh            # Maintenance tasks
│   ├── check_traceability.sh          # Validate spec-test-code links
│   ├── setup-dev-env.sh               # Developer onboarding
│   └── README.md                      # Script documentation
│
├── .github/
│   ├── workflows/                     # ← Final automation
│   │   ├── test-and-deploy.yml       # Main CI/CD pipeline
│   │   ├── nightly-cleanup.yml       # Scheduled maintenance
│   │   ├── security-scan.yml         # Daily security scans
│   │   ├── dependency-update.yml     # Automated dependency PRs
│   │   └── README.md                 # Workflow documentation
│   └── PULL_REQUEST_TEMPLATE.md      # PR checklist
│
├── infrastructure/                     # Infrastructure as code
│   ├── terraform/                     # Terraform configs
│   ├── docker/                        # Dockerfiles
│   └── k8s/                           # Kubernetes manifests
│
├── docs/                               # Documentation
│   ├── api/                           # API documentation
│   ├── architecture/                  # Architecture docs
│   ├── runbooks/                      # Operational procedures
│   └── onboarding/                    # New developer guides
│
├── migrations/                         # Database migrations
│   ├── 001_create_users.sql
│   └── 002_add_auth_indexes.sql
│
├── .git/
│   └── hooks/                         # Git hooks (auto-installed)
│       ├── pre-commit                 # Run tests before commit
│       ├── pre-push                   # Full validation before push
│       └── commit-msg                 # Validate commit message format
│
├── RUNBOOK.md                         # Manual procedures (last resort)
├── CHANGELOG.md                       # Auto-generated from commits
├── run_tests.sh                       # Local test runner (= CI)
├── check_traceability.sh              # Spec-test-code validation
├── requirements.txt                   # Production dependencies
├── requirements-dev.txt               # Development dependencies
├── .env.example                       # Environment variable template
└── README.md                          # Project overview
```

---

## TRACEABILITY SYSTEM

### Bidirectional Linking

```
SPEC (specs/FEAT-001.md)
  │
  ├─→ "Test: tests/test_auth.py::test_valid_login"
  │
  ↓
TEST (tests/test_auth.py::test_valid_login)
  │
  ├─→ """Implements: specs/FEAT-001.md#AC-001"""
  │
  ↓
CODE (src/auth.py::login)
  │
  ├─→ """Implements: FEAT-001#AC-001"""
  ├─→ """Tests: tests/test_auth.py::test_valid_login"""
  │
  ↓
WORKFLOW (.github/workflows/test-and-deploy.yml)
  │
  └─→ Runs tests automatically on every push
```

### Automated Validation

```bash
#!/bin/bash
# scripts/check_traceability.sh
# Validates all spec-test-code links

set -e

echo "🔍 Checking traceability..."

# 1. Check specs have tests
for spec in specs/FEAT-*.md; do
    spec_id=$(basename "$spec" .md)

    # Extract test references from spec
    test_refs=$(grep -o 'tests/[^)]*' "$spec" || true)

    if [ -z "$test_refs" ]; then
        echo "❌ $spec_id: No test references found"
        exit 1
    fi

    # Verify each test exists
    for test_ref in $test_refs; do
        if ! grep -r "Implements.*$spec_id" tests/ > /dev/null; then
            echo "❌ $spec_id: Test $test_ref doesn't reference spec"
            exit 1
        fi
    done
done

# 2. Check tests have specs
for test_file in tests/test_*.py; do
    if ! grep -q "Implements: specs/" "$test_file"; then
        echo "⚠️  $test_file: No spec reference found"
    fi
done

# 3. Check code has specs
for code_file in src/**/*.py; do
    if ! grep -q "Implements: FEAT-" "$code_file"; then
        echo "⚠️  $code_file: No spec reference found"
    fi
done

# 4. Generate traceability matrix
python scripts/generate_traceability_matrix.py > specs/traceability.md

echo "✅ Traceability check passed"
```

```python
# scripts/generate_traceability_matrix.py
"""Generate traceability matrix: Spec ↔ Test ↔ Code"""

import re
from pathlib import Path
from typing import Dict, List

def extract_spec_refs(file_path: Path) -> List[str]:
    """Extract spec references from file"""
    content = file_path.read_text()
    return re.findall(r'FEAT-\d+', content)

def extract_test_refs(file_path: Path) -> List[str]:
    """Extract test references from spec"""
    content = file_path.read_text()
    return re.findall(r'tests/[^\)]+', content)

def build_traceability_matrix():
    specs = {}

    # Scan specs
    for spec_file in Path('specs').glob('FEAT-*.md'):
        spec_id = spec_file.stem
        test_refs = extract_test_refs(spec_file)
        specs[spec_id] = {
            'tests': test_refs,
            'code': [],
            'status': '❓'
        }

    # Scan tests
    for test_file in Path('tests').rglob('test_*.py'):
        content = test_file.read_text()
        for spec_id in specs:
            if spec_id in content:
                # Find implementing code
                functions = re.findall(r'def (test_\w+)', content)
                for func in functions:
                    if spec_id in content[content.find(func):content.find(func) + 500]:
                        specs[spec_id]['tests'].append(f"{test_file}::{func}")

    # Scan code
    for code_file in Path('src').rglob('*.py'):
        content = code_file.read_text()
        for spec_id in specs:
            if spec_id in content:
                specs[spec_id]['code'].append(str(code_file))
                # Check if tests pass
                if specs[spec_id]['tests']:
                    specs[spec_id]['status'] = '✅'

    # Generate markdown table
    print("# Traceability Matrix\n")
    print("| Spec ID | Tests | Implementation | Status |")
    print("|---------|-------|----------------|--------|")

    for spec_id, data in sorted(specs.items()):
        tests = '<br>'.join(data['tests'][:3]) + ('...' if len(data['tests']) > 3 else '')
        code = '<br>'.join(data['code'][:3]) + ('...' if len(data['code']) > 3 else '')
        status = data['status']
        print(f"| {spec_id} | {tests} | {code} | {status} |")

if __name__ == '__main__':
    build_traceability_matrix()
```

---

## EDGE CASES & EMERGENCIES

### Hotfix Procedure (Production Down)

```markdown
# P0 HOTFIX PROTOCOL

## Immediate Actions (Do First)
1. **Fix production immediately** - Don't wait for tests
2. **Deploy hotfix** - Use emergency deploy script
3. **Notify team** - Page on-call, post in #incidents
4. **Monitor** - Watch metrics/logs for 30 minutes

## Follow-Up Actions (Within 24 hours)
1. **Write test** - Reproduce the bug with failing test
2. **Proper fix** - Follow normal workflow (spec → test → code)
3. **Post-mortem** - Document in `docs/incidents/YYYY-MM-DD-incident.md`
4. **Update runbook** - Add detection/mitigation steps

## Emergency Deploy Script
```bash
# scripts/emergency-deploy.sh
#!/bin/bash
# ONLY USE FOR P0 INCIDENTS

read -p "Incident ticket #: " ticket
read -p "Confirm production deploy (yes): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled"
    exit 1
fi

echo "🚨 EMERGENCY DEPLOY - Incident #$ticket"
git tag -a "hotfix-$ticket" -m "Emergency hotfix for #$ticket"
./scripts/deploy.sh production --skip-tests --force
echo "📝 Create follow-up ticket to add tests"
```
```

### Legacy Code Migration

```markdown
# ADOPTING THESE RULES ON EXISTING CODEBASE

## Phase 1: Bootstrap (Week 1)
- [ ] Create `specs/` directory
- [ ] Set up GitHub Actions skeleton
- [ ] Install pre-commit hooks
- [ ] Add `run_tests.sh` script
- [ ] Create `check_traceability.sh` (lenient mode)

## Phase 2: New Code Only (Weeks 2-4)
- [ ] All NEW features follow full workflow
- [ ] Legacy code exempted (for now)
- [ ] Document legacy areas in `TECHNICAL_DEBT.md`

## Phase 3: Gradual Retrofit (Month 2+)
- [ ] When touching legacy code, add tests first
- [ ] Create spec for modified areas
- [ ] Add traceability references
- [ ] Track progress: `scripts/coverage-report.sh`

## Don't Boil the Ocean
- ✅ DO: Add tests when fixing bugs in legacy code
- ✅ DO: Spec new features completely
- ❌ DON'T: Rewrite everything at once
- ❌ DON'T: Block work on "perfect" setup
```

### Non-Code Changes

```markdown
# HANDLING NON-CODE CHANGES

## Documentation Changes
- Treat like code: PR → review → merge
- No tests needed, but CI spell-checks

## Configuration Changes
- Spec: Document what's changing and why
- Test: Validate config with smoke test
- Code: Use infrastructure-as-code (Terraform/Ansible)
- Automate: Apply via GitHub Actions

## Database Migrations
- Spec: Migration plan with rollback procedure
- Test: Run migration on test DB, verify rollback
- Code: Write both up and down migrations
- Automate: Apply in deploy script with safety checks

## Infrastructure Changes
- Spec: Architecture decision record (ADR)
- Test: Terraform plan, cost estimate
- Code: Terraform/CloudFormation
- Automate: Apply via GitHub Actions with approval gate
```

### When Tests Are Impossible

```markdown
# EXEMPTIONS (Use Sparingly)

## Legitimate Cases for No Automated Tests
1. **UI pixel-perfect alignment** - Manual QA acceptable
2. **Third-party API changes** - Contract tests + monitoring
3. **Performance tuning** - Benchmark tests instead
4. **Security patches** - Apply immediately, test after

## Required Documentation
```yaml
# specs/EXEMPT-001-ui-polish.md
exempt: true
reason: "Pixel-perfect alignment requires human judgment"
alternative_validation: "Manual QA checklist"
qa_checklist:
  - [ ] Mobile responsive
  - [ ] Dark mode works
  - [ ] Accessibility verified
manual_tester: "@designer"
```
```

---

## BOOTSTRAP SCRIPTS

### Initial Setup

```bash
#!/bin/bash
# scripts/bootstrap-project.sh
# Sets up test-first automation-first workflow from scratch

set -e

echo "🚀 Bootstrapping test-first automation-first project..."

# 1. Create directory structure
mkdir -p specs tests/{unit,integration,e2e,fixtures} src scripts .github/workflows docs infrastructure

# 2. Create spec template
cat > specs/TEMPLATE.md << 'EOF'
# Feature: [Feature Name]
**ID:** FEAT-XXX
**Status:** Draft
**Owner:** @username

## User Story
As a [user type]
I want [feature]
So that [benefit]

## Acceptance Criteria
- AC-001: [Specific, testable requirement]

## Test Scenarios
- TEST-001: tests/test_feature.py::test_scenario

## Tasks
- [ ] TASK-001: (1-3h) [Atomic task]
EOF

# 3. Create test template
cat > tests/TEMPLATE.py << 'EOF'
"""[Feature name] tests
Implements: specs/FEAT-XXX.md
"""
import pytest

def test_example():
    """Implements: specs/FEAT-XXX.md#AC-001"""
    assert True  # Replace with actual test
EOF

# 4. Install pre-commit hooks
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
set -e
pytest tests/ --quiet --exitfirst || {
    echo "❌ Tests failed - commit blocked"
    exit 1
}
EOF
chmod +x .git/hooks/pre-commit

# 5. Create run_tests.sh (same as CI)
cat > run_tests.sh << 'EOF'
#!/bin/bash
set -e
pytest tests/ --cov=src --cov-fail-under=80 -v
./check_traceability.sh
EOF
chmod +x run_tests.sh

# 6. Create traceability checker
cat > check_traceability.sh << 'EOF'
#!/bin/bash
# Validates spec-test-code links
echo "🔍 Checking traceability..."
# Add validation logic here
echo "✅ Traceability check passed"
EOF
chmod +x check_traceability.sh

# 7. Create basic GitHub Action
cat > .github/workflows/test-and-deploy.yml << 'EOF'
name: Test & Deploy
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./run_tests.sh
EOF

# 8. Create README
cat > README.md << 'EOF'
# Project Name

## Development Workflow
1. Write spec in `specs/FEAT-XXX.md`
2. Write failing tests in `tests/`
3. Implement in `src/`
4. Push - CI auto-deploys on green

## Quick Start
```bash
./scripts/setup-dev-env.sh
./run_tests.sh
```
EOF

echo "✅ Bootstrap complete!"
echo "Next steps:"
echo "  1. Create your first spec: cp specs/TEMPLATE.md specs/FEAT-001-myfeature.md"
echo "  2. Write failing tests: cp tests/TEMPLATE.py tests/test_myfeature.py"
echo "  3. Run tests: ./run_tests.sh"
```

### Developer Onboarding

```bash
#!/bin/bash
# scripts/setup-dev-env.sh
# One-command developer environment setup

set -e

echo "👋 Setting up development environment..."

# 1. Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git required"; exit 1; }

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Install git hooks
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 5. Set up local database
docker compose up -d postgres redis

# 6. Run migrations
python scripts/migrate.py

# 7. Create .env from template
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Update .env with your local settings"
fi

# 8. Run tests to verify setup
./run_tests.sh

echo "✅ Development environment ready!"
echo "To activate: source .venv/bin/activate"
echo "To run tests: ./run_tests.sh"
echo "To start coding: Read CLAUDE.md for workflow"
```

---

## METRICS & MONITORING

### Track These Metrics

```yaml
# .github/workflows/metrics.yml
name: Track Metrics
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Calculate metrics
        run: |
          echo "## Development Metrics" > metrics.md
          echo "Generated: $(date)" >> metrics.md
          echo "" >> metrics.md

          # Test coverage
          coverage=$(pytest --cov=src --cov-report=term | grep TOTAL | awk '{print $4}')
          echo "- **Test Coverage:** $coverage" >> metrics.md

          # Traceability
          specs=$(find specs -name 'FEAT-*.md' | wc -l)
          tests=$(grep -r "Implements: specs" tests | wc -l)
          echo "- **Specs:** $specs" >> metrics.md
          echo "- **Traced Tests:** $tests" >> metrics.md
          echo "- **Traceability:** $((tests * 100 / specs))%" >> metrics.md

          # Automation
          manual=$(grep -c "# TODO: Automate" scripts/*.sh || echo 0)
          automated=$(find .github/workflows -name '*.yml' | wc -l)
          echo "- **Automated Workflows:** $automated" >> metrics.md
          echo "- **Manual TODOs:** $manual" >> metrics.md

          # Task sizing
          large_tasks=$(grep -r "estimated_hours: [9-9][0-9]\|[0-9][0-9][0-9]" specs || true | wc -l)
          echo "- **Oversized Tasks:** $large_tasks" >> metrics.md

          cat metrics.md

      - name: Post to dashboard
        run: |
          # Send metrics to monitoring system
          curl -X POST ${{ secrets.METRICS_WEBHOOK }} \
            -H "Content-Type: application/json" \
            -d @metrics.md
```

---

## QUICK REFERENCE

### Common Commands

```bash
# Daily workflow
git pull                           # Get latest
./run_tests.sh                     # Run all tests (= CI)
git commit -m "feat: description"  # Commit (runs pre-commit hook)
git push                           # Push (triggers CI → deploy)

# Creating new feature
cp specs/TEMPLATE.md specs/FEAT-042-new-thing.md
# Edit spec with acceptance criteria
cp tests/TEMPLATE.py tests/test_new_thing.py
# Write failing tests
./run_tests.sh                     # Verify tests fail
# Implement feature
./run_tests.sh                     # Verify tests pass

# Automation
./scripts/automate-command.sh "command to automate"
# Creates script + GitHub Action

# Validation
./check_traceability.sh            # Verify all links valid
pytest tests/ --cov=src            # Check coverage
```

### Commit Message Format

```
<type>(<scope>): <description>

Types: feat, fix, docs, refactor, test, chore
Scope: FEAT-XXX or component name

Examples:
  feat(FEAT-001): add user authentication
  fix(FEAT-001): handle empty password
  test(FEAT-001): add rate limiting tests
  docs: update API documentation
  chore: upgrade dependencies
```

---

## SUMMARY: The Rules

1. **Spec → Test → Code → Automate** (always this order)
2. **Tests pass locally before push** (enforced by pre-commit hook)
3. **Everything is traced** (Spec ↔ Test ↔ Code ↔ Automation)
4. **Tasks ≤ 3 hours** (atomic, independent, testable)
5. **No manual commands twice** (script it, then automate it)
6. **CI = Local** (same tests, same results)
7. **Green before merge** (CI must pass)
8. **Auto-deploy on green** (staging immediately, production on tag)
9. **Hotfixes allowed** (but follow up within 24h)
10. **Gradual adoption OK** (new code first, legacy incrementally)

**Emergency Override:** Production down? Fix first, follow up after.
**Legacy Code:** Exempt until touched, then add tests.
**When Stuck:** Document in RUNBOOK.md, create issue to automate.

---

**Remember: If you do it twice, script it. If you script it, automate it. If you code it, test it first.**
