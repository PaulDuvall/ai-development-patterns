#!/usr/bin/env python3
"""Record one sanitized local Codex search receipt in a run-bound ledger."""

import argparse
import ipaddress
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit, urlunsplit

import yaml

from local_verification import (
    SEARCH_TOOLS,
    append_search_event,
    load_manifest,
    load_search_ledger,
    new_search_ledger,
    refuse_hosted_or_api_execution,
    search_ledger_ref_for_id,
    write_search_ledger,
)


ROOT = Path(__file__).parent.parent.resolve()
MAX_CANDIDATES_PER_EVENT = 100
SECRET_PATTERNS = (
    re.compile(r"\bsk-ant-(?:api\d+-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{32,}"),
    re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b"),
    re.compile(r"(?i)\b(?:authorization|bearer)\s*[:= ]\s*[A-Za-z0-9+/=._-]{20,}"),
    re.compile(
        r"(?i)\b(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret|password)"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9+/=_-]{20,}"),
)
SENSITIVE_PARAMETER_RE = re.compile(
    r"(?i)(?:^|[_-])(?:auth|authorization|credential|key|password|secret|sig|signature|token)"
    r"(?:$|[_-])")
SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(?:api[_ -]?key|auth(?:orization)?|credential|password|secret|signature|token)"
    r"\s*[:=]\s*\S+")


def reject_sensitive_text(value, label):
    """Reject likely credentials without echoing the candidate value."""
    if any(pattern.search(value) for pattern in SECRET_PATTERNS):
        raise ValueError(f"{label} resembles a credential and was not recorded")


def sanitized_query(value):
    """Admit only one bounded, credential-free query line."""
    if not isinstance(value, str) or not value or value != value.strip() \
            or any(character in value for character in ("\n", "\r", "\x00")):
        raise ValueError("query must be one non-empty line without surrounding whitespace")
    if len(value.encode("utf-8")) > 2048:
        raise ValueError("query exceeds 2048 UTF-8 bytes")
    reject_sensitive_text(value, "query")
    if SENSITIVE_ASSIGNMENT_RE.search(value):
        raise ValueError("query contains a credential-like assignment and was not recorded")
    return value


def canonical_candidate_url(value):
    """Validate a public credential-free candidate URL for count derivation."""
    if not isinstance(value, str) or not value or any(character.isspace() for character in value):
        raise ValueError("candidate URL must be a concrete HTTP(S) URL")
    reject_sensitive_text(value, "candidate URL")
    parsed = urlsplit(value)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("candidate URL has an invalid port") from exc
    if parsed.scheme not in {"http", "https"} or not parsed.hostname \
            or parsed.username is not None or parsed.password is not None:
        raise ValueError("candidate URL must be credential-free HTTP(S)")
    host = parsed.hostname.rstrip(".").casefold()
    if "%" in host or host == "localhost" \
            or host.endswith((".localhost", ".local", ".internal")):
        raise ValueError("candidate URL must use a public host")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise ValueError("candidate URL must use a public host")
    for name, _ in parse_qsl(parsed.query, keep_blank_values=True):
        if SENSITIVE_PARAMETER_RE.search(name):
            raise ValueError("candidate URL contains a credential-like query parameter")
    reject_sensitive_text(parsed.fragment, "candidate URL fragment")
    for name, _ in parse_qsl(parsed.fragment, keep_blank_values=True):
        if SENSITIVE_PARAMETER_RE.search(name):
            raise ValueError("candidate URL contains a credential-like fragment parameter")
    default_port = (parsed.scheme == "http" and port == 80) \
        or (parsed.scheme == "https" and port == 443)
    rendered_host = f"[{host}]" if address is not None and address.version == 6 else host
    netloc = rendered_host if port is None or default_port else f"{rendered_host}:{port}"
    return urlunsplit((parsed.scheme, netloc, parsed.path or "/", parsed.query, ""))


def candidate_count(urls):
    """Derive a count from distinct admitted URLs without retaining the URLs."""
    if len(urls) > MAX_CANDIDATES_PER_EVENT:
        raise ValueError(
            f"one search receipt may contain at most {MAX_CANDIDATES_PER_EVENT} candidates")
    canonical = [canonical_candidate_url(url) for url in urls]
    if len(canonical) != len(set(canonical)):
        raise ValueError("candidate URLs must be distinct within one search receipt")
    return len(canonical)


def record_event(
        root, manifest_ref, manifest_sha256, unit, mode, tool, query,
        candidate_urls):
    """Validate one receipt, append it, and return its sanitized event metadata."""
    refuse_hosted_or_api_execution()
    manifest, _, actual_digest = load_manifest(
        root, manifest_ref, manifest_sha256, require_approved=True)
    if actual_digest != manifest_sha256:
        raise ValueError("approved manifest digest changed before event recording")
    ledger_ref = search_ledger_ref_for_id(manifest["run_id"])
    path = Path(root) / ledger_ref
    if path.exists() or path.is_symlink():
        ledger, _ = load_search_ledger(
            root, ledger_ref, manifest, manifest_ref, manifest_sha256,
            require_complete=False)
    else:
        ledger = new_search_ledger(manifest, manifest_ref, manifest_sha256)
    event = append_search_event(
        ledger, manifest, manifest_ref, manifest_sha256,
        unit, mode, tool, sanitized_query(query), candidate_count(candidate_urls))
    write_search_ledger(
        path, ledger, manifest, manifest_ref, manifest_sha256,
        require_complete=False)
    return ledger_ref, event


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--unit", required=True)
    parser.add_argument(
        "--mode", choices=("name", "mechanism", "artifact", "discovery"),
        required=True)
    parser.add_argument("--tool", choices=sorted(SEARCH_TOOLS), required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument(
        "--candidate-url", action="append", default=[],
        help="One credible candidate actually examined; values are counted then discarded")
    args = parser.parse_args()
    try:
        ledger_ref, event = record_event(
            ROOT, args.manifest, args.manifest_sha256, args.unit, args.mode,
            args.tool, args.query, args.candidate_url)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"SEARCH_LEDGER_REF={ledger_ref}")
    print(f"RECORDED_SEQUENCE={event['sequence']}")
    print(f"RECORDED_CANDIDATE_COUNT={event['candidate_count']}")
    print(f"EVENT_SHA256={event['event_sha256']}")
    print("Candidate URLs, raw tool output, reasoning, and credentials were not retained.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
