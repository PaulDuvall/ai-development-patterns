#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Create a dedicated "research" repository for asynchronous investigations.

Usage:
  ./setup/create-research-repo.sh <repo-name>

Notes:
- Requires GitHub CLI (gh) and git.
- Creates a private repo by default.
- Safe to run multiple times; will refuse to overwrite an existing directory.
EOF
}

if [[ "${1:-}" == "" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

repo_name="$1"

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh (GitHub CLI) is required." >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is required." >&2
  exit 1
fi

if [[ -e "$repo_name" ]]; then
  echo "ERROR: '$repo_name' already exists. Refusing to overwrite." >&2
  exit 1
fi

echo "Creating GitHub repo: $repo_name (private)"
gh repo create "$repo_name" --private --confirm

echo "Cloning..."
git clone "https://github.com/$(gh api user -q .login)/$repo_name.git"
cd "$repo_name"

cat > README.md <<'EOF'
# Research Repository

Autonomous code investigations using asynchronous coding agents.

Each folder contains one research task with:
- `prompt.md` (the research prompt)
- `README.md` (findings)
- supporting code/data as needed
EOF

git add README.md
git commit -m "Initialize research repository"
git push -u origin main

echo "Done: $(pwd)"

