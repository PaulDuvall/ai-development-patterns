#!/usr/bin/env python3
"""Validate pattern adoption evidence files in verification/evidence/.

Every evidence file must recompute cleanly: adoption_score, verdict, and
naming_alignment are derived values, never asserted by hand (or by a model).
Run: python3 scripts/validate-evidence.py [--dir verification/evidence]
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

TIER_WEIGHTS = {"T1": 5, "T2": 4, "T3": 3, "T4": 2, "T5": 1}
MATCH_VALUES = {"named", "aliased", "unnamed"}
MAX_ENTRIES_PER_TIER = 3
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_TOP_FIELDS = [
    "pattern", "slug", "verified", "adoption_score",
    "naming_alignment", "evidence", "verdict",
]
REQUIRED_ENTRY_FIELDS = ["tier", "match", "source", "url", "date", "retrieved", "claim"]


def is_iso_date(value):
    """Return True when value is an ISO 8601 date (YYYY-MM-DD)."""
    return ISO_DATE_RE.match(str(value)) is not None


def is_none_found(evidence):
    """Return True when evidence records a searched-but-empty result."""
    return isinstance(evidence, str) and evidence.strip().lower() == "none found"


def compute_adoption_score(entries):
    """Sum tier weights across entries (tier caps enforced separately)."""
    return sum(TIER_WEIGHTS.get(entry.get("tier"), 0) for entry in entries)


def compute_verdict(score, entries):
    """Derive verdict from adoption score and tier mix."""
    has_strong_tier = any(entry.get("tier") in ("T1", "T2", "T3") for entry in entries)
    if score >= 8 and has_strong_tier:
        return "verified"
    if score <= 2:
        return "unverified"
    return "weak"


def compute_naming_alignment(entries):
    """Derive naming alignment from the match field distribution."""
    named = sum(1 for entry in entries if entry.get("match") == "named")
    aliased = sum(1 for entry in entries if entry.get("match") == "aliased")
    if not entries or (named == 0 and aliased == 0):
        return "none"
    if named * 2 > len(entries):
        return "strong"
    return "weak"


def validate_entry(entry, index, errors):
    """Validate one evidence entry; append findings to errors."""
    for field in REQUIRED_ENTRY_FIELDS:
        if not entry.get(field):
            errors.append(f"evidence[{index}]: missing required field '{field}'")
    if entry.get("tier") not in TIER_WEIGHTS:
        errors.append(f"evidence[{index}]: tier must be one of {sorted(TIER_WEIGHTS)}")
    if entry.get("match") not in MATCH_VALUES:
        errors.append(f"evidence[{index}]: match must be one of {sorted(MATCH_VALUES)}")
    for field in ("date", "retrieved"):
        if entry.get(field) and not is_iso_date(entry[field]):
            errors.append(f"evidence[{index}]: '{field}' must be ISO 8601 (YYYY-MM-DD)")
    if entry.get("match") in ("aliased", "unnamed") and not entry.get("mechanism_quote"):
        errors.append(f"evidence[{index}]: {entry.get('match')} entries require mechanism_quote")


def validate_tier_caps(entries, errors):
    """Enforce the max-entries-per-tier cap."""
    counts = {}
    for entry in entries:
        tier = entry.get("tier")
        counts[tier] = counts.get(tier, 0) + 1
    for tier, count in sorted(counts.items()):
        if count > MAX_ENTRIES_PER_TIER:
            errors.append(f"tier {tier} has {count} entries (max {MAX_ENTRIES_PER_TIER})")


def validate_computed_fields(data, entries, errors):
    """Check score, verdict, and naming_alignment against recomputed values."""
    score = compute_adoption_score(entries)
    if data.get("adoption_score") != score:
        errors.append(f"adoption_score is {data.get('adoption_score')}, recomputes to {score}")
    verdict = compute_verdict(score, entries)
    if data.get("verdict") != verdict:
        errors.append(f"verdict is '{data.get('verdict')}', recomputes to '{verdict}'")
    alignment = compute_naming_alignment(entries)
    if data.get("naming_alignment") != alignment:
        errors.append(
            f"naming_alignment is '{data.get('naming_alignment')}', recomputes to '{alignment}'")


def validate_top_fields(data, path, errors):
    """Check required top-level fields, slug/filename match, and verified date."""
    for field in REQUIRED_TOP_FIELDS:
        if field not in data:
            errors.append(f"missing required field '{field}'")
    if data.get("slug") and path.stem != data["slug"]:
        errors.append(f"filename '{path.name}' does not match slug '{data['slug']}'")
    if data.get("verified") and not is_iso_date(data["verified"]):
        errors.append("'verified' must be ISO 8601 (YYYY-MM-DD)")


def validate_evidence_entries(data, errors):
    """Validate evidence shape; return only dict-shaped entries for scoring."""
    evidence = data.get("evidence")
    if not isinstance(evidence, list) and not is_none_found(evidence):
        errors.append("'evidence' must be a list of entries or the string 'none found'")
    entries = []
    for index, item in enumerate(evidence if isinstance(evidence, list) else []):
        if isinstance(item, dict):
            validate_entry(item, index, errors)
            entries.append(item)
        else:
            errors.append(f"evidence[{index}]: entry must be a mapping")
    return entries


def validate_file(path):
    """Validate a single evidence file; return a list of error strings."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return ["file is not a YAML mapping"]
    errors = []
    validate_top_fields(data, path, errors)
    entries = validate_evidence_entries(data, errors)
    validate_tier_caps(entries, errors)
    validate_computed_fields(data, entries, errors)
    return errors


def main():
    """Validate every evidence file; exit non-zero on any failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default="verification/evidence",
                        help="Directory containing evidence YAML files")
    args = parser.parse_args()
    evidence_dir = Path(args.dir)
    if not evidence_dir.is_dir():
        print(f"error: evidence directory not found: {evidence_dir}")
        return 1
    files = sorted(evidence_dir.glob("*.yaml"))
    failures = 0
    for path in files:
        errors = validate_file(path)
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {path}")
    print(f"\n{len(files)} file(s) checked, {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
