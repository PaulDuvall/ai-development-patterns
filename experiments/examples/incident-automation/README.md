# Incident Automation Example

This example supports the experimental [Incident Automation](../../README.md#incident-automation) pattern: derive and execute governed incident-response workflows from telemetry, current system state, and historical incidents. It provides a worked incident response playbook showing what pattern outputs look like — severity classification, per-incident runbooks, AI analysis prompts, and communication templates.

## Current Status

This example ships two files: this README and [`incident_playbook.md`](incident_playbook.md), a reference playbook document. The automation itself — runbook generation from incident history, automated triage and routing, historical pattern analysis, and alert optimization — is described in the pattern but has no executable implementation here. The kubectl, psql, and `ai` commands inside the playbook are illustrative templates targeting a fictional Kubernetes environment; adapt them to your infrastructure before use.

## Pattern Boundary

Static runbooks already tell responders what to do for known failures. This pattern begins when response procedures are derived from evidence and kept current:

- classify incidents by severity with explicit response and escalation times;
- generate runbook steps from telemetry, deployment history, and prior incidents;
- separate reversible automated actions from actions requiring human approval;
- feed post-incident findings back into the playbooks; and
- record which evidence justified each step.

## Files

- [`incident_playbook.md`](incident_playbook.md) — reference playbook containing a P1–P4 severity classification scheme, five worked incident runbooks (database connection pool exhaustion, authentication service degradation, production memory leak, API gateway overload, data inconsistency), a health-check script template, AI prompts for root-cause analysis and incident summaries, communication templates, and post-incident procedures.

## Using the Playbook

Treat `incident_playbook.md` as a starting structure, not a drop-in artifact:

1. Replace the illustrative namespaces, deployment names, and connection details with your own.
2. Wire the AI prompts into whatever assistant or CLI your team uses.
3. Test each runbook's steps in a sandbox before an incident, as the pattern requires.
4. After each real incident, update the affected runbook so procedures reflect observed failure modes.

## Known Limitations

- No triage automation, historical-analysis tooling, or alert-optimization code is included; those capabilities exist only as pattern description.
- The playbook's commands assume a specific fictional Kubernetes setup and will not run unmodified.
- The `ai "..."` invocations assume an AI CLI wrapper that adopters must supply.
- The playbook is a static document; the pattern's continuous-improvement loop must be operated manually until generation tooling exists.

## Promotion Path

Promotion requires an executable workflow that generates triage documents and runbooks from real incident history, sandbox verification of generated steps, demonstrated separation of reversible actions from approval-gated actions, and independent practitioner adoption with evidence that derived runbooks outperform static ones.

## Anti-pattern: Static Runbooks

Maintaining response procedures that never incorporate observed failure modes causes responders to repeat obsolete or unsafe steps during an incident. A playbook like this one only delivers the pattern's value when post-incident learnings flow back into it.
