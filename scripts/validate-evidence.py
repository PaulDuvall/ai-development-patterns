#!/usr/bin/env python3
"""Validate pattern adoption evidence files in verification/evidence/.

Every evidence file must recompute cleanly: adoption_score, verdict, and
naming_alignment are derived values, never asserted by hand (or by a model).
Run: python3 scripts/validate-evidence.py [--dir verification/evidence]
"""

import argparse
import datetime
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

TIER_WEIGHTS = {"T1": 5, "T2": 4, "T3": 3, "T4": 2, "T5": 1}
MATCH_VALUES = {"named", "aliased", "unnamed"}
MAX_ENTRIES_PER_TIER = 3
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# A pattern row in the experiments reference table: linked bold name, then a
# Maturity column — section headings linked in the same table have no maturity.
EXPERIMENT_ROW_RE = re.compile(
    r"^\|\s*\*\*\[[^\]]+\]\(#([a-z0-9-]+)\)\*\*\s*\|\s*(?:Beginner|Intermediate|Advanced)\s*\|")

REQUIRED_TOP_FIELDS = [
    "pattern", "slug", "adoption_score",
    "naming_alignment", "evidence", "verdict",
]
# 'date' (the source's own publication date) is optional: undated pages omit it.
REQUIRED_ENTRY_FIELDS = ["tier", "match", "source", "url", "retrieved", "claim"]


def is_iso_date(value):
    """Return True when value is a real ISO 8601 calendar date (YYYY-MM-DD)."""
    if ISO_DATE_RE.match(str(value)) is None:
        return False
    try:
        datetime.date.fromisoformat(str(value))
    except ValueError:
        return False
    return True


def is_valid_url(value):
    """Return True for a concrete http(s) URL — no placeholders or whitespace."""
    url = str(value)
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return False
    return "..." not in url and not any(ch.isspace() for ch in url)


def is_none_found(evidence):
    """Return True when evidence records a searched-but-empty result."""
    return isinstance(evidence, str) and evidence.strip().lower() == "none found"


def compute_adoption_score(entries):
    """Sum tier weights across entries (tier caps enforced separately)."""
    return sum(TIER_WEIGHTS.get(entry.get("tier"), 0) for entry in entries)


def compute_tier_counts(entries):
    """Count entries per tier (only tiers that appear)."""
    counts = {}
    for entry in entries:
        tier = entry.get("tier")
        if tier in TIER_WEIGHTS:
            counts[tier] = counts.get(tier, 0) + 1
    return counts


def compute_verdict(score, entries, strict=False):
    """Derive verdict from adoption score, tier mix, and (strict) independence."""
    has_strong_tier = any(entry.get("tier") in ("T1", "T2", "T3") for entry in entries)
    # strict: vendor docs alone cannot verify — require a practitioner-side
    # source (conference/paper/blog/social) alongside the strong tier.
    has_practitioner = any(entry.get("tier") in ("T3", "T4", "T5") for entry in entries)
    if score >= 8 and has_strong_tier and (has_practitioner or not strict):
        return "verified"
    if score <= 2:
        return "unverified"
    return "weak"


def compute_naming_alignment(entries, strict=False):
    """Derive naming alignment from the match field distribution."""
    named = sum(1 for entry in entries if entry.get("match") == "named")
    aliased = sum(1 for entry in entries if entry.get("match") == "aliased")
    if not entries or (named == 0 and aliased == 0):
        return "none"
    if strict and named == 0:
        return "aliased"  # industry uses other stable names — the rename signal
    if named * 2 > len(entries):
        return "strong"
    return "weak"


def validate_entry(entry, index, errors, strict=False):
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
    if is_iso_date(entry.get("date")) and is_iso_date(entry.get("retrieved")) \
            and str(entry["date"]) > str(entry["retrieved"]):
        errors.append(f"evidence[{index}]: 'date' must not be after 'retrieved'")
    if entry.get("url") and not is_valid_url(entry["url"]):
        errors.append(f"evidence[{index}]: url must be a concrete http(s) URL")
    if entry.get("match") in ("aliased", "unnamed") and not entry.get("mechanism_quote"):
        errors.append(f"evidence[{index}]: {entry.get('match')} entries require mechanism_quote")
    if (strict and entry.get("match") == "named"
            and entry.get("tier") in ("T1", "T2") and not entry.get("mechanism_quote")):
        errors.append(
            f"evidence[{index}]: named T1/T2 entries require mechanism_quote "
            "(a name match alone must not earn top weights)")


# Hosts where many unrelated organizations publish — a shared domain there says
# nothing about shared authorship, so the diversity check skips them.
PLATFORM_HOSTS = {
    "arxiv.org", "news.ycombinator.com", "youtube.com", "youtu.be",
    "medium.com", "x.com", "twitter.com", "reddit.com",
}


def source_key(url):
    """Best-effort org key for a URL: github owner, else registrable host."""
    parsed = urlparse(str(url))
    host = parsed.netloc.lower().removeprefix("www.")
    if host == "github.com":
        owner = parsed.path.strip("/").split("/")[0] if parsed.path.strip("/") else ""
        return ("github.com", owner) if owner else None
    if host in PLATFORM_HOSTS or not host:
        return None
    return (host,)


def validate_source_diversity(entries, errors):
    """One entry per organization per file (strict generation only)."""
    seen = {}
    for index, entry in enumerate(entries):
        key = source_key(entry.get("url", ""))
        if key is None:
            continue
        if key in seen:
            errors.append(
                f"evidence[{index}]: same organization as evidence[{seen[key]}] "
                f"({'/'.join(key)}) — one entry per org per file; keep the strongest")
        else:
            seen[key] = index


def validate_tier_caps(entries, errors):
    """Enforce the max-entries-per-tier cap."""
    counts = {}
    for entry in entries:
        tier = entry.get("tier")
        counts[tier] = counts.get(tier, 0) + 1
    for tier, count in sorted(counts.items()):
        if count > MAX_ENTRIES_PER_TIER:
            errors.append(f"tier {tier} has {count} entries (max {MAX_ENTRIES_PER_TIER})")


def validate_computed_fields(data, entries, errors, strict=False):
    """Check score, verdict, naming_alignment, tier_counts against recomputed values."""
    score = compute_adoption_score(entries)
    if data.get("adoption_score") != score:
        errors.append(f"adoption_score is {data.get('adoption_score')}, recomputes to {score}")
    verdict = compute_verdict(score, entries, strict)
    if data.get("verdict") != verdict:
        errors.append(f"verdict is '{data.get('verdict')}', recomputes to '{verdict}'")
    alignment = compute_naming_alignment(entries, strict)
    if data.get("naming_alignment") != alignment:
        errors.append(
            f"naming_alignment is '{data.get('naming_alignment')}', recomputes to '{alignment}'")
    if "tier_counts" in data and data["tier_counts"] != compute_tier_counts(entries):
        errors.append(
            f"tier_counts is {data.get('tier_counts')}, "
            f"recomputes to {compute_tier_counts(entries)}")


def validate_check_date(data, errors):
    """Require last_checked (ISO date); accept legacy 'verified' until migration."""
    if "last_checked" in data and "verified" in data:
        errors.append("use 'last_checked' only — drop the legacy 'verified' field")
        return
    if "last_checked" not in data and "verified" not in data:
        errors.append("missing required field 'last_checked'")
        return
    value = data.get("last_checked", data.get("verified"))
    if not value:
        errors.append("'last_checked' must be non-empty")
    elif not is_iso_date(value):
        errors.append("'last_checked' must be ISO 8601 (YYYY-MM-DD)")


def validate_top_fields(data, path, errors):
    """Check required top-level fields, slug/filename match, and check date."""
    for field in REQUIRED_TOP_FIELDS:
        if field not in data:
            errors.append(f"missing required field '{field}'")
    for field in ("pattern", "slug", "naming_alignment", "verdict"):
        if field in data and not data[field]:
            errors.append(f"'{field}' must be non-empty")
    if data.get("slug") and path.stem != data["slug"]:
        errors.append(f"filename '{path.name}' does not match slug '{data['slug']}'")
    validate_check_date(data, errors)


def validate_evidence_entries(data, errors, strict=False):
    """Validate evidence shape; return only dict-shaped entries for scoring."""
    evidence = data.get("evidence")
    if not isinstance(evidence, list) and not is_none_found(evidence):
        errors.append("'evidence' must be a list of entries or the string 'none found'")
    if isinstance(evidence, list) and not evidence:
        errors.append("empty evidence must be recorded as the string 'none found'")
    entries = []
    for index, item in enumerate(evidence if isinstance(evidence, list) else []):
        if isinstance(item, dict):
            validate_entry(item, index, errors, strict)
            entries.append(item)
        else:
            errors.append(f"evidence[{index}]: entry must be a mapping")
    return entries


def validate_file(path):
    """Validate a single evidence file; return a list of error strings."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, ValueError) as exc:
        # ValueError: PyYAML raises it for unquoted impossible dates (e.g. 2026-02-30)
        return [f"invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return ["file is not a YAML mapping"]
    # Generation marker: files regenerated since the last_checked rename get the
    # strict rules (aliased alignment, practitioner requirement, named-T1/T2
    # quotes, source diversity); legacy 'verified:' files keep the original
    # rules until the pipeline rewrites them.
    strict = "last_checked" in data
    errors = []
    validate_top_fields(data, path, errors)
    entries = validate_evidence_entries(data, errors, strict)
    validate_tier_caps(entries, errors)
    if strict:
        validate_source_diversity(entries, errors)
    validate_computed_fields(data, entries, errors, strict)
    return errors


def load_registry_slugs(registry_path, experiments_path):
    """Return catalog slugs: patterns.yaml ids plus experimental table anchors."""
    registry = yaml.safe_load(Path(registry_path).read_text(encoding="utf-8"))
    slugs = {pattern["id"] for pattern in registry.get("patterns") or []}
    experiments = Path(experiments_path)
    if experiments.is_file():
        for line in experiments.read_text(encoding="utf-8").splitlines():
            row = EXPERIMENT_ROW_RE.match(line)
            if row:
                slugs.add(row.group(1))
    return slugs


def load_allowlist(path):
    """Return the set of slugs allowed to lack an evidence file."""
    if not path:
        return set()
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return set(data.get("pending") or [])


def cross_check_registry(evidence_slugs, registry_slugs, allowlist):
    """Return errors for orphan evidence files and uncovered catalog patterns."""
    errors = [
        f"orphan evidence file '{slug}.yaml' — no such pattern in the catalog "
        "(renamed or deleted?)"
        for slug in sorted(evidence_slugs - registry_slugs)]
    errors += [
        f"pattern '{slug}' has no evidence file and is not in the pending allowlist"
        for slug in sorted(registry_slugs - evidence_slugs - allowlist)]
    return errors


def report_shared_urls(files):
    """Print NOTEs for URLs scored in more than one evidence file (non-fatal)."""
    citations = {}
    for path in files:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (yaml.YAMLError, ValueError):
            continue
        evidence = data.get("evidence") if isinstance(data, dict) else None
        for entry in evidence if isinstance(evidence, list) else []:
            if isinstance(entry, dict) and entry.get("url"):
                citations.setdefault(str(entry["url"]), set()).add(path.stem)
    for url, slugs in sorted(citations.items()):
        if len(slugs) > 1:
            print(f"NOTE shared source scored in {', '.join(sorted(slugs))}: {url}")


def report_registry_alignment(args, evidence_slugs):
    """Run catalog cross-checks when --registry is given; return failure count."""
    if not args.registry:
        return 0
    registry_slugs = load_registry_slugs(args.registry, args.experiments)
    allowlist = load_allowlist(args.allowlist)
    errors = cross_check_registry(evidence_slugs, registry_slugs, allowlist)
    for error in errors:
        print(f"FAIL registry: {error}")
    for slug in sorted(evidence_slugs & allowlist):
        print(f"NOTE '{slug}' now has evidence — remove it from the pending allowlist")
    return len(errors)


def build_arg_parser():
    """Define the CLI: evidence directory plus optional catalog cross-checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default="verification/evidence",
                        help="Directory containing evidence YAML files")
    parser.add_argument("--registry",
                        help="patterns.yaml path; enables catalog slug cross-checks")
    parser.add_argument("--experiments", default="experiments/README.md",
                        help="Experimental patterns README (used with --registry)")
    parser.add_argument("--allowlist",
                        help="YAML file whose 'pending' list may lack evidence files")
    return parser


def main():
    """Validate every evidence file; exit non-zero on any failure."""
    args = build_arg_parser().parse_args()
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
    report_shared_urls(files)
    failures += report_registry_alignment(args, {path.stem for path in files})
    print(f"\n{len(files)} file(s) checked, {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
