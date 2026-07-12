#!/bin/bash
# Safely integrate remote parallel-agent branches into a local main branch.

# Configuration is evaluated when the file is sourced, but sourcing has no
# filesystem, network, branch, or shell-option side effects.
MAIN_BRANCH="${MAIN_BRANCH:-main}"
AGENT_BRANCH_PREFIX="${AGENT_BRANCH_PREFIX:-agent/}"
REPORTS_DIR="${REPORTS_DIR:-./reports}"
SHARED_MEMORY="${SHARED_MEMORY:-./shared-memory/agent_memory.json}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

require_clean_worktree() {
    # A dirty index can make --refresh return nonzero; the explicit checks
    # below produce the actionable failure and status output.
    git update-index -q --refresh || true
    if ! git diff --quiet --ignore-submodules -- \
            || ! git diff --cached --quiet --ignore-submodules -- \
            || [ -n "$(git ls-files --others --exclude-standard)" ]; then
        log_error "Refusing to merge with tracked or untracked worktree changes:"
        git status --short >&2
        return 1
    fi
}

merge_in_progress() {
    git rev-parse -q --verify MERGE_HEAD >/dev/null 2>&1
}

analyze_shared_memory() {
    if [ ! -f "$SHARED_MEMORY" ]; then
        return 0
    fi

    log_info "Analyzing shared memory for agent results..."
    python3 - "$SHARED_MEMORY" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    memory = json.loads(path.read_text(encoding="utf-8"))
except (OSError, ValueError) as exc:
    print(f"Error reading shared memory: {exc}", file=sys.stderr)
    raise SystemExit(1)

agents = memory.get("agents", {})
if isinstance(agents, dict) and agents:
    print("\n=== Deterministic agent results ===")
    for agent_id, result in sorted(agents.items()):
        if not isinstance(result, dict):
            continue
        artifacts = result.get("artifacts", [])
        print(
            f"{agent_id}: {result.get('status', 'unknown')} "
            f"({result.get('task_id', 'unknown')}; {len(artifacts)} artifacts)"
        )
PY
}

create_merge_report() {
    local branch=$1
    local status=$2
    local details=$3
    local safe_branch=${branch//[^A-Za-z0-9._-]/_}
    local report_file
    report_file="$REPORTS_DIR/merge_${safe_branch}_$(date -u +%Y%m%dT%H%M%SZ).json"

    mkdir -p "$REPORTS_DIR"
    python3 - "$report_file" "$branch" "$status" "$details" "$MAIN_BRANCH" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

path, branch, status, details, main_branch = sys.argv[1:]
report = {
    "branch": branch,
    "details": details,
    "main_branch": main_branch,
    "status": status,
    "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
}
Path(path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
}

resolve_json_conflict() {
    local file=$1
    python3 - "$file" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

file_path = sys.argv[1]
destination = Path(file_path)
MISSING = object()


def load_stage(stage):
    result = subprocess.run(
        ["git", "show", f":{stage}:{file_path}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return MISSING
    return json.loads(result.stdout)


def merge_value(base, ours, theirs, location="$"):
    if ours is not MISSING and theirs is not MISSING and ours == theirs:
        return ours
    if ours is MISSING and theirs is MISSING:
        return MISSING
    if base is not MISSING and ours is not MISSING and ours == base:
        return theirs
    if base is not MISSING and theirs is not MISSING and theirs == base:
        return ours
    if base is MISSING and ours is MISSING:
        return theirs
    if base is MISSING and theirs is MISSING:
        return ours

    if (
        isinstance(ours, dict)
        and isinstance(theirs, dict)
        and (base is MISSING or isinstance(base, dict))
    ):
        base_map = {} if base is MISSING else base
        merged = {}
        for key in sorted(set(base_map) | set(ours) | set(theirs)):
            value = merge_value(
                base_map.get(key, MISSING),
                ours.get(key, MISSING),
                theirs.get(key, MISSING),
                f"{location}.{key}",
            )
            if value is not MISSING:
                merged[key] = value
        return merged

    raise ValueError(f"overlapping JSON changes at {location}")


try:
    if destination.is_symlink():
        raise ValueError("refusing to resolve a symbolic-link path")
    merged = merge_value(load_stage(1), load_stage(2), load_stage(3))
    if merged is MISSING:
        destination.unlink(missing_ok=True)
    else:
        serialized = json.dumps(merged, indent=2, sort_keys=True) + "\n"
        # Parse the exact bytes before replacing the conflicted worktree file.
        json.loads(serialized)
        destination.write_text(serialized, encoding="utf-8")
except (OSError, ValueError, json.JSONDecodeError) as exc:
    print(f"Cannot auto-resolve {file_path}: {exc}", file=sys.stderr)
    raise SystemExit(1)
PY
}

resolve_conflicts() {
    local found_conflict=false
    local file

    while IFS= read -r file; do
        [ -n "$file" ] || continue
        found_conflict=true
        log_info "Analyzing conflict in: $file"
        case "$file" in
            *.json)
                if resolve_json_conflict "$file"; then
                    # Stage only the path whose complete three-way result was
                    # parsed successfully. Never use git add -A here.
                    git add -- "$file"
                    log_success "Resolved and staged JSON conflict: $file"
                else
                    log_warning "JSON conflict requires human review: $file"
                fi
                ;;
            *)
                log_warning "Unsupported conflict requires human review: $file"
                ;;
        esac
    done < <(git diff --name-only --diff-filter=U)

    if [ "$found_conflict" = false ]; then
        return 0
    fi
    if [ -n "$(git diff --name-only --diff-filter=U)" ]; then
        return 1
    fi
    log_success "All conflicts resolved automatically"
}

merge_agent_branch() (
    set -euo pipefail

    local branch=$1
    local branch_name=${branch#origin/}
    TEMP_BRANCH_TO_CLEAN="temp-merge-$$-$(date +%s)"

    cleanup_temp_branch() {
        local exit_status=$?
        trap - EXIT
        if merge_in_progress; then
            git merge --abort >/dev/null 2>&1 || true
        fi
        git checkout --quiet "$MAIN_BRANCH" >/dev/null 2>&1 || true
        if git show-ref --verify --quiet "refs/heads/$TEMP_BRANCH_TO_CLEAN"; then
            git branch -D "$TEMP_BRANCH_TO_CLEAN" >/dev/null 2>&1 || true
        fi
        return "$exit_status"
    }
    trap cleanup_temp_branch EXIT

    log_info "Processing branch: $branch_name"
    git checkout -b "$TEMP_BRANCH_TO_CLEAN" "$MAIN_BRANCH" >/dev/null

    if git merge --no-commit --no-ff "$branch"; then
        # MERGE_HEAD, not worktree status, distinguishes a real merge from an
        # already-integrated branch. Reports and other ignored files cannot
        # turn a no-op into an empty commit.
        if merge_in_progress; then
            git commit -m "Merge $branch_name - Automated parallel agent integration"
            git checkout --quiet "$MAIN_BRANCH"
            git merge --ff-only "$TEMP_BRANCH_TO_CLEAN"
            create_merge_report "$branch_name" "success" "Clean merge finished"
        else
            log_info "No changes in $branch_name"
            create_merge_report "$branch_name" "no_changes" "Branch is already integrated"
        fi
        return 0
    fi

    log_warning "Conflicts detected in $branch_name"
    if ! resolve_conflicts; then
        local conflicts
        conflicts=$(git diff --name-only --diff-filter=U | tr '\n' ',')
        create_merge_report \
            "$branch_name" \
            "conflict" \
            "Manual resolution required for: ${conflicts%,}"
        log_error "Manual intervention required for $branch_name"
        return 1
    fi

    git commit -m "Merge $branch_name with automated conflict resolution"
    git checkout --quiet "$MAIN_BRANCH"
    git merge --ff-only "$TEMP_BRANCH_TO_CLEAN"
    create_merge_report \
        "$branch_name" \
        "success" \
        "Merged with conservative JSON conflict resolution"
)

main() (
    set -euo pipefail

    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log_error "Not in a Git repository"
        return 1
    fi
    require_clean_worktree

    ORIGINAL_BRANCH_TO_RESTORE=$(git symbolic-ref --quiet --short HEAD || true)
    ORIGINAL_COMMIT_TO_RESTORE=$(git rev-parse HEAD)

    restore_original_checkout() {
        local exit_status=$?
        trap - EXIT
        if [ -n "$ORIGINAL_BRANCH_TO_RESTORE" ]; then
            git checkout --quiet "$ORIGINAL_BRANCH_TO_RESTORE" >/dev/null 2>&1 || true
        else
            git checkout --quiet --detach "$ORIGINAL_COMMIT_TO_RESTORE" \
                >/dev/null 2>&1 || true
        fi
        return "$exit_status"
    }
    trap restore_original_checkout EXIT

    if ! git show-ref --verify --quiet "refs/heads/$MAIN_BRANCH"; then
        log_error "Local main branch does not exist: $MAIN_BRANCH"
        return 1
    fi

    log_info "Fetching remote branches"
    git fetch --all --prune
    git checkout --quiet "$MAIN_BRANCH"
    git pull --ff-only origin "$MAIN_BRANCH"

    mkdir -p "$REPORTS_DIR"
    analyze_shared_memory

    local agent_branches
    agent_branches=$(git for-each-ref \
        --format='%(refname:short)' \
        "refs/remotes/origin/${AGENT_BRANCH_PREFIX}*")
    if [ -z "$agent_branches" ]; then
        log_warning "No origin branches found with prefix: ${AGENT_BRANCH_PREFIX}"
        return 0
    fi

    log_info "Found agent branches:"
    while IFS= read -r branch; do
        echo "  - $branch"
    done <<< "$agent_branches"

    while IFS= read -r branch; do
        [ -n "$branch" ] || continue
        merge_agent_branch "$branch"
    done <<< "$agent_branches"

    local summary_file
    summary_file="$REPORTS_DIR/merge_summary_$(date -u +%Y%m%dT%H%M%SZ).txt"
    {
        echo "Parallel Agent Merge Summary"
        echo "============================="
        echo "Main Branch: $MAIN_BRANCH"
        echo
        echo "Processed Branches:"
        echo "$agent_branches"
        echo
        echo "Reports Generated:"
        find "$REPORTS_DIR" -maxdepth 1 -type f -name 'merge_*.json' -print \
            | sort | tail -10
    } > "$summary_file"

    log_success "Parallel agent branch integration finished"
    log_info "Review local commits and reports before pushing"
)

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main "$@"
fi
