#!/usr/bin/env bash
#
# Canonical build entrypoint for the AI Development Patterns website.
#
# README.md is the single source of record. This rebuilds every generated
# artifact from it so the published site can never drift from the docs:
#   - refreshes the pattern-count badges (README.md + index.html)
#   - regenerates assets/js/patterns-data.js (cards + full detail)
#   - regenerates the branded dependency diagram injected into index.html
#
# Used by:
#   - .github/workflows/deploy-pages.yml   (runs on every push to main)
#   - scripts/pre-commit-patterns.sh        (keeps commits in sync locally)
#   - any static host (set this as the build command, e.g. Vercel/Netlify)
#
# Idempotent: safe to run repeatedly. Requires python3 (stdlib + pyyaml for
# the badge script).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[build] refreshing pattern-count badges from patterns.yaml…"
python3 scripts/update-pattern-count.py

echo "[build] generating patterns dataset + diagram from README.md…"
python3 scripts/generate-patterns-data.py

echo "[build] done — site is in sync with README.md"
