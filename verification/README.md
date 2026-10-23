# Pattern Adoption Verification

This directory contains the structured evidence behind adoption verdicts. The system measures
whether a practice exists in industry independently from whether industry uses this catalog's name
for it. `patterns.yaml` remains the canonical stable-pattern registry; the reference table in
`experiments/README.md` is the exploratory-pattern registry.

An evidence file is an **assessment**, not automatically a verification. Only schema-v2 evidence
with complete search, source, retrieval, local-run, and verifier provenance can earn
`verdict: verified`. Migrated evidence is explicitly marked `provenance_status: legacy-import`,
appears as **needs refresh** in [STATUS.md](STATUS.md), and cannot earn a verified verdict.

## Trust model

The capability deliberately separates three operations:

1. **Validate** — deterministic, offline, read-only checks recompute every score, dimension,
   verdict, naming signal, catalog mapping, pending entry, and generated status row.
2. **Check links and content** — networked, read-only checks confirm cited pages remain reachable
   and recorded mechanism quotes remain present. This runs weekly and can be requested manually.
   When a source keeps its quote but moves, `scripts/hydrate-evidence-content.py --recheck` records
   the move without a model: it re-fetches every admitted source in the file, aborts unless every
   mechanism quote is still present, then advances `last_checked` and each `retrieved` while leaving
   `search.checked_at` pinned to the search run. `last_checked` therefore dates the most recent
   verification and `search.checked_at` dates the search, and the two may differ in that one
   direction. Rewording or withdrawal of a quote is out of scope here and requires operation 3.

   A source hosted at a mutable branch tip drifts for reasons that have nothing to do with the
   claim: editing a README restates a mechanism without withdrawing it, and this check cannot tell
   the two apart. Such a source is cited at a commit-pinned permalink
   (`raw.githubusercontent.com/<org>/<repo>/<sha>/<path>`) whenever its mechanism quote is verified
   present at that revision. That narrows what the weekly check proves for the entry, and the trade
   is deliberate: **a pinned citation shows the mechanism existed at that revision, not that it
   still ships.** Currency is carried instead by the 90-day freshness requirement the weekly
   schedule enforces, which forces re-evaluation rather than re-fetching. A source whose quote is
   already gone from the tip is never pinned to an earlier revision, because freezing a claim its
   owner has withdrawn asserts something the project does not know to be true.
3. **Evaluate locally** — bounded, model-backed web research runs only in an interactive local
   evaluator client (Codex today). A deterministic plan and exact human approval precede every agent call. Read-only
   research agents return proposals to one root writer; a separate agent reviews each batch before
   trusted local code hydrates, validates, and scans the result.

The flow is:

```text
signed-in local evaluator request
  -> deterministic catalog inventory and immutable plan
  -> exact human approval: APPROVE LOCAL EVALUATION <plan-id>
  -> up to three read-only research agents at a time
  -> root task writes one evidence file per selected pattern
  -> trusted URL/quote hydration -> content-bound evidence
  -> independent read-only semantic verifier per batch
  -> exact scope, provenance, derivation, secret, and test checks
  -> second human publication approval
  -> one draft PR -> manual human review and merge
```

`scripts/build-verification-inventory.py` owns catalog parsing, freshness ordering, in-flight PR
deduplication, and bounded selection. The research agents receive its generated inventory and
worklist; they do not choose or expand their own scope. The local finalizer removes selected slugs
from `pending-evidence.yaml`, synchronizes evidence-derived naming signals, and
regenerates `STATUS.md` once. Overlaps, unknown or duplicate pending slugs, orphan evidence,
duplicate canonical URLs, and multiple scored entries from one independence group fail validation.

The repository never reads an evaluator API key. Execution follows the active local Codex
authentication: a client signed in through a ChatGPT plan uses that plan's Codex allowance or
credits, while a local CLI authenticated with an API key is billed as OpenAI Platform API usage.
The planner requires an operator attestation and rejects known evaluator key environment variables;
that attestation is explicit but not cryptographic proof. Use the signed-in Codex app when the
intended billing path is the ChatGPT plan. See OpenAI's [Codex pricing](https://learn.chatgpt.com/docs/pricing),
[ChatGPT-plan usage guide](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan),
and [Codex rate card](https://help.openai.com/en/articles/20001106-codex-rate-card-2).

Both approval phrases are interactive operator controls. The planner enforces the first phrase in
the supported local workflow, and the skill enforces the second before publication, but neither is
a digital signature. A repository writer can edit YAML, so CI acceptance proves manifest
consistency—not that it cryptographically observed a person typing the phrase. Human review of the
conversation, final diff, draft PR, and manual merge remains part of the trust model. Actions uses a
read-only default token and is not allowed to create or approve pull requests.

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
checks through `workflow_dispatch` and `workflow_call`, runs for every pull request, and
runs weekly. `scripts/validate-workflow-policy.py` runs on every push as a lint over
`.github/workflows`. It semantically parses each `.yml` and `.yaml` workflow as bounded inert
data; aliases, duplicate keys, and unsupported structures fail closed. It rejects local and
Docker actions, permits only commit-pinned external action repositories from an explicit
allowlist, and rejects hosted model/provider entry points, provider SDK and CLI invocations,
provider API endpoints, blanket workflow permissions, and retired credential markers.

The property that matters is unchanged: **GitHub Actions never runs an evaluator model and never
receives an evaluator credential.** That is enforced mechanically, by this lint plus
`test_model_backed_pattern_evaluation_is_local_only`, not by anyone approving anything.

A previous design added a `pull_request_target` validator that byte-compared a "trust root" of
`scripts/`, `tests/` and `.github/workflows/` against the default branch, and required an owner
comment naming the head SHA to permit any difference. It was retired in October 2026. The threat
it addressed is a multi-party one, and this repository has a single maintainer, so in practice it
asked that maintainer to approve their own work. The costs were concrete: seven approval comments
for one change because each push invalidated the last, five dependency pull requests that could
never land, and a clock-dependence defect that sat on `main` for 14 days waiting to clear the
gate. Reinstate it if a second maintainer joins or the repository starts accepting fork pull
requests, at which point the trust boundary is real.
Before requesting the rerun, that job asks GitHub to mark `Trusted evidence checks` failed on the
current head; only a complete trusted validation can restore success. Resolver and validation failures
also attempt to publish failure. As with any GitHub-hosted control, an outage of the Statuses or Actions
API can prevent that update or rerun, so maintainers must use the live required-check result rather than
an earlier notification as the merge signal.
The rerun compares the API's current head repository, head SHA, base ref, and base SHA with its
immutable event payload before validating or honoring the exact owner comment. Removing or editing
the approval requests a fresh run, and candidate workflow code cannot manufacture the approval output.

```bash
gh workflow run evidence-validation.yml
```

An administrator can idempotently install the required-check ruleset and least-privilege Actions
setting. The required contexts are `Trusted evidence checks`, `Validation gate`, and
`Dependency Review`. Actions is limited to the repositories admitted by the trusted workflow
scanner plus `github/codeql-action` for default setup; blanket GitHub-owned and Marketplace
verified-creator access are disabled, and every action reference must use a full commit SHA. Every
workflow run from an external contributor's fork requires maintainer approval, the default token is
read-only, and Actions cannot approve pull requests. The same configuration enables secret
scanning, push protection, CodeQL
default setup for Actions, JavaScript/TypeScript, and Python using the extended remote-threat
suite. CodeQL scans main, same-repository pull requests, and the weekly schedule, but is not a
native merge rule because GitHub default setup excludes public fork pull requests and would leave
them unmergeable.

[GitHub Models repository enablement is a public-preview feature](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-github-models-in-your-repository)
whose Settings route is not exposed for this repository. [GitHub also documents that some Models
clients are outside organization policy enforcement](https://docs.github.com/en/github-models/github-models-at-scale/manage-models-at-scale#exceptions-to-your-organizations-model-settings).
This repository therefore does
not use that preview UI as a spend boundary or require an unverifiable manual attestation. For the
checked-in default-branch workflows and pull-request candidates, the trusted workflow policy rejects
GitHub Models permissions and direct model/provider action, endpoint, SDK, CLI, and credential surfaces
in workflow YAML; repository Actions is limited to an exact SHA-pinned action allowlist. A changed
protected script still requires the exact, commit-bound owner trust approval described above.

These controls are not an account-wide or absolute Actions kill switch. A collaborator with direct
write access could push a new same-repository branch workflow containing only `run:` steps before PR
policy validation, and personal PAT, Marketplace, and local extension/CLI use are outside this
repository's enforcement boundary. Keep direct write access restricted. Disabling repository Actions
is the absolute Actions-level stop. For paid GitHub Models usage across clients, opt out of paid usage
at the account or organization level, or use a budget with **Stop usage when budget limit is reached**
where GitHub offers it; see [GitHub Models billing](https://docs.github.com/en/billing/concepts/product-billing/github-models)
and [hard-stop budget configuration](https://docs.github.com/en/billing/how-tos/set-up-budgets).
BYOK and direct OpenAI, Anthropic, or other provider API usage requires a separate hard limit or key
revocation at that provider. This project keeps Actions model-free: required deterministic gates,
advisory read-only link/content checks and live Docker compatibility builds, Pages deployment, and
issue/reconciliation housekeeping. No workflow receives a model-provider credential or invokes a
model.

The command remains a dry run unless `--apply` is supplied. Apply mode also removes the named retired
evaluator and assistant credentials and the former paid-research environment, so historical workflow
definitions cannot access those retired repository credentials or that environment:

```bash
python3 scripts/configure-repository-rules.py
python3 scripts/configure-repository-rules.py --apply
```

### Network link and content check

Run the slow, read-only checks locally or request the Adoption Evidence Actions workflow:

```bash
python3 -m pytest tests/test_evidence_files.py tests/test_evidence_content.py -m slow
gh workflow run evidence-validation.yml -f check_links=true
```

Bot-protected responses are handled separately from dead links. Trusted retrieval makes at most
three attempts with a 30-second per-attempt timeout and bounded exponential backoff for transient
connection failures, timeouts, truncated streams, 408/425/429 responses, and selected 5xx errors;
certificate and other permanent failures fail closed.

Complete evidence records a normalized-content SHA-256 and an exact mechanism quote, so content
drift is observable even when a URL remains live. Trusted hydration fails unless the quote is
present and overwrites the resolved URL, digest, and retrieval date. Weekly checks fail when the
quote disappears and warn when normalized content changes. A strict second fetch is available as a
diagnostic for sources expected to be byte-stable:

```bash
EVIDENCE_HASH_STRICT=1 python3 -m pytest tests/test_evidence_content.py -m slow
```

### Local evidence evaluation

What this step requires is a capability, not a vendor: an interactive session that can take an
exact human plan approval, and that mints a run ID CI cannot produce. Which tool supplies it is
repository configuration, carried by the agent definitions under `.codex/` and the
`evaluate-pattern-adoption` skill. Codex is the configured implementation today, and the
identifiers below are wire format rather than a preference: `codex-local:<uuid>` run IDs,
`codex-local-<uuid>.yaml` manifests, the `codex-app`/`codex-cli`/`codex-ide` surfaces, and the
`evidence-v2-codex-local-v1` prompt contract are validated by regex in
`scripts/local_verification.py` and already recorded in committed evidence, so retargeting the
evaluator is a schema migration, not a docs change.

Open this repository in the signed-in evaluator client, the Codex app today, and invoke:

```text
$evaluate-pattern-adoption
```

Start from a dedicated clean branch or worktree at the current `origin/main`. Fetch `origin`, verify
that `HEAD` equals `origin/main`, and require `git status --short` to produce no output before
planning. Do not stash, discard, absorb, or work around existing changes. In particular, no
unrelated tracked or untracked changes may exist under `verification/` or in
`experiments/NOTES.md`. The final scope validator intentionally inspects the whole checkout and
fails when any changed path falls outside the exact approved run.

Ask for one explicit scope:

| Scope | Selection |
|---|---|
| `stale` | Up to 10 missing, legacy, or stale patterns by default |
| `stable` | All 29 stable patterns from `patterns.yaml` |
| `exploratory` | All 18 exploratory patterns from `experiments/README.md` |
| `all` | All 47 catalog patterns plus one discovery unit |
| `single` | One exact catalog pattern name |
| `discovery` | Discovery only; no pattern evidence |

The skill first runs a deterministic, non-model planner. Equivalent direct planning commands are:

```bash
python3 scripts/plan-local-verification.py plan \
  --scope stale --surface codex-app --attest-chatgpt
python3 scripts/plan-local-verification.py plan \
  --scope single --pattern "Security Sandbox" \
  --surface codex-app --attest-chatgpt
python3 scripts/plan-local-verification.py plan \
  --scope all --surface codex-app --attest-chatgpt
```

The planner first reads open main-targeting PR file lists through `gh` so it cannot unknowingly
repeat already-paid evidence work. Stale scope excludes in-flight evidence. Exact `stable`,
`exploratory`, `all`, and `single` scopes fail visibly when a selected pattern is in flight rather
than silently shrinking the advertised 29/18/47/1 pattern count.

The planner writes an ephemeral inventory and worklist plus a pending manifest under
`verification/local-runs/`. It reports the exact plan ID, stable/exploratory unit counts, discovery
flag, maximum searches, and number of open-PR exclusions checked. It refuses GitHub Actions and
known evaluator API-key variables. No model, subagent, web search, provider preflight, or repository
publication occurs during planning; the read-only GitHub PR query is not model research.

Research begins only after the user responds with the exact phrase printed by the planner:

```text
APPROVE LOCAL EVALUATION <plan-id>
```

Bind that response to the immutable plan:

```bash
python3 scripts/plan-local-verification.py approve \
  --manifest verification/local-runs/codex-local-<uuid>.yaml \
  --confirmation "APPROVE LOCAL EVALUATION <plan-id>"
```

Approval records the plan ID and UTC time, then makes the manifest read-only. Its SHA-256 becomes
part of every search, ledger, and verifier record, and approval prints the deterministic
`SEARCH_LEDGER_REF`. A changed plan, changed manifest, new run, or retry with a new plan needs new
approval. An earlier blanket instruction is not approval for a plan that did not yet exist.

If the user cancels or declines while the manifest is still pending, run no agents and commit
nothing. Remove only that pending manifest and the ephemeral `verification/pattern-inventory.yaml`,
`.verify-worklist`, and `verification/run-plan/` artifacts created by that plan. Never delete an
approved manifest, evidence, or unrelated work as cancellation cleanup.

The approved evaluation runs at most three `adoption_researcher` subagents concurrently, one
pattern per agent. The root task is the only writer. Each worker searches the name, mechanism, and
artifact modes with at most 12 live queries total and returns a structured proposal plus one
sanitized receipt per actual query. The root records each receipt with
`scripts/record-local-search-event.py`; the recorder derives candidate counts from distinct public
candidate URLs and then discards those URLs. The committed ledger retains only the tool, mode,
exact query, derived count, immutable run bindings, and event hash chain—never raw tool output,
reasoning, credentials, cookies, headers, or signed URLs. Trusted local code hydrates every source
URL and quote. A real retry is a new ordered event even when its exact query repeats. The
in-progress ledger is owner-only on the local filesystem. A fresh
`adoption_verifier` then independently reviews each batch's mechanism
matches, tier admissions, dates, quotes, independence claims, and ledger projection.
The pre-approval plan lists researcher turns, two verifier turns per deterministic batch of up to
three patterns (initial and post-fix), the maximum total subagent turns, model, surface, auth mode,
and search cap. Researcher retries and any third verifier turn require a new approved plan.
Verifiers may reopen only evidence URLs and cannot perform additional searches; discovery has no
verifier turn. These caps bound the work but are not a fixed-price guarantee. OpenAI notes that
[subagent workflows consume more tokens](https://learn.chatgpt.com/docs/agent-configuration/subagents)
than comparable single-agent work, so review the complete unit count before approving a plan.

After all approved units have been written, hydrated, and independently reviewed, finalize the run:

```bash
python3 scripts/finalize-local-verification.py \
  --manifest verification/local-runs/codex-local-<uuid>.yaml \
  --manifest-sha256 <approved-manifest-sha256>
```

Finalization validates the ledger's run ID, approved-manifest and research-contract digests, event
hash chain, approved scope, mode coverage, and query bound. It requires every evidence file's exact
queries and per-mode candidate counts to match the ledger before enforcing changed-path provenance,
removing selected pending slugs, synchronizing evidence-derived decision signals, regenerating
`STATUS.md`, recomputing every verdict, scanning candidate files for credentials, and running the
evidence tests. It does not commit, push, open a pull request, or merge.

The user must inspect the final diff and give a second, post-validation approval for the exact plan:

```text
APPROVE DRAFT EVIDENCE PR <plan-id>
```

Only then may the root task create one commit and one **draft** evidence PR for the run, including
the approved manifest and sanitized search-event ledger. Evidence-gap issues are tracking outputs,
not separate decision surfaces. Naming and rubric decisions remain human-owned in
[DECISIONS.md](DECISIONS.md). The workflow never marks the PR ready and never merges it; a human
reviews and merges it manually.

GitHub Actions deliberately cannot run this evaluation. The `Adoption Evidence` workflow contains
no evaluator key, model action, provider preflight, research matrix, or scheduled model refresh;
its weekly role is limited to deterministic validation, freshness reporting, and read-only source
checks. The former general `@claude` Actions assistant is removed. A separate fixed-purpose Claude
PR-review workflow is also removed, so Actions has no provider-backed assistant, evidence-research,
or model-refresh path.

## Schema v2

Every evidence file uses `schema_version: 2`. New complete evidence uses local manifest provenance
(values abbreviated):

```yaml
schema_version: 2
provenance_status: complete      # complete | legacy-import
pattern: Spec-Driven Development
slug: spec-driven-development
last_checked: 2026-07-10
search:
  run_id: "codex-local:123e4567-e89b-42d3-a456-426614174000"
  run_ref: verification/local-runs/codex-local-123e4567-e89b-42d3-a456-426614174000.yaml
  run_manifest_sha256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
  provider: openai
  model: codex-managed
  prompt_version: evidence-v2-codex-local-v1+sha256.0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
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
      model: codex-managed
      prompt_version: evidence-v2-codex-local-v1+sha256.0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
      run_ref: verification/local-runs/codex-local-123e4567-e89b-42d3-a456-426614174000.yaml
      run_manifest_sha256: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
    date: 2026-07-10       # omit when the source supplies no publication/update date
    retrieved: 2026-07-10
    claim: Runnable toolkit implements a specification-to-plan-to-tasks workflow.
verdict: weak
```

`scripts/validate-evidence.py` rejects asserted derived values; it recomputes them from the entries
on every run.

### Local run manifest

Every future complete assessment points to one committed, content-addressed file under
`verification/local-runs/`. The manifest records:

- a `codex-local:<UUIDv4>` run ID and matching safe repository-relative path;
- the base Git SHA, checked date, scope, exact selected slugs, and discovery flag;
- the local Codex surface, model label, versioned prompt contract, and
  `auth_mode: chatgpt-operator-attested`; and
- the exact plan ID plus human approval status and UTC approval time.

The plan ID hashes immutable plan fields; `run_manifest_sha256` hashes the approved manifest bytes.
The validator rejects missing, pending, changed, symlinked, traversing, mismatched, or unselected
manifests. The auth mode records the operator's assertion and does not claim cryptographic
verification of the account's billing configuration. Likewise, `approval.status: approved` is an
auditable operator attestation, not a signature or independent proof that the exact phrase was
typed.

Historical complete evidence with canonical `github-actions:<run-number>` IDs and matching
repository Actions URLs remains valid historical provenance. New model-backed GitHub Actions runs
are disabled and unsupported; local evidence uses `run_ref` and `run_manifest_sha256`, never
`run_url`.

### Search provenance

Complete provenance records all three search modes:

- **name** — the catalog name and observed terminology variants;
- **mechanism** — the behavior and problem, excluding the catalog name; and
- **artifact** — code/configuration fingerprints from working implementations.

Each local mode requires exact queries and a candidate count projected from the run's sibling
`codex-local-<uuid>-search-events.yaml` ledger. One ledger event corresponds to one actual query;
trusted code derives its count from distinct credential-free public candidate URLs, then discards
the URLs. The ledger binds the run ID, approved-manifest digest, and SHA-256 research-contract
fingerprint covering the skill, methodology, and two agent definitions. Its events are hash-chained,
scope-checked, and capped at 12 per unit. The combined candidate count cannot be smaller than the
admitted evidence set. Complete runs set `search.checked_at` to the run's own check date, which a
later model-free recheck leaves pinned while advancing `last_checked`, and bind every
verifier to the same model, prompt version, run manifest, and manifest digest. `evidence: none found`
is valid only when all three modes exactly reconcile with the ledger. This is a deterministic audit
record, not cryptographic proof that an operator or tool performed a search.

A legacy import uses `run_id: legacy-import`, empty query lists, and null candidate counts. It also
records the immutable original PR in `legacy_run_url` and states precisely what was not retained in
`legacy_limitations`; unknown data is never reconstructed or fabricated.

### Source provenance

Every entry records:

- `source_kind` constrained by its tier;
- `organization` and stable lowercase `independence_group`;
- submitted `url`, fetched `resolved_url`, and normalized `content_sha256`;
- verifier method, model, prompt version, local manifest reference, and manifest digest;
- actual `retrieved` date; and
- a short verbatim `mechanism_quote` demonstrating the same mechanism.

Complete entries require every provenance value and a mechanism quote. Legacy imports retain
truthful null hash/verifier values and historical quote gaps; this incompleteness is why they cannot
verify. A source's `date` is included only when the source itself supplies a publication or update
date—retrieval dates are never substituted.

Organization labels map consistently to one independence group across the corpus. Complete content
digests and canonical URLs are globally unique. The network checker rejects local/private DNS and
IP targets, revalidates every redirect, caps redirects and response size, compares the observed
final URL with `resolved_url`, and requires a mechanism quote that normalizes to at least 20
characters.

Use the deterministic producer to inspect one proposed source before adding it:

```bash
python3 scripts/evidence_content.py https://example.com/source \
  --quote "The exact source passage demonstrating the mechanism."
```

## Evidence tiers

At most three entries per tier may be scored. One `independence_group` may score only once in a
pattern file.

| Tier | Weight | Allowed `source_kind` | Admission test |
|---|---:|---|---|
| T1 | 5 | `shipped_product`, `open_source_implementation` | Can a user run the implementation today? |
| T2 | 4 | `official_documentation`, `reference_architecture` | Is it canonical guidance rather than promotion? |
| T3 | 3 | `conference_talk`, `peer_reviewed_research` | Is there a dated talk record or reviewed publication? |
| T4 | 2 | `practitioner_report`, `case_study` | Does it show real implementation or adoption detail? |
| T5 | 1 | `social_discussion`, `opinion`, `podcast` | Is it attributable, dated, and linkable? |

T5 is a discovery/naming signal. It never unlocks a verified adoption verdict.

## Derived fields

**`adoption_score`** is the tier-weight sum, capped at three entries per tier (range 0–45). The
displayed score includes T5, but the verified threshold counts T1–T4 points only.

**`adoption_dimensions`** separates availability from adoption:

- `implementation_available` — at least one T1 implementation exists;
- `independent_adoption` — at least one T3/T4 source belongs to a different independence group
  from at least one T1 source; and
- `independence_groups` — the number of unique scored groups.

**`verdict`** is recomputed:

- `verified` — complete v2 provenance, at least 8 T1–T4 points, an implementation, and independent
  adoption;
- `weak` — assessed evidence that does not meet every verified condition, including every
  positive-score legacy import; and
- `unverified` — score <= 2. Complete provenance proves that this follows a three-mode search; a
  legacy import with this verdict still remains **needs refresh**.

**`naming_alignment`** is a separate terminology signal computed from each entry's `match`:

- `strong` — more than half the entries use the catalog name (`named`);
- `weak` — at least one does, but not a majority;
- `aliased` — none use the catalog name, but sources use other stable names; and
- `none` — the mechanism is practiced without a stable name.

`terminology_variants` records alternative names. A strong adoption verdict with weak or aliased
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

No missing search, quote, or hash was invented. A complete local refresh is the only route from
**needs refresh** to a verified verdict.

## Generated status and human decisions

`scripts/generate-verification-status.py` builds [STATUS.md](STATUS.md). Its headings report
assessed, verified, weak, unverified, and pending counts separately. `needs refresh` is an
overlapping provenance signal, not a verdict.

Every cell is a function of the committed inputs alone, so `--check` fails only on a real input
change. The table therefore reports no age-derived currency column: it shows `Last checked` as a
date and leaves the 90-day judgment to the weekly
`validate-evidence.py --max-age-days 90` gate, which names the evidence files to refresh. An
age-derived column here was both wrong and actively harmful. It desynchronized the committed file
on a calendar boundary with no commit, and its remediation message told CI to regenerate the
table, which turns the build green by writing the word `stale` into a cell while refreshing no
evidence at all.

[DECISIONS.md](DECISIONS.md) is the human-owned naming and rubric ledger. Local finalization
synchronizes evidence-derived Alignment and may add a neutral review placeholder, but never edits
an existing human Decision. Humans own detailed terms, recommendations, and decisions. After a
human edit, regenerate the status file:

```bash
python3 scripts/generate-verification-status.py
```

## Files

- `evidence/<slug>.yaml` — one schema-v2 assessment per catalog slug.
- `local-runs/codex-local-<uuid>.yaml` — immutable approved plan and local execution attestation.
- `local-runs/codex-local-<uuid>-search-events.yaml` — sanitized, run-bound search receipts.
- `pending-evidence.yaml` — catalog slugs with no assessment; updated during local finalization.
- `STATUS.md` — generated coverage, verdict, naming, and provenance view.
- `DECISIONS.md` — human-owned naming and rubric decisions.
- `pattern-inventory.yaml`, `.verify-worklist`, and `run-plan/` — ephemeral planning artifacts.
