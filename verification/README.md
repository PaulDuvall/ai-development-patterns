# Pattern Adoption Verification

This directory contains the structured evidence behind adoption verdicts. The system measures
whether a practice exists in industry independently from whether industry uses this catalog's name
for it. `patterns.yaml` remains the canonical pattern registry.

An evidence file is an **assessment**, not automatically a verification. Only schema-v2 evidence
with complete search, source, retrieval, and verifier provenance can earn `verdict: verified`.
Migrated evidence is explicitly marked `provenance_status: legacy-import`, appears as **needs
refresh** in [STATUS.md](STATUS.md), and cannot earn a verified verdict.

## Trust model

The capability deliberately separates three operations:

1. **Validate** — deterministic, offline, read-only checks recompute every score, dimension,
   verdict, naming signal, catalog mapping, pending entry, and generated status row.
2. **Check links and content** — networked, read-only checks confirm cited pages remain reachable
   and that recorded mechanism quotes remain present in fetched content. This runs weekly and can
   also be requested manually.
3. **Refresh evidence** — bounded web research creates one isolated artifact per selected pattern.
   Research has no repository mutation credential; trusted post-model code hydrates source
   retrieval metadata, then clean matrix jobs validate every fixed-path unit before trusted code
   assembles shared state and a scoped publisher opens one run-level PR.

The flow is:

```text
schedule/manual request
  -> deterministic catalog inventory
  -> one read-only research unit per pattern
  -> trusted URL/quote hydration -> content-bound unit artifact
  -> exact per-unit validation
  -> trusted all-or-nothing assembly and global validation
  -> scoped publisher -> one reviewable PR
```

`scripts/build-verification-inventory.py` owns catalog parsing, freshness ordering, in-flight PR
deduplication, and bounded selection. The research model receives its generated inventory and
worklist; it does not choose or expand its own scope.

The trusted assembler writes each validated evidence file, removes the same slugs from
`pending-evidence.yaml` atomically, synchronizes evidence-derived naming signals, and regenerates
`STATUS.md` once. Overlaps, unknown pending slugs, duplicate pending slugs,
orphan evidence, duplicate canonical URLs, and multiple scored entries from one independence group
all fail validation.

## Run it

Use Python 3.11 or newer. The repository pins Python 3.11 in `.python-version` and exact test
dependencies in `tests/requirements.txt`.

### Deterministic validation

Run this on demand before every evidence change; it performs no network calls and makes no writes:

```bash
python3 scripts/validate-evidence.py \
  --registry patterns.yaml \
  --allowlist verification/pending-evidence.yaml
python3 scripts/generate-verification-status.py --check
python3 -m pytest tests/test_evidence_files.py -m "not slow"
```

The `Adoption Evidence` workflow (`.github/workflows/evidence-validation.yml`) exposes the same
checks through `workflow_dispatch` and `workflow_call`, runs for every pull request, and runs
weekly. A separate `pull_request_target` workflow executes the default branch's trusted validator
against pull-request data without executing pull-request code. It posts the required commit-status
context `Trusted evidence checks` on the immutable candidate revision.

```bash
gh workflow run evidence-validation.yml
```

After this workflow exists on the default branch, an administrator can idempotently install its
required-check ruleset and the scoped Actions publisher setting. The command is a dry run unless
`--apply` is supplied:

```bash
python3 scripts/configure-repository-rules.py
python3 scripts/configure-repository-rules.py --apply
```

### Network link and content check

Run the slow, read-only checks locally with:

```bash
python3 -m pytest tests/test_evidence_files.py tests/test_evidence_content.py -m slow
gh workflow run evidence-validation.yml -f check_links=true
```

Bot-protected responses are handled separately from dead links. Complete evidence also records a
normalized-content SHA-256 and an exact mechanism quote so content drift is observable even when a
URL remains live. Legacy imports have null hashes and are skipped by semantic provenance checks
until refreshed. During refresh, trusted post-model hydration fails unless the quote is present and
overwrites the resolved URL, digest, and retrieval date before the unit manifest is created. Weekly
checks later fail when the quote disappears and warn when the normalized digest changes. A strict
second fetch is available as a diagnostic for sources expected to be byte-stable, but dynamic pages
can legitimately produce a different normalized digest between requests:

```bash
EVIDENCE_HASH_STRICT=1 python3 -m pytest tests/test_evidence_content.py -m slow
```

### Evidence refresh

The `Pattern Verification & Discovery` workflow (`.github/workflows/verify-patterns.yml`) uses
OpenAI by default, refreshes the stalest evidence on Monday at 05:00 UTC, and runs discovery on the
first day of each month at 06:00 UTC. Trigger it from the Actions tab or with:

```bash
gh workflow run verify-patterns.yml                        # up to 10 stalest/missing patterns
gh workflow run verify-patterns.yml -f mode=full           # every available main + experimental pattern
gh workflow run verify-patterns.yml -f mode=discover-only  # discovery only
gh workflow run verify-patterns.yml -f mode=single-pattern -f pattern="Security Sandbox"
gh workflow run verify-patterns.yml -f provider=anthropic  # explicit alternate provider
```

By default, preparation fails while another same-repository `verify/refresh-*` PR is open, and the
publisher repeats that check after research. This keeps the generated status, pending list, and
decision ledger on one review branch at a time. A maintainer may intentionally overlap a manual
run with `-f allow_open_verification_pr=true`; evidence slugs already changed by the older PR are
excluded, but the resulting aggregate PR may still need a rebase because both branches regenerate
shared files.

As a local alternative, Claude Code can run the same evidence methodology from the repository root:

```text
/verify-patterns
/verify-patterns --pattern "Security Sandbox"
/verify-patterns --discover-only
/verify-patterns --full
```

Research produces candidate data only. Every selected pattern gets its own immutable worklist,
research process, artifact, and fresh validation job. A run publishes nothing unless every unit
succeeds. Trusted code then combines only the disjoint evidence files, applies pending-list
removals, synchronizes deterministic decision-ledger signals, regenerates `STATUS.md`, and opens
one draft PR for the run. Renames and demotions remain human decisions.

The draft PR is the single review surface. Evidence-gap issues are tracking outputs, not separate
approval requests. If the aggregate adds `Review naming signal` rows, make any naming choice in
`verification/DECISIONS.md` on that PR (or in a follow-up PR); no response is required when no such
row appears.

Each provider has a separate `contents: read` research job, disables persisted checkout
credentials, and disallows direct GitHub mutation tools. Keeping the jobs separate prevents the
OpenAI action from receiving the OIDC permission used only by optional Anthropic federation. The
publisher prefers a short-lived GitHub App token configured with the `VERIFY_PATTERNS_APP_ID`
repository variable and `VERIFY_PATTERNS_APP_PRIVATE_KEY` secret.
After opening a draft PR, it dispatches trusted default-branch validation by PR number, so the
required result is attached to the candidate revision even when an automation-created PR event is
approval-gated. No long-lived personal access token is passed to the research agent.

The default OpenAI path uses the official pinned
[`openai/codex-action`](https://learn.chatgpt.com/docs/github-action) with native web search,
one directory-scoped bubblewrap root, and a dedicated unprivileged OS account per research unit
operating on a
private copy with no `.git` or `.beads` data (only empty, locked sandbox sentinels). Root-owned
read-only directories restrict that account to exactly one assigned evidence YAML, or to
`experiments/NOTES.md` for the single discovery unit; an OS-boundary check and a keyless pinned-CLI
sandbox smoke test verify
the effective profile and immutable Python 3.11 research environment before the model starts.
`CODEX_HOME` remains root-owned except for Codex's required `installation_id` file and
`tmp/arg0` runtime directory; a credential-free missing-thread smoke initializes the same
in-process app server used by the model action. Its reviewed network profile permits public
evidence fetches while the sandbox continues to reject local/private targets; model-run commands
inherit only core process variables and cannot launch a login shell that rehydrates the runner
environment. After Codex exits, the workflow kills every research-user process and the API proxy;
trusted code from the untouched checkout then hydrates retrieval metadata and exports that one fixed
unit path. Configure a
dedicated OpenAI Platform project or
[service-account key](https://platform.openai.com/docs/api-reference/project-service-accounts) as
the `OPENAI_API_KEY` Actions secret. A ChatGPT subscription/session token is not an API key, and API
usage is billed to the Platform project. The default model is
[`gpt-5.6-terra`](https://developers.openai.com/api/docs/guides/latest-model) at medium reasoning
effort; set the optional `OPENAI_EVIDENCE_MODEL` repository variable to another permitted model
identifier.

```bash
gh secret set OPENAI_API_KEY       # prompts without echoing the key
gh variable set OPENAI_EVIDENCE_MODEL --body gpt-5.6-terra  # optional
```

Anthropic remains an explicit `provider=anthropic` option. That path prefers workload-identity
federation when `ANTHROPIC_FEDERATION_RULE_ID`, `ANTHROPIC_ORGANIZATION_ID`, and optional
service-account/workspace repository variables are configured, then uses `ANTHROPIC_API_KEY` only
when federation is absent. Provider selection never silently falls back to the other provider.
The Anthropic job root-locks the checkout except for the assigned unit path, uses `dontAsk` mode
with an exact project-read/one-file-edit permission rule, restricts the built-in tool set, disables
all MCP and Bash tools, and derives retrieval metadata afterward with an immutable trusted helper.
This verifier provider is independent from the optional `Claude Code Review` workflow. That PR
reviewer runs only when the `ENABLE_ANTHROPIC_REVIEW` repository variable is `true`; with the
variable absent or `ANTHROPIC_API_KEY` unset, deterministic PR checks continue without Claude
review.
No provider final-message or raw execution-file artifact is retained; normal action progress remains
in GitHub's retained Actions log. For both providers, trusted hydration happens after the model and
before export, so each immutable unit manifest binds the fetched resolved URLs, content hashes, and
retrieval dates.
The provider stage scans each fixed unit before upload; a fresh clean runner rejects unsafe entries
and scans again after download without duplicating the just-completed fetch. The trusted assembler rejects
missing, extra, duplicate, or mismatched units and reruns global cross-pattern validation before
PR creation.

## Schema v2

Every evidence file uses `schema_version: 2`. A complete file has this shape (values abbreviated):

```yaml
schema_version: 2
provenance_status: complete      # complete | legacy-import
pattern: Spec-Driven Development
slug: spec-driven-development
last_checked: 2026-07-10
search:
  run_id: "github-actions:123456789"
  run_url: https://github.com/PaulDuvall/ai-development-patterns/actions/runs/123456789
  provider: openai
  model: gpt-5.6-terra
  prompt_version: evidence-v2-openai-codex-v1+sha256.0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
  checked_at: 2026-07-10
  modes:
    name:
      queries: ["spec driven development coding agents"]
      candidate_count: 4
    mechanism:
      queries: ["written requirements generate implementation tasks coding agent"]
      candidate_count: 6
    artifact:
      queries: ["path:.specify/memory/constitution.md"]
      candidate_count: 3
adoption_score: 5
tier_counts: {T1: 1}
adoption_dimensions:
  implementation_available: true
  independent_adoption: false
  independence_groups: 1
naming_alignment: strong
terminology_variants: []
evidence:
  - tier: T1
    match: named
    mechanism_quote: "Specifications become executable and generate working implementations."
    source: GitHub Spec Kit
    source_kind: open_source_implementation
    organization: GitHub
    independence_group: github
    url: https://github.com/github/spec-kit
    resolved_url: https://github.com/github/spec-kit
    content_sha256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
    verifier:
      method: automated
      model: gpt-5.6-terra
      prompt_version: evidence-v2-openai-codex-v1+sha256.0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
      run_url: https://github.com/PaulDuvall/ai-development-patterns/actions/runs/123456789
    date: 2026-07-10       # omit when the source supplies no publication/update date
    retrieved: 2026-07-10
    claim: Runnable toolkit implements a specification-to-plan-to-tasks workflow.
verdict: weak
```

`scripts/validate-evidence.py` rejects asserted derived values; it recomputes them from the
entries on every run.

### Search provenance

Complete provenance records all three search modes:

- **name** — the catalog name and observed terminology variants;
- **mechanism** — the behavior and problem, excluding the catalog name;
- **artifact** — code/config fingerprints from working implementations.

Each mode requires the exact queries and candidate count, and the combined candidate count cannot
be smaller than the admitted evidence set. Complete runs also record the selected research
provider, actual model, and versioned contract identifier—even when `evidence: none found`—use at
most 12 queries, and carry a
`github-actions:<run-number>` ID bound to this repository's canonical Actions run URL, bind every
verifier to that same run, require its model and prompt version to match the workflow-selected
provider, and set `search.checked_at` equal to `last_checked`. The prompt version includes a SHA-256
fingerprint of the pinned workflow, permission profile, and shared research methodology, so a
contract change produces a new machine-checked identifier. The clean candidate job additionally
binds selected files to the current run and requires exact completion of the deterministic
worklist. `evidence: none found` is valid only with this auditable complete search record; its run
URL identifies the immutable provider execution even though there are no entry-level verifiers.

A legacy import uses `run_id: legacy-import`, empty query lists, and null candidate counts. It also
records the immutable original PR in `legacy_run_url` and states precisely what was not retained in
`legacy_limitations`; unknown data is never reconstructed or fabricated.

### Source provenance

Every entry records:

- `source_kind` — constrained by its tier;
- `organization` — human-readable source owner or author affiliation;
- `independence_group` — a stable lowercase machine key used to prevent double-counting;
- `url` and `resolved_url` — the submitted and final canonical URLs;
- `content_sha256` — SHA-256 of normalized fetched response text;
- `verifier` — method, model, prompt version, and immutable run URL;
- `retrieved` — the actual fetch date; and
- `mechanism_quote` — a verbatim passage demonstrating the same mechanism.

Complete entries require all provenance values and a mechanism quote. Legacy imports retain
truthful null hash/verifier values and any historical quote gaps; this incompleteness is why they
cannot verify. A source's `date` is included only when the source itself supplies a publication or
update date—retrieval dates are never substituted.

Organization labels map consistently to one independence group across the evidence corpus, so one
company cannot become “independent” by inventing two group keys. Complete content digests are also
globally unique. The network checker rejects local/private DNS and IP targets, revalidates every
redirect, caps redirects and response size, compares the observed final URL with `resolved_url`,
and requires a mechanism quote that normalizes to at least 20 characters.

Use the deterministic producer to fetch a source, follow redirects, normalize visible text, compute
the digest, and verify the proposed quote before adding an entry:

```bash
python3 scripts/evidence_content.py https://example.com/source \
  --quote "The exact source passage demonstrating the mechanism."
```

## Evidence tiers

At most three entries per tier may be scored. One `independence_group` may score only once in a
pattern file.

| Tier | Weight | Allowed `source_kind` | Admission test |
|------|--------|-----------------------|----------------|
| T1 | 5 | `shipped_product`, `open_source_implementation` | Can a user run the implementation today? |
| T2 | 4 | `official_documentation`, `reference_architecture` | Is it canonical guidance rather than promotion? |
| T3 | 3 | `conference_talk`, `peer_reviewed_research` | Is there a dated talk record or reviewed publication? |
| T4 | 2 | `practitioner_report`, `case_study` | Does it show real implementation or adoption detail? |
| T5 | 1 | `social_discussion`, `opinion`, `podcast` | Is it attributable, dated, and linkable? |

T5 is a discovery/naming signal. It never unlocks a verified adoption verdict.

## Derived fields

**`adoption_score`** is the tier-weight sum, capped at three entries per tier (range 0–45). The
displayed score includes T5, but the verified threshold counts T1–T4 points only, so a social or
opinion point cannot supply the deciding eighth point.

**`adoption_dimensions`** separates availability from adoption:

- `implementation_available` — at least one T1 implementation exists;
- `independent_adoption` — at least one T3/T4 source belongs to a different independence group
  from at least one T1 source; and
- `independence_groups` — the number of unique scored groups.

**`verdict`** is recomputed:

- `verified` — complete v2 provenance, at least 8 T1–T4 points,
  `implementation_available: true`, and
  `independent_adoption: true`;
- `weak` — assessed evidence that does not meet every verified condition, including every
  positive-score legacy import; and
- `unverified` — score <= 2. Complete provenance proves that this follows a three-mode search;
  a legacy import with this verdict still remains **needs refresh**.

**`naming_alignment`** is a separate terminology signal computed from each entry's `match`:

- `strong` — more than half the entries use the catalog name (`named`);
- `weak` — at least one does, but not a majority;
- `aliased` — none use the catalog name, but sources use other stable names; and
- `none` — the mechanism is practiced without a stable name.

`terminology_variants` records those other names. A strong adoption verdict with weak or aliased
naming is a rename/alias discussion, not an adoption failure.

## Legacy migration

The ten assessments collected on 2026-07-02 predate v2. Their merged PRs prove aggregate query
counts, all three search modes, and an independent URL re-fetch, but do not preserve exact queries,
per-mode candidate counts, content hashes, or verifier metadata. Migration therefore:

- marks every file `provenance_status: legacy-import` and `verdict: weak`;
- links its immutable evidence PR and lists the missing provenance;
- removes duplicate canonical URLs and multiple entries from one independence group;
- drops sources that do not satisfy the v2 tier admission test;
- removes publication dates that were actually retrieval dates; and
- leaves hashes and unavailable verifier data null.

No missing search, quote, or hash was invented. A normal complete refresh is the only route from
**needs refresh** to a verified verdict.

## Generated status and human decisions

`scripts/generate-verification-status.py` builds [STATUS.md](STATUS.md). Its headings report
assessed, verified, weak, unverified, and pending counts separately. `stale` (more than 90 days
since a complete check) and `needs refresh` are overlapping freshness/provenance signals, not
verdicts.

[DECISIONS.md](DECISIONS.md) is the human-owned naming and rubric ledger. Trusted aggregation
synchronizes evidence-derived Alignment and may add a neutral review placeholder, but never edits
an existing human Decision. Humans own detailed terms, recommendations, and decisions. After a
human edit, regenerate the status file:

```bash
python3 scripts/generate-verification-status.py
```

## Files

- `evidence/<slug>.yaml` — one schema-v2 assessment per catalog slug.
- `pending-evidence.yaml` — catalog slugs with no assessment; shrinks atomically with evidence.
- `STATUS.md` — generated at-a-glance coverage, verdict, naming, and freshness view.
- `DECISIONS.md` — human-owned naming and rubric decisions.
- `pattern-inventory.yaml` and candidate artifacts — ephemeral and never committed.
