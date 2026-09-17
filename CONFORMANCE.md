# Delivery Conformance

This repository is scored against [MinimumCD](https://minimumcd.org/), the
[Agentic CD](https://beyond.minimumcd.org/docs/agentic-cd/) repo-readiness rubric, and the
[AWS Deployment Pipeline Reference Architecture](https://aws-samples.github.io/aws-deployment-pipeline-reference-architecture/application-pipeline/index.html)
security practices by [Ratchet](https://github.com/PaulDuvall/ratchet).

Ratchet is report-only: it never fails a build, never opens a pull request, and never writes to
the repository it analyses. This file is the maintainer's standing answer to the rules it reports
as gaps — the record of which are deliberate positions and which are measurement artifacts.

Ratchet reaching no verdict is not a failing grade. A rule it cannot assess is counted in neither
total, for or against.

## Deliberate positions

### ACD-1 — Agents cannot self-promote

**Rule:** the default branch is protected, at least one approving review is required, and no bot
bypass actors exist.

**State:** the `Protect main with adoption evidence validation` ruleset is active with
`required_approving_review_count: 0` and an empty `bypass_actors` list.

**Decision: keep zero required approvals.** This repository has one maintainer. GitHub does not
permit a pull request author to approve their own pull request, so requiring one approval would
make every change unmergeable without a second account or a bypass actor — and a bypass actor is
itself what ACD-1 counts against. The rule assumes a team, and there is no configuration of it
that a solo maintainer can satisfy honestly.

What does gate change:

- The ruleset requires pull requests to `main`, blocks non-fast-forward pushes, and blocks branch
  deletion.
- Three status checks are required to pass before merge: `Validation gate`,
  `Trusted evidence checks`, and `Dependency Review`.
- `required_review_thread_resolution` is enabled, so an unresolved review thread blocks merge.
- Changes to the trust root — `tests/`, `scripts/`, `.github/workflows/` — require an explicit
  owner approval comment naming the head SHA, re-issued after any branch update.

ACD-1 is therefore reported as an open self-promotion path and left open by choice. Revisit if a
second maintainer joins.

### MCD-TBD-1 — Longest-lived unmerged branch

Branch age alone does not separate a neglected branch from a deliberately held one. Ratchet says
as much in the rule's own note: long-lived branches are indistinguishable from stale feature
branches by commit topology.

A pull request held pending a maintainer decision — a naming review, a rubric question, an
evidence identity that has to be rebound before the work can land — ages exactly like an abandoned
one and is counted the same way. A held pull request states the hold in its title and body.

**Check the named branch before acting on this rule.** Evidence pull requests in particular bind
their approved run and evidence identity to a pattern slug, so a requested rename invalidates the
evaluation rather than merely retitling it, and the work must be re-run rather than merged.

## Measurement artifacts

Four rules report *not assessed* because the analysing token cannot read repository
administration, not because the control is absent. Ratchet declines to guess, which is the correct
behaviour: it reports no verdict rather than a fabricated gap.

| Rule | Ratchet verdict | Configured state |
| --- | --- | --- |
| `DPRA-SEC-1` Secrets detection | not assessed | secret scanning enabled; push protection enabled |
| `DPRA-SEC-2` Static analysis | not assessed | code scanning configured — extended query suite, weekly |
| `DPRA-SEC-3` Dependency scanning | not assessed | Dependabot security updates enabled; `dependency-review-action` gates every pull request |
| `ACD-1` Self-promotion | not assessed | readable with an administration-scoped token; see the decision above |

Closing this gap is a change to the analysing workflow, not to this repository: the dashboard run
needs a fine-grained token carrying `Administration: Read`. The procedure is documented in
Ratchet's `docs/DASHBOARD-TOKEN.md`.

`DPRA-SEC-4` and `DPRA-SEC-5` look for a signed SBOM attestation and signed build provenance on a
released artifact. This repository publishes patterns and evidence rather than a build artifact
and has no releases, so there is no subject digest to attest and no verdict to reach.

## Rules that report and never gate

`MCD-CI-2` measures pull request size and `ACD-5` measures whether a delivery artifact ships
alongside a source change. Both are advisory in Ratchet and neither is wired to enforcement here.

`ACD-5` identifies delivery artifacts by path convention. Evidence refresh changes in
`verification/` carry their intent in the evidence YAML itself, which the convention does not
always recognise as an artifact.

## Rules with a trailing window

`MCD-CI-3` measures the share of merges that landed on a passing check rollup across a ninety-day
window. The ruleset that requires status checks was created on 2026-07-10, so merges predating it
were never gated and continue to weigh on the figure until they age out of the window.

The rollup covers every check on the pull request, not only the required ones, so a failing
advisory check lowers the figure even where the required gate held.
