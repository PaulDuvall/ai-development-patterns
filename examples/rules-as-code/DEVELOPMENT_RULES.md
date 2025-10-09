# DEVELOPMENT_RULES - Test-First Specification-Driven Development

**IMPORTANT: Review these rules before EVERY code change. These are non-negotiable requirements.**

## CORE MANDATE

1. **NEVER write implementation code before tests**
2. **ALWAYS run tests locally before committing**  
3. **ONLY push code when all tests pass locally**
4. **CI must validate all tests before merge**
5. **Every specification needs corresponding tests**
6. **Tasks must be atomic and independently testable**

---

## WORKFLOW REQUIREMENTS

### For Every New Feature or Change:

#### 1. CHECK SPECIFICATION EXISTS
```
IF no specification exists for this change:
   STOP - Create specification first in specs/ directory
   Include acceptance criteria and test scenarios
   Add unique identifiers for traceability
ELSE:
   PROCEED to step 2
```

**SPECIFICATION REQUIREMENTS:**
```markdown
# specs/feature-name.md
## Feature ID: FEAT-001
## Status: Draft|Ready|Implemented|Tested

### User Story
As a [user type]
I want [feature]
So that [benefit]

### Acceptance Criteria
- [ ] AC-001: Specific, testable requirement
- [ ] AC-002: Another testable requirement

### Test Scenarios
- TEST-001: Links to test_feature.py::test_scenario_one
- TEST-002: Links to test_feature.py::test_scenario_two

### Task Breakdown
- [ ] TASK-001: Atomic task (1-3 hours)
- [ ] TASK-002: Another atomic task (1-3 hours)
```

#### 2. WRITE TESTS FIRST
```
For each acceptance criterion in specification:
   1. Create test file with traceable name
   2. Write failing test that defines success
   3. Include specification reference in test
   4. Run test locally to confirm it fails
   5. Commit test with message: "test: add failing test for [feature-id]"
```

**TEST TRACEABILITY:**
```python
def test_user_authentication():
    """
    Implements: specs/auth.md#AC-001
    Feature: FEAT-001
    Task: TASK-001
    
    Test that user can authenticate with valid credentials.
    """
    # Test implementation
    assert login("user@example.com", "password").status_code == 200
```

#### 3. GENERATE STRUCTURED WORK ITEMS
```yaml
work_item_requirements:
  task_id: "FEAT-001-TASK-001"
  title: "Implement user authentication endpoint"
  size: "1-3 hours (max 4-8 hours for complex items)"
  
  acceptance_criteria:
    - "Returns 200 for valid credentials"
    - "Returns 401 for invalid credentials"
    - "Handles rate limiting"
  
  test_files:
    - "tests/test_auth.py::test_valid_login"
    - "tests/test_auth.py::test_invalid_login"
    - "tests/test_auth.py::test_rate_limiting"
  
  dependencies: []  # Must be empty for atomic tasks
  
  definition_of_done:
    - "All tests passing locally"
    - "Code reviewed"
    - "Documentation updated"
    - "CI pipeline green"
```

#### 4. IMPLEMENT TO PASS TESTS
```
While tests are failing:
   1. Write MINIMAL code to pass current failing test
   2. Run tests locally: pytest tests/ or npm test
   3. Do NOT add features beyond what tests require
   4. Do NOT refactor until tests pass
   5. Include traceability comments in implementation
```

**IMPLEMENTATION TRACEABILITY:**
```python
class AuthenticationService:
    """Service for user authentication.
    
    Implements specifications from:
    - specs/auth.md#authentication-service
    - Features: FEAT-001, FEAT-002
    """
    
    def authenticate(self, email: str, password: str):
        """Authenticate user with credentials.
        
        Implements: specs/auth.md#AC-001
        Tests: tests/test_auth.py::test_valid_login
        """
        # Implementation code
```

#### 5. VALIDATE LOCALLY
```bash
# Before EVERY commit:
pytest tests/           # Run all tests
pytest tests/ --cov     # Check coverage >= 80%
behave tests/features   # Run behavior tests if present
./check_traceability.sh # Verify spec-test-code links

IF any test fails:
   DO NOT COMMIT - Fix the issue first
   
IF traceability broken:
   DO NOT COMMIT - Update references
```

#### 6. PUSH ONLY WHEN GREEN
```bash
git add .
git commit -m "feat(FEAT-001): [description] - all tests passing locally"
git push

MONITOR CI pipeline - if CI fails but local passed:
   INVESTIGATE environment differences immediately
   Document in specs/environment-issues.md
```

---

## TASK DECOMPOSITION STANDARDS

### Atomic Task Requirements
```yaml
task_sizing:
  ideal: "1-3 hours"
  maximum: "4-8 hours"
  parallel_ai: "1-2 hours"  # For AI agent execution
  
task_attributes:
  atomic: true  # Completable independently
  testable: true  # Has clear success criteria
  traceable: true  # Links to spec and tests
  
reject_if:
  - duration > 8 hours
  - has_dependencies_on_other_tasks
  - no_clear_completion_criteria
  - no_test_scenarios
```

**GOOD TASK EXAMPLE:**
```yaml
task:
  id: "USER-001-TASK-003"
  title: "Add email validation to user model"
  estimated_hours: 2
  
  acceptance_criteria:
    - "Rejects invalid email formats"
    - "Accepts valid email formats"
    - "Handles edge cases (unicode, long domains)"
  
  test_first:
    - "tests/models/test_user.py::test_email_validation_invalid"
    - "tests/models/test_user.py::test_email_validation_valid"
    - "tests/models/test_user.py::test_email_edge_cases"
  
  no_dependencies: true
  can_be_done_in_isolation: true
```

**BAD TASK EXAMPLE:**
```yaml
task:  # ❌ TOO BIG, DEPENDENT
  title: "Implement complete user system"
  estimated_hours: 40  # ❌ Way too large
  dependencies: ["database", "email_service"]  # ❌ Not atomic
  criteria: "User system works"  # ❌ Too vague
```

---

## SPECIFICATION-TEST TRACEABILITY

### Every Specification Element MUST Have Tests
```python
# check_traceability.py
def validate_traceability():
    specifications = load_specifications("specs/")
    test_files = load_tests("tests/")
    
    for spec in specifications:
        for criterion in spec.acceptance_criteria:
            if not has_corresponding_test(criterion, test_files):
                ERROR: f"No test for {spec.id}#{criterion.id}"
                
        for test_ref in spec.test_references:
            if not test_exists(test_ref):
                ERROR: f"Missing test: {test_ref}"
    
    for test in test_files:
        if not has_specification_reference(test):
            WARNING: f"Test without spec: {test.name}"
```

### Traceability Matrix Requirements
```markdown
# docs/traceability.md
| Spec ID | Acceptance Criteria | Test File | Implementation | Status |
|---------|-------------------|-----------|----------------|--------|
| AUTH-001 | AC-001: Valid login | test_auth.py::test_valid | auth.py:15-45 | ✓ |
| AUTH-001 | AC-002: Invalid login | test_auth.py::test_invalid | auth.py:47-65 | ✓ |
| AUTH-001 | AC-003: Rate limiting | test_auth.py::test_rate | auth.py:67-95 | 🚧 |
```

---

## AI AGENT INSTRUCTIONS

When asked to implement a feature:

### STEP 1: Request Specification
```
"Show me the specification for this feature"
"What are the acceptance criteria?"
"What test scenarios define success?"
"What is the unique feature ID?"
```

### STEP 2: Request Tests
```
"Show me the failing tests for this feature"
"Which test files correspond to the specification?"
"What is the expected behavior from the tests?"
```

### STEP 3: Implement Against Tests
```python
# ALWAYS structure responses like this:

## Specification Reference
Feature: FEAT-001
Acceptance Criteria: AC-001, AC-002

## Current Failing Test
[Show the specific test that's failing]

## Implementation to Pass Test
[Minimal code to make test pass]
[Include traceability comments]

## Verification
Run: pytest tests/test_feature.py -v
Expected: All tests pass
Coverage: Must maintain or improve
```

### STEP 4: Validate Before Delivering
```
Before marking any task complete:
1. ✓ All specified tests pass locally
2. ✓ No existing tests broken
3. ✓ Coverage maintained or improved
4. ✓ Implementation matches specification
5. ✓ Traceability references included
6. ✓ Task completed within time estimate
```

---

## PROGRESSIVE ENHANCEMENT PATTERN

### Build Features Incrementally
```markdown
## Day 1: Minimal Implementation [TEST→CODE→DEPLOY]
TASK-001: Basic functionality (1-3 hours)
- [ ] Write failing test
- [ ] Implement minimal code
- [ ] Local tests pass
- [ ] Deploy to staging

## Day 2: Add Validation [TEST→CODE→DEPLOY]
TASK-002: Input validation (1-3 hours)
- [ ] Write validation tests
- [ ] Add validation logic
- [ ] Local tests pass
- [ ] Deploy to staging

## Day 3: Add Error Handling [TEST→CODE→DEPLOY]
TASK-003: Comprehensive errors (1-3 hours)
- [ ] Write error case tests
- [ ] Implement error handling
- [ ] Local tests pass
- [ ] Deploy to staging

## Day 4: Performance Optimization [TEST→CODE→DEPLOY]
TASK-004: Optimize queries (1-3 hours)
- [ ] Write performance tests
- [ ] Optimize implementation
- [ ] Local tests pass
- [ ] Deploy to production
```

---

## ANTI-PATTERNS TO REJECT

### ❌ REJECT: Code Without Tests
```python
# If code is submitted without tests:
"ERROR: No tests found. Write tests first, then implementation."
```

### ❌ REJECT: Tests After Code
```python
# If implementation exists before tests:
"ERROR: Implementation found before tests. Delete code, write tests first."
```

### ❌ REJECT: Untested Commits
```bash
# If attempting to commit without running tests:
"ERROR: Run tests locally first: pytest tests/"
```

### ❌ REJECT: Missing Specifications
```python
# If no specification exists:
"ERROR: Create specification in specs/ before implementation"
```

### ❌ REJECT: Broken Traceability
```python
# If tests don't reference specs:
"ERROR: Test missing specification reference"

# If specs don't reference tests:
"ERROR: Specification missing test references"
```

### ❌ REJECT: Oversized Tasks
```python
# If task > 8 hours:
"ERROR: Break into smaller tasks (ideally 1-3 hours, max 4-8)"

# If task has dependencies:
"ERROR: Make task atomic and independent"
```

### ❌ REJECT: Vague Acceptance Criteria
```python
# If criteria like "it should work":
"ERROR: Acceptance criteria must be specific and testable"
```

---

## FILE STRUCTURE ENFORCEMENT

### Required Structure:
```
project/
├── specs/                      # Specifications (source of truth)
│   ├── feature-001.md         # With unique IDs and criteria
│   └── traceability.md        # Spec-test-code mapping
├── tests/                     # Tests (written first)
│   ├── unit/                 # Unit tests with spec refs
│   ├── integration/          # Integration tests
│   └── features/            # Behavior tests
├── src/                      # Implementation (written last)
│   └── feature.py           # With traceability comments
├── docs/
│   └── task-breakdown.md    # Atomic task definitions
└── run_tests.sh             # Local test runner (identical to CI)
```

### File Creation Order:
1. `specs/feature-001.md` - Specification with IDs and criteria
2. `docs/task-breakdown.md` - Atomic tasks (1-3 hours each)
3. `tests/test_feature.py` - Failing tests with spec references
4. `src/feature.py` - Implementation to pass tests

---

## QUICK REFERENCE COMMANDS

### Before Starting Work:
```bash
# Pull latest and run tests
git pull
pytest tests/  # Must pass before starting
./check_traceability.sh  # Verify all links valid
```

### Creating New Feature:
```bash
# 1. Write specification
vim specs/feature-001.md

# 2. Generate task breakdown
python generate_tasks.py specs/feature-001.md

# 3. Write first test
vim tests/test_feature.py
# Add: """Implements: specs/feature-001.md#AC-001"""

# 4. Verify test fails
pytest tests/test_feature.py  # Should fail

# 5. Implement feature
vim src/feature.py
# Add: # Implements: FEAT-001-TASK-001

# 6. Verify test passes
pytest tests/test_feature.py  # Should pass

# 7. Check coverage and traceability
pytest tests/ --cov=src --cov-fail-under=80
./check_traceability.sh
```

### Before Committing:
```bash
# Full validation
pytest tests/ --cov=src --cov-fail-under=80
behave tests/features  # If behavior tests exist
./check_traceability.sh  # Verify all references
```

### Before Pushing:
```bash
# Final check (same as CI)
./run_tests.sh
git push
```

---

## METRICS TO TRACK

Monitor these on every change:

```python
metrics = {
    "tests_written_first": True,  # MUST be True
    "local_tests_passed": True,   # MUST be True before push
    "coverage": ">=80%",          # MUST maintain or improve
    "ci_pipeline": "green",       # MUST pass before merge
    "spec_coverage": "100%",      # Every spec has tests
    "task_size_hours": "<=8",     # Ideally 1-3, max 4-8
    "traceability_complete": True,  # All references valid
}
```

---

## CONSTITUTION (NON-NEGOTIABLE)

1. **Tests define correctness** - If tests pass, implementation is correct
2. **Specifications are contracts** - Implementation must match spec exactly
3. **Local = CI** - Tests must behave identically locally and in CI
4. **No test, no merge** - Untested code is broken code
5. **Tests first, always** - Implementation follows tests, never leads
6. **Tasks are atomic** - Every task completable independently
7. **Everything is traceable** - Spec→Test→Code links maintained

---

## ENFORCEMENT HOOKS

### Pre-commit Hook:
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running pre-commit checks..."

# Check for tests
for file in $(git diff --cached --name-only | grep "^src/"); do
    test_file="tests/test_$(basename $file)"
    if [ ! -f "$test_file" ]; then
        echo "❌ Missing test for $file"
        exit 1
    fi
done

# Run tests
pytest tests/ --quiet --exitfirst || {
    echo "❌ Tests failed - commit blocked"
    echo "Run: pytest tests/ to see failures"
    exit 1
}

# Check traceability
./check_traceability.sh || {
    echo "❌ Traceability broken - fix references"
    exit 1
}

echo "✓ All checks passed"
```

### Pre-push Hook:
```bash
#!/bin/bash
# .git/hooks/pre-push

./run_tests.sh || {
    echo "❌ Full test suite failed - push blocked"
    exit 1
}

# Verify task size
for task in $(git diff origin/main --name-only | grep "tasks/"); do
    hours=$(grep "estimated_hours:" $task | awk '{print $2}')
    if [ $hours -gt 8 ]; then
        echo "❌ Task exceeds 8 hours: $task"
        exit 1
    fi
done
```

---

## FOR CLAUDE CODE / AI ASSISTANTS

When reviewing changes or implementing features:

### 1. FIRST: Check Specification
```python
if not specification_exists(feature):
    REJECT("Create specification first in specs/")
    
if not has_unique_id(specification):
    REJECT("Add unique feature ID to specification")
```

### 2. SECOND: Verify Tests Exist
```python
if not tests_written_first(feature):
    REJECT("Write tests before implementation")
    
if not test_references_spec(test):
    REJECT("Add specification reference to test")
```

### 3. THIRD: Validate Task Size
```python
if task_hours > 8:
    REJECT("Break into smaller tasks (ideally 1-3 hours)")
    
if task_has_dependencies:
    REJECT("Make task atomic - no dependencies")
```

### 4. FOURTH: Check Traceability
```python
if not spec_has_test_references:
    REJECT("Add test references to specification")
    
if not code_has_spec_references:
    REJECT("Add specification references to code")
```

### 5. FIFTH: Ensure Tests Pass
```python
if not all_tests_passing_locally:
    REJECT("Fix failing tests before commit")
    
if coverage_decreased:
    REJECT("Maintain or improve test coverage")
```

If ANY of these checks fail, STOP and report the issue.

---

## REVIEW CHECKLIST

Before approving any change:

### Specifications
- [ ] Specification exists with unique ID
- [ ] Acceptance criteria are specific and testable
- [ ] Test scenarios documented
- [ ] Task breakdown complete

### Tests
- [ ] Tests written before implementation
- [ ] Tests reference specifications
- [ ] Tests pass locally
- [ ] Coverage >= 80%

### Tasks
- [ ] Tasks sized 1-3 hours (max 4-8)
- [ ] Tasks are atomic (no dependencies)
- [ ] Clear completion criteria

### Traceability
- [ ] Spec → Test references valid
- [ ] Test → Spec references valid
- [ ] Code → Spec references valid
- [ ] Traceability matrix updated

### Quality
- [ ] All tests passing in CI
- [ ] No decrease in coverage
- [ ] Documentation updated
- [ ] Progressive enhancement followed

**Remember: The test IS the specification. The specification IS the test. Write tests first, implement second, deploy third.**