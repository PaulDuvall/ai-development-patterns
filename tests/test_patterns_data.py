"""
Tests for the patterns website dataset generator.

Verifies that assets/js/patterns-data.js (which powers the interactive patterns
page) stays in sync with README.md - the single source of record - and that the
generated data is well-formed.
"""

import importlib.util
import json
import re
import subprocess
import sys

import pytest

from conftest import EXPECTED_PATTERNS, README_PATH, REPO_ROOT

SCRIPT_PATH = REPO_ROOT / "scripts" / "generate-patterns-data.py"
DATA_PATH = REPO_ROOT / "assets" / "js" / "patterns-data.js"
INDEX_PATH = REPO_ROOT / "index.html"

VALID_CATEGORIES = {"foundation", "development", "operations"}
VALID_MATURITIES = {"Beginner", "Intermediate", "Advanced"}


def _load_generator():
    """Import the hyphenated generator script as a module."""
    spec = importlib.util.spec_from_file_location("generate_patterns_data", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generator():
    return _load_generator()


@pytest.fixture(scope="module")
def dataset(generator):
    """Freshly parsed dataset from README.md."""
    return generator.build_dataset()


@pytest.fixture(scope="module")
def data_file_dataset():
    """The dataset as currently committed in assets/js/patterns-data.js."""
    text = DATA_PATH.read_text(encoding="utf-8")
    # The file is `window.PATTERNS_DATA = {...};` preceded by // comments (no
    # braces). Slice from the first { to the last } so embedded ';' in body
    # markdown can never confuse the parse.
    start, end = text.index("{"), text.rindex("}")
    return json.loads(text[start:end + 1])


class TestArtifactsInSync:
    def test_check_mode_passes(self):
        """`--check` confirms the committed artifacts match README.md."""
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--check"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, (
            "patterns-data.js / index.html are out of sync with README.md.\n"
            f"{result.stdout}\n{result.stderr}\n"
            "Run: python3 scripts/generate-patterns-data.py"
        )

    def test_data_file_matches_fresh_render(self, generator, dataset):
        """The committed data file equals a fresh render (no manual drift)."""
        expected = generator.render_data_js(dataset)
        assert DATA_PATH.read_text(encoding="utf-8") == expected

    def test_generation_is_idempotent(self, generator, dataset):
        rendered_once = generator.render_data_js(dataset)
        rendered_twice = generator.render_data_js(generator.build_dataset())
        assert rendered_once == rendered_twice


class TestDatasetShape:
    def test_data_file_exists_and_parses(self, data_file_dataset):
        assert isinstance(data_file_dataset, dict)
        for key in ("patternCount", "categories", "patterns", "dependencyDiagram"):
            assert key in data_file_dataset, f"missing key: {key}"

    def test_pattern_count_matches_readme_table(self, data_file_dataset):
        assert data_file_dataset["patternCount"] == len(EXPECTED_PATTERNS)
        assert len(data_file_dataset["patterns"]) == len(EXPECTED_PATTERNS)

    def test_all_readme_patterns_present(self, data_file_dataset):
        names = {p["name"] for p in data_file_dataset["patterns"]}
        missing = set(EXPECTED_PATTERNS) - names
        assert not missing, f"Patterns in README but missing from dataset: {missing}"

    def test_pattern_ids_unique(self, data_file_dataset):
        ids = [p["id"] for p in data_file_dataset["patterns"]]
        dupes = {i for i in ids if ids.count(i) > 1}
        assert not dupes, f"Duplicate pattern ids: {dupes}"

    def test_category_counts_consistent(self, data_file_dataset):
        patterns = data_file_dataset["patterns"]
        total = 0
        for cat in data_file_dataset["categories"]:
            actual = sum(1 for p in patterns if p["category"] == cat["id"])
            assert cat["count"] == actual, f"{cat['id']} count mismatch"
            total += cat["count"]
        assert total == data_file_dataset["patternCount"]


class TestPatternRecords:
    def test_every_pattern_is_well_formed(self, data_file_dataset):
        problems = []
        for p in data_file_dataset["patterns"]:
            if not p.get("name"):
                problems.append(f"{p.get('id')}: empty name")
            if p.get("maturity") not in VALID_MATURITIES:
                problems.append(f"{p['id']}: bad maturity {p.get('maturity')!r}")
            if p.get("category") not in VALID_CATEGORIES:
                problems.append(f"{p['id']}: bad category {p.get('category')!r}")
            if not (p.get("shortDescription") or "").strip():
                problems.append(f"{p['id']}: empty shortDescription")
            if len((p.get("bodyMarkdown") or "").strip()) < 40:
                problems.append(f"{p['id']}: body too short")
            if p.get("githubUrl") != f"{data_file_dataset['repoUrl']}#{p['id']}":
                problems.append(f"{p['id']}: bad githubUrl")
        assert not problems, "Malformed patterns:\n" + "\n".join(problems)

    def test_dependencies_reference_known_patterns(self, data_file_dataset):
        ids = {p["id"] for p in data_file_dataset["patterns"]}
        broken = []
        for p in data_file_dataset["patterns"]:
            for dep in p.get("dependencies", []):
                assert dep.get("name"), f"{p['id']}: empty dependency name"
                if dep.get("id") is not None and dep["id"] not in ids:
                    broken.append(f"{p['id']} -> {dep}")
        assert not broken, f"Dependencies pointing at unknown patterns: {broken}"

    def test_body_excludes_next_pattern_heading(self, data_file_dataset):
        """Section extraction must stop before the next pattern's H2/H3 heading."""
        names = {p["name"] for p in data_file_dataset["patterns"]}
        # A real (non-fenced) heading for ANOTHER pattern must not appear in a body.
        offenders = []
        for p in data_file_dataset["patterns"]:
            in_fence = False
            for line in p["bodyMarkdown"].split("\n"):
                stripped = line.strip()
                if stripped.startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                m = re.match(r"^#{2,3}\s+(.+?)\s*$", line)
                if m and m.group(1).strip() in names and m.group(1).strip() != p["name"]:
                    offenders.append(f"{p['id']} bleeds into '{m.group(1).strip()}'")
        assert not offenders, "Section boundary leaks:\n" + "\n".join(offenders)


class TestLenses:
    def test_known_lenses_present(self, data_file_dataset):
        ids = {l["id"] for l in data_file_dataset.get("lenses", [])}
        for expected in ("harness-engineering-lens", "loop-engineering-lens"):
            assert expected in ids, f"{expected} missing from dataset lenses"

    def test_lens_count_matches_readme(self, data_file_dataset):
        readme = README_PATH.read_text(encoding="utf-8")
        in_fence = False
        heading_lenses = 0
        for line in readme.split("\n"):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = re.match(r"^##\s+(.+?)\s*$", line)
            if m and m.group(1).strip().lower().endswith("lens"):
                heading_lenses += 1
        assert len(data_file_dataset.get("lenses", [])) == heading_lenses

    def test_lenses_well_formed(self, data_file_dataset):
        problems = []
        for l in data_file_dataset.get("lenses", []):
            if not l.get("name", "").lower().endswith("lens"):
                problems.append(f"{l.get('id')}: name should end with 'Lens'")
            if not (l.get("shortDescription") or "").strip():
                problems.append(f"{l.get('id')}: empty shortDescription")
            if len((l.get("bodyMarkdown") or "").strip()) < 40:
                problems.append(f"{l.get('id')}: body too short")
            if l.get("githubUrl") != f"{data_file_dataset['repoUrl']}#{l['id']}":
                problems.append(f"{l.get('id')}: bad githubUrl")
        assert not problems, "Malformed lenses:\n" + "\n".join(problems)


class TestDependencyDiagram:
    def test_diagram_matches_readme_first_mermaid(self, data_file_dataset):
        readme = README_PATH.read_text(encoding="utf-8")
        match = re.search(r"```mermaid\n(.*?)```", readme, re.DOTALL)
        assert match, "README has no mermaid diagram"
        assert data_file_dataset["dependencyDiagram"] == match.group(1).rstrip("\n")

    def test_index_renders_generated_site_diagram(self, data_file_dataset):
        """index.html's injected diagram is the branded, data-driven siteDiagram."""
        index = INDEX_PATH.read_text(encoding="utf-8")
        assert "PATTERNS:DIAGRAM:START" in index
        assert "PATTERNS:DIAGRAM:END" in index
        block = re.search(
            r'<div class="mermaid">\s*(.*?)\s*</div>', index, re.DOTALL
        )
        assert block, "index.html has no mermaid diagram block"
        assert block.group(1).strip() == data_file_dataset["siteDiagram"].strip()

    def test_site_diagram_covers_every_pattern_with_clicks(self, data_file_dataset):
        diagram = data_file_dataset["siteDiagram"]
        for p in data_file_dataset["patterns"]:
            node = p["id"].replace("-", "_")
            assert f'{node}[' in diagram, f"{p['id']} missing as a diagram node"
            assert f"click {node} openPatternFromDiagram" in diagram, \
                f"{p['id']} missing an in-page click handler"
        for cat in ("foundation", "development", "operations"):
            assert f"classDef {cat}" in diagram


class TestParserRobustness:
    def test_trim_removes_related_anywhere(self, generator):
        body = (
            "**Maturity**: Beginner\n**Description**: keep me\n\n"
            "> quick start note\n\n**Related Patterns**: [A](#a)\n\nReal body."
        )
        out = generator.trim_redundant_meta(body)
        assert "**Maturity**" not in out
        assert "**Related Patterns**" not in out
        assert "**Description**" in out and "Real body." in out

    def test_parse_headings_handles_quad_backtick_fence(self, generator):
        md = "## Real\n\n````markdown\n## Not A Heading\n```\ninner\n```\n````\n\n## After\n"
        heads = [h["text"] for h in generator.parse_headings(md.split("\n"))]
        assert "Real" in heads and "After" in heads
        assert "Not A Heading" not in heads

    def test_reference_table_handles_escaped_pipe(self, generator):
        table = (
            "## Complete Pattern Reference\n\n"
            "| Pattern | Maturity | Type | Description | Dependencies |\n"
            "|--|--|--|--|--|\n"
            "| **[Foo](#foo)** | Beginner | Development | uses `a \\| b` | None |\n\n"
            "## Next\n"
        )
        rows = generator.parse_reference_table(table)
        assert len(rows) == 1
        assert rows[0]["description"] == "uses `a | b`"
        assert rows[0]["deps_raw"] == "None"

    def test_dependency_resolution_fails_loud_on_unknown(self, generator):
        with pytest.raises(ValueError):
            generator.resolve_deps("Nonexistent Pattern", {"Foo": "foo"})

    def test_inject_diagram_raises_clear_error_without_markers(self, generator):
        with pytest.raises(ValueError, match="PATTERNS:DIAGRAM"):
            generator.inject_index_diagram("<html>no markers</html>", "graph TD; A-->B")


class TestRefreshMechanism:
    """Guard the instrumentation that keeps the website in sync with README.md.

    These tests fail if the auto-refresh wiring is ever removed, so the
    'README changes -> site rebuilds' guarantee cannot silently regress."""

    WORKFLOWS = REPO_ROOT / ".github" / "workflows"
    BUILD = REPO_ROOT / "scripts" / "build.sh"

    def test_build_script_rebuilds_from_readme(self):
        assert self.BUILD.exists(), "scripts/build.sh (canonical build entrypoint) is missing"
        text = self.BUILD.read_text(encoding="utf-8")
        assert "generate-patterns-data.py" in text

    def test_deploy_rebuilds_on_every_push(self):
        deploy = (self.WORKFLOWS / "deploy-pages.yml").read_text(encoding="utf-8")
        # Triggers on push to main (covers any README.md change)…
        assert re.search(r"push:\s*\n\s*branches:\s*\[?\s*main", deploy)
        # …and rebuilds from README before publishing.
        assert "build.sh" in deploy or "generate-patterns-data.py" in deploy

    def test_validation_blocks_readme_drift(self):
        validation = (self.WORKFLOWS / "pattern-validation.yml").read_text(encoding="utf-8")
        assert "generate-patterns-data.py --check" in validation

    def test_precommit_hook_available(self):
        hook = REPO_ROOT / "scripts" / "pre-commit-patterns.sh"
        assert hook.exists(), "scripts/pre-commit-patterns.sh is missing"
        assert "build.sh" in hook.read_text(encoding="utf-8")


class TestSiteAssetsTracked:
    """Guard against .gitignore silently dropping committed site assets.

    The macOS 'Icon?' rule once matched the assets/icons/ directory
    (case-insensitive on macOS), so favicons under it were never committed."""

    @pytest.mark.parametrize("path", [
        "assets/icons/example.svg",
        "assets/img/example.svg",
        "assets/css/example.css",
        "assets/js/example.js",
    ])
    def test_asset_paths_are_not_gitignored(self, path):
        result = subprocess.run(
            ["git", "check-ignore", path],
            cwd=str(REPO_ROOT), capture_output=True, text=True,
        )
        # git check-ignore: returncode 0 == ignored, 1 == NOT ignored.
        assert result.returncode == 1, (
            f"{path} is gitignored — committed site assets there would silently "
            f"never ship. Offending rule: {result.stdout.strip()}"
        )
