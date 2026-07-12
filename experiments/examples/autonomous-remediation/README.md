# Autonomous Remediation Example

A working PostToolUse hook that detects code-quality violations after the AI writes or edits a file, then returns a structured violation report so the LLM can self-correct in the same session.

This is a concrete instantiation of the [Autonomous Remediation](../../README.md#autonomous-remediation) pattern.

## Current Status

The tracked hook, detectors, configuration, and thresholds form a runnable Claude Code reference
for Python files. It requires Python and PyYAML, and it reports proposed corrections to
the active assistant rather than applying changes outside that session.

## Files

| File | Purpose |
|---|---|
| `auto-remediate.py` | PostToolUse hook entry point. Reads the event JSON on stdin, runs detectors, emits a block decision when violations exist. |
| `detectors/__init__.py` | `run_all_detectors(file_path)` — dispatches the file to language-specific detectors. |
| `detectors/python_smells.py` | AST-based detectors for complexity, long functions, deep nesting. |
| `detectors/secrets.py` | Regex scanner for AWS keys, GitHub tokens, common secret patterns. |
| `detectors/fixes.py` | `FIX_HINTS` dictionary and `format_report()` helper. |
| `claude-settings.json` | Hook registration for `~/.claude/settings.json`. |
| `thresholds.yml` | Per-rule threshold overrides and per-directory skip list. |

## Setup

```bash
# 1. Copy the hook somewhere stable
mkdir -p ~/.claude/hooks
cp -r . ~/.claude/hooks/autonomous-remediation/

# 2. Make the entry point executable
chmod +x ~/.claude/hooks/autonomous-remediation/auto-remediate.py

# 3. Install the configuration dependency
pip install pyyaml

# 4. Register the hook in ~/.claude/settings.json
#    (merge the contents of claude-settings.json into your existing settings)
```

## How it works

```
AI edits file.py
      ↓
PostToolUse fires → auto-remediate.py reads event JSON
      ↓
run_all_detectors("file.py")
      ↓
  ┌───┴───┐
  │ clean │ → exit 0, AI continues
  └───┬───┘
      │ violations
      ↓
format_report() → JSON: { decision: "block", reason: "<structured report>" }
      ↓
AI receives report in same session → applies fix → loop
```

## Retry budget

The hook tracks consecutive blocks per file in `/tmp/.auto-remediate-state.json`. After 3 blocks on the same file, the hook surfaces a warning to the developer instead of blocking again, with two configured actions:

1. Raise the threshold for this rule in `thresholds.yml`
2. Add the file or directory to the skip list

This is the escape hatch from the "Unbounded Loop" anti-pattern documented in [Autonomous Remediation](../../README.md#autonomous-remediation).

## Skip list

Directories that should never trigger the loop are listed in `thresholds.yml`:

```yaml
skip_directories:
  - tests/
  - generated/
  - vendored/
  - migrations/
```

Generated code, test fixtures, and vendored dependencies are common sources of false-positive blocks.

## Extending

To add a detector, import it explicitly in `detectors/__init__.py` and call its `detect` function
from `run_all_detectors`. The Python-smell detector receives `(file_path, config)` while the secret
detector receives `file_path`; a new detector must define and wire its arguments explicitly. Each
finding includes `rule_id`, `file`, `line`, `severity`, and `message`. Add a matching `rule_id` entry
to `FIX_HINTS` when the report should include a remediation hint.

## Known Limitations

- The hook event and settings file target Claude Code; other assistants need an adapter.
- Python smell detection and regex-based secret detection are examples, not a complete quality or
  credential-scanning system.
- Retry state is local to one machine under `/tmp` and is not suitable for distributed execution.
- Detector output can contain false positives, so the retry limit and developer escape hatch remain
  mandatory.
- A detector exception is logged and fails open; production use needs an explicit fail-closed or
  quarantine policy for scanner outages.

## Promotion Path

Promotion requires portable lifecycle adapters, concurrent and crash-safe retry state, adversarial
tests for detector bypasses, and evidence that bounded self-correction improves validated outcomes
without hiding failures or weakening human review.

## See also

- [Agent Hooks](../../../README.md#agent-hooks) — the hook mechanism this pattern is built on
- [Codified Rules](../../../README.md#codified-rules) — where the detector thresholds live
- [Guided Refactoring](../../../README.md#guided-refactoring) — same loop applied specifically to code smells
- [Error Resolution](../../../README.md#error-resolution) — same loop applied to runtime errors
