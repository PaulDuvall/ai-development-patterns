---
name: evaluate-pattern-adoption
description: Run or plan this repository's pattern-adoption evidence evaluation locally with signed-in Codex agents. Use when asked to refresh stale evidence, assess stable or exploratory patterns, evaluate one or all catalog patterns, discover possible new patterns, or prepare a reviewable evidence PR without model-backed GitHub Actions or provider API keys.
---

# Evaluate Pattern Adoption

Run model-backed research only in the user's interactive local Codex client. Keep GitHub Actions deterministic and credentialless for this capability.

## Establish the execution boundary

1. Work from the repository root in a local Codex app, CLI, or IDE session signed in with the user's ChatGPT account. Prefer the Codex app.
2. Confirm that evaluation will use the active Codex authentication. Local execution alone does not determine billing: a signed-in ChatGPT-plan client uses that plan's Codex allowance or credits, while API-key authentication is billed as OpenAI Platform API usage.
3. Do not continue when `GITHUB_ACTIONS=true`, when an evaluator API-key environment variable is present, or when the active client is authenticated with an API key. Never request, read, copy, print, or store a provider key.
4. Do not treat the user's initial request as approval to spend agent credits or publish results. Both gates below occur after the relevant plan or diff exists.
5. Fetch `origin`, then start from a dedicated branch or worktree whose `HEAD` is the current `origin/main`. Require `git status --short` to be empty before planning. Do not stash, discard, absorb, or work around unrelated changes; stop and move to a clean worktree instead.
6. Confirm there are no unrelated tracked or untracked changes under `verification/` or in `experiments/NOTES.md`. The final scope validator intentionally examines the whole worktree and fails on every changed path outside the approved run.

Read [references/evidence-methodology.md](references/evidence-methodology.md) completely before starting research.

## Build the deterministic plan

Choose one explicit scope:

- `stale` — up to 10 missing, legacy, or stale patterns by default;
- `stable` — every stable pattern in `patterns.yaml`;
- `exploratory` — every pattern in `experiments/README.md`;
- `all` — stable plus exploratory patterns and one discovery unit;
- `single` — one exact catalog name; or
- `discovery` — discovery only, with no evidence pattern.

Run no model or subagent before the planner. Use the current local surface:

```bash
python3 scripts/plan-local-verification.py plan \
  --scope <scope> \
  --surface codex-app \
  --attest-chatgpt
```

For `single`, also pass `--pattern "<exact catalog name>"`. For a non-default stale bound, pass `--limit <count>`. The attestation records the operator's confirmation; it is not cryptographic proof of billing mode.

Show the complete planner output, including the plan ID, manifest path, stable and exploratory counts, discovery flag, researcher and verifier turns, maximum total subagent turns, maximum searches, model, surface, and auth mode. Warn that these bounds are not a fixed-price guarantee and that parallel subagents consume more tokens than comparable single-agent work. Verifier turns are capped at two per deterministic batch of three patterns (or the final smaller batch): an initial review and a final review of the post-fix state. Discovery does not add a verifier.

The planner also reads open main-targeting PR file lists with `gh`. Stale scope excludes their evidence slugs. Exact `stable`, `exploratory`, `all`, and `single` scopes fail visibly if any selected pattern is already in flight; never bypass that failure or silently shrink an exact scope.

Then stop. Start no research until the user responds with exactly:

```text
APPROVE LOCAL EVALUATION <plan-id>
```

Do not accept a paraphrase, an earlier blanket approval, or an approval for another plan. Bind the approval:

```bash
python3 scripts/plan-local-verification.py approve \
  --manifest <run-manifest-path> \
  --confirmation "APPROVE LOCAL EVALUATION <plan-id>"
```

Retain the printed `RUN_ID`, `RUN_REF`, `RUN_MANIFEST_SHA256`, `SEARCH_LEDGER_REF`, `CHECKED_DATE`, `MODEL`, and `PROMPT_VERSION`. Stop if the manifest or its digest changes. The prompt version's contract digest covers this skill, the methodology, and both read-only agent definitions.

This is an interactive operator control, not a cryptographic identity proof. The manifest is content-bound and CI rejects `pending`, but a repository writer could forge an `approved` YAML record. Never describe validator acceptance alone as proof that a human typed the phrase; the root task must actually receive it in the conversation.

If the user cancels or declines before approval, start no agents and do not commit the pending
manifest. Remove only that plan's pending manifest and the ephemeral planner artifacts it created
(`verification/pattern-inventory.yaml`, `.verify-worklist`, and `verification/run-plan/`) using
scoped file operations. Do not delete an approved manifest, evidence, or unrelated work.

## Research approved units

Use the approved execution matrix; never add a pattern or discovery unit after approval.

Process selected patterns in their execution-matrix order. Use exactly three remaining patterns per batch until the final smaller batch, so the planner's verifier-turn cap remains true. For each batch:

1. Spawn one `adoption_researcher` subagent turn per pattern, with no more than three research subagents active at once. Assign exactly one immutable unit to each and include its catalog definition, known aliases, local provenance values, and the methodology reference path. Do not retry, replace, or follow up with a researcher; an incomplete researcher stops this plan and any additional turn requires a new exact plan approval.
2. Wait for every researcher in the batch. The root task is the sole repository writer; subagents return a structured evidence proposal plus one sanitized receipt per actual search. A receipt contains only the tool identifier, mode, exact query, and distinct public candidate URLs actually examined. It never contains raw tool output, reasoning, headers, cookies, credentials, or signed URLs.
3. Before writing evidence, have the root task record every receipt with trusted local code. Repeat `--candidate-url` once per credible candidate actually examined; omit it for a zero-candidate search:

```bash
python3 scripts/record-local-search-event.py \
  --manifest "$RUN_REF" \
  --manifest-sha256 "$RUN_MANIFEST_SHA256" \
  --unit <slug> \
  --mode <name|mechanism|artifact> \
  --tool web.search_query \
  --query "<exact-query>" \
  --candidate-url https://example.com/candidate
```

   The recorder rejects hosted/API-key execution and credential-like input, derives the count from distinct admitted URLs, then discards the URLs. It stores only the run/manifest/contract binding and a hash-chained sanitized event in an owner-only local file. Record every actual retry even when its exact query repeats; sequence and the event hash distinguish it. Do not copy a researcher-supplied aggregate count into the ledger, invent a receipt, or hand-edit the ledger.
4. Have the root task translate each proposal into `verification/evidence/<slug>.yaml`. Set each mode's queries, in event order, and candidate count to the exact ledger projection. Preserve truthful gaps. `evidence: none found` cannot complete without all three modes in the reconciled ledger.
5. Hydrate each selected file with trusted local code:

```bash
python3 scripts/hydrate-evidence-content.py \
  verification/evidence/<slug>.yaml \
  --retrieved-date <checked-date>
```

6. Close completed research threads if needed, then spawn exactly one fresh `adoption_verifier` turn for the batch. Give it only the approved manifest, sanitized ledger, methodology, and batch evidence paths. It independently checks semantics, source admission, and ledger projection; it does not edit. It may open only URLs already present in the evidence and must not search, discover, or add candidate URLs.
7. Resolve every initial verifier finding in the root task and rehydrate after changing a URL or quote. Then use exactly one final follow-up verifier turn on the complete post-fix batch. Make no material evidence, source, quote, tier, mechanism, or provenance edit after that final review. If the final review fails, stop this plan; a replacement or third verifier turn requires a new exact plan approval. Run the secret scan only after the final verifier passes:

```bash
python3 scripts/scan-candidate-secrets.py verification/evidence/<slug> [...]
```

Process discovery as a separate read-only research unit. Record its searches under `--unit discovery --mode discovery` with the same recorder. The root task may add only genuinely novel candidates to `experiments/NOTES.md`; discovery never edits pattern evidence.

## Finalize without publishing

After all approved units pass independent review, run the local finalizer:

```bash
python3 scripts/finalize-local-verification.py \
  --manifest "$RUN_REF" \
  --manifest-sha256 "$RUN_MANIFEST_SHA256"
```

The finalizer requires the run's sanitized ledger, validates its run ID, approved-manifest digest, research-contract digest, event hash chain, scope, three-mode coverage, and 12-query bound, then reconciles every exact query and candidate count before changing derived files. It also enforces exact path/provenance scope, updates the pending list and generated status, synchronizes evidence-derived decision signals, recomputes verdicts, scans for secrets, and runs the evidence tests. Fix any failure and rerun it. Do not hand-edit the ledger or a derived verdict, and do not claim that model review replaces these checks.

Review the final diff and summarize the exact changed paths, verdict changes, naming signals, and any unresolved evidence gaps. Do not commit, push, or open a PR until the user gives a second, post-validation publication approval for this exact plan:

```text
APPROVE DRAFT EVIDENCE PR <plan-id>
```

After that approval, create one commit and one draft PR for the entire run, including its approved manifest and sanitized search-event ledger. Never split approval across issues, never publish more than one evidence PR for a run, never mark it ready automatically, and never auto-merge it. The human reviews naming decisions and merges manually.

The publication phrase is likewise a local conversational gate, not a signed GitHub approval. GitHub Actions is configured read-only by default and cannot create or approve pull requests, so no hosted evaluator can substitute for this interaction.

## Preserve CI's role

GitHub Actions may run deterministic schema, derivation, status-drift, link, and content checks on demand, on pull requests, and weekly. It must not start Codex, call a model provider, refresh evidence, or receive evaluator credentials.
