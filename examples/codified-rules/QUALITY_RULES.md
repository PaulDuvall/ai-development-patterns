# QUALITY_RULES - Code Quality & AI Standards Enforcement

**CRITICAL: Review these patterns before EVERY code change. Reject code that violates these quality standards.**

## IMMEDIATE SMELL DETECTION

### On Every Code Change, Check For:
```python
def validate_code_change(file_path, content):
    """Run these checks on EVERY modified file."""
    
    CHECK: Method length > 20 lines?
        → REJECT: "Extract method - function exceeds 20 lines"
    
    CHECK: Class > 250 lines OR > 20 methods?
        → REJECT: "Extract class - violates Single Responsibility"
    
    CHECK: Cyclomatic complexity > 10?
        → REJECT: "Simplify logic - complexity too high"
    
    CHECK: Hardcoded values (URLs, ports, paths)?
        → REJECT: "Externalize configuration"
    
    CHECK: Missing error handling on external calls?
        → REJECT: "Add try/except for external operations"
    
    CHECK: Global variables or mutable module state?
        → REJECT: "Encapsulate state in classes"
    
    CHECK: Missing structured logging?
        → REJECT: "Use JSON logging with correlation IDs"
    
    CHECK: Task exceeds 8 hours?
        → REJECT: "Break down into smaller tasks (ideally 1-3 hours, max 4-8 hours)"
    
    CHECK: AI component without interface contract?
        → REJECT: "Define interface contract for AI integration"
```

---

## AI DEVELOPMENT STANDARDS

### Rules as Code
```bash
# AUTOMATED CHECK:
[ ! -d ".ai" ] && echo "MISSING: .ai/ configuration directory"
[ ! -f ".ai/standards.yaml" ] && echo "MISSING: AI coding standards"

REJECT IF:
- No .ai/ configuration directory
- AI prompts scattered in code comments
- Inconsistent AI tool configurations

REQUIRE:
.ai/
├── standards.yaml      # AI coding standards
├── prompts/           # Versioned prompt templates
├── tools.yaml         # Tool configurations
└── validation.yaml    # AI output validation rules
```

**FIX COMMAND:**
```yaml
# .ai/standards.yaml
ai_standards:
  model_selection:
    simple_queries: "gpt-3.5-turbo"  # <500 tokens
    complex_analysis: "gpt-4"        # >2000 tokens
  
  validation:
    require_tests: true
    min_coverage: 80
    security_scan: true
  
  prompts:
    temperature: 0.7
    max_tokens: 2000
    system_prompt: "You are a senior developer following SOLID principles"
```

### Contract-First AI Integration
```python
# REJECT: AI component without contract
class AIService:  # ❌
    def process(self, data):
        result = ai_model.generate(data)
        return result

# REQUIRE: Defined interfaces and contracts
from abc import ABC, abstractmethod
from typing import Protocol, TypedDict

class AIRequest(TypedDict):  # ✓
    prompt: str
    max_tokens: int
    temperature: float

class AIResponse(TypedDict):  # ✓
    content: str
    confidence: float
    model_version: str
    alternative_responses: List[str]

class AIServiceContract(Protocol):  # ✓
    """Contract for AI service integration."""
    
    def validate_input(self, request: AIRequest) -> bool:
        """Pre-condition: Validate request format."""
        
    def process(self, request: AIRequest) -> AIResponse:
        """Post-condition: Returns response with confidence score."""
        
    def handle_failure(self, error: Exception) -> AIResponse:
        """Invariant: Always return valid response or fallback."""
```

---

## SOLID PRINCIPLES ENFORCEMENT

### Single Responsibility Violation
```bash
# AUTOMATED CHECK:
grep -c "def " class_file.py  # >10 methods = possible SRP violation
grep -c "and\|or" class_docstring  # Multiple "and/or" = multiple responsibilities

REJECT IF:
- Class description contains multiple "and" statements
- Class has unrelated method groups (e.g., data + network + UI)
- Class name contains "Manager", "Handler", "Processor" (too generic)
```

**FIX COMMAND:**
```python
# REJECT: Multiple responsibilities
class EmailDigestManager:  # ❌
    def fetch_feeds(self): ...
    def send_emails(self): ...
    def generate_reports(self): ...
    def authenticate_users(self): ...

# REQUIRE: Single responsibility
class FeedFetcher: ...  # ✓
class EmailSender: ...  # ✓
class ReportGenerator: ...  # ✓
```

### Open/Closed Principle
```python
# REJECT: Modification required for extension
def process_payment(payment_type, amount):  # ❌
    if payment_type == "credit":
        # credit card logic
    elif payment_type == "paypal":
        # paypal logic
    # Adding new payment = modifying function

# REQUIRE: Open for extension, closed for modification
class PaymentProcessor(ABC):  # ✓
    @abstractmethod
    def process(self, amount: float): ...

class CreditCardProcessor(PaymentProcessor): ...
class PayPalProcessor(PaymentProcessor): ...
# Adding new payment = new class, no modification
```

### Dependency Inversion
```python
# REJECT: Direct dependency on concrete class
class EmailService:  # ❌
    def __init__(self):
        self.smtp = SmtpClient()  # Concrete dependency

# REQUIRE: Depend on abstractions
class EmailService:  # ✓
    def __init__(self, email_client: EmailClientProtocol):
        self.client = email_client  # Abstract dependency
```

---

## OBSERVABILITY STANDARDS

### Structured Logging Requirements
```bash
# AUTOMATED CHECK:
grep -r "print(" . --include="*.py"  # No print statements
grep -r "logger\." . | grep -v "correlation_id"  # Missing correlation ID

REJECT IF:
- Using print() instead of logger
- Log messages without structure
- Missing correlation IDs
- No operation context
```

**FIX COMMAND:**
```python
# REJECT: Unstructured logging
logger.info("Processing item")  # ❌
logger.error(f"Failed: {error}")  # ❌
print(f"Debug: {value}")  # ❌

# REQUIRE: Structured JSON logging
logger.info({  # ✓
    "event": "item_processing",
    "correlation_id": request.correlation_id,
    "item_id": item.id,
    "timestamp": datetime.utcnow().isoformat(),
    "context": {
        "user_id": user.id,
        "session_id": session.id
    }
})

logger.error({  # ✓
    "event": "processing_failed",
    "correlation_id": request.correlation_id,
    "error_code": "PROC_001",
    "error_message": str(error),
    "error_type": error.__class__.__name__,
    "stack_trace": traceback.format_exc(),
    "remediation": "Retry with exponential backoff",
    "affected_component": "EmailProcessor",
    "severity": "high"
})
```

### Transparent Error Messages
```python
# REJECT: Vague error handling
except Exception:  # ❌
    return {"error": "Something went wrong"}

# REQUIRE: Contextual error information
except ValidationError as e:  # ✓
    return {
        "error_code": "VAL_001",
        "error_message": "Input validation failed",
        "details": str(e),
        "affected_fields": e.fields,
        "remediation": "Check field formats against API documentation",
        "documentation_url": "/api/docs#validation"
    }
```

---

## TASK DECOMPOSITION

### Atomic Task Requirements
```yaml
# REJECT: Tasks with dependencies
task_1:
  description: "Create user and send email"  # ❌ Two responsibilities
  depends_on: ["task_2"]  # ❌ Cross-dependency

# REQUIRE: Independent atomic tasks
task_1:  # ✓
  id: "USR-001"
  description: "Create user record"
  max_hours: 3  # Ideally 1-3 hours
  acceptance_criteria:
    - "User saved to database"
    - "Returns user ID"
  no_dependencies: true

task_2:  # ✓
  id: "EML-001"  
  description: "Send welcome email"
  max_hours: 2  # Ideally 1-3 hours
  acceptance_criteria:
    - "Email queued successfully"
    - "Retry on failure"
  no_dependencies: true
```

---

## BLOATER VIOLATIONS

### Long Method Detection
```bash
# AUTOMATED CHECKS:
radon cc -nc file.py | grep -E "C |D |E |F "  # Complexity > 10
flake8 file.py --select=C901  # Complex function
grep -c "def\|if\|for\|while\|try" method  # > 20 control structures

REJECT IF:
- Method > 20 lines (excluding docstring)
- Cyclomatic complexity > 10
- More than 5 control flow statements
- Multiple responsibilities in one function
```

### Large Class Detection
```bash
# AUTOMATED CHECKS:
wc -l class_file.py  # > 250 lines
grep -c "def " class_file.py  # > 20 methods
grep -c "self\." __init__  # > 10 attributes

REJECT IF:
- Class > 250 lines
- More than 20 methods
- More than 10 instance variables
- Mixed responsibilities
```

---

## PRIMITIVE OBSESSION VIOLATIONS

### Detection Pattern:
```bash
# Find primitive obsession:
grep -r "split(','" .  # String parsing
grep -r "if.*==['\"]" .  # String type codes
grep -r "dict\[" . | grep -v "Dict\["  # Dict abuse

REJECT IF:
- Email addresses as strings without validation class
- URLs as strings without URL class
- Comma-separated strings instead of lists
- Dictionaries used as pseudo-objects
```

---

## ERROR HANDLING VIOLATIONS

### Detection Pattern:
```bash
# Find missing error handling:
grep -r "requests\." . | grep -v "try:"
grep -r "open(" . | grep -v "with"
grep -r "json\.loads" . | grep -v "try:"
grep -r "\.get(" . | grep -v "if.*is not None"

REJECT IF:
- Network calls without try/except
- File operations without context managers
- JSON parsing without error handling
- Missing None checks after .get()
- No timeout on external calls
- AI API calls without retry logic
```

---

## CONFIGURATION VIOLATIONS

### Detection Pattern:
```bash
# Find hardcoded values:
grep -r "http://" . --include="*.py"
grep -r "https://" . --include="*.py"
grep -r ":[0-9]\{4\}" . --include="*.py"  # Ports
grep -r "sk-[a-zA-Z0-9]" . --include="*.py"  # API keys

REJECT IF:
- Hardcoded URLs/endpoints
- Hardcoded ports or timeouts
- Hardcoded file paths
- API keys/secrets in code (CRITICAL)
- Model names hardcoded (use config)
```

---

## STATE MANAGEMENT VIOLATIONS

### Detection Pattern:
```bash
# Find global state:
grep -r "^[A-Z_]*\s*=.*\[\]" . --include="*.py"  # Global lists
grep -r "^[A-Z_]*\s*=.*{}" . --include="*.py"  # Global dicts
grep -r "global " . --include="*.py"

REJECT IF:
- Global mutable variables
- Module-level state containers
- Singleton abuse
- Hidden state dependencies
- Shared state between AI agents
```

---

## TESTING VIOLATIONS

### Detection Pattern:
```bash
# Find untested complex logic:
radon cc -nc . | grep -E "C |D |E |F " | while read f; do
    test_file="test_$(basename $f)"
    [ ! -f "$test_file" ] && echo "MISSING TEST: $f"
done

REJECT IF:
- Complex function (CC > 5) without tests
- Business logic without tests
- AI integration without mocks
- Coverage < 80% for critical modules
- No test for error paths
```

---

## AI-SPECIFIC ANTI-PATTERNS

### No Black Box Systems
```python
# REJECT: Minimal observability
def ai_process(data):  # ❌
    result = model.generate(data)
    return result

# REQUIRE: Full observability
def ai_process(data):  # ✓
    logger.info({
        "event": "ai_processing_start",
        "model": model.name,
        "input_size": len(data),
        "correlation_id": context.correlation_id
    })
    
    try:
        result = model.generate(data)
        
        logger.info({
            "event": "ai_processing_complete",
            "confidence": result.confidence,
            "tokens_used": result.token_count,
            "latency_ms": result.latency,
            "correlation_id": context.correlation_id
        })
        
        return result
    except Exception as e:
        logger.error({
            "event": "ai_processing_failed",
            "error": str(e),
            "fallback": "Using rule-based approach",
            "correlation_id": context.correlation_id
        })
        raise
```

### No AI Without Contracts
```python
# REJECT: AI without interface
ai_result = some_model.predict(data)  # ❌ No contract

# REQUIRE: Explicit contracts
class AIModelContract(Protocol):
    def predict(self, data: InputSchema) -> OutputSchema: ...
    def get_confidence(self) -> float: ...
    def get_alternatives(self) -> List[OutputSchema]: ...
    def validate_input(self, data: Any) -> bool: ...
```

---

## AUTOMATED ENFORCEMENT

### Pre-Commit Hook:
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Checking code quality..."

# AI standards check
[ ! -d ".ai" ] && echo "❌ Missing .ai/ configuration" && exit 1

# Complexity check
radon cc -nc . | grep -E "C |D |E |F " && {
    echo "❌ Complexity too high"
    exit 1
}

# SOLID principles check
./scripts/check_solid_principles.py || exit 1

# Logging standards
grep -r "print(" . --include="*.py" && {
    echo "❌ Use logger instead of print()"
    exit 1
}

# Configuration check
grep -r "https://" . --include="*.py" | grep -v "^#" && {
    echo "❌ Hardcoded URLs found"
    exit 1
}

echo "✓ Code quality checks passed"
```

### Quick Fix Commands:
```bash
# Auto-format
black . && isort .

# Find complexity issues
radon cc -nc . | sort -t: -k2 -n -r | head -20

# Find missing tests
coverage run -m pytest && coverage report --skip-empty --sort=cover

# Check SOLID violations
pylint . --disable=all --enable=R0901,R0902,R0903,R0904

# Find missing contracts
grep -r "class.*AI" . --include="*.py" | xargs grep -L "Protocol\|Contract\|ABC"
```

---

## FOR CLAUDE CODE / AI ASSISTANTS

When reviewing code changes:

### 1. VERIFY AI STANDARDS
```python
if not exists(".ai/standards.yaml"):
    REJECT("Create .ai/standards.yaml with AI coding standards")

if ai_component_without_contract:
    REJECT("Define interface contract for AI component")
```

### 2. CHECK SOLID PRINCIPLES
```python
if class_has_multiple_responsibilities:
    REJECT("Split class - violates Single Responsibility")
    
if requires_modification_for_extension:
    REJECT("Violates Open/Closed Principle")
```

### 3. ENFORCE OBSERVABILITY
```python
if not structured_logging_with_correlation_id:
    REJECT("Use JSON logging with correlation IDs")
    
if error_without_context:
    REJECT("Add error code, remediation, and context")
```

### 4. VALIDATE TASK SIZE
```python
if task_estimate > 8_hours:
    REJECT("Break into smaller tasks (ideally 1-3 hours, max 4-8 hours)")
    
if task_has_dependencies:
    REJECT("Make task atomic and independent")
```

### 5. SCAN ALL ORIGINAL VIOLATIONS
```python
# All original checks still apply:
if method_lines > 20 or complexity > 10:
    REJECT("Extract method - too complex")
    
if external_call_without_try_except:
    REJECT("Add error handling for external operations")
```

---

## REVIEW CHECKLIST

Before approving ANY change:

### Structure & Design
- [ ] All methods < 20 lines
- [ ] All classes < 250 lines  
- [ ] Cyclomatic complexity < 10
- [ ] SOLID principles followed
- [ ] Tasks sized ideally 1-3 hours, max 4-8 hours

### AI Integration
- [ ] .ai/standards.yaml exists
- [ ] AI components have contracts
- [ ] AI calls have retry logic
- [ ] Model selection justified

### Quality & Safety
- [ ] No hardcoded configuration
- [ ] Error handling for external calls
- [ ] No global mutable state
- [ ] Structured JSON logging
- [ ] Correlation IDs present

### Testing
- [ ] Tests for complex logic
- [ ] AI integrations mocked
- [ ] Coverage > 80%
- [ ] Error paths tested

**Remember: Code without contracts is chaos. Systems without observability are black boxes. If you can't test it easily, refactor it.**