#!/usr/bin/env python3
"""Populate trusted retrieval fields for one model-authored evidence file.

The retrieval date means something different in each of the two supported
modes, so the mode is always explicit:

``--retrieved-date`` hydrates inside an approved local evaluation. That caller
already owns ``last_checked`` and ``search.checked_at`` and passes the run's own
check date, so this mode writes entry fields only.

``--recheck`` is the standalone, model-free re-verification of an already
published file: it advances ``last_checked`` together with the retrieval dates
it writes, and leaves ``search.checked_at`` pinned to the search run that
actually happened. No search reran, so the file never claims one did.

Running with neither mode is refused rather than defaulted. Both silent
defaults produced a wrong file: today's date left ``last_checked`` behind and
failed validation, while passing the existing ``last_checked`` validated
cleanly and backdated a fresh digest.
"""

import argparse
import datetime
import re
import sys
from pathlib import Path

import requests
import yaml

FIELD_RE = re.compile(r"^(?P<indent>\s*)(?P<key>[A-Za-z_][A-Za-z0-9_]*):[ ](?P<value>\S.*)$")
TOP_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")

from evidence_content import (
    ResponseTooLarge,
    UnsafeURL,
    UnsupportedContent,
    fetch,
)


def parse_iso_date(value, label):
    """Return one ISO 8601 calendar date or name the offending field."""
    try:
        return datetime.date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be ISO 8601 (YYYY-MM-DD)") from exc


def today_utc():
    """Return the current UTC calendar date."""
    return datetime.datetime.now(datetime.timezone.utc).date()


def resolve_retrieval_date(retrieved_date, recheck):
    """Resolve the single retrieval date this invocation may write."""
    if recheck and retrieved_date is not None:
        raise ValueError("--recheck derives its own date; drop --retrieved-date")
    if not recheck and retrieved_date is None:
        raise ValueError(
            "select a mode: --recheck re-verifies a published file and advances "
            "'last_checked'; --retrieved-date <run check date> hydrates inside an "
            "approved local evaluation. There is no safe default")
    if recheck:
        return today_utc()
    return parse_iso_date(retrieved_date, "retrieved_date")


def evidence_block(lines):
    """Return the line numbers spanning the top-level evidence list."""
    try:
        start = next(
            number for number, line in enumerate(lines)
            if line.rstrip() == "evidence:")
    except StopIteration:
        return range(0, 0)
    # A list may be indented at its parent key's level, so only a new top-level
    # key ends the block; a column-zero "- " is still an evidence entry.
    stop = next(
        (number for number in range(start + 1, len(lines))
         if TOP_KEY_RE.match(lines[number])), len(lines))
    return range(start + 1, stop)


def entry_index_by_line(lines):
    """Map each line number to the evidence entry that contains it."""
    mapping = {}
    marker_indent = None
    index = -1
    for number in evidence_block(lines):
        stripped = lines[number].lstrip()
        if stripped.startswith("- "):
            indent = len(lines[number]) - len(stripped)
            marker_indent = indent if marker_indent is None else marker_indent
            index += 1 if indent == marker_indent else 0
        if index >= 0:
            mapping[number] = index
    return mapping


def rewrite_value(line, new_value):
    """Replace one scalar value, preserving the line's existing quoting style."""
    match = FIELD_RE.match(line)
    old = match.group("value")
    quoted = old[:1] in ("'", '"') and old[-1:] == old[:1] and len(old) > 1
    quote = old[0] if quoted else ""
    return f"{line[:match.start('value')]}{quote}{new_value}{quote}"


def apply_updates(text, updates):
    """Rewrite only the updated scalar lines, or return None if one is missing."""
    lines = text.splitlines(keepends=True)
    owner = entry_index_by_line(lines)
    pending = {(scope, key): value for scope, key, value in updates}
    for number, line in enumerate(lines):
        body = line.rstrip("\n")
        match = FIELD_RE.match(body)
        if match is None:
            continue
        target = (owner.get(number), match.group("key"))
        if target not in pending:
            continue
        lines[number] = rewrite_value(body, pending.pop(target)) + line[len(body):]
    return None if pending else "".join(lines)


def normalized(value):
    """Render dates as ISO strings so parsed and intended documents compare."""
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: normalized(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalized(item) for item in value]
    return value


def write_document(path, original_text, data, updates):
    """Write the smallest faithful diff, proving it reparses to the intended document."""
    text = apply_updates(original_text, updates)
    if text is not None and normalized(yaml.safe_load(text)) == normalized(data):
        Path(path).write_text(text, encoding="utf-8")
        return []
    Path(path).write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return ["note: fields were not all rewritable in place; the file was reformatted"]


def load_document(path):
    """Read one evidence document and return its text, data, and admitted entries."""
    text = Path(path).read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("evidence document must be a mapping")
    entries = data.get("evidence")
    if entries == "none found":
        return text, data, None
    if not isinstance(entries, list):
        raise ValueError("evidence must be a list or 'none found'")
    return text, data, entries


def reject_backdating(entries, retrieved_date):
    """Refuse a retrieval date earlier than one already recorded."""
    for index, entry in enumerate(entries):
        recorded = entry.get("retrieved") if isinstance(entry, dict) else None
        if recorded is None:
            continue
        previous = parse_iso_date(recorded, f"evidence[{index}] 'retrieved'")
        if retrieved_date < previous:
            raise ValueError(
                f"evidence[{index}]: refusing to backdate 'retrieved' from "
                f"{previous.isoformat()} to {retrieved_date.isoformat()}; a fetch "
                "performed today cannot be recorded as an earlier retrieval")


def fetch_verified(index, entry):
    """Fetch one admitted source and require its recorded quote to still be present."""
    if not isinstance(entry, dict):
        raise ValueError(f"evidence[{index}] must be a mapping")
    url = entry.get("url")
    quote = entry.get("mechanism_quote")
    if not isinstance(url, str) or not isinstance(quote, str):
        raise ValueError(f"evidence[{index}] requires url and mechanism_quote")
    result = fetch(url, quote=quote)
    if not result["mechanism_quote_present"]:
        raise ValueError(
            f"evidence[{index}] mechanism_quote is absent from fetched content")
    return result


def refresh_entry(index, entry, retrieved_date):
    """Persist verified retrieval fields and report the updates they imply."""
    result = fetch_verified(index, entry)
    moved = entry.get("resolved_url") != result["resolved_url"]
    entry["resolved_url"] = result["resolved_url"]
    entry["content_sha256"] = result["content_sha256"]
    entry["retrieved"] = retrieved_date.isoformat()
    updates = [
        (index, field, entry[field])
        for field in ("resolved_url", "content_sha256", "retrieved")
    ]
    note = f"evidence[{index}]: resolved_url -> {result['resolved_url']}" if moved else None
    return updates, note


def advance_check_date(data, date):
    """Advance the document check date and leave the search run's date pinned."""
    previous = data.get("last_checked")
    if previous is not None and parse_iso_date(previous, "'last_checked'") > date:
        raise ValueError(
            f"refusing to backdate 'last_checked' from {previous} to {date.isoformat()}")
    data["last_checked"] = date.isoformat()
    search = data.get("search")
    pinned = search.get("checked_at") if isinstance(search, dict) else None
    note = f"last_checked -> {data['last_checked']}"
    if pinned is not None and str(pinned) != data["last_checked"]:
        note += f"; search.checked_at stays {pinned} because no search reran"
    return [(None, "last_checked", data["last_checked"])], [note]


def hydrate(path, retrieved_date=None, recheck=False):
    """Fetch every admitted source and persist verified retrieval metadata."""
    date = resolve_retrieval_date(retrieved_date, recheck)
    text, data, entries = load_document(path)
    if entries is None:
        return 0, ["'none found' admits no source to re-fetch; nothing written"]
    reject_backdating(entries, date)
    updates, notes = [], []
    for index, entry in enumerate(entries):
        entry_updates, note = refresh_entry(index, entry, date)
        updates.extend(entry_updates)
        notes.extend([note] if note else [])
    if recheck:
        check_updates, check_notes = advance_check_date(data, date)
        updates.extend(check_updates)
        notes.extend(check_notes)
    notes.extend(write_document(path, text, data, updates))
    return len(entries), notes


def build_parser():
    """Build the argument parser with both retrieval modes made explicit."""
    parser = argparse.ArgumentParser(
        description="Populate trusted retrieval fields for one evidence file.")
    parser.add_argument("path")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--retrieved-date",
        help="run check date; use inside an approved local evaluation")
    mode.add_argument(
        "--recheck", action="store_true",
        help="re-verify a published file and advance 'last_checked'")
    return parser


def main():
    args = build_parser().parse_args()
    try:
        count, notes = hydrate(args.path, args.retrieved_date, args.recheck)
    except (
            OSError, ValueError, yaml.YAMLError, requests.RequestException,
            UnsafeURL, ResponseTooLarge, UnsupportedContent) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for note in notes:
        print(note)
    print(f"Hydrated {count} evidence source(s) with trusted retrieval metadata")
    return 0


if __name__ == "__main__":
    sys.exit(main())
