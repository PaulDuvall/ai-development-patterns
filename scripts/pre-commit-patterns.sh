#!/usr/bin/env bash
#
# Pre-commit hook: keep the generated patterns website in sync with README.md.
#
# Whenever README.md (or another site source) is part of a commit, this rebuilds
# the generated artifacts and stages them, so a stale site can never be
# committed. This is the local mirror of the CI deploy refresh.
#
# Install:
#   cp scripts/pre-commit-patterns.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# Only rebuild when README or the site sources are part of this commit.
if git diff --cached --name-only \
    | grep -qE '^(README\.md|patterns\.yaml|index\.html|scripts/generate-patterns-data\.py|assets/)'; then
  echo "[pre-commit] README/site change detected — rebuilding patterns site…"
  bash scripts/build.sh >/dev/null
  git add README.md index.html assets/js/patterns-data.js
  echo "[pre-commit] staged regenerated patterns-data.js + index.html"
fi
