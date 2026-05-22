# Autonomous Remediation Example

A working PostToolUse hook that detects code-quality violations after the AI writes or edits a file, then returns a structured violation report so the LLM can self-correct in the same session.

This is a concrete instantiation of the [Autonomous Remediation](../../README.md#autonomous-remediation) pattern.

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

# 3. Install detector dependencies
pip install lizard pyyaml

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

The hook tracks consecutive blocks per file in `/tmp/.auto-remediate-state.json`. After 3 blocks on the same file, the hook surfaces a warning to the developer instead of blocking again, with one of three suggested actions:

1. Raise the threshold for this rule in `thresholds.yml`
2. Add the file or directory to the skip list
3. Add an inline `# rule: ignore` marker

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

To add a new detector, drop a module into `detectors/` exposing `detect(file_path) -> list[Violation]`. Register the module name in `detectors/__init__.py`. Each `Violation` must include `rule_id`, `file`, `line`, `severity`, and a `fix_hint` keyed in `FIX_HINTS`.

## See also

- [Event Automation](../../README.md#event-automation) — the hook mechanism this pattern is built on
- [Codified Rules](../../README.md#codified-rules) — where the detector thresholds live
- [Guided Refactoring](../../README.md#guided-refactoring) — same loop applied specifically to code smells
- [Error Resolution](../../README.md#error-resolution) — same loop applied to runtime errors
