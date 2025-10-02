# Scratchpad - Working Memory

Temporary notes for active exploration and debugging. Clear after task completion.

---

## Current Exploration

[What you're currently investigating or debugging]

### Hypothesis
[What you think might be the issue or solution]

### Evidence
- [Observation 1]
- [Observation 2]
- [Test result or metric]

### Next Steps
- [What to try next]
- [Question to answer]

---

## Quick Notes

[Unstructured observations, ideas, and snippets during active work]

- [Random observation]
- [Idea to explore]
- [Code snippet or command to remember]
- [Link to check later]

---

## Debug Log

```
[Timestamp] Tried: [what you attempted]
Result: [what happened]
Next: [what to try next]

[Timestamp] Tried: [another attempt]
Result: [outcome]
Conclusion: [learning or decision]
```

---

## Usage Guidelines

### When to Use scratchpad.md
- Active exploration and debugging within a single session
- Quick notes that don't yet warrant structured memory
- Hypothesis testing and experimental results
- Temporary reference information (snippets, commands, links)
- Stream-of-consciousness problem solving

### When to Clear scratchpad.md
- ✅ After task is completed
- ✅ After moving insights to NOTES.md or DECISIONS.log
- ✅ After extracting patterns to knowledge/
- ✅ At end of session if no longer relevant
- ❌ Don't clear if investigation spans multiple sessions (move to NOTES.md instead)

### Lifecycle of Information

```
scratchpad.md (active work)
  ↓ (if important)
NOTES.md (session discoveries)
  ↓ (if architectural)
DECISIONS.log (permanent decisions)
  ↓ (if reusable pattern)
knowledge/ (prompt patterns with success rates)
```

### Best Practices
- ✅ Write freely without worrying about structure
- ✅ Use timestamps for debug attempts
- ✅ Capture metrics and observations as you go
- ✅ Move important findings to NOTES.md before clearing
- ✅ Extract successful patterns to knowledge/ for reuse
- ❌ Don't let scratchpad accumulate indefinitely
- ❌ Don't skip extracting insights before clearing
- ❌ Don't use as permanent storage (promote to NOTES.md)

### Integration with Other Memory
- Promote discoveries to NOTES.md at end of session
- Extract architectural decisions to DECISIONS.log
- Link to TODO.md for tracking follow-up investigations
- Move successful prompts to knowledge/ patterns

### Example Usage

---

## Current Exploration

Investigating why JWT verification is failing intermittently (5% of requests).

### Hypothesis
Clock skew between auth server and API gateway causing `exp` claim to fail validation.

### Evidence
- Failures occur only on api-gateway-2 instance (not -1 or -3)
- `docker exec api-gateway-2 date` shows time is 47 seconds behind
- NTP sync is disabled in container config (found in docker-compose.yml)
- Added 60s clock skew tolerance → failures dropped to 0.1%

### Next Steps
- Enable NTP sync in container configuration
- Add monitoring for clock drift across instances
- Document decision about clock skew tolerance in DECISIONS.log

---

## Quick Notes

- JWT library: `jsonwebtoken` v9.0.2
- Test command: `wrk -t4 -c100 -d30s --latency http://api-gateway/health`
- RS256 public key location: `/etc/ssl/jwt-public.pem`
- Useful debug: `docker exec <container> date && date` to compare times
- Check: Are other services also affected by clock skew?

---

## Debug Log

```
14:23 Tried: Increased JWT expiry from 15min to 30min
Result: Failure rate unchanged (still ~5%)
Next: Check if issue is time-based (clock skew?)

14:35 Tried: Added 60s clock skew tolerance to JWT verification
Result: Failure rate dropped from 5% to 0.1%
Conclusion: Clock skew is the issue. Need to fix NTP sync.

14:42 Tried: Enabled NTP sync on api-gateway-2
Result: Clock synchronized, failures dropped to 0%
Conclusion: Root cause confirmed. Document tolerance decision.
```

---

[CLEAR ABOVE AFTER MOVING INSIGHTS TO NOTES.MD AND DECISIONS.LOG]

---
