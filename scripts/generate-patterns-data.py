#!/usr/bin/env python3
"""
Generate the patterns dataset that powers the interactive patterns website.

README.md is the single source of record. This script parses it at build time
and emits two synced artifacts:

  1. assets/js/patterns-data.js  - window.PATTERNS_DATA consumed by the web page
                                (card metadata, brief descriptions, full
                                 per-pattern markdown, the README dependency
                                 diagram, and a generated branded siteDiagram)
  2. index.html               - the Mermaid diagram block between the
                                <!-- PATTERNS:DIAGRAM:START/END --> markers is
                                refreshed with the generated, in-page-clickable
                                siteDiagram (built from parsed dependencies),
                                keeping the page in sync with README content.

Usage:
    python3 scripts/generate-patterns-data.py          # write artifacts
    python3 scripts/generate-patterns-data.py --check   # verify in sync (CI/tests)

Stdlib only - no third-party dependencies.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"
DATA_PATH = REPO_ROOT / "assets" / "js" / "patterns-data.js"
INDEX_PATH = REPO_ROOT / "index.html"

REPO_URL = "https://github.com/PaulDuvall/ai-development-patterns"

DIAGRAM_START = "<!-- PATTERNS:DIAGRAM:START (generated from README.md - do not edit) -->"
DIAGRAM_END = "<!-- PATTERNS:DIAGRAM:END -->"

# Canonical three-tier grouping keyed by the enclosing H1 section in README.
CATEGORY_BY_H1 = {
    "Foundation Patterns": "foundation",
    "Development Patterns": "development",
    "Operations Patterns": "operations",
}

CATEGORY_META = {
    "foundation": {
        "name": "Foundation",
        "blurb": "Establish team readiness, security, and the basics of AI integration.",
        "accent": "#2d5a3f",
        "icon": "🟢",
    },
    "development": {
        "name": "Development",
        "blurb": "Daily workflows for AI-assisted coding, planning, and review.",
        "accent": "#b7950b",
        "icon": "🟡",
    },
    "operations": {
        "name": "Operations",
        "blurb": "CI/CD, security, compliance, and production management with AI.",
        "accent": "#c0392b",
        "icon": "🔴",
    },
}

CATEGORY_ORDER = ["foundation", "development", "operations"]


def slugify(heading: str) -> str:
    """GitHub-style heading anchor (mirrors tests/test_diagram.py)."""
    anchor = heading.lower()
    anchor = re.sub(r"[^\w\s-]", "", anchor)
    anchor = anchor.replace(" ", "-")
    anchor = re.sub(r"-+", "-", anchor)
    return anchor


def parse_headings(lines):
    """Return real markdown headings, ignoring '#' lines inside code fences.

    Each entry: {"line": idx, "level": n, "text": str, "slug": str}.
    """
    headings = []
    in_fence = False
    fence_marker = ""
    for idx, line in enumerate(lines):
        stripped = line.strip()
        fence_open = re.match(r"^(`{3,}|~{3,})", stripped)
        if not in_fence and fence_open:
            in_fence = True
            fence_marker = fence_open.group(1)
            continue
        if in_fence:
            # A closing fence is the same character, at least as long, with no
            # info string. This correctly handles 4+ backtick fences that wrap
            # an inner ``` block (CommonMark).
            close = re.match(r"^(`{3,}|~{3,})\s*$", stripped)
            if close and close.group(1)[0] == fence_marker[0] and len(close.group(1)) >= len(fence_marker):
                in_fence = False
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            text = match.group(2).strip()
            headings.append(
                {
                    "line": idx,
                    "level": len(match.group(1)),
                    "text": text,
                    "slug": slugify(text),
                }
            )
    return headings


def category_for_line(line_no, headings):
    """Map a line number to its enclosing H1 category, if any."""
    category = None
    for heading in headings:
        if heading["line"] > line_no:
            break
        if heading["level"] == 1 and heading["text"] in CATEGORY_BY_H1:
            category = CATEGORY_BY_H1[heading["text"]]
    return category


def extract_section_markdown(lines, headings, target):
    """Return the raw markdown body for the heading `target` (exclusive of the
    heading line), stopping at the next heading of the same or higher level."""
    start = target["line"] + 1
    end = len(lines)
    for heading in headings:
        if heading["line"] > target["line"] and heading["level"] <= target["level"]:
            end = heading["line"]
            break
    # Compatibility anchors belong to the following README heading and are
    # unnecessary in the in-page dataset, whose cards already have canonical
    # IDs. Without filtering, an anchor immediately before the next heading is
    # incorrectly appended to the preceding pattern's body.
    body = [
        line for line in lines[start:end]
        if not re.fullmatch(
            r"\s*<a\s+id=[\"'][^\"']+[\"']\s*></a>\s*", line, re.IGNORECASE
        )
    ]
    # Trim leading/trailing blanks and a trailing horizontal rule.
    while body and not body[0].strip():
        body.pop(0)
    while body and (not body[-1].strip() or body[-1].strip() == "---"):
        body.pop()
    return "\n".join(body).strip()


def parse_reference_table(text):
    """Parse the 'Complete Pattern Reference' table.

    Returns ordered list of dicts: name, id, maturity, category, type,
    description, deps.
    Category-only rows (empty maturity / no link) are skipped.
    """
    section = re.search(
        r"##\s+Complete Pattern Reference\s*\n(.*?)(?:\n##\s|\Z)",
        text,
        re.DOTALL,
    )
    if not section:
        raise ValueError("Could not locate '## Complete Pattern Reference' table")

    rows = []
    columns = None
    link_re = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")
    for raw in section.group(1).splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        inner = line[1:] if line.startswith("|") else line
        inner = inner[:-1] if inner.endswith("|") else inner
        # Split on unescaped pipes so a GFM-escaped pipe (\|) inside a cell
        # (e.g. inline code or a regex alternation) does not shift columns.
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", inner)]
        if not cells:
            continue
        if cells[0].lower() == "pattern":
            columns = {name.lower(): index for index, name in enumerate(cells)}
            required = {
                "pattern", "maturity", "category", "type", "description",
                "dependencies",
            }
            missing = required - set(columns)
            if missing:
                raise ValueError(
                    "Complete Pattern Reference table is missing columns: "
                    + ", ".join(sorted(missing))
                )
            continue
        if set(cells[0]) <= {"-", ":"}:
            continue  # divider row
        if columns is None or max(columns.values()) >= len(cells):
            continue
        name_cell = cells[columns["pattern"]]
        maturity = cells[columns["maturity"]]
        category = cells[columns["category"]]
        ptype = cells[columns["type"]]
        description = cells[columns["description"]]
        deps = cells[columns["dependencies"]]
        link = link_re.search(name_cell)
        if not link or not maturity:
            continue  # category-only row
        rows.append(
            {
                "name": link.group(1).strip(),
                "id": link.group(2).strip(),
                "maturity": maturity,
                "category": category,
                "type": ptype,
                "description": description,
                "deps_raw": deps,
            }
        )
    return rows


def trim_redundant_meta(body):
    """Drop the leading **Maturity** and **Related Patterns** lines.

    Both are surfaced as structured chrome in the detail view (a maturity tag
    and clickable relation chips), so repeating them in the rendered body is
    noise. The richer **Description** line is kept - the modal relies on it.
    """
    removed = {"maturity": False, "related": False}
    out = []
    for line in body.split("\n"):
        # These bold-labelled metadata lines appear once near the top of every
        # pattern section (per pattern-spec.md). Strip the first of each wherever
        # it sits - some sections place Related Patterns after a Quick-start note.
        if not removed["maturity"] and re.match(r"^\*\*Maturity\*\*:", line):
            removed["maturity"] = True
            continue
        if not removed["related"] and re.match(r"^\*\*Related Patterns\*\*:", line):
            removed["related"] = True
            continue
        out.append(line)
    while out and not out[0].strip():
        out.pop(0)
    return "\n".join(out).strip()


def parse_related(section_markdown):
    """Extract [Name](#id) links from a '**Related Patterns**:' line."""
    match = re.search(r"\*\*Related Patterns\*\*:\s*(.+)", section_markdown)
    related = []
    if match:
        for name, anchor in re.findall(r"\[([^\]]+)\]\(#([^)]+)\)", match.group(1)):
            related.append({"name": name.strip(), "id": anchor.strip()})
    return related


def lens_short_description(body, limit=220):
    """Plain-text summary from a lens section's first paragraph."""
    paragraph = []
    for line in body.split("\n"):
        if not line.strip():
            if paragraph:
                break
            continue
        if line.lstrip().startswith(("|", "#", "-", "*", ">")):
            if paragraph:
                break
            continue
        paragraph.append(line.strip())
    text = " ".join(paragraph)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links -> text
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"(?<![\w*])\*(?!\s)([^*]+)\*", r"\1", text)  # italics -> text
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        cut = text[:limit]
        match = re.search(r"^(.*[.!?])\s", cut)
        text = match.group(1) if match else cut.rsplit(" ", 1)[0] + "…"
    return text


def parse_lenses(lines, headings):
    """Extract '## ... Lens' sections (framing perspectives over the catalog).

    These are not patterns (absent from the reference table) but are first-class
    content in the README; surface them as their own section on the site."""
    lenses = []
    for heading in headings:
        if heading["level"] == 2 and heading["text"].strip().lower().endswith("lens"):
            body = extract_section_markdown(lines, headings, heading)
            lenses.append(
                {
                    "id": heading["slug"],
                    "name": heading["text"].strip(),
                    "shortDescription": lens_short_description(body),
                    "bodyMarkdown": body,
                    "githubUrl": f"{REPO_URL}#{heading['slug']}",
                }
            )
    return lenses


def parse_dependency_diagram(text):
    """Return the first ```mermaid block body (the dependency diagram)."""
    match = re.search(r"```mermaid\n(.*?)```", text, re.DOTALL)
    if not match:
        raise ValueError("Could not find the dependency Mermaid diagram in README")
    return match.group(1).rstrip("\n")


def resolve_deps(deps_raw, name_to_id):
    """Turn a dependency cell into [{name, id}] entries."""
    cleaned = deps_raw.strip()
    if not cleaned or cleaned.lower() == "none":
        return []
    out = []
    for part in cleaned.split(","):
        raw_name = part.strip()
        if not raw_name:
            continue
        link = re.fullmatch(r"\[([^\]]+)\]\(#([^)]+)\)", raw_name)
        name = link.group(1).strip() if link else raw_name
        pid = name_to_id.get(name)
        if pid is None:
            # Fail loud: a dependency that matches no pattern signals table drift
            # (or silent corruption) rather than something to render as a dead link.
            raise ValueError(
                f"Dependency '{name}' does not match any pattern in the "
                f"Complete Pattern Reference table"
            )
        if link and link.group(2) != pid:
            raise ValueError(
                f"Dependency link for '{name}' points to '#{link.group(2)}', "
                f"expected '#{pid}'"
            )
        out.append({"name": name, "id": pid})
    return out


def node_id(pattern_id):
    """Mermaid node id (kebab anchors are not valid bare mermaid ids)."""
    return pattern_id.replace("-", "_")


def build_site_diagram(patterns):
    """Generate a branded dependency diagram from parsed data.

    Patterns are grouped into category subgraphs; edges run dependency ->
    dependent (matching README semantics); nodes are tinted per category and
    wired to open the in-page detail modal via the openPatternFromDiagram
    callback (mermaid securityLevel 'loose')."""
    cat_titles = {k: CATEGORY_META[k]["name"] for k in CATEGORY_ORDER}
    cat_fill = {
        "foundation": ("#e4f0e8", "#2d5a3f", "#1a3a25"),
        "development": ("#f7efcf", "#b7950b", "#5c4a00"),
        "operations": ("#f7e2df", "#c0392b", "#78281f"),
    }
    # Left-to-right reads as a Foundation -> Development -> Operations
    # progression and stays well-proportioned; top-down sprawls too wide.
    lines = ["graph LR"]
    for cat in CATEGORY_ORDER:
        members = [p for p in patterns if p["category"] == cat]
        if not members:
            continue
        lines.append(f'  subgraph sg_{cat}["{cat_titles[cat]}"]')
        lines.append("    direction TB")
        for pattern in members:
            label = pattern["name"].replace('"', "'")
            lines.append(f'    {node_id(pattern["id"])}["{label}"]')
        lines.append("  end")
    for pattern in patterns:
        for dep in pattern.get("dependencies", []):
            if dep.get("id"):
                lines.append(f'  {node_id(dep["id"])} --> {node_id(pattern["id"])}')
    for cat in CATEGORY_ORDER:
        fill, stroke, text = cat_fill[cat]
        lines.append(
            f"  classDef {cat} fill:{fill},stroke:{stroke},stroke-width:1.5px,"
            f"color:{text},rx:4,ry:4;"
        )
    for cat in CATEGORY_ORDER:
        ids = [node_id(p["id"]) for p in patterns if p["category"] == cat]
        if ids:
            lines.append(f'  class {",".join(ids)} {cat};')
    for pattern in patterns:
        lines.append(
            f'  click {node_id(pattern["id"])} openPatternFromDiagram "Open {pattern["name"]}"'
        )
    return "\n".join(lines)


def build_dataset():
    """Parse README.md and return the dataset dict."""
    text = README_PATH.read_text(encoding="utf-8")
    lines = text.split("\n")
    headings = parse_headings(lines)
    slug_to_heading = {}
    slug_counts = {}
    for heading in headings:
        if heading["level"] in (2, 3):
            slug_to_heading.setdefault(heading["slug"], heading)
            slug_counts[heading["slug"]] = slug_counts.get(heading["slug"], 0) + 1

    table_rows = parse_reference_table(text)
    name_to_id = {row["name"]: row["id"] for row in table_rows}

    patterns = []
    counts = {key: 0 for key in CATEGORY_ORDER}
    for row in table_rows:
        heading = slug_to_heading.get(row["id"])
        if heading is None:
            raise ValueError(
                f"Pattern '{row['name']}' (#{row['id']}) has no matching "
                f"## or ### section heading in README.md"
            )
        if slug_counts.get(row["id"], 0) > 1:
            # Two headings slugify to the same anchor; section extraction would
            # silently pick the first. Fail loud rather than ship wrong content.
            raise ValueError(
                f"Anchor '#{row['id']}' is ambiguous: multiple README headings "
                f"resolve to it"
            )
        body = extract_section_markdown(lines, headings, heading)
        category = category_for_line(heading["line"], headings)
        if category is None:
            raise ValueError(
                f"Pattern '{row['name']}' is not under a known category H1"
            )
        expected_category = CATEGORY_META[category]["name"]
        if row["category"] != expected_category:
            raise ValueError(
                f"Pattern '{row['name']}' declares category "
                f"'{row['category']}' in the reference table but is under "
                f"'{expected_category} Patterns'"
            )
        counts[category] += 1
        patterns.append(
            {
                "id": row["id"],
                "name": row["name"],
                "maturity": row["maturity"],
                "type": row["type"],
                "category": category,
                "shortDescription": row["description"],
                "dependencies": resolve_deps(row["deps_raw"], name_to_id),
                "related": parse_related(body),
                "bodyMarkdown": trim_redundant_meta(body),
                "githubUrl": f"{REPO_URL}#{row['id']}",
            }
        )

    categories = []
    for key in CATEGORY_ORDER:
        meta = CATEGORY_META[key]
        categories.append(
            {
                "id": key,
                "name": meta["name"],
                "blurb": meta["blurb"],
                "accent": meta["accent"],
                "icon": meta["icon"],
                "count": counts[key],
            }
        )

    return {
        "repoUrl": REPO_URL,
        "patternCount": len(patterns),
        "categories": categories,
        "maturities": ["Beginner", "Intermediate", "Advanced"],
        # Framing lenses (## ... Lens sections) - not patterns, shown separately
        "lenses": parse_lenses(lines, headings),
        # README's hand-authored diagram (kept for reference / GitHub rendering)
        "dependencyDiagram": parse_dependency_diagram(text),
        # Branded diagram rendered on the standalone site (in-page clicks)
        "siteDiagram": build_site_diagram(patterns),
        "patterns": patterns,
    }


def render_data_js(dataset):
    """Serialize the dataset as an assignable JS module string."""
    payload = json.dumps(dataset, indent=2, ensure_ascii=False)
    # U+2028/U+2029 are valid JSON but break older JS string parsing.
    payload = payload.replace(" ", "\\u2028").replace(" ", "\\u2029")
    header = (
        "// AUTO-GENERATED FROM README.md - DO NOT EDIT BY HAND.\n"
        "// Regenerate with: python3 scripts/generate-patterns-data.py\n"
        "// README.md is the single source of record for all pattern content.\n"
    )
    return f"{header}window.PATTERNS_DATA = {payload};\n"


def render_index_diagram_block(diagram):
    """The Mermaid diagram block injected into index.html (static for tests)."""
    return (
        f"{DIAGRAM_START}\n"
        f'        <div class="mermaid">\n'
        f"{diagram}\n"
        f"        </div>\n"
        f"        {DIAGRAM_END}"
    )


def inject_index_diagram(index_text, diagram):
    """Replace the diagram block between markers in index.html content."""
    block = render_index_diagram_block(diagram)
    pattern = re.compile(
        re.escape(DIAGRAM_START) + r".*?" + re.escape(DIAGRAM_END), re.DOTALL
    )
    if not pattern.search(index_text):
        raise ValueError(
            "index.html is missing the PATTERNS:DIAGRAM markers; cannot sync diagram"
        )
    return pattern.sub(lambda _m: block, index_text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify artifacts are in sync with README.md without writing.",
    )
    args = parser.parse_args()

    dataset = build_dataset()
    data_js = render_data_js(dataset)
    index_text = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else ""

    # Diagram injection is independent of data-file generation. Keep them
    # decoupled so a missing/renamed marker can never abort the whole run.
    new_index, diagram_problem = index_text, None
    if index_text:
        try:
            new_index = inject_index_diagram(index_text, dataset["siteDiagram"])
        except ValueError as error:
            diagram_problem = str(error)

    if args.check:
        problems = []
        current_data = DATA_PATH.read_text(encoding="utf-8") if DATA_PATH.exists() else ""
        if current_data != data_js:
            problems.append(f"{DATA_PATH.relative_to(REPO_ROOT)} is out of date")
        if diagram_problem:
            problems.append(diagram_problem)
        elif index_text and new_index != index_text:
            problems.append(
                f"{INDEX_PATH.relative_to(REPO_ROOT)} dependency diagram is out of date"
            )
        if problems:
            print("OUT OF SYNC with README.md:")
            for problem in problems:
                print(f"  - {problem}")
            print("Run: python3 scripts/generate-patterns-data.py")
            sys.exit(1)
        print(f"In sync: {dataset['patternCount']} patterns from README.md")
        return

    # Always write the data file first - it does not depend on index.html.
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(data_js, encoding="utf-8")
    print(f"Wrote {DATA_PATH.relative_to(REPO_ROOT)} ({dataset['patternCount']} patterns)")
    if diagram_problem:
        print(f"Warning: {diagram_problem}", file=sys.stderr)
    elif index_text and new_index != index_text:
        INDEX_PATH.write_text(new_index, encoding="utf-8")
        print(f"Synced dependency diagram in {INDEX_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
