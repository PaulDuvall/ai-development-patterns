#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_ROOT="${1:-${SCRIPT_DIR}/sample-project}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "error: Python 3 is required (set PYTHON_BIN to its executable)" >&2
  exit 1
fi

exec "$PYTHON_BIN" "${SCRIPT_DIR}/scripts/rules_validator.py" \
  specifications "$SCRIPT_DIR" "$PROJECT_ROOT"
