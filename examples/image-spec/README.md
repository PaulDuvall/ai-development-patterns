# Image Spec Example

This example provides a repeatable [Image Spec](../../README.md#image-spec) workflow: translate one screenshot or design mockup into UI code, then refine it with annotated visual feedback. Industry aliases include *design-to-code* and *screenshot-to-code*.

## Workflow

1. Choose a **single** UI screenshot or mockup and name the state it represents.
2. Attach it with a short prompt that supplies only the missing behavior, stack, accessibility, and component-library constraints.
3. Run the generated UI, capture a screenshot, and annotate visual differences.
4. Re-attach the annotated screenshot and iterate on one screen or state at a time.

## Recommended Inputs

- `checkout-empty.png`: empty-cart layout and calls to action
- `checkout-filled.png`: populated state, totals, and validation placement
- `checkout-mobile.png`: responsive target at the named viewport
- `design-tokens.json`: non-visual constraint referenced by the prompt

## Prompt Template

```text
Implement the attached <screen/state> as a <framework> component.
Match: <layout, spacing, colors, typography, responsive viewport>.
Reuse: <existing tokens and component library>.
Behavior not visible in the image: <interactions and validation>.
Do not invent: <backend behavior or unshown screens>.
Output: component + focused interaction/accessibility tests.
```

Architecture and flow diagrams may accompany the prompt as context, but this pattern does not treat them as independently verified executable specifications.
