# Test Promotion Threat Model

## Attack Vectors and Mitigations

### Attack Vector 1: AI Weakens Test Assertions

**Threat**: AI generates buggy code, then weakens test to make it pass (self-grading student).

```python
# AI writes buggy code
def process_payment(id, amount):
    return {"status": "success"}  # BUG: No idempotency check

# AI weakens test to pass
def test_payment_idempotency():
    process_payment("123", 100)
    process_payment("123", 100)  # Missing duplicate check!
```

**Mitigation**: Golden tests are immutable - AI cannot modify them.
**Enforcement**: CI/CD detects changes, CODEOWNERS requires approval.

---

### Attack Vector 2: AI Uses Edit/Write Tools on Golden Tests

**Threat**: AI attempts to modify golden test directly using Edit or Write tools.

```python
# AI tries:
# Edit(file="tests/golden/test_payment.py", ...)
```

**Mitigation**: AI hooks block Edit/Write tools on `tests/golden/**` paths.
**Enforcement**: `.ai/hooks/protect-golden.sh` returns exit code 2 (BLOCK).
**Reliability**: ✅ High (blocks tool before execution)

---

### Attack Vector 3: AI Bypasses Permissions via Bash

**Threat**: AI uses Bash to bypass file permissions, modifies golden test, restores permissions.

```bash
# AI could run:
chmod 644 tests/golden/test_payment.py
echo "# weakened" >> tests/golden/test_payment.py
chmod 444 tests/golden/test_payment.py
```

**Why File Permissions Alone Fail**: AI with bash access can change permissions.

**Mitigation**: CI/CD detects **ANY** modification via git diff.
**Enforcement**: `.github/workflows/test-protection.yml` checks:
```yaml
git diff --name-only | grep '^tests/golden/' && exit 1
```
**Reliability**: ✅ High (catches all git changes regardless of method)

---

### Attack Vector 4: AI Commits Modified Golden Tests

**Threat**: AI successfully modifies and commits golden test changes.

**Mitigation**: CODEOWNERS requires human approval before merge.
**Enforcement**: `.github/CODEOWNERS`:
```
tests/golden/**  @tech-leads @qa-leads
```
**Reliability**: ✅ Very High (human gate cannot be automated away)

---

### Attack Vector 5: AI Deletes Golden Tests

**Threat**: AI deletes golden test file to remove failing assertions.

```bash
rm tests/golden/test_payment.py
```

**Mitigation**: CI/CD detects deletion in git diff, CODEOWNERS requires approval.
**Enforcement**: Same as modification (git diff + CODEOWNERS).
**Reliability**: ✅ High

---

## Defense Layers Summary

| Layer | Purpose | Blocks | Reliability | Can Be Bypassed? |
|-------|---------|--------|-------------|------------------|
| 1. File Permissions (444) | Prevent accidental edits | Direct file writes | Medium | ✅ Yes (chmod) |
| 2. AI Hooks | Block Edit/Write tools | Tool-based edits | Medium | ✅ Yes (Bash) |
| 3. CI/CD Git Diff | Detect all modifications | Any git change | **High** | ❌ No |
| 4. CODEOWNERS | Human approval gate | Merge to main | **Very High** | ❌ No |

## Primary vs. Defense-in-Depth

**Primary Enforcement** (Cannot be bypassed):
- ✅ **CI/CD git diff detection** - Catches all changes
- ✅ **CODEOWNERS approval** - Human gate

**Defense-in-Depth** (Reduces attack surface):
- File permissions (444) - Prevents accidents
- AI hooks - Makes intent explicit

## What If AI Becomes More Sophisticated?

**Scenario**: AI learns to hide changes from git diff.

**Answer**: Not possible. Git diff operates at filesystem level, comparing tree objects. AI cannot modify git's internal state without access to `.git/` directory, which should be blocked by repository permissions.

**Scenario**: AI social engineers human approvers.

**Answer**: Out of scope for technical controls. This is a human process issue requiring:
- Review checklist enforcement
- Multiple approvers (2+ required)
- Separation of duties (AI cannot approve own PRs)

## Security Principle

The pattern follows **defense-in-depth**:
- Multiple independent layers
- Failure of one layer doesn't compromise security
- Primary enforcement (CI/CD + CODEOWNERS) is robust
- Permissions and hooks make attacks explicit and detectable

## Recommended Configuration

```bash
# Minimum viable protection
✅ CI/CD git diff check (required)
✅ CODEOWNERS approval (required)

# Defense-in-depth
✅ File permissions 444 (recommended)
✅ AI hooks (recommended)
✅ Branch protection rules (recommended)
```

## Monitoring and Alerts

Track attempted bypasses:
```yaml
# Alert on promotion workflow usage
- name: Track Test Promotions
  if: contains(github.event.pull_request.labels.*.name, 'test-promotion')
  run: |
    echo "Test promotion attempted by: ${{ github.actor }}"
    # Send to monitoring system
```

## Testing the Threat Model

Verify enforcement by attempting each attack vector:

```bash
# Test 1: Try to edit golden test directly
echo "test" >> tests/golden/test_payment.py
# Expected: Permission denied (444)

# Test 2: Try to use chmod bypass
chmod 644 tests/golden/test_payment.py && echo "test" >> tests/golden/test_payment.py
git add tests/golden/test_payment.py
git push
# Expected: CI blocks PR

# Test 3: Try to merge without approval
# Create PR with golden test changes
# Expected: CODEOWNERS blocks merge
```

All attack vectors should be blocked by at least one enforcement layer.
