# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Subscription Alerts is a lightweight application that monitors recurring subscription charges and sends timely email reminders. It reads subscription data from Google Sheets, calculates upcoming charge dates, and notifies users 7 days in advance, with special emphasis on quarterly and annual payments.

## Core Philosophy
Build a simple, reliable subscription reminder system that helps users avoid unexpected charges while maintaining minimal infrastructure requirements.

### Key Principles:
1. **Simplicity First**: Use existing Google services (Sheets, Gmail) to minimize complexity
2. **User-Focused**: Provide clear, actionable reminders that prevent surprise charges
3. **Reliability**: Ensure no reminder is missed through robust error handling
4. **Privacy-Conscious**: Handle financial data securely with minimal data retention
5. **Documentation-Driven**: Maintain clear specifications with traceability markers

---

## 🚨 MANDATORY RULE ENFORCEMENT

**CRITICAL: Before ANY code change, review and enforce ALL three rule files:**

### 1. DEVELOPMENT_RULES.md - Test-First Specification-Driven Development
- **NEVER** write implementation before tests
- **ALWAYS** create specifications with unique IDs (SPEC-XXX)
- **ENFORCE** task sizing: ideally 1-3 hours, max 4-8 hours
- **MAINTAIN** complete traceability: Spec → Test → Code
- **RUN** all tests locally before committing

### 2. QUALITY_RULES.md - Code Quality & Standards
- **REJECT** methods > 20 lines, classes > 250 lines
- **ENFORCE** SOLID principles and clean architecture
- **REQUIRE** structured JSON logging with correlation IDs
- **VALIDATE** all AI-generated code
- **MAINTAIN** .ai/ configuration directory with standards

### 3. DELIVERY_RULES.md - CI/CD Pipeline & Deployment
- **ENFORCE** branch age < 2 days
- **REQUIRE** build time < 10 minutes
- **VALIDATE** all AI output through security gates
- **COMPLETE** Operational Readiness Review (ORR) before deploy
- **MAINTAIN** infrastructure specifications before IaC

**If ANY rule violation is detected, STOP and report the issue immediately.**

---

## Development Requirements

### Security & Privacy (Financial Data)
**CRITICAL**: This application handles sensitive financial information:
- ✅ **Secure API key management** using environment variables
- ✅ **Minimal data storage** (read-only from Google Sheets)
- ✅ **Email-only notifications** (no data persistence)
- ✅ **Comprehensive error logging** without exposing sensitive data
- ❌ **Never log** payment amounts or personal information
- ❌ **Never store** credentials in code or configuration files

### Specification Standards
Per DEVELOPMENT_RULES.md requirements:
1. **Unique IDs**: Every requirement has ID (SPEC-XXX, AC-XXX, TEST-XXX)
2. **Traceability**: Complete mapping from spec → test → implementation
3. **Test-First**: Write failing tests before any implementation
4. **Atomic Tasks**: Break work into 1-3 hour chunks
5. **Progressive Enhancement**: Deploy incrementally, not all at once

### Quality Standards
Per QUALITY_RULES.md requirements:
1. **Method Complexity**: Max 20 lines, cyclomatic complexity < 10
2. **Class Size**: Max 250 lines, < 20 methods
3. **Observability**: Structured JSON logging required:
   ```python
   logger.info({
       "event": "subscription_processed",
       "correlation_id": request_id,
       "subscription_id": sub.id,
       "days_until_charge": days,
       "notification_sent": True
   })
   ```
4. **Error Context**: All errors must include remediation:
   ```python
   {
       "error_code": "GSHEET_001",
       "error_message": "Failed to connect to Google Sheets",
       "remediation": "Check service account credentials",
       "documentation": "/docs/troubleshooting.md#gsheet-errors"
   }
   ```

### Pipeline Requirements
Per DELIVERY_RULES.md requirements:
1. **Version Control**: All configs, specs, and IaC in Git
2. **Testing Pyramid**: 70% unit, 20% integration, 10% E2E
3. **Deployment Safety**: Feature flags for gradual rollout
4. **Monitoring**: Health endpoints required:
   - `/health` - Service status
   - `/metrics` - Performance metrics
   - `/ready` - Readiness probe

---

## Working with Claude Code

### Workflow for New Features

1. **CREATE SPECIFICATION** (DEVELOPMENT_RULES.md)
   ```markdown
   # specs/feature-xxx.md
   Feature ID: FEAT-XXX
   Acceptance Criteria:
   - AC-001: Specific testable requirement
   Test Scenarios:
   - TEST-001: Links to test file
   ```

2. **WRITE TESTS FIRST** (DEVELOPMENT_RULES.md)
   ```python
   def test_subscription_reminder():
       """
       Implements: specs/reminders.md#AC-001
       Feature: FEAT-001
       """
       assert reminder_sent() == True
   ```

3. **IMPLEMENT TO PASS TESTS** (QUALITY_RULES.md)
   - Keep methods < 20 lines
   - Follow SOLID principles
   - Include traceability comments

4. **VALIDATE LOCALLY** (DELIVERY_RULES.md)
   ```bash
   pytest tests/ --cov=src --cov-fail-under=90
   ./check_traceability.sh
   pre-commit run --all-files
   ```

5. **DEPLOY SAFELY** (DELIVERY_RULES.md)
   - Complete ORR checklist
   - Use feature flags
   - Monitor rollout

### Project-Specific Requirements

#### Google API Integration
- **OAuth2**: Use service account credentials
- **Rate Limiting**: Implement exponential backoff
- **Quotas**: Stay within Google API limits
- **Mocking**: Use mock APIs in tests, never real services

#### Data Processing
- **Batch Size**: Process max 100 subscriptions per run
- **Performance**: Complete processing in < 10 seconds
- **Validation**: Verify all dates, amounts, emails
- **Deduplication**: Prevent duplicate reminders

#### Email Notifications
- **Template**: Clear subject line with charge date
- **Content**: Include subscription name, amount, action link
- **Frequency**: One reminder 7 days before charge
- **Tracking**: Log sends without storing email content

---

## Progress Tracking

Maintain PROGRESS.md file throughout development:

**After each task completion:**
1. Update task status from "Current" to "Completed"
2. Record commit hash and actual time spent
3. Update code metrics (SLOC, coverage, complexity)
4. Set next task as "Current Task"
5. Update progress percentages
6. Log all human prompts from current session (avoid duplicates)
7. Commit PROGRESS.md with the task code

**File location:** `/PROGRESS.md` (project root)

**Update frequency:** After every completed task, before git commit

**Purpose:**
- Enables context reconstruction in new sessions
- Provides stakeholder visibility
- Tracks estimates vs actuals
- Documents quality metrics over time
- Records complete interaction history for continuity

**Session Logging:**
- Log every human prompt/request from the current session
- Include task context and decisions made
- Ensure no duplicate entries (check before adding)
- Maintain chronological order
- Helps AI reconstruct conversation context in future sessions

---

## File Structure Requirements

```
subscription-alerts/
├── specs/                          # Specifications (FEAT-XXX)
│   ├── subscription-alerts-specs.md
│   └── traceability.md
├── tests/                          # Test-first development
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── src/                           # Implementation
│   ├── models/
│   ├── services/
│   └── api/
├── .ai/                           # AI configuration
│   ├── standards.yaml
│   └── prompts/
├── infrastructure/                # IaC with specs
│   ├── specs/
│   └── terraform/
├── docs/
│   ├── DEVELOPMENT_RULES.md      # Test-first practices
│   ├── QUALITY_RULES.md          # Code standards
│   └── DELIVERY_RULES.md         # CI/CD requirements
└── run_tests.sh                   # Local = CI
```

---

## Testing Requirements

### Coverage Standards
Per DEVELOPMENT_RULES.md:
- **Specification Coverage**: 100% - Every SPEC-XXX has tests
- **Code Coverage**: 90% minimum
- **Test Execution**: All tests must pass before next task
- **Traceability**: Every test references its specification

### Test Categories
1. **Unit Tests** (70%)
   - Test individual functions
   - Mock external dependencies
   - Run in < 2 seconds total

2. **Integration Tests** (20%)
   - Test Google Sheets reading
   - Test Gmail sending (mocked)
   - Verify data flow

3. **E2E Tests** (10%)
   - Full workflow simulation
   - Performance validation
   - Error recovery scenarios

---

## Security Checklist

Before ANY commit involving sensitive data:

- [ ] API keys in environment variables only
- [ ] No credentials in code or configs
- [ ] No payment amounts in logs
- [ ] Input validation implemented
- [ ] Rate limiting configured
- [ ] Error messages sanitized
- [ ] Security scan passed
- [ ] Secrets scan passed

---

## Quick Reference Commands

```bash
# Before starting work
./check_rules.sh  # Validates all three rule files

# Development workflow
pytest tests/ --cov=src --cov-fail-under=90
./check_traceability.sh
black . && isort . && flake8 .

# Before commit
pre-commit run --all-files
./run_tests.sh

# Before deployment
./run_orr_checklist.sh
./validate_deployment.sh
```

---

## AI Assistant Instructions

When reviewing or implementing code:

1. **FIRST**: Check DEVELOPMENT_RULES.md
   - Specification exists?
   - Tests written first?
   - Task < 8 hours?

2. **SECOND**: Check QUALITY_RULES.md
   - Methods < 20 lines?
   - SOLID principles followed?
   - Logging structured?

3. **THIRD**: Check DELIVERY_RULES.md
   - Branch < 2 days old?
   - Build < 10 minutes?
   - ORR complete?

If ANY check fails, STOP and report the violation.

---

## Remember

**The three rules are LAW:**
- DEVELOPMENT_RULES.md = How we write (test-first, traceable)
- QUALITY_RULES.md = What we write (clean, observable)
- DELIVERY_RULES.md = How we ship (safe, automated)

**Every code change must comply with ALL THREE rule files. No exceptions.**