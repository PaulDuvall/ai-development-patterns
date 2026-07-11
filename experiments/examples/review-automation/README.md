# Review Automation Example

This example accompanies the experimental [Review Automation](../../README.md#review-automation)
pattern: semantic reviewers may propose findings, while deterministic checks and human-owned merge
policy remain authoritative.

## Current Status

This directory ships this README and a runnable, diff-based deterministic reviewer. The script
resolves an explicit base and head revision to immutable commits, reads added or modified blobs as
inert data, performs bounded syntax and heuristic security checks, and writes a
`review-findings-v1` JSON report. It never calls a model, executes candidate code, changes a
worktree, approves a pull request, or merges.

## Pattern Boundary

The catalog's Review Contract reviews one code change identified by `base_sha` and `head_sha`.
`merge_authority: human_policy` means a clean report is input to review, never an approval. Parallel
workspace reconciliation and automatic merge behavior belong to workflow orchestration, not this
example.

## Files

- [`automated-review.sh`](automated-review.sh) — validates Python, shell, YAML, and JSON syntax;
  rejects changed symlinks, binaries, files over 1 MiB, credential markers, and Python
  `eval`/`exec`; and emits commit-bound findings. Requires Bash, Git, Python 3.11+, and PyYAML.

## Quick Start

Run the script from any location inside a Git repository and supply the exact change boundary:

```bash
repo_root=$(git rev-parse --show-toplevel)
base_sha=$(git -C "$repo_root" rev-parse HEAD^)
head_sha=$(git -C "$repo_root" rev-parse HEAD)

"$repo_root/experiments/examples/review-automation/automated-review.sh" \
  --base "$base_sha" \
  --head "$head_sha" \
  --output /tmp/review-findings.json

cat /tmp/review-findings.json
```

The command exits non-zero when it records a finding. It does not run a project's test suite;
authoritative CI remains a separate required check.

## Known Limitations

- Credential and dynamic-execution checks are heuristics with false positives and false negatives.
- Syntax checks do not establish correctness, test coverage, dependency safety, or secure behavior.
- Deleted and renamed-away content is not inspected; the human reviewer still evaluates the full
  patch and repository history.
- No semantic reviewer ships here. An empty deterministic report is not proof that a change is
  safe, useful, or ready to merge.
- Production use needs a trusted-base runner, protected check configuration, report signing or
  provenance, and repository-specific deterministic gates.

## Promotion Path

Promotion requires independent semantic reviewers whose deduplicated findings conform to the same
commit-bound contract, deterministic checks wired into CI as the authoritative gate, protected
human-owned merge policy, and evidence that practitioners use the workflow without treating
reviewer silence as approval.

## Anti-pattern: Blind Review

Auto-approving a change because an AI reviewer returned no findings turns a probabilistic reviewer
into its own quality gate. Deterministic checks must remain authoritative, and silence from a
semantic reviewer must never substitute for human policy.
