# Pipeline Synthesis Example

This example implements the experimental [Pipeline Synthesis](../../README.md#pipeline-synthesis) pattern: convert a reviewed plain-language delivery specification into validated build, deployment, and release workflows, where executable checks and a human approval gate — not the model — arbitrate what ships.

## Current Status

This directory ships documentation only: this README plus two specification documents, [`ci_spec.md`](ci_spec.md) and [`blue_green_deployment.md`](blue_green_deployment.md). The pipeline generators, reusable templates, and validation tooling the pattern describes are documented concepts, not shipped code; adopters supply their own generation prompts and platform-native validators (for example, `actionlint` for GitHub Actions workflows).

## Files

- [`ci_spec.md`](ci_spec.md) — plain-English CI/CD pipeline specification covering dependency installation, quality checks, testing, security validation, build artifacts, environment-specific configuration, quality gates, failure handling, monitoring, and compliance. This is the source document an agent converts into platform-specific configuration.
- [`blue_green_deployment.md`](blue_green_deployment.md) — blue-green deployment extension: the atomic traffic-switch invariants, illustrative AWS and Kubernetes reference implementations, canary-versus-blue-green anti-pattern detection, and deployment checklists.
- [`../../../docs/agentic-cicd.md`](../../../docs/agentic-cicd.md) - Extended, non-normative EARS requirements input for review and tailoring

## Quick Start

Use the shipped specification as the input contract, then validate the generated output with platform-native tooling. The `ai` command below stands in for whichever coding-agent CLI you use.

```bash
# Generate pipeline configuration from the shipped specification
ai "Generate a GitHub Actions workflow from the specification in ci_spec.md:
- Include all specified quality gates and thresholds
- Pin third-party actions to commit SHAs
- Add proper error handling
- Enable caching for performance"

# Validate the generated workflow with a platform-native validator
actionlint .github/workflows/ci.yml
```

Generate into a reviewable branch and run the workflow in a disposable environment before promotion. The model may propose a workflow, but schema checks, dry runs, and an approval gate decide whether it can deploy.

## Validated Blue-Green Deployment

Deployment generation is a pipeline concern, not a separate synthesis pattern. Add the invariants in [`blue_green_deployment.md`](blue_green_deployment.md) to the delivery specification, then validate that the generated workflow:

1. deploys only to the idle environment;
2. runs health and smoke checks before switching traffic;
3. switches 100% of traffic atomically rather than performing a canary rollout; and
4. retains the previous environment as the rollback target.

## Deterministic Release Notes

Release notes should come from a pinned, machine-readable commit range. Use AI only for an optional reviewed summary; never let it decide which commits belong to the release.

```bash
BASE_SHA=$(git merge-base origin/main HEAD)
HEAD_SHA=$(git rev-parse HEAD)

# Deterministic input and grouping from conventional commits.
git log --format='%H%x09%s' "$BASE_SHA..$HEAD_SHA" > release-commits.tsv
git cliff "$BASE_SHA..$HEAD_SHA" --strip header > RELEASE_NOTES.md

# Preserve provenance beside the generated notes.
printf 'base=%s\nhead=%s\n' "$BASE_SHA" "$HEAD_SHA" > RELEASE_NOTES.provenance
test -s release-commits.tsv && test -s RELEASE_NOTES.md
```

Fail when the range is empty, a referenced commit is unavailable, or conventional-commit parsing rejects an entry. Those conditions must remain visible rather than being filled with invented prose.

## Known Limitations

- Generation and validation tooling is described, not shipped; adopters supply prompts, templates, and validators for their target platform (GitHub Actions, GitLab CI, Jenkins, or others).
- [`ci_spec.md`](ci_spec.md) targets an illustrative Python, Docker, and Kubernetes application; thresholds, commands, and integrations need adaptation to each repository.
- The scripts in [`blue_green_deployment.md`](blue_green_deployment.md) are reference implementations with placeholder account IDs and resource names, not drop-in automation.
- A generated workflow that passes syntax validation still proves nothing about runtime behavior; disposable-environment runs and human approval remain required before it can deploy.

## Promotion Path

Promotion requires executable specification-to-configuration generators and validators for at least two CI/CD platforms, evidence that generated pipelines pass platform-native validation and run correctly in disposable environments, enforcement of the blue-green invariants as machine checks, and independent practitioner adoption beyond hand-written pipeline configuration.

## Anti-pattern: Confused Deployment

Mixing blue-green and canary semantics — gradual percentage-based traffic shifting inside a workflow labeled blue-green — produces an unreviewable strategy whose rollback behavior differs from the stated requirement. Detect and fail on canary vocabulary in blue-green scripts, as shown in [`blue_green_deployment.md`](blue_green_deployment.md).
