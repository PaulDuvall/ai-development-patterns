# Image Spec Example

This example provides a repeatable, image-first workflow for the [Image Spec](../../README.md#image-spec) pattern: use diagrams and mockups as primary specifications, then iterate with annotated visuals.

## Workflow

1. Create a **single** high-level diagram (architecture, UI mock, or flow) with labels and constraints (ports, component names, state transitions).
2. Attach the image and provide a short prompt that clarifies only what the image cannot (tech stack, scope, constraints).
3. Run the generated result, capture a screenshot, and annotate what’s missing or incorrect.
4. Re-attach the annotated image and iterate on one slice at a time.

## Recommended Image Set

- `architecture.png`: components + boundaries + ports
- `data-model.png`: fields + relationships + example payloads
- `ui-mock.png`: layout + key interactions
- `flow.png`: sequence of steps + decision points

## Prompt Template

```text
Build the system from the attached images.
Tech stack: <stack>
Scope: <what to implement first>
Constraints: <performance/security/testing constraints>
Output: code + tests + a short runbook
```

