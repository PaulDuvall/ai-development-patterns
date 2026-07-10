#!/usr/bin/env python3
"""Populate trusted retrieval fields for one model-authored evidence file."""

import argparse
import sys
from pathlib import Path

import requests
import yaml

from evidence_content import (
    ResponseTooLarge,
    UnsafeURL,
    UnsupportedContent,
    fetch,
)


def hydrate(path):
    """Fetch every admitted source and persist verified retrieval metadata."""
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("evidence document must be a mapping")
    entries = data.get("evidence")
    if entries == "none found":
        return 0
    if not isinstance(entries, list):
        raise ValueError("evidence must be a list or 'none found'")
    for index, entry in enumerate(entries):
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
        entry["resolved_url"] = result["resolved_url"]
        entry["content_sha256"] = result["content_sha256"]
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return len(entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    args = parser.parse_args()
    try:
        count = hydrate(args.path)
    except (
            OSError, ValueError, yaml.YAMLError, requests.RequestException,
            UnsafeURL, ResponseTooLarge, UnsupportedContent) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Hydrated {count} evidence source(s) with trusted retrieval metadata")
    return 0


if __name__ == "__main__":
    sys.exit(main())
