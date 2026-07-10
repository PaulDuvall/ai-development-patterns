#!/usr/bin/env python3
"""Validate versioned pattern-adoption evidence.

The validator is deliberately deterministic: asserted scores, dimensions,
verdicts, and naming alignment must match values recomputed from source records.
Run: python3 scripts/validate-evidence.py [--dir verification/evidence]
"""

import argparse
import datetime
import ipaddress
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import yaml
from yaml.constructor import ConstructorError
from yaml.events import AliasEvent


SCHEMA_VERSION = 2
TIER_WEIGHTS = {"T1": 5, "T2": 4, "T3": 3, "T4": 2, "T5": 1}
TIER_SOURCE_KINDS = {
    "T1": {"shipped_product", "open_source_implementation"},
    "T2": {"official_documentation", "reference_architecture"},
    "T3": {"conference_talk", "peer_reviewed_research"},
    "T4": {"practitioner_report", "case_study"},
    "T5": {"social_discussion", "opinion", "podcast"},
}
MATCH_VALUES = {"named", "aliased", "unnamed"}
PROVENANCE_VALUES = {"complete", "legacy-import"}
SEARCH_MODES = {"name", "mechanism", "artifact"}
RESEARCH_PROVIDERS = {"openai", "anthropic"}
MAX_ENTRIES_PER_TIER = 3
MAX_QUERIES = 12
MIN_MECHANISM_QUOTE_LENGTH = 20
MAX_YAML_BYTES = 1024 * 1024
EVIDENCE_REPOSITORY = "PaulDuvall/ai-development-patterns"
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GROUP_RE = re.compile(r"^[a-z0-9][a-z0-9._:/-]*$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RUN_ID_RE = re.compile(r"^github-actions:([1-9][0-9]*)$")
RUN_URL_RE = re.compile(
    rf"^https://github\.com/{re.escape(EVIDENCE_REPOSITORY)}/actions/runs/([1-9][0-9]*)$")
LEGACY_RUN_URL_RE = re.compile(
    rf"^https://github\.com/{re.escape(EVIDENCE_REPOSITORY)}/pull/([1-9][0-9]*)$")
EXPERIMENT_ROW_RE = re.compile(
    r"^\|\s*\*\*\[([^\]]+)\]\(#([a-z0-9-]+)\)\*\*\s*\|\s*"
    r"(?:Beginner|Intermediate|Advanced)\s*\|")

REQUIRED_TOP_FIELDS = {
    "schema_version", "provenance_status", "pattern", "slug", "last_checked",
    "search", "adoption_score", "tier_counts", "adoption_dimensions",
    "naming_alignment", "evidence", "verdict",
}
OPTIONAL_TOP_FIELDS = {"terminology_variants", "legacy_run_url", "legacy_limitations"}
REQUIRED_ENTRY_FIELDS = {
    "tier", "match", "source", "source_kind", "organization",
    "independence_group", "url", "resolved_url", "retrieved", "claim",
    "content_sha256", "verifier",
}
OPTIONAL_ENTRY_FIELDS = {"date", "mechanism_quote"}
TERMINOLOGY_FIELDS = {"term", "used_by", "url"}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""

    def compose_node(self, parent, index):
        if self.check_event(AliasEvent):
            event = self.peek_event()
            raise ConstructorError(
                "while composing YAML", event.start_mark,
                "aliases are not allowed in evidence data", event.start_mark)
        return super().compose_node(parent, index)


def _construct_unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ConstructorError(
                "while constructing a mapping", node.start_mark,
                "found an unhashable key", key_node.start_mark) from exc
        if duplicate:
            raise ConstructorError(
                "while constructing a mapping", node.start_mark,
                f"found duplicate key {key!r}", key_node.start_mark)
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping)


def load_yaml(path):
    """Load a YAML file safely and reject duplicate mapping keys."""
    source = Path(path)
    if source.is_symlink():
        raise ValueError("symbolic links are not allowed")
    if source.stat().st_size > MAX_YAML_BYTES:
        raise ValueError(f"YAML file exceeds {MAX_YAML_BYTES} bytes")
    return yaml.load(source.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)


def date_string(value):
    """Return a stable string for YAML strings and YAML date objects."""
    return value.isoformat() if isinstance(value, datetime.date) else str(value)


def stable_sorted(values):
    """Sort heterogeneous YAML values without raising a comparison TypeError."""
    return sorted(values, key=lambda value: (type(value).__name__, repr(value)))


def is_iso_date(value):
    """Return True when value is a real ISO calendar date (YYYY-MM-DD)."""
    text = date_string(value)
    if ISO_DATE_RE.fullmatch(text) is None:
        return False
    try:
        datetime.date.fromisoformat(text)
    except ValueError:
        return False
    return True


def parsed_date(value):
    return datetime.date.fromisoformat(date_string(value)) if is_iso_date(value) else None


def is_valid_url(value):
    """Return True for a concrete, credential-free HTTP(S) URL."""
    if not isinstance(value, str) or "..." in value or any(c.isspace() for c in value):
        return False
    parsed = urlsplit(value)
    try:
        parsed.port
    except ValueError:
        return False
    if not (
            parsed.scheme in {"http", "https"} and parsed.netloc and parsed.hostname
            and parsed.username is None and parsed.password is None):
        return False
    hostname = parsed.hostname.rstrip(".").casefold()
    if "%" in hostname or hostname == "localhost" \
            or hostname.endswith((".localhost", ".local", ".internal")):
        return False
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return True
    return address.is_global


def canonical_url(value):
    """Normalize a resolved URL for deterministic duplicate detection."""
    if not is_valid_url(value):
        return None
    parsed = urlsplit(value)
    host = parsed.hostname.rstrip(".").lower()
    try:
        if ipaddress.ip_address(host).version == 6:
            host = f"[{host}]"
    except ValueError:
        pass
    try:
        port = parsed.port
    except ValueError:
        return None
    if port and not ((parsed.scheme == "http" and port == 80)
                     or (parsed.scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)), doseq=True)
    return urlunsplit((parsed.scheme.lower(), host, path, query, ""))


def is_none_found(evidence):
    return evidence == "none found"


def compute_adoption_score(entries):
    return sum(TIER_WEIGHTS.get(entry.get("tier"), 0) for entry in entries)


def compute_tier_counts(entries):
    counts = {}
    for entry in entries:
        tier = entry.get("tier")
        if tier in TIER_WEIGHTS:
            counts[tier] = counts.get(tier, 0) + 1
    return counts


def compute_adoption_dimensions(entries):
    """Compute implementation, independent-adoption, and diversity signals."""
    implementation_groups = {
        entry.get("independence_group") for entry in entries
        if entry.get("tier") == "T1" and entry.get("independence_group")
    }
    adoption_groups = {
        entry.get("independence_group") for entry in entries
        if entry.get("tier") in {"T3", "T4"} and entry.get("independence_group")
    }
    all_groups = {
        entry.get("independence_group") for entry in entries
        if entry.get("independence_group")
    }
    independent = any(
        implementation_group != adoption_group
        for implementation_group in implementation_groups
        for adoption_group in adoption_groups
    )
    return {
        "implementation_available": bool(implementation_groups),
        "independent_adoption": independent,
        "independence_groups": len(all_groups),
    }


def compute_verdict(score, entries, provenance_status="complete"):
    """Derive verdict; legacy imports and T5 mentions cannot establish adoption."""
    # Incomplete searches cannot justify either terminal claim. Imported source
    # sets remain weak until a complete run proves verification or exhaustion.
    if provenance_status != "complete":
        return "weak"
    if score <= 2:
        return "unverified"
    dimensions = compute_adoption_dimensions(entries)
    # T5 remains visible in adoption_score as a ranking signal, but cannot be
    # the point that crosses the establishment threshold.
    qualifying_score = sum(
        TIER_WEIGHTS.get(entry.get("tier"), 0)
        for entry in entries if entry.get("tier") != "T5")
    if (qualifying_score >= 8
            and dimensions["implementation_available"]
            and dimensions["independent_adoption"]):
        return "verified"
    return "weak"


def compute_naming_alignment(entries):
    named = sum(entry.get("match") == "named" for entry in entries)
    aliased = sum(entry.get("match") == "aliased" for entry in entries)
    if not entries or (named == 0 and aliased == 0):
        return "none"
    if named == 0:
        return "aliased"
    return "strong" if named * 2 > len(entries) else "weak"


def _require_mapping_keys(value, required, allowed, label, errors):
    if not isinstance(value, dict):
        errors.append(f"'{label}' must be a mapping")
        return False
    keys = set(value)
    for field in stable_sorted(required - keys):
        errors.append(f"{label}: missing required field '{field}'")
    for field in stable_sorted(keys - allowed):
        errors.append(f"{label}: unknown field '{field}'")
    return True


def pipeline_run_number(value):
    """Return a run number only for this repository's canonical Actions URL."""
    if not isinstance(value, str):
        return None
    match = RUN_URL_RE.fullmatch(value)
    return match.group(1) if match else None


def validate_search(data, errors):
    search = data.get("search")
    provenance = data.get("provenance_status")
    base = {"run_id", "checked_at", "modes"}
    execution = {"provider", "model", "prompt_version"}
    required = base | execution if provenance == "complete" else base
    allowed = base | execution | {"run_url"}
    if not _require_mapping_keys(search, required, allowed, "search", errors):
        return
    if not isinstance(search.get("run_id"), str) or not search.get("run_id", "").strip():
        errors.append("search: 'run_id' must be a non-empty string")
    if not is_iso_date(search.get("checked_at")):
        errors.append("search: 'checked_at' must be ISO 8601 (YYYY-MM-DD)")
    elif is_iso_date(data.get("last_checked")) \
            and date_string(search["checked_at"]) != date_string(data["last_checked"]):
        errors.append("search: 'checked_at' must equal 'last_checked'")
    modes = search.get("modes")
    if not isinstance(modes, dict):
        errors.append("search: 'modes' must be a mapping")
        return
    missing = SEARCH_MODES - modes.keys()
    unknown = modes.keys() - SEARCH_MODES
    for mode in stable_sorted(missing):
        errors.append(f"search.modes: missing required mode '{mode}'")
    for mode in stable_sorted(unknown):
        errors.append(f"search.modes: unknown mode '{mode}'")
    total_queries = 0
    seen_queries = set()
    for mode in sorted(SEARCH_MODES & modes.keys()):
        value = modes[mode]
        if not _require_mapping_keys(
                value, {"queries", "candidate_count"}, {"queries", "candidate_count"},
                f"search.modes.{mode}", errors):
            continue
        queries = value.get("queries")
        count = value.get("candidate_count")
        if provenance == "legacy-import":
            if queries != [] or count is not None:
                errors.append(
                    f"search.modes.{mode}: legacy-import requires queries: [] "
                    "and candidate_count: null")
        else:
            if not isinstance(queries, list) or not queries:
                errors.append(f"search.modes.{mode}: 'queries' must be a non-empty list")
            else:
                for index, query in enumerate(queries):
                    if not isinstance(query, str) or not query.strip():
                        errors.append(
                            f"search.modes.{mode}.queries[{index}] must be non-empty")
                    elif query in seen_queries:
                        errors.append(f"search: duplicate query {query!r}")
                    else:
                        seen_queries.add(query)
                total_queries += len(queries)
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                errors.append(
                    f"search.modes.{mode}: 'candidate_count' must be a non-negative integer")
    if provenance == "legacy-import":
        if search.get("run_id") != "legacy-import":
            errors.append("search: legacy-import requires run_id: legacy-import")
        if "run_url" in search:
            errors.append("search: legacy-import must use top-level legacy_run_url")
        for field in sorted(execution):
            if field in search:
                errors.append(f"search: legacy-import must omit {field}")
    elif provenance == "complete":
        run_id = search.get("run_id")
        run_id_match = RUN_ID_RE.fullmatch(run_id) if isinstance(run_id, str) else None
        run_number = pipeline_run_number(search.get("run_url"))
        if not run_id_match:
            errors.append(
                "search: complete provenance requires run_id 'github-actions:<run-number>'")
        if not run_number:
            errors.append(
                "search: complete provenance requires this repository's canonical "
                "Actions run_url")
        if run_id_match and run_number and run_id_match.group(1) != run_number:
            errors.append("search: run_id must match the run number in run_url")
        if search.get("provider") not in RESEARCH_PROVIDERS:
            errors.append(
                f"search: provider must be one of {sorted(RESEARCH_PROVIDERS)}")
        for field in ("model", "prompt_version"):
            if not isinstance(search.get(field), str) or not search.get(field, "").strip():
                errors.append(f"search: '{field}' must be a non-empty string")
        if total_queries > MAX_QUERIES:
            errors.append(f"search: {total_queries} queries exceeds max {MAX_QUERIES}")


def validate_verifier(
        verifier, index, provenance, search_run_url, search_model,
        search_prompt_version, errors):
    label = f"evidence[{index}].verifier"
    fields = {"method", "model", "prompt_version", "run_url"}
    if not _require_mapping_keys(verifier, fields, fields, label, errors):
        return
    if provenance == "legacy-import":
        expected = {
            "method": "legacy-import", "model": None,
            "prompt_version": None, "run_url": None,
        }
        if verifier != expected:
            errors.append(f"{label}: legacy-import metadata must be {expected}")
        return
    if verifier.get("method") not in {"automated", "human"}:
        errors.append(f"{label}: method must be 'automated' or 'human'")
    for field in ("model", "prompt_version"):
        if not isinstance(verifier.get(field), str) or not verifier.get(field, "").strip():
            errors.append(f"{label}: '{field}' must be a non-empty string")
    verifier_url = verifier.get("run_url")
    if not pipeline_run_number(verifier_url):
        errors.append(f"{label}: 'run_url' must be this repository's canonical Actions URL")
    elif canonical_url(verifier_url) != canonical_url(search_run_url):
        errors.append(f"{label}: 'run_url' must equal search.run_url")
    if verifier.get("model") != search_model:
        errors.append(f"{label}: 'model' must equal search.model")
    if verifier.get("prompt_version") != search_prompt_version:
        errors.append(f"{label}: 'prompt_version' must equal search.prompt_version")


def validate_entry(
        entry, index, errors, provenance, last_checked, search_run_url,
        search_model, search_prompt_version, today):
    label = f"evidence[{index}]"
    allowed = REQUIRED_ENTRY_FIELDS | OPTIONAL_ENTRY_FIELDS
    if not _require_mapping_keys(entry, REQUIRED_ENTRY_FIELDS, allowed, label, errors):
        return
    for field in ("source", "organization", "claim"):
        if not isinstance(entry.get(field), str) or not entry.get(field, "").strip():
            errors.append(f"{label}: '{field}' must be a non-empty string")
    tier = entry.get("tier")
    if tier not in TIER_WEIGHTS:
        errors.append(f"{label}: tier must be one of {sorted(TIER_WEIGHTS)}")
    elif entry.get("source_kind") not in TIER_SOURCE_KINDS[tier]:
        errors.append(
            f"{label}: source_kind for {tier} must be one of "
            f"{sorted(TIER_SOURCE_KINDS[tier])}")
    if entry.get("match") not in MATCH_VALUES:
        errors.append(f"{label}: match must be one of {sorted(MATCH_VALUES)}")
    group = entry.get("independence_group")
    if not isinstance(group, str) or GROUP_RE.fullmatch(group) is None:
        errors.append(f"{label}: independence_group must be a lowercase machine key")
    for field in ("url", "resolved_url"):
        if not is_valid_url(entry.get(field)):
            errors.append(f"{label}: '{field}' must be a concrete HTTP(S) URL")
    for field in ("date", "retrieved"):
        if field in entry and not is_iso_date(entry.get(field)):
            errors.append(f"{label}: '{field}' must be ISO 8601 (YYYY-MM-DD)")
    source_date = parsed_date(entry.get("date")) if "date" in entry else None
    retrieved = parsed_date(entry.get("retrieved"))
    checked = parsed_date(last_checked)
    if source_date and retrieved and source_date > retrieved:
        errors.append(f"{label}: 'date' must not be after 'retrieved'")
    if source_date and source_date > today:
        errors.append(f"{label}: 'date' must not be in the future")
    # A complete run re-fetches every admitted source, so its retrieval date is
    # the run's check date. A legacy import may truthfully re-fetch individual
    # URLs during migration without claiming that all three searches reran.
    if provenance == "complete" and retrieved and checked and retrieved != checked:
        errors.append(f"{label}: complete provenance requires 'retrieved' == 'last_checked'")
    if retrieved and retrieved > today:
        errors.append(f"{label}: 'retrieved' must not be in the future")
    # Imported records preserve only the quote requirements enforced when they
    # were produced. Complete v2 runs must capture a checkable excerpt for every
    # source, regardless of name alignment or tier.
    quote_required = (
        provenance == "complete" or entry.get("match") in {"aliased", "unnamed"})
    quote = entry.get("mechanism_quote")
    if quote_required and (not isinstance(quote, str) or not quote.strip()):
        errors.append(f"{label}: mechanism_quote is required")
    elif quote_required:
        normalized_quote = re.sub(
            r"[^\w]+", " ", unicodedata.normalize("NFKC", quote)).strip()
        if len(normalized_quote) < MIN_MECHANISM_QUOTE_LENGTH:
            errors.append(
                f"{label}: mechanism_quote must normalize to at least "
                f"{MIN_MECHANISM_QUOTE_LENGTH} characters")
    digest = entry.get("content_sha256")
    if provenance == "legacy-import":
        if digest is not None:
            errors.append(f"{label}: legacy-import content_sha256 must be null")
    elif not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        errors.append(f"{label}: content_sha256 must be 64 lowercase hex characters")
    validate_verifier(
        entry.get("verifier"), index, provenance, search_run_url,
        search_model, search_prompt_version, errors)


def validate_terminology_variants(data, errors):
    """Validate the machine-readable record of alternate industry names."""
    if "terminology_variants" not in data:
        return
    variants = data.get("terminology_variants")
    if not isinstance(variants, list):
        errors.append("'terminology_variants' must be a list")
        return
    seen_terms = set()
    for index, variant in enumerate(variants):
        label = f"terminology_variants[{index}]"
        if not _require_mapping_keys(
                variant, TERMINOLOGY_FIELDS, TERMINOLOGY_FIELDS, label, errors):
            continue
        for field in ("term", "used_by"):
            if not isinstance(variant.get(field), str) or not variant.get(field, "").strip():
                errors.append(f"{label}: '{field}' must be a non-empty string")
        if not is_valid_url(variant.get("url")):
            errors.append(f"{label}: 'url' must be a concrete public HTTP(S) URL")
        term = variant.get("term")
        if isinstance(term, str) and term.strip():
            key = unicodedata.normalize("NFKC", term).casefold().strip()
            if key in seen_terms:
                errors.append(f"{label}: duplicate terminology term {term!r}")
            seen_terms.add(key)


def validate_top_fields(data, path, errors, today, max_age_days=None):
    allowed = REQUIRED_TOP_FIELDS | OPTIONAL_TOP_FIELDS
    keys = set(data)
    for field in stable_sorted(REQUIRED_TOP_FIELDS - keys):
        errors.append(f"missing required field '{field}'")
    for field in stable_sorted(keys - allowed):
        errors.append(f"unknown top-level field '{field}'")
    if type(data.get("schema_version")) is not int \
            or data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be integer {SCHEMA_VERSION}")
    if "verified" in data:
        errors.append("legacy 'verified' is forbidden; use 'last_checked'")
    provenance = data.get("provenance_status")
    if provenance not in PROVENANCE_VALUES:
        errors.append(f"provenance_status must be one of {sorted(PROVENANCE_VALUES)}")
    for field in ("pattern", "slug", "naming_alignment", "verdict"):
        if not isinstance(data.get(field), str) or not data.get(field, "").strip():
            errors.append(f"'{field}' must be a non-empty string")
    if isinstance(data.get("slug"), str) and SLUG_RE.fullmatch(data["slug"]) is None:
        errors.append("'slug' must be a lowercase hyphenated identifier")
    if data.get("naming_alignment") not in {"strong", "weak", "aliased", "none"}:
        errors.append("'naming_alignment' has an unknown value")
    if data.get("verdict") not in {"verified", "weak", "unverified"}:
        errors.append("'verdict' has an unknown value")
    score = data.get("adoption_score")
    if isinstance(score, bool) or not isinstance(score, int) or score < 0:
        errors.append("'adoption_score' must be a non-negative integer")
    counts = data.get("tier_counts")
    if not isinstance(counts, dict):
        errors.append("'tier_counts' must be a mapping")
    else:
        for tier, count in counts.items():
            if tier not in TIER_WEIGHTS:
                errors.append(f"tier_counts: unknown tier {tier!r}")
            if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                errors.append(f"tier_counts.{tier}: count must be a positive integer")
    dimensions = data.get("adoption_dimensions")
    dimension_fields = {
        "implementation_available", "independent_adoption", "independence_groups"}
    if not isinstance(dimensions, dict) or set(dimensions) != dimension_fields:
        errors.append(
            "'adoption_dimensions' must contain exactly implementation_available, "
            "independent_adoption, and independence_groups")
    else:
        for field in ("implementation_available", "independent_adoption"):
            if not isinstance(dimensions[field], bool):
                errors.append(f"adoption_dimensions.{field} must be boolean")
        group_count = dimensions["independence_groups"]
        if isinstance(group_count, bool) or not isinstance(group_count, int) \
                or group_count < 0:
            errors.append(
                "adoption_dimensions.independence_groups must be a non-negative integer")
    if data.get("slug") and path.stem != data["slug"]:
        errors.append(f"filename '{path.name}' does not match slug '{data['slug']}'")
    checked = parsed_date(data.get("last_checked"))
    if not checked:
        errors.append("'last_checked' must be ISO 8601 (YYYY-MM-DD)")
    else:
        if checked > today:
            errors.append("'last_checked' must not be in the future")
        if max_age_days is not None and (today - checked).days > max_age_days:
            errors.append(
                f"'last_checked' is {(today - checked).days} days old "
                f"(max {max_age_days})")
    if provenance == "legacy-import":
        if not isinstance(data.get("legacy_run_url"), str) \
                or LEGACY_RUN_URL_RE.fullmatch(data["legacy_run_url"]) is None:
            errors.append(
                "legacy-import requires this repository's canonical pull-request URL")
        if not isinstance(data.get("legacy_limitations"), str) \
                or not data.get("legacy_limitations", "").strip():
            errors.append("legacy-import requires non-empty legacy_limitations")
    elif "legacy_run_url" in data or "legacy_limitations" in data:
        errors.append("legacy_run_url/legacy_limitations are only valid for legacy-import")
    validate_terminology_variants(data, errors)


def validate_evidence_entries(data, errors, today):
    evidence = data.get("evidence")
    if not isinstance(evidence, list) and not is_none_found(evidence):
        errors.append("'evidence' must be a list of entries or exactly 'none found'")
    if isinstance(evidence, list) and not evidence:
        errors.append("empty evidence must be recorded as the string 'none found'")
    if is_none_found(evidence) and data.get("provenance_status") != "complete":
        errors.append("'none found' requires complete three-mode search provenance")
    entries = []
    search = data.get("search") if isinstance(data.get("search"), dict) else {}
    for index, item in enumerate(evidence if isinstance(evidence, list) else []):
        if isinstance(item, dict):
            validate_entry(
                item, index, errors, data.get("provenance_status"),
                data.get("last_checked"),
                search.get("run_url"), search.get("model"),
                search.get("prompt_version"),
                today)
            entries.append(item)
        else:
            errors.append(f"evidence[{index}]: entry must be a mapping")
    return entries


def validate_tier_caps_and_groups(entries, errors):
    counts = compute_tier_counts(entries)
    for tier, count in sorted(counts.items()):
        if count > MAX_ENTRIES_PER_TIER:
            errors.append(f"tier {tier} has {count} entries (max {MAX_ENTRIES_PER_TIER})")
    seen = {}
    organization_groups = {}
    for index, entry in enumerate(entries):
        group = entry.get("independence_group")
        if group and group in seen:
            errors.append(
                f"evidence[{index}]: independence_group {group!r} already scored by "
                f"evidence[{seen[group]}]")
        elif group:
            seen[group] = index
        organization = entry.get("organization")
        if isinstance(organization, str) and organization.strip() and group:
            organization_key = normalize_organization(organization)
            previous = organization_groups.get(organization_key)
            if previous and previous[0] != group:
                errors.append(
                    f"evidence[{index}]: organization {organization!r} uses independence_group "
                    f"{group!r}, but evidence[{previous[1]}] uses {previous[0]!r}")
            else:
                organization_groups[organization_key] = (group, index)


def normalize_organization(value):
    """Return a conservative comparison key for organization ownership labels."""
    text = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def validate_search_entry_consistency(data, entries, errors):
    """Every admitted complete entry must have appeared in the candidate pool."""
    if data.get("provenance_status") != "complete" or not entries:
        return
    search = data.get("search")
    modes = search.get("modes") if isinstance(search, dict) else None
    if not isinstance(modes, dict):
        return
    counts = [
        value.get("candidate_count")
        for value in modes.values() if isinstance(value, dict)
    ]
    if len(counts) == len(SEARCH_MODES) \
            and all(type(count) is int and count >= 0 for count in counts) \
            and sum(counts) < len(entries):
        errors.append(
            "search: total candidate_count must be at least the number of admitted evidence entries")


def validate_computed_fields(data, entries, errors):
    score = compute_adoption_score(entries)
    if data.get("adoption_score") != score:
        errors.append(f"adoption_score is {data.get('adoption_score')}, recomputes to {score}")
    counts = compute_tier_counts(entries)
    if data.get("tier_counts") != counts:
        errors.append(f"tier_counts is {data.get('tier_counts')}, recomputes to {counts}")
    dimensions = compute_adoption_dimensions(entries)
    if data.get("adoption_dimensions") != dimensions:
        errors.append(
            f"adoption_dimensions is {data.get('adoption_dimensions')}, "
            f"recomputes to {dimensions}")
    verdict = compute_verdict(score, entries, data.get("provenance_status"))
    if data.get("verdict") != verdict:
        errors.append(f"verdict is {data.get('verdict')!r}, recomputes to {verdict!r}")
    alignment = compute_naming_alignment(entries)
    if data.get("naming_alignment") != alignment:
        errors.append(
            f"naming_alignment is {data.get('naming_alignment')!r}, "
            f"recomputes to {alignment!r}")


def validate_file(path, today=None, max_age_days=None):
    """Validate a single evidence file; return a list of error strings."""
    today = today or datetime.date.today()
    try:
        data = load_yaml(path)
    except (OSError, yaml.YAMLError, ValueError) as exc:
        return [f"invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return ["file is not a YAML mapping"]
    errors = []
    validate_top_fields(data, Path(path), errors, today, max_age_days)
    validate_search(data, errors)
    entries = validate_evidence_entries(data, errors, today)
    validate_tier_caps_and_groups(entries, errors)
    validate_search_entry_consistency(data, entries, errors)
    validate_computed_fields(data, entries, errors)
    return errors


def load_catalog(registry_path, experiments_path):
    """Return slug->canonical-name catalog, rejecting duplicate identifiers."""
    registry = load_yaml(registry_path)
    if not isinstance(registry, dict) or not isinstance(registry.get("patterns"), list):
        raise ValueError("registry must contain a 'patterns' list")
    catalog = {}
    for index, pattern in enumerate(registry["patterns"]):
        if not isinstance(pattern, dict):
            raise ValueError(f"registry patterns[{index}] must be a mapping")
        slug, name = pattern.get("id"), pattern.get("name")
        if not isinstance(slug, str) or not slug or not isinstance(name, str) or not name:
            raise ValueError(f"registry patterns[{index}] requires non-empty id and name")
        if slug in catalog:
            raise ValueError(f"duplicate catalog slug {slug!r}")
        catalog[slug] = name
    experiments = Path(experiments_path)
    if experiments.is_file():
        for line in experiments.read_text(encoding="utf-8").splitlines():
            match = EXPERIMENT_ROW_RE.match(line)
            if not match:
                continue
            name, slug = match.groups()
            if slug in catalog:
                raise ValueError(f"duplicate catalog slug {slug!r}")
            catalog[slug] = name
    return catalog


def load_allowlist(path):
    """Return pending slugs plus schema errors; duplicates remain observable."""
    if not path:
        return [], []
    try:
        data = load_yaml(path)
    except (OSError, yaml.YAMLError, ValueError) as exc:
        return [], [f"invalid allowlist YAML: {exc}"]
    errors = []
    if not isinstance(data, dict) or set(data) != {"pending"}:
        return [], ["allowlist must be a mapping containing only 'pending'"]
    pending = data.get("pending")
    if not isinstance(pending, list):
        return [], ["allowlist 'pending' must be a list"]
    seen = set()
    for index, slug in enumerate(pending):
        if not isinstance(slug, str) or not slug:
            errors.append(f"allowlist pending[{index}] must be a non-empty string")
        elif slug in seen:
            errors.append(f"duplicate allowlist entry {slug!r}")
        else:
            seen.add(slug)
    return pending, errors


def validate_catalog_alignment(files, catalog, pending):
    evidence_slugs = {path.stem for path in files}
    allowlist = set(pending)
    errors = []
    errors.extend(
        f"orphan evidence file '{slug}.yaml' — no such pattern in the catalog"
        for slug in sorted(evidence_slugs - catalog.keys()))
    errors.extend(
        f"pattern '{slug}' has no evidence file and is not in the pending allowlist"
        for slug in sorted(catalog.keys() - evidence_slugs - allowlist))
    errors.extend(
        f"unknown pending allowlist entry {slug!r} — no such pattern in the catalog"
        for slug in sorted(allowlist - catalog.keys()))
    errors.extend(
        f"pattern {slug!r} has both evidence and a pending allowlist entry"
        for slug in sorted(evidence_slugs & allowlist))
    for path in files:
        if path.stem not in catalog:
            continue
        try:
            data = load_yaml(path)
        except (OSError, yaml.YAMLError, ValueError):
            continue
        if isinstance(data, dict) and data.get("pattern") != catalog[path.stem]:
            errors.append(
                f"{path.name}: pattern {data.get('pattern')!r} does not match canonical "
                f"catalog name {catalog[path.stem]!r}")
    return errors


def validate_canonical_url_uniqueness(files):
    """Return fatal errors when a resolved source URL is scored more than once."""
    seen = {}
    errors = []
    for path in files:
        try:
            data = load_yaml(path)
        except (OSError, yaml.YAMLError, ValueError):
            continue
        evidence = data.get("evidence") if isinstance(data, dict) else None
        for index, entry in enumerate(evidence if isinstance(evidence, list) else []):
            if not isinstance(entry, dict):
                continue
            key = canonical_url(entry.get("resolved_url"))
            if not key:
                continue
            if key in seen:
                first_path, first_index = seen[key]
                errors.append(
                    f"canonical URL {key!r} scored by {path.name} evidence[{index}] and "
                    f"{first_path.name} evidence[{first_index}]")
            else:
                seen[key] = (path, index)
    return errors


def validate_global_source_consistency(files):
    """Reject cross-file owner aliases and duplicate complete-page fingerprints."""
    organizations = {}
    digests = {}
    errors = []
    for path in files:
        try:
            data = load_yaml(path)
        except (OSError, yaml.YAMLError, ValueError):
            continue
        evidence = data.get("evidence") if isinstance(data, dict) else None
        for index, entry in enumerate(evidence if isinstance(evidence, list) else []):
            if not isinstance(entry, dict):
                continue
            organization = entry.get("organization")
            group = entry.get("independence_group")
            if isinstance(organization, str) and organization.strip() \
                    and isinstance(group, str) and group:
                key = normalize_organization(organization)
                previous = organizations.get(key)
                if previous and previous[0] != group:
                    errors.append(
                        f"organization {organization!r} uses independence_group {group!r} in "
                        f"{path.name} evidence[{index}], but {previous[1].name} "
                        f"evidence[{previous[2]}] uses {previous[0]!r}")
                else:
                    organizations[key] = (group, path, index)
            digest = entry.get("content_sha256")
            if isinstance(digest, str) and SHA256_RE.fullmatch(digest):
                previous = digests.get(digest)
                if previous:
                    errors.append(
                        f"content digest {digest!r} scored by {path.name} evidence[{index}] "
                        f"and {previous[0].name} evidence[{previous[1]}]")
                else:
                    digests[digest] = (path, index)
    return errors


def build_arg_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default="verification/evidence",
                        help="Directory containing evidence YAML files")
    parser.add_argument("--registry", help="patterns.yaml; enables catalog checks")
    parser.add_argument("--experiments", default="experiments/README.md")
    parser.add_argument("--allowlist", help="YAML whose pending list may lack evidence")
    parser.add_argument("--max-age-days", type=int,
                        help="Fail evidence last checked more than this many days ago")
    return parser


def main():
    args = build_arg_parser().parse_args()
    evidence_dir = Path(args.dir)
    if not evidence_dir.is_dir():
        print(f"error: evidence directory not found: {evidence_dir}")
        return 1
    if args.max_age_days is not None and args.max_age_days < 0:
        print("error: --max-age-days must be non-negative")
        return 1
    if args.allowlist and not args.registry:
        print("error: --allowlist requires --registry")
        return 1
    files = sorted(evidence_dir.glob("*.yaml"))
    failures = 0
    if not files:
        failures += 1
        print(f"FAIL {evidence_dir}: no evidence YAML files found")
    for path in files:
        errors = validate_file(path, max_age_days=args.max_age_days)
        if errors:
            failures += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {path}")
    url_errors = validate_canonical_url_uniqueness(files)
    if url_errors:
        failures += 1
        for error in url_errors:
            print(f"FAIL URLs: {error}")
    source_errors = validate_global_source_consistency(files)
    if source_errors:
        failures += 1
        for error in source_errors:
            print(f"FAIL sources: {error}")
    if args.registry:
        try:
            catalog = load_catalog(args.registry, args.experiments)
        except (OSError, yaml.YAMLError, ValueError) as exc:
            catalog = None
            failures += 1
            print(f"FAIL registry: {exc}")
        pending, allowlist_errors = load_allowlist(args.allowlist)
        alignment_errors = (
            validate_catalog_alignment(files, catalog, pending) if catalog is not None else [])
        for error in allowlist_errors + alignment_errors:
            print(f"FAIL registry: {error}")
        failures += len(allowlist_errors) + len(alignment_errors)
    print(f"\n{len(files)} file(s) checked, {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
