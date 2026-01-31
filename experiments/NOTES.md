# Experimental Pattern Notes

This file tracks patterns under exploration that may eventually be formalized into full patterns.

## Pattern Exploration Queue

### Voice-to-Code Interface

**Status**: Early exploration
**Date Added**: 2025-12-04

**Description**: Using voice input tools (e.g., WisprFlow, Talon Voice, Voice Control for VSCode) to dictate code, commands, and AI prompts for hands-free development.

**Potential Use Cases**:
- Accessibility for developers with mobility limitations
- Reducing repetitive strain injuries (RSI)
- Faster prompt composition for AI interactions
- Multi-modal input (voice + keyboard/mouse hybrid)
- Hands-free code review and exploration

**Tools to Evaluate**:
- [WisprFlow](https://wisprflow.ai/) - Voice-to-text for coding
- [Talon Voice](https://talonvoice.com/) - Voice control for development
- [Voice Control for VSCode](https://marketplace.visualstudio.com/items?itemName=pokey.cursorless) - VSCode voice extensions
- Native OS voice control (macOS Voice Control, Windows Speech Recognition)

**Research Questions**:
1. How accurate is voice-to-code for technical terminology (function names, variable names)?
2. Can voice dictation handle AI prompt composition effectively?
3. What's the learning curve for voice commands vs. keyboard shortcuts?
4. Does voice input improve or hinder AI-assisted development workflows?
5. How does voice integrate with existing AI coding tools (Claude Code, Cursor, Copilot)?

**Next Steps**:
- [ ] Test WisprFlow with Claude Code for prompt dictation
- [ ] Evaluate voice accuracy for Python/JavaScript/TypeScript
- [ ] Measure WPM (words per minute) voice vs. keyboard for prompts
- [ ] Document voice command vocabulary for common AI interactions
- [ ] Assess impact on [Context Persistence](../README.md#context-persistence) pattern

**Related Patterns**:
- [Tool Integration](../README.md#tool-integration) - Voice as input tool for AI
- [Developer Lifecycle](../README.md#developer-lifecycle) - Voice-triggered workflow commands
- [Context Persistence](../README.md#context-persistence) - Voice input as context source

**Anti-patterns to Avoid**:
- Over-reliance on voice for precise code editing (better for high-level commands)
- Using voice in noisy environments (poor transcription accuracy)
- Voice-only workflow without keyboard fallback (voice fatigue)

---

### Agentic Loops

**Status**: Early exploration
**Date Added**: 2025-01-11

**Description**: Enable long autonomous coding sessions where AI iteratively improves work until explicit completion criteria are met. Uses a stop hook to intercept exit attempts and feed the same prompt back, allowing Claude to self-correct through test failures, error messages, and its own code. See the [Claude Code Ralph Wiggum plugin](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md).

**Core Mechanics**:
- **Stop hook** intercepts exit attempts and re-injects the original prompt
- **File persistence** allows each iteration to see previous work
- **Completion promise** (e.g., `<promise>COMPLETE</promise>`) signals success
- **Iteration limits** provide safety bounds (e.g., `--max-iterations 50`)

**Potential Use Cases**:
- Greenfield projects you can start and walk away from
- TDD workflows: write failing tests → implement → run tests → fix → repeat
- Multi-phase feature builds with clear success criteria
- Tasks with automatic verification (tests, linters, type checkers)

**Tools to Evaluate**:
- [Ralph Wiggum Plugin](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md) - Official Claude Code agentic loop implementation
- Custom stop hooks with iteration tracking
- Prompt templates with completion promises

**Research Questions**:
1. How do you craft effective completion promises that prevent false positives?
2. What iteration limits balance thoroughness vs. cost for different task types?
3. How should prompts structure incremental goals for multi-phase work?
4. When should loops include explicit fallback/escape instructions?
5. What metrics distinguish productive iteration from thrashing?

**Next Steps**:
- [ ] Test /ralph-loop with various task types (API builds, test suites, refactoring)
- [ ] Document effective prompt templates with completion promises
- [ ] Measure iteration counts and API costs for common workflows
- [ ] Define prompt patterns for self-correction (TDD cycles, debug loops)
- [ ] Identify tasks unsuitable for agentic loops (design decisions, unclear criteria)

**Related Patterns**:
- [Parallel Agents](../README.md#parallel-agents) - Multiple loops running concurrently
- [Developer Lifecycle](../README.md#developer-lifecycle) - Triggering loops on events
- [CheckPoint](#checkpoint) - Validation criteria within loop iterations

**Anti-patterns to Avoid**:
- Missing iteration limits (runaway costs, infinite loops)
- Vague completion criteria ("make it good" vs. explicit success metrics)
- Tasks requiring human judgment or design decisions
- Prompts without self-correction guidance (test → fix → retry cycles)
- Generating large codebases you don't understand or know how to maintain

---

### CheckPoint

**Status**: Early exploration
**Date Added**: 2025-01-11

**Description**: A systematic validation gate that runs a series of quality checks (refactoring, security, code quality, performance, architecture, documentation) after each development task to ensure continuous quality.

**Potential Use Cases**:
- Post-commit quality validation before pushing
- Pre-merge checks in pull request workflows
- Continuous compliance verification during development
- Architecture drift detection after feature additions
- Documentation freshness validation

**Tools to Evaluate**:
- Claude Code slash commands (/xsecurity, /xquality, /xrefactor, etc.)
- Pre-commit hooks with multi-check orchestration
- Custom checkpoint scripts with configurable check suites
- CI/CD pipeline quality gates

**Research Questions**:
1. What's the optimal set of checks to run after each task?
2. How do you balance thoroughness vs. developer velocity?
3. Should checkpoints be blocking or advisory?
4. How do you handle check failures mid-workflow?
5. Can AI assistants auto-remediate checkpoint failures?

**Next Steps**:
- [ ] Define standard checkpoint check categories
- [ ] Create configurable checkpoint profiles (quick, standard, thorough)
- [ ] Implement checkpoint as Claude Code custom command
- [ ] Measure impact on code quality metrics over time
- [ ] Document checkpoint integration with CI/CD pipelines

**Related Patterns**:
- [Readiness Assessment](../README.md#readiness-assessment) - Code quality prerequisites before automation
- [Security Sandbox](../README.md#security-sandbox) - Running agents in isolated environments
- [Agentic Loops](#agentic-loops) - Long autonomous coding sessions with self-correction
- [Guided Refactoring](../README.md#guided-refactoring) - Code improvement checks

**Anti-patterns to Avoid**:
- Running all checks on every minor change (developer fatigue)
- Checkpoint failures without actionable remediation guidance
- Skipping checkpoints under time pressure (quality debt)
- One-size-fits-all checks regardless of change scope

---

## Notes Template

When adding new pattern explorations, copy this template:

```markdown
### [Pattern Name]

**Status**: [Early exploration | Active testing | Ready for formalization]
**Date Added**: YYYY-MM-DD

**Description**: Brief 1-2 sentence description

**Potential Use Cases**:
- Use case 1
- Use case 2

**Tools to Evaluate**:
- Tool 1 with link
- Tool 2 with link

**Research Questions**:
1. Question 1
2. Question 2

**Next Steps**:
- [ ] Step 1
- [ ] Step 2

**Related Patterns**:
- Link to pattern 1
- Link to pattern 2

**Anti-patterns to Avoid**:
- Anti-pattern 1
- Anti-pattern 2
```
