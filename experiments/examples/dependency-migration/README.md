# Dependency Migration Example

This example implements the experimental [Dependency Migration](../../README.md#dependency-migration) pattern: an agent analyzes a specific version transition, proves compatibility in an isolated branch, and produces a reviewable migration rather than merely opening a version-bump pull request.

## Current Status

The workflow is a documented, tool-agnostic reference implementation. It is suitable for trial runs in a disposable worktree; package-manager adapters and repository-specific done checks still need to be supplied by adopters.

## Pattern Boundary

Dependency bots already discover new versions and create simple lockfile updates. This pattern begins when an upgrade requires compatibility reasoning or code migration:

- map affected APIs and transitive constraints;
- read authoritative release notes and migration guides;
- change application code, configuration, tests, and build tooling together;
- prove old behavior and new compatibility with executable checks; and
- retain a human approval and rollback boundary.

## Files

- [`dependency_migration.md`](dependency_migration.md) — migration contract, agent workflow, evidence bundle, and example plan.

## Quick Start

Create an isolated worktree and a version-pinned migration contract:

```bash
git worktree add ../migrate-react-19 -b deps/react-19
cd ../migrate-react-19

cat > dependency-migration.yml <<'YAML'
package: react
from: 18.3.1
to: 19.1.0
authoritative_sources:
  - https://react.dev/blog/2024/04/25/react-19-upgrade-guide
scope:
  include: [src/**, tests/**, package.json, package-lock.json]
  exclude: [infrastructure/**]
checks:
  - npm ci
  - npm run typecheck
  - npm test
  - npm run test:e2e
bounds:
  max_turns: 20
  max_files: 40
approval: human_before_merge
YAML
```

Ask the agent for an inventory and plan first. After approval, let it implement only the declared scope and require the check bundle plus a machine-readable list of changed APIs.

## Known Limitations

- Release-note retrieval and API-usage mapping vary by ecosystem.
- Passing tests prove only the behavior covered by those tests.
- Transitive runtime behavior may require staging or canary validation.
- The agent cannot approve its own migration or expand the declared scope silently.

## Promotion Path

Promotion requires reusable adapters for multiple ecosystems, evidence that the compatibility inventory catches real breaking changes, bounded execution, and independent practitioner adoption beyond version-bump automation.

## Anti-pattern: Version-Only Upgrades

Changing a manifest and lockfile while ignoring removed APIs, changed defaults, and operational behavior creates a green dependency bot PR that fails after deployment. Treat a major or compatibility-sensitive upgrade as a code migration with evidence.
