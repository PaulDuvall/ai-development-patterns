# Session Notes

Capture context, discoveries, and progress across AI development sessions for continuity.

---

## Session [YYYY-MM-DD]

**Context**: [What you're working on this session]

**Discoveries**:
- [Key finding or insight]
- [Another important discovery]

**Blockers**:
- [Current roadblock or uncertainty]
- [Decision needed]

**Next Actions**:
- [What to do in next session]
- [Follow-up investigation needed]

**References**:
- [Links to related docs, specs, or code]

---

## Session [YYYY-MM-DD]

**Context**: [Another session's focus]

**Discoveries**:
- [What was learned]

**Blockers**:
- [none / or list blockers]

**Next Actions**:
- [Next steps]

---

## Previously On...

[Concise 3-5 sentence recap for context window compaction]

As of [YYYY-MM-DD], we're implementing [main objective]. Key decisions include [decision 1] and [decision 2]. Current focus is [current task]. Main blocker is [blocker if any]. Next milestone is [next goal].

---

## Usage Guidelines

### When to Use NOTES.md
- Maintain context between AI development sessions
- Record non-obvious discoveries and insights
- Track complex debugging or exploration journeys
- Create "Previously on..." recaps for session continuity
- Compact context window by summarizing long investigations

### Session Note Structure
- **Context**: 1-2 sentences on what you're working on
- **Discoveries**: Key findings, performance insights, gotchas uncovered
- **Blockers**: What's preventing progress (link to TODO.md for tracking)
- **Next Actions**: Clear steps for next session
- **References**: Links to specs, docs, or code relevant to this session

### "Previously On..." Recap
Create a concise summary when:
- Starting a new session after a break (>1 day)
- Context window is approaching limits
- Handing off work to another developer or AI session
- Resuming after completing a different task

Keep recaps to 3-5 sentences maximum:
1. What's the overall objective?
2. What key decisions have been made?
3. What's the current focus?
4. What's blocking progress (if anything)?
5. What's the next milestone?

### Best Practices
- ✅ Write session notes immediately after each session
- ✅ Be specific with discoveries (metrics, observations, gotchas)
- ✅ Link to relevant TODO items and DECISIONS
- ✅ Update "Previously on..." when context is scattered
- ✅ Archive old sessions (>30 days) to keep file scannable
- ❌ Don't duplicate information from TODO.md or DECISIONS.log
- ❌ Don't write general observations ("auth is important")
- ❌ Don't let notes grow beyond 500 lines (archive or compact)

### Integration with Other Memory
- Reference TODO.md tasks mentioned in discoveries or next actions
- Link to DECISIONS.log entries made during this session
- Use scratchpad.md for active working notes during session
- Extract patterns to knowledge/ if success rate is high

### Example Session

---

## Session 2024-01-15

**Context**: Implementing JWT authentication with RS256 signing

**Discoveries**:
- bcrypt has performance degradation above 100 req/s (tested with wrk)
- RS256 verification is only 2ms slower than HS256 at p99 (negligible)
- httpOnly cookies prevent XSS but need CSRF protection (sameSite=strict helps)

**Blockers**:
- Need to decide on refresh token storage (DB vs Redis vs JWT-in-JWT)
- Unclear how to handle token revocation for RS256 (no shared state)

**Next Actions**:
- Benchmark argon2 vs bcrypt for password hashing
- Research token revocation patterns (blocklist, short expiry, token versioning)
- Document JWT decision in DECISIONS.log

**References**:
- [OWASP JWT Security Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- `benchmarks/auth-performance.md` for bcrypt metrics

---

## Previously On...

As of 2024-01-15, we're implementing a JWT-based authentication system for the API. We decided to use RS256 for signing (see DECISIONS.log) to enable better key rotation. Current focus is evaluating password hashing algorithms (bcrypt vs argon2) due to performance concerns at scale. Main blocker is determining the refresh token revocation strategy. Next milestone is completing auth middleware with <50ms p99 latency.

---
