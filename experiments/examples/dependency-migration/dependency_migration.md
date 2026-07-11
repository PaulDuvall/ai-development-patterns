# Agentic Dependency Migration Contract

## Goal

Move one dependency from an exact current version to an exact target version while preserving declared behavior and producing evidence a reviewer can reproduce.

## Inputs

```yaml
package: example-sdk
from: 3.8.4
to: 4.0.2
package_manager: npm
authoritative_sources:
  - https://vendor.example/migrations/v4
  - https://vendor.example/changelog/4.0.2
allowed_files: [package.json, package-lock.json, src/**, tests/**]
forbidden_files: [.github/workflows/**, infrastructure/**, secrets/**]
done_checks:
  - npm ci
  - npm run typecheck
  - npm test
  - npm run test:e2e
rollback: git revert the migration commit
```

Pin source URLs and versions before research starts. A floating `latest` target makes the result irreproducible.

## Phase 1: Deterministic Inventory

Collect facts before asking the agent to reason:

```bash
npm ls example-sdk --all --json > evidence/dependency-tree.before.json
rg -n "from ['\"]example-sdk|require\(['\"]example-sdk" src tests \
  > evidence/api-usage.before.txt
npm test -- --runInBand > evidence/test-baseline.txt
git rev-parse HEAD > evidence/base-commit.txt
```

The inventory must identify direct imports, configuration keys, generated clients, peer dependencies, and runtime integrations. Empty results stay explicit; the model must not infer that an unsearched API is unused.

## Phase 2: Compatibility Analysis

Require one row per affected behavior:

| Current usage | Target change | Source | Required migration | Verification |
|---------------|---------------|--------|--------------------|--------------|
| `client.retry(3)` | Retry options moved to constructor | v4 migration guide §2 | Configure `new Client({retries: 3})` | Retry integration test |
| Legacy error enum | Enum removed | v4 changelog | Map new typed error codes | Error-contract test |

Reject any row without an authoritative source or repository location. Separate confirmed breaking changes from hypotheses that require an experiment.

## Phase 3: Isolated Agent Implementation

Give the agent the approved table, allowed paths, and hard bounds. The agent works on a dedicated branch or worktree and commits one behaviorally coherent step at a time:

1. update the package and lockfile;
2. migrate confirmed API usages;
3. add or update focused compatibility tests;
4. run every done check; and
5. stop on scope expansion, an exhausted retry budget, or an unexplained regression.

The agent may propose a new file or check, but a human must approve changes to the contract.

## Phase 4: Evidence Bundle

```json
{
  "package": "example-sdk",
  "from": "3.8.4",
  "to": "4.0.2",
  "base_commit": "<sha>",
  "migration_commit": "<sha>",
  "sources": ["https://vendor.example/migrations/v4"],
  "changed_apis": ["retry configuration", "error enum"],
  "checks": {
    "npm_ci": "pass",
    "typecheck": "pass",
    "unit": "pass",
    "e2e": "pass"
  },
  "unresolved_risks": ["production retry volume requires staged observation"]
}
```

Store raw command output beside the summary. The summary is an index, not a substitute for evidence.

## Phase 5: Human Gate and Rollback

The reviewer checks the source mapping, diff, test changes, lockfile, unresolved risks, and rollback command. Merge only after all declared checks pass at the migration commit. If runtime validation fails, execute the recorded rollback rather than asking the agent to improvise in production.

## Anti-pattern: Self-Certified Migration

The same agent researches a release, edits the code, weakens failing tests, and declares compatibility. Separate the migration contract and final approval from the writing agent, and keep deterministic behavior checks immutable during the run unless a human explicitly approves their change.
