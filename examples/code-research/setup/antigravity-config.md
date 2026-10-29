# Google Antigravity Configuration (Code Research)

This guide mirrors the Claude Code setup, but applies to agent workflows that work through PRs/branches.

Antigravity describes itself as "our agentic development platform, allowing anyone to build in the
agent-first era." Its app manages multiple local agents in parallel across workspaces. For install and
configuration steps, follow the vendor documentation at <https://antigravity.google/docs/overview>; the
checklist below is the repository-side setup this example needs, and is platform-independent.

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

