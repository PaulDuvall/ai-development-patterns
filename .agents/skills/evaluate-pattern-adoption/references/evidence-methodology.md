# Evidence methodology

Use this methodology for every approved local pattern-adoption unit. Research whether the mechanism is practiced in industry under this catalog's name or another name; do not merely search for a phrase collision. The approved manifest's research-contract digest covers this methodology, the parent skill, and both read-only agent definitions.

## Unit inputs and bounds

The parent supplies one catalog name, slug, definition, known aliases, and the approved local run values. Do not change the scope. Use at most 12 live search queries total for a pattern, counting retries and query variants. Return one sanitized tool-event receipt per actual search: admitted tool identifier, mode, exact query, and the distinct public candidate URLs actually examined. Record a repeated identical query again when it was actually retried; its ordered sequence and event hash distinguish the attempts. Never return a self-calculated aggregate candidate count; trusted parent-side code derives the count from admitted URLs and discards those URLs from the ledger.

Run all three modes even when an earlier mode finds evidence:

1. `name` — search the canonical name and known terminology variants.
2. `mechanism` — search the behavior, problem, and outcome without the catalog name.
3. `artifact` — search for executable tools, repositories, configuration fingerprints, templates, or other working artifacts.

A search result is a candidate, not evidence. Open the source, identify the mechanism, reject marketing-only or name-collision results, and record `none found` if the bounded search cannot support an entry. Never fabricate a query, receipt, candidate URL, quote, source date, or adoption claim. Receipts must never contain raw tool output, hidden reasoning, chain-of-thought, request or response headers, cookies, credentials, signed URLs, or credential-bearing query parameters.

## Source admission

Prefer direct, attributable sources. Admit at most three entries per tier and only one scored entry per `independence_group` in a pattern file. A canonical URL may appear in only one pattern file across the corpus. Use stable lowercase group keys so one organization cannot masquerade as multiple independent adopters.

| Tier | Weight | Allowed source kinds | Admission test |
|---|---:|---|---|
| T1 | 5 | `shipped_product`, `open_source_implementation` | A user can run the implementation now. |
| T2 | 4 | `official_documentation`, `reference_architecture` | Canonical guidance describes how to practice the mechanism. |
| T3 | 3 | `conference_talk`, `peer_reviewed_research` | A dated talk or reviewed publication demonstrates the mechanism. |
| T4 | 2 | `practitioner_report`, `case_study` | A real implementation or adoption account contains operational detail. |
| T5 | 1 | `social_discussion`, `opinion`, `podcast` | The item is attributable, dated, linkable, and useful only as a discovery or naming signal. |

For each admitted source provide:

- tier, `source_kind`, source title, organization, and independence group;
- submitted URL;
- `named`, `aliased`, or `unnamed` match;
- a short verbatim `mechanism_quote` that directly supports the claim;
- the source-supplied publication or update date, if present; and
- a concise claim describing what is implemented or practiced.

Do not use retrieval time as the source's `date`. Keep quotes as short as practical while retaining the mechanism. The trusted hydrator supplies `resolved_url`, `content_sha256`, and `retrieved`; do not invent them.

## Local provenance

All complete evidence from this workflow uses the approved local run values exactly:

```yaml
search:
  run_id: "codex-local:<uuid-v4>"
  run_ref: verification/local-runs/codex-local-<uuid-v4>.yaml
  run_manifest_sha256: <approved-manifest-sha256>
  provider: openai
  model: <manifest-model>
  prompt_version: <manifest-prompt-version>
  checked_at: <checked-date>
  modes:
    name: {queries: [], candidate_count: 0}
    mechanism: {queries: [], candidate_count: 0}
    artifact: {queries: [], candidate_count: 0}
```

Every evidence entry uses the same manifest binding:

```yaml
verifier:
  method: automated
  model: <manifest-model>
  prompt_version: <manifest-prompt-version>
  run_ref: verification/local-runs/codex-local-<uuid-v4>.yaml
  run_manifest_sha256: <approved-manifest-sha256>
```

Do not add a GitHub Actions `run_url` to local provenance. The committed, content-addressed run manifest and its sibling `codex-local-<uuid>-search-events.yaml` ledger are the local audit record. The evidence `search.modes` mapping must be the exact ledger projection: queries in event order and each mode's candidate count equal to the sum of its machine-derived event counts. The ledger binds the run ID, approved-manifest digest, and research-contract digest and hash-chains its sanitized events. It deliberately retains neither candidate URLs nor raw reasoning. `auth_mode: chatgpt-operator-attested` records a human assertion about the client session; it is not cryptographic proof that a search occurred or of the account's billing mode.

## Derivation and semantic review

The repository computes scores, dimensions, naming alignment, and verdicts. Proposals should be internally coherent but must not override deterministic output.

- `implementation_available` requires at least one T1 entry.
- `independent_adoption` requires a T3 or T4 source from a different group than a T1 implementation.
- `verified` requires complete provenance, at least eight T1-T4 points, an implementation, and independent adoption.
- T5 can affect discovery or naming, but cannot unlock `verified`.
- `strong` naming means most entries use the catalog name; `weak` means some do; `aliased` means stable alternative names dominate; `none` means no stable name is evidenced.

The independent verifier must revisit the batch without relying on the researchers' confidence. It checks mechanism equivalence, tier admission, source independence, quote support, truthful dates, terminology, local manifest binding, and exact ledger projection. It may open or re-fetch only exact URLs already present in the assigned evidence; it performs no search or discovery query and introduces no candidate URL. Each deterministic batch of up to three patterns receives two bounded verifier turns: an initial review, then a final review after the parent resolves findings. No material evidence field may change after the final review, and a failed final review stops the plan rather than starting an unapproved third turn. No verifier reviews the discovery-only unit, and researchers receive no retry or follow-up turn under the plan. Deterministic scripts separately check ledger scope, mode coverage, event hash chains, queries/counts, schema, content hashes, changed-path scope, derived values, duplicate URLs, secrets, pending-list consistency, and generated status. `none found` cannot complete without a fully reconciled three-mode ledger.

## Discovery unit

Discovery looks for recurring, implemented AI-development practices not already represented by a stable or exploratory catalog entry. Return a candidate only when it has a clear mechanism, a distinct problem/outcome, and at least one direct artifact or practitioner source. Report possible overlaps explicitly. The parent task is the sole writer and decides whether a candidate note belongs in `experiments/NOTES.md`; discovery never creates or renames a catalog pattern.
Use no more than 12 live search queries for the discovery unit, counting retries and variants, so the planner's displayed maximum remains a real upper bound. Return the same sanitized receipts with unit and mode `discovery`; the parent records them in the approved run's ledger.
