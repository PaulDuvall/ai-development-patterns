# Gemini Jules Configuration (Code Research)

This guide mirrors the Claude Code setup, but applies to "async agent" workflows that work through PRs/branches.

## Checklist

1. Use a dedicated repository with no production secrets.
2. Create one folder per research task:
   - `prompt.md` (the task prompt)
   - `README.md` (findings)
3. Require reproducibility:
   - include commands to run
   - include raw results (JSON/CSV) when possible
4. Keep tasks bounded (10–30 minutes of agent time):
   - measure/compare/prove a single question

