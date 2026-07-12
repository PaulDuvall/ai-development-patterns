# Parallel Agents - Deterministic Local Simulator

This directory is a runnable, provider-free simulation of the
**[Parallel Agents](../../README.md#parallel-agents)** pattern. Four isolated workers create
stable example artifacts while a coordinator summarizes their progress.

The simulator makes **zero model calls and zero provider API calls**. It does not need an OpenAI,
Anthropic, GitHub Models, or other API key, so running it cannot incur model-token charges. It is a
local orchestration example, not an AI research or pattern-adoption evaluation.

## What it demonstrates

- Four task-specific workers following an explicit dependency graph
- Separate writable workspaces for each worker
- A shared, lock-protected JSON coordination file
- A provider-free coordinator with a stable machine-readable report
- Completion-gated handoffs between dependent fixture generators
- An internal Docker network with no external egress
- Reviewable integration of remote `agent/*` branches

The generated artifacts are deterministic fixtures. Replace the worker implementation only in a
separate integration that has its own credential, budget, review, and network controls.

## Maintained files

```text
parallel-agents/
├── config/tasks.yaml
├── docker/
│   ├── Dockerfile.ai-agent
│   └── requirements.txt
├── scripts/
│   ├── agent_runner.py
│   ├── coordinator.py
│   └── merge-parallel-work.sh
├── .dockerignore
├── .env.example
└── docker-compose.parallel-agents.yml
```

The Python entrypoints are committed source files. You do not need to copy code out of this README
or generate scripts before building the image.

## Container quick start

Prerequisites:

- Docker Engine
- Docker Compose v2

From this directory:

```bash
mkdir -p workspace/{frontend,backend,database,tests} shared-memory reports

docker compose -f docker-compose.parallel-agents.yml build --pull
docker compose -f docker-compose.parallel-agents.yml up -d
docker compose -f docker-compose.parallel-agents.yml logs -f
```

All five services use the same image,
`ai-development-patterns/parallel-agent:local`. Compose therefore builds and reuses one image
instead of producing one image per service. The image contains Python 3.14 and Node.js 24 LTS;
Node is available for experimenting with the generated JavaScript fixture but is not used to call
a provider.

Compose starts the database and frontend fixture generators independently. The backend generator
waits for the database service to exit successfully, and the test-plan generator waits for both
the frontend and backend services to exit successfully. A failed prerequisite therefore prevents
its dependents from publishing misleading fixtures; service start order alone is not treated as
success.

Each one-shot worker exits after reporting `status: fixture_generated` and
`execution: simulated`. Inspect the results after the worker containers exit:

```bash
docker compose -f docker-compose.parallel-agents.yml ps -a
find workspace -type f -print | sort
cat shared-memory/agent_memory.json
cat reports/parallel-agent-status.json
```

The coordinator remains active so it can observe later changes. Stop and remove all containers
when finished:

```bash
docker compose -f docker-compose.parallel-agents.yml down
```

### Equivalent explicit image build

The Compose image name and this manual tag are deliberately identical:

```bash
docker build --pull \
  --tag ai-development-patterns/parallel-agent:local \
  --file docker/Dockerfile.ai-agent .
docker compose -f docker-compose.parallel-agents.yml up --no-build -d
```

The example directory is the build context because the Dockerfile copies
`docker/requirements.txt` and `scripts/`. The allowlist-based `.dockerignore` excludes `.env`,
workspaces, shared memory, reports, merge helpers, and every other unneeded path from that
context. Only the two runtime entrypoints are admitted from `scripts/`.

## Run directly with local Python

Python 3.11 or later is sufficient for the simulator itself:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --requirement docker/requirements.txt
mkdir -p workspace/{frontend,backend,database,tests} shared-memory reports

AGENT_ID=frontend python scripts/agent_runner.py \
  --task-file config/tasks.yaml \
  --task-id frontend-components \
  --workspace workspace/frontend \
  --shared-memory shared-memory/agent_memory.json

python scripts/coordinator.py \
  --watch-dir workspace \
  --report-dir reports \
  --shared-memory shared-memory/agent_memory.json \
  --once
```

Run the other task IDs in dependency order with their corresponding workspaces:

| Task ID | Depends on | Workspace | Exact fixture |
| --- | --- | --- | --- |
| `frontend-components` | Nothing | `workspace/frontend` | `components/TaskList.tsx` |
| `database-schema` | Nothing | `workspace/database` | `schema.prisma` |
| `backend-api` | `database-schema` | `workspace/backend` | `server.js` |
| `test-suite` | `frontend-components`, `backend-api` | `workspace/tests` | `test-plan.md` |

Given the same task ID, agent ID, and starting shared-memory document, the worker writes the same
artifact bytes and sorted JSON result on every run.

### Machine-checked fixture contracts

`config/tasks.yaml` is deliberately narrow: it declares this as simulated execution with zero
model/provider calls, lists each dependency edge, and binds every task to an artifact path, media
type, outcome, and SHA-256 digest. `agent_runner.py` validates the complete catalog before writing
anything. It rejects missing or extra task IDs, duplicate or cyclic dependencies, unsafe paths,
unexpected status/execution labels, path drift, and content-digest drift. The configuration cannot
silently promise work that the hard-coded simulator does not perform.

Shared memory is likewise a versioned two-key document (`version` and `agents`). The runner and
coordinator reject legacy discovery schemas and any result not labeled `fixture_generated` and
`simulated` instead of translating it into an apparently successful run.

## Configuration and cost boundary

`.env.example` contains optional local orchestration settings only. It intentionally contains no
provider name, model name, token, or credential placeholder. Docker Compose reads
`COMPOSE_PROJECT_NAME` automatically. To use its remaining values with the merge helper, export
them explicitly:

```bash
cp .env.example .env
set -a
. ./.env
set +a
./scripts/merge-parallel-work.sh
```

Do not add provider credentials to this example. The internal Compose network prevents external
egress, and neither Python entrypoint imports a provider SDK or contains an inference path.

## Merge helper safety

`scripts/merge-parallel-work.sh` discovers remote `origin/agent/*` branches and integrates them
sequentially into a local `main` branch. Before doing any network or branch operation, it requires
a clean tracked and untracked worktree. Updating local `main` is fast-forward-only.

For JSON conflicts, the helper performs a conservative three-way object merge using Git's base,
ours, and theirs blobs. It stages a file only after the merged result parses as JSON. Conflicting
changes to the same value, non-JSON conflicts, and unsupported file types are left for human
review. Temporary branches and in-progress merges are cleaned up when a branch cannot be
integrated.

The script's functions can be sourced without starting a merge:

```bash
source scripts/merge-parallel-work.sh
declare -F resolve_conflicts require_clean_worktree
```

Review the local commits and reports before pushing anything. The helper never pushes.

## Security properties

- No API keys or model credentials are accepted or mounted.
- The image build context is an explicit allowlist.
- The Compose network is `internal: true`.
- Configuration is mounted read-only.
- Test workers can read frontend/backend output but cannot modify it.
- Dependent workers start only after prerequisite containers exit successfully.
- Provider SDKs are not installed.
- Generated work is never merged into a remote branch automatically.

This example demonstrates mechanics, not autonomous production development. Production systems
also need least-privilege identities, resource limits, artifact review, observability, and an
explicit approval boundary before publishing generated changes.
