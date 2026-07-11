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

Show the complete planner output, including the plan ID, manifest path, stable and exploratory counts, discovery flag, and maximum searches. Warn that these bounds are not a fixed-price guarantee and that parallel subagents consume more tokens than comparable single-agent work.

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

Retain the printed `RUN_ID`, `RUN_REF`, `RUN_MANIFEST_SHA256`, `CHECKED_DATE`, `MODEL`, and `PROMPT_VERSION`. Stop if the manifest or its digest changes.

This is an interactive operator control, not a cryptographic identity proof. The manifest is content-bound and CI rejects `pending`, but a repository writer could forge an `approved` YAML record. Never describe validator acceptance alone as proof that a human typed the phrase; the root task must actually receive it in the conversation.

If the user cancels or declines before approval, start no agents and do not commit the pending
manifest. Remove only that plan's pending manifest and the ephemeral planner artifacts it created
(`verification/pattern-inventory.yaml`, `.verify-worklist`, and `verification/run-plan/`) using
scoped file operations. Do not delete an approved manifest, evidence, or unrelated work.

## Research approved units

Use the approved execution matrix; never add a pattern or discovery unit after approval.

For each batch:

1. Spawn one `adoption_researcher` subagent per pattern, with no more than three research subagents active at once. Assign exactly one immutable unit to each and include its catalog definition, known aliases, local provenance values, and the methodology reference path.
2. Wait for every researcher in the batch. The root task is the sole repository writer; subagents return structured proposals and never edit files.
3. Have the root task translate each proposal into `verification/evidence/<slug>.yaml`. Preserve truthful gaps. Use `evidence: none found` when the bounded search admits nothing.
4. Hydrate each selected file with trusted local code:

```bash
python3 scripts/hydrate-evidence-content.py \
  verification/evidence/<slug>.yaml \
  --retrieved-date <checked-date>
```

5. Close completed research threads if needed, then spawn one fresh `adoption_verifier` for the batch. Give it only the approved manifest, methodology, and batch evidence paths. It independently checks semantics and source admission; it does not edit.
6. Resolve every verifier finding in the root task. Rehydrate a file after changing a URL or quote. Run the secret scan on the batch before proceeding:

```bash
python3 scripts/scan-candidate-secrets.py verification/evidence/<slug> [...]
```

Process discovery as a separate read-only research unit. The root task may add only genuinely novel candidates to `experiments/NOTES.md`; discovery never edits pattern evidence.

## Finalize without publishing

After all approved units pass independent review, run the local finalizer:

```bash
python3 scripts/finalize-local-verification.py \
  --manifest "$RUN_REF" \
  --manifest-sha256 "$RUN_MANIFEST_SHA256"
```

The finalizer enforces exact scope and provenance, updates the pending list and generated status, synchronizes evidence-derived decision signals, recomputes verdicts, scans for secrets, and runs the evidence tests. Fix any failure and rerun it. Do not hand-edit a derived verdict or claim that model review replaces these checks.

Review the final diff and summarize the exact changed paths, verdict changes, naming signals, and any unresolved evidence gaps. Do not commit, push, or open a PR until the user gives a second, post-validation publication approval for this exact plan:

```text
APPROVE DRAFT EVIDENCE PR <plan-id>
```

After that approval, create one commit and one draft PR for the entire run. Never split approval across issues, never publish more than one evidence PR for a run, never mark it ready automatically, and never auto-merge it. The human reviews naming decisions and merges manually.

The publication phrase is likewise a local conversational gate, not a signed GitHub approval. GitHub Actions is configured read-only by default and cannot create or approve pull requests, so no hosted evaluator can substitute for this interaction.

## Preserve CI's role

GitHub Actions may run deterministic schema, derivation, status-drift, link, and content checks on demand, on pull requests, and weekly. It must not start Codex, call a model provider, refresh evidence, or receive evaluator credentials.
