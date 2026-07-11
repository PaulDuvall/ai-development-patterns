# Experimental Pattern Notes

This file tracks ideas that are not yet full catalog patterns. Formal experimental patterns live in
[README.md](README.md).

## Pattern Exploration Queue

### Voice-to-Code Interface

**Status**: Early exploration
**Date Added**: 2025-12-04

**Description**: Use voice input tools to dictate prompts, commands, and limited code while
preserving keyboard or pointer fallback for precision work.

**Potential Use Cases**:

- Accessibility for developers with mobility limitations
- Reduced repetitive strain during prompt-heavy work
- Faster high-level prompt composition
- Hands-free code review and navigation

**Tools to Evaluate**:

- [Wispr Flow](https://wisprflow.ai/)
- [Talon Voice](https://talonvoice.com/)
- [Cursorless](https://www.cursorless.org/)
- Native operating-system voice control

**Research Questions**:

1. How accurately does voice input handle identifiers and technical vocabulary?
2. Which tasks benefit from voice rather than keyboard input?
3. How should sensitive dictated content be detected and redacted?
4. Does voice input improve throughput without increasing correction time?

**Related Patterns**:

- [Tool Integration](../README.md#tool-integration) — voice is an input tool.
- [Developer Lifecycle](../README.md#developer-lifecycle) — voice may trigger workflow steps.
- [Agent Memory](../README.md#agent-memory) — transcripts can become retained context.

**Anti-patterns to Avoid**:

- Voice-only workflows without a precision fallback
- Dictating secrets or regulated data into unapproved transcription services
- Treating transcription confidence as code correctness

---

### Mention Delegation

**Status**: Early exploration
**Date Added**: 2026-07-10

**Description**: Trigger asynchronous agent work by mentioning an agent in an existing collaboration
thread so the request inherits bounded context and reports status back to the same surface.

This exploration owns only the **trigger**. [Code Research](../README.md#code-research) owns
investigative intent; [Long-Running Orchestration](README.md#long-running-orchestration) owns
duration, durable state, and checkpoints; [Bounded Autonomy](../README.md#bounded-autonomy) owns
turn, spend, time, stall, and divergence limits; and
[Handoff Protocols](README.md#handoff-protocols) owns return, approval, correction, and takeover.

**Potential Use Cases**:

- Assigning a repository task from a Slack or Teams discussion
- Turning incident or support conversations into agent-executed follow-up work
- Letting non-IDE collaborators request analysis, documentation, issues, or pull requests
- Preserving a visible delegation and status trail in the originating thread

**Tools to Evaluate**:

- [Claude in Slack](https://www.anthropic.com/news/introducing-claude-tag)
- [GitHub Copilot coding agent for Slack](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/integrate-cloud-agent-with-slack)
- [ChatGPT workspace agents](https://help.openai.com/en/articles/20001143-chatgpt-workspace-agents-for-enterprise-and-business)

**Trigger Contract**:

```yaml
mention_delegation:
  requester: user-123
  source_thread: slack:C0123:1720000000.0001
  requested_scope: repository-analysis
  authorization: read-only
  context_policy: summarize-and-redact
  accepted_statuses: [queued, running, blocked, completed]
  mutation_requires_separate_approval: true
```

**Research Questions**:

1. What permission model prevents a casual mention from granting repository write access?
2. How should private thread context be redacted before becoming durable task context?
3. Which status markers make queued, blocked, and completed work visible?
4. When should a mention create a durable issue or pull request?

**Related Patterns**:

- [Handoff Protocols](README.md#handoff-protocols) — receives completed or blocked work.
- [Long-Running Orchestration](README.md#long-running-orchestration) — persists state after the trigger.
- [Code Research](../README.md#code-research) — supplies one bounded asynchronous intent.

**Anti-patterns to Avoid**:

- Treating every mention as authorization to mutate a repository
- Persisting sensitive conversation context in a public issue or pull request
- Hiding agent status in side threads without clear ownership
- Executing incident-response mutations from a mention without explicit approval

## Consolidated Concepts

Iteration and retry-loop mechanics belong to
[Long-Running Orchestration](README.md#long-running-orchestration), while all turn, spend, time,
stall, and divergence controls belong to [Bounded Autonomy](../README.md#bounded-autonomy).

Post-task quality checkpoints belong to [Testing Orchestration](README.md#testing-orchestration)
for test and quality-gate execution and [Autonomous Acceptance](README.md#autonomous-acceptance) for
separately owned release policy. They are not tracked as an independent exploration.

## Notes Template

```markdown
### Exploration Name

**Status**: Early exploration
**Date Added**: YYYY-MM-DD

**Description**: One-sentence mechanism and outcome.

**Research Questions**:
1. What makes this distinct from existing linked patterns?
2. Which runnable implementation demonstrates it?
3. What evidence would justify formalization?

**Related Patterns**:
- [Existing Pattern](link)

**Anti-patterns to Avoid**:
- Concrete failure mode
```
