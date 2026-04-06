Audit and fix the experiments/ directory (experiments/README.md, experiments/NOTES.md, and all experiments/examples/**/README.md plus their supporting files). Run these checks in parallel, then fix what you find:

1. Runnable code audit: For every fenced code block (python, bash, yaml, json), verify:
   - Python: imports exist in stdlib/PyPI, function signatures match real APIs, class definitions are syntactically valid. Flag datetime.utcnow(), Pydantic v1 syntax, and other deprecated calls.
   - Bash: commands and flags are real (no fabricated CLI options). Verify referenced file paths (e.g., scripts/promote-test.sh, .ai/hooks/protect-golden.sh) exist on disk where claimed.
   - YAML: valid syntax, correct GitHub Actions schema (uses: keys reference real actions at current major versions), Docker Compose v2 syntax (not v1 version: key).
   - Mermaid: valid diagram syntax (matching graph/sequenceDiagram/flowchart keywords, balanced brackets, no dangling edges).
   Prioritize anything that would fail if copy-pasted.

2. Pattern spec compliance (against pattern-spec.md): Each pattern in experiments/README.md must have:
   - Two-word Title Case name (per naming rules)
   - Maturity, Description, Related Patterns fields
   - At least one implementation section
   - An Anti-pattern section
   - All Related Patterns hyperlinked with working anchors
   Flag any pattern missing required sections or violating naming rules.

3. Internal consistency:
   - Cross-check the experiments/examples/README.md index against actual subdirectories in experiments/examples/ (flag missing or extra entries).
   - Verify that file references in any README (e.g., "see scripts/promote-test.sh") match actual filenames on disk.
   - Check that Mermaid diagram node labels match the pattern names used in prose and the reference table.

4. Link integrity: Verify every internal anchor link resolves correctly. Apply GitHub's anchor generation rules:
   - lowercase, spaces to hyphens, strip punctuation except hyphens
   - special chars like & are omitted (not double-dash)
   - duplicate anchors get -1, -2 suffixes
   Flag any broken anchor references.

5. Security review of examples: In all Python, Bash, and YAML files under experiments/examples/:
   - No hardcoded credentials, tokens, or API keys
   - Shell scripts quote variables and validate inputs
   - File operations check for path traversal (no unsanitized user input in open()/os.path.join())
   - Claims of read-only or network_mode: none are actually enforced in the code/config
   - File permission claims (e.g., chmod 444) match what the scripts actually set

For each issue found, fix it directly in the file rather than just reporting it. After all fixes, provide a summary grouped by check category with file:line references.
