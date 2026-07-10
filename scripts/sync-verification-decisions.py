#!/usr/bin/env python3
"""Synchronize deterministic naming signals without writing human decisions."""

import argparse
import sys
from pathlib import Path

import yaml


HEADER = "| Pattern | Alignment | Industry terms | Recommendation | Decision |"


def cells(line):
    return [cell.strip() for cell in line.split("|")][1:-1]


def safe_cell(value):
    return " ".join(str(value).replace("|", "/").splitlines()).strip()


def derived_terms(evidence):
    terms = []
    for item in evidence.get("terminology_variants") or []:
        term = item.get("term") if isinstance(item, dict) else None
        if term and term not in terms:
            terms.append(safe_cell(term))
    return "; ".join(terms[:6]) or "No stable industry term recorded"


def synchronize(root):
    root = Path(root)
    path = root / "verification" / "DECISIONS.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        header_index = lines.index(HEADER)
    except ValueError as exc:
        raise ValueError("naming-decision ledger header is missing") from exc
    separator_index = header_index + 1
    if separator_index >= len(lines) or not lines[separator_index].startswith("|---"):
        raise ValueError("naming-decision ledger separator is missing")
    end_index = separator_index + 1
    while end_index < len(lines) and lines[end_index].startswith("|"):
        end_index += 1
    row_lines = lines[separator_index + 1:end_index]
    rows = {}
    order = []
    for line in row_lines:
        row = cells(line)
        if len(row) != 5 or not row[0]:
            raise ValueError(f"invalid naming-decision ledger row: {line}")
        if row[0] in rows:
            raise ValueError(f"duplicate naming-decision row: {row[0]}")
        rows[row[0]] = row
        order.append(row[0])

    evidence_records = []
    for evidence_path in sorted((root / "verification" / "evidence").glob("*.yaml")):
        evidence = yaml.safe_load(evidence_path.read_text(encoding="utf-8")) or {}
        name = evidence.get("pattern")
        alignment = evidence.get("naming_alignment")
        if not isinstance(name, str) or not isinstance(alignment, str):
            continue
        evidence_records.append((name, evidence))
        if name in rows:
            rows[name][1] = safe_cell(alignment)

    for name, evidence in evidence_records:
        if name in rows:
            continue
        if evidence.get("verdict") != "verified" \
                or evidence.get("naming_alignment") == "strong":
            continue
        rows[name] = [
            safe_cell(name),
            safe_cell(evidence["naming_alignment"]),
            derived_terms(evidence),
            "Review naming signal",
            "—",
        ]
        order.append(name)

    rendered = ["| " + " | ".join(rows[name]) + " |" for name in order]
    updated = lines[:separator_index + 1] + rendered + lines[end_index:]
    content = "\n".join(updated) + "\n"
    path.write_text(content, encoding="utf-8")
    return len(rendered)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    try:
        count = synchronize(args.root)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Synchronized {count} naming-decision ledger row(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
