# Test Promotion Threat Model

Golden tests are valuable only when the actor generating code cannot also weaken, delete, or approve
the contracts used to grade that code. This example provides templates; it does not establish the
repository controls merely by storing them under this nested example directory.

## Required Trust Assumptions

Before treating promotion as a binding control, an adopter must:

1. Copy the workflow to the repository-root `.github/workflows/` directory and require its check.
2. Merge the sample rule into the active root CODEOWNERS file, replace placeholder owners, and
   require code-owner review.
3. Protect the workflow, CODEOWNERS file, and branch/ruleset configuration from unreviewed candidate
   changes, for example with a trusted-base validation workflow and owner approval.
4. Prevent the generating agent from approving its own pull request or changing repository rules.
5. Review changes to the golden-test harness and production code; a protected assertion can still
   be meaningless or grade the wrong behavior.

Without these assumptions, the files in this example are documentation and local guardrails, not
an unbypassable security boundary.

## Threats and Controls

### Assertion weakening

**Threat:** The generator changes an existing assertion so buggy production code passes.

**Binding control:** The required root workflow rejects modifications, renames, and deletions under
`tests/golden/`. Required CODEOWNERS review is still needed for changes to the control itself.

### Contract deletion

**Threat:** The generator deletes a failing golden test.

**Binding control:** Deletion is a non-addition and the required workflow rejects it.

### Unreviewed test addition

**Threat:** The generator adds a weak or irrelevant test and labels it golden.

**Binding control:** A `test-promotion` label makes an addition structurally eligible; it does not
approve it. Required CODEOWNERS review owns the semantic promotion decision.

### Shell or file-mode bypass

**Threat:** A shell-capable agent changes `444` to `644`, edits a contract, then restores the mode.

**Control:** Git does not preserve `444`, so file mode is only an accidental-edit guard in one
checkout. The commit-bound diff check, not the local mode, detects the content change.

### Hook bypass

**Threat:** The agent bypasses a normal Edit/Write hook through shell commands or another tool.

**Control:** The hook reduces accidental and tool-mediated edits but is advisory. Required CI and
human review remain authoritative.

### Trust-root modification

**Threat:** The same pull request weakens the workflow, CODEOWNERS, or rules that protect golden
tests.

**Control:** An owner-approved trusted-base policy must protect those files. The sample workflow
does not solve this threat by itself.

### Human approval failure

**Threat:** An approver accepts a misleading, flaky, or self-serving golden test.

**Control:** Review checklists, separation of duties, deterministic test execution, flake analysis,
and multiple owners for high-impact contracts. Technical controls cannot eliminate social
engineering or careless approval.

## Control Summary

| Layer | Purpose | Binding? | Principal limitation |
|---|---|---:|---|
| Local `444` mode | Discourage accidental writes | No | Not preserved by Git; shell can change it |
| Assistant hook | Block ordinary Edit/Write tools | No | Other tools and shell can bypass it |
| Required root diff check | Reject non-addition golden changes | Yes, when protected | Same-PR trust-root changes must be gated |
| Required CODEOWNERS review | Human decision on additions | Yes, when configured | Approvers can make mistakes |
| Branch/ruleset protection | Protect checks and ownership | Yes, when configured | Repository administrators retain authority |

## Validation Exercises

After installing and protecting the root controls, use a disposable branch to verify:

1. An unlabeled golden addition fails the required check.
2. A labeled addition passes the structural check but still requires CODEOWNERS review.
3. A labeled modification, rename, or deletion fails.
4. A proposed change to the protection workflow or CODEOWNERS requires owner review.
5. Removing local `444` mode does not bypass the commit-bound diff check.

Record the resulting check URLs and ruleset configuration in the adopting repository. Do not infer
protection from a local permission error or from the presence of these template files.
