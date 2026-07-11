# Security Orchestration Example

This example documents the experimental [Security Orchestration](../../README.md#security-orchestration) pattern: aggregate the output of multiple security scanning tools, then use AI to deduplicate, prioritize, and summarize findings into a single actionable review artifact instead of a pile of disconnected alerts.

## Current Status

This is a documented concept and design reference only. The directory contains this README and no implementation files — there is no orchestration script, summarizer, tool configuration, or CI/CD integration to run here. All code below is illustrative design showing the intended shape of an implementation, not shipped files.

## Pattern Boundary

Individual scanners (dependency auditors, SAST linters, container scanners) already detect issues well. This pattern begins where their combined output becomes the problem:

- collect machine-readable results from each scanner in one place;
- deduplicate findings that multiple tools report for the same issue;
- prioritize by exploitability and blast radius rather than raw severity labels;
- summarize into a reviewable artifact (for example, a pull request comment); and
- keep the source scanners authoritative — the model groups and explains, but never silently lowers a severity or erases a scanner result.

## Design Sketch

An implementation of this pattern would follow the pipeline shape below. The commands assume the scanner CLIs and an AI CLI are installed in the adopting repository; nothing in this directory provides them.

```bash
# Illustrative pipeline — not runnable from this directory
snyk test --json > snyk.json
bandit -r src -f json > bandit.json
trivy fs --format json . > trivy.json
ai "Deduplicate these findings and summarize critical issues with source tool and rule IDs" \
  snyk.json bandit.json trivy.json > pr-comment.md
gh pr comment --body-file pr-comment.md
```

Design constraints an implementation should preserve:

- **Traceability**: every summarized finding retains its source tool, rule ID, file, and revision.
- **Suppression rationale**: any finding the summary demotes or groups must carry an explicit reason, reviewable by a human.
- **Scanner authority**: the AI layer is a presentation and prioritization aid; scanner output remains the system of record.
- **Pipeline placement**: aggregation runs after all scanners complete, so a scanner failure surfaces as a missing input rather than a silently thinner summary.

Related patterns in the stable catalog: [Tool Integration](../../../README.md#tool-integration) for wiring scanners into agent-accessible workflows, and [Policy Generation](../../../README.md#policy-generation) for turning recurring findings into enforced policy.

## Known Limitations

- No reference implementation exists here to validate the design against real scanner output.
- Deduplication quality depends on how consistently tools identify the same underlying issue; naive matching either merges distinct findings or misses duplicates.
- An AI summary can misjudge exploitability; without the traceability constraints above, a wrong summary hides real findings.
- Summarization adds model cost and latency to every scan run, which matters at CI frequency.

## Promotion Path

Promotion to the stable catalog requires a working reference implementation (orchestration script, summarizer, and example scanner configurations), evidence that AI summarization reduces triage time without suppressing true positives, and independent practitioner adoption beyond single-tool scanning workflows.

## Anti-pattern: Summarizer as Suppressor

Letting the AI layer decide which findings are "not worth showing" — without retaining the full scanner output and a per-finding suppression rationale — converts alert fatigue into silent risk acceptance. The summary must compress presentation, not evidence.
