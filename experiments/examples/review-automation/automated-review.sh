#!/usr/bin/env bash
# Deterministic, inert review of the files changed between two immutable commits.

set -euo pipefail

base_ref=
head_ref=
output=review-findings.json

usage() {
  cat <<'EOF'
Usage: automated-review.sh --base <commit> --head <commit> [--output <file>]

Parses added and modified files without executing candidate code. The command
writes a review-findings-v1 JSON report and exits non-zero when it finds an
unsafe file type, syntax error, credential marker, or eval/exec call.
EOF
}

while (( $# > 0 )); do
  case "$1" in
    --base)
      [[ $# -ge 2 ]] || { usage >&2; exit 2; }
      base_ref=$2
      shift 2
      ;;
    --head)
      [[ $# -ge 2 ]] || { usage >&2; exit 2; }
      head_ref=$2
      shift 2
      ;;
    --output)
      [[ $# -ge 2 ]] || { usage >&2; exit 2; }
      output=$2
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

[[ -n "$base_ref" && -n "$head_ref" ]] || { usage >&2; exit 2; }
root=$(git rev-parse --show-toplevel)
cd "$root"
base_sha=$(git rev-parse --verify "${base_ref}^{commit}")
head_sha=$(git rev-parse --verify "${head_ref}^{commit}")
changed=$(mktemp)
trap 'rm -f "$changed"' EXIT
git diff --name-only --diff-filter=ACMR -z "$base_sha" "$head_sha" > "$changed"

python3 - "$base_sha" "$head_sha" "$output" "$changed" <<'PY'
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml


base_sha, head_sha, output_name, changed_name = sys.argv[1:]
paths = [
    item.decode("utf-8")
    for item in Path(changed_name).read_bytes().split(b"\0")
    if item
]
findings = []
credential_markers = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def add(rule_id, severity, path, line, message):
    findings.append({
        "rule_id": rule_id,
        "severity": severity,
        "path": path,
        "line": line,
        "message": message,
        "source": "deterministic",
    })


for path in paths:
    tree = subprocess.run(
        ["git", "ls-tree", head_sha, "--", path],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if not tree:
        continue
    mode = tree.split(None, 1)[0]
    if mode == "120000":
        add("unsafe-symlink", "error", path, 1,
            "Changed symbolic links require separate human review")
        continue

    content = subprocess.run(
        ["git", "show", f"{head_sha}:{path}"],
        check=True,
        capture_output=True,
    ).stdout
    if len(content) > 1_048_576:
        add("oversized-file", "error", path, 1,
            "Changed file exceeds the 1 MiB review bound")
        continue
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        add("binary-file", "error", path, 1,
            "Binary changes are outside this example's review contract")
        continue

    suffix = Path(path).suffix.casefold()
    try:
        if suffix == ".py":
            compile(text, path, "exec")
        elif suffix in {".yaml", ".yml"}:
            yaml.safe_load(text)
        elif suffix == ".json":
            json.loads(text)
        elif suffix == ".sh":
            result = subprocess.run(
                ["bash", "-n"], input=content, capture_output=True)
            if result.returncode:
                raise ValueError(result.stderr.decode("utf-8", "replace").strip())
    except (SyntaxError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        line = getattr(exc, "lineno", None) or getattr(
            getattr(exc, "problem_mark", None), "line", 0) + 1
        add("syntax-error", "error", path, line,
            f"{suffix or 'text'} syntax validation failed")

    for line_number, line in enumerate(text.splitlines(), 1):
        if any(marker.search(line) for marker in credential_markers):
            add("credential-marker", "error", path, line_number,
                "Credential-like value found; the value is intentionally omitted")
        if suffix == ".py" and re.search(r"\b(?:eval|exec)\s*\(", line):
            add("dynamic-execution", "error", path, line_number,
                "Dynamic eval/exec requires explicit human security review")

report = {
    "schema_version": "review-findings-v1",
    "base_sha": base_sha,
    "head_sha": head_sha,
    "deterministic_checks": "required",
    "merge_authority": "human_policy",
    "files_reviewed": len(paths),
    "findings": findings,
}
Path(output_name).write_text(
    json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"Reviewed {len(paths)} changed file(s); {len(findings)} finding(s)")
raise SystemExit(1 if findings else 0)
PY
