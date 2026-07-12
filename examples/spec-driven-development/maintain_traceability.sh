#!/usr/bin/env bash
# Deterministic entry point for this example's traceability quality gates.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
CONFIG_PATH="examples/spec-driven-development/.pre-commit-config.yaml"
PYTHON_BIN="${PYTHON:-python3}"

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Required command not found: $1" >&2
        return 1
    fi
}

run_validator() {
    require_command "$PYTHON_BIN"
    "$PYTHON_BIN" "$SCRIPT_DIR/spec_validator.py" \
        --check-coverage \
        --authority-conflicts \
        --spec-file "$SCRIPT_DIR/iam_policy_spec.md" \
        --test-dir "$SCRIPT_DIR/tests"
}

run_tests() {
    require_command "$PYTHON_BIN"
    (
        cd "$SCRIPT_DIR"
        "$PYTHON_BIN" -m pytest
    )
}

run_pre_commit() {
    require_command pre-commit
    (
        cd "$REPO_ROOT"
        pre-commit run --config "$CONFIG_PATH" "$@"
    )
}

install_hooks() {
    require_command pre-commit
    (
        cd "$REPO_ROOT"
        pre-commit install --config "$CONFIG_PATH"
    )
}

show_usage() {
    cat <<'EOF'
Deterministic Spec-Driven Development traceability maintenance

Usage:
  maintain_traceability.sh --validate       Validate syntax, links, and authority
  maintain_traceability.sh --test           Run tests and the enforced coverage gate
  maintain_traceability.sh --pre-commit     Run configured hooks for staged files
  maintain_traceability.sh --all            Run configured hooks for every tracked file
  maintain_traceability.sh --install-hooks  Ask pre-commit to install managed hooks
  maintain_traceability.sh --help           Show this help

The script never performs model inference or manages Git hook files itself.
EOF
}

case "${1:---validate}" in
    --validate)
        run_validator
        ;;
    --test)
        run_tests
        ;;
    --pre-commit|--validate-staged)
        run_pre_commit
        ;;
    --all)
        run_pre_commit --all-files
        ;;
    --install-hooks)
        install_hooks
        ;;
    --help|-h)
        show_usage
        ;;
    *)
        echo "Unknown command: $1" >&2
        show_usage >&2
        exit 2
        ;;
esac
