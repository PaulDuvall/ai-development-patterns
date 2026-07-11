#!/usr/bin/env python3
"""Shared fail-closed helpers for local Codex evaluation run manifests."""

import datetime
import hashlib
import json
import os
import re
import stat
import tempfile
from pathlib import Path

import yaml
from yaml.constructor import ConstructorError
from yaml.events import AliasEvent


LOCAL_MANIFEST_VERSION = 1
SEARCH_LEDGER_VERSION = 1
LOCAL_RUN_ID_RE = re.compile(
    r"^codex-local:([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12})$")
LOCAL_RUN_REF_RE = re.compile(
    r"^verification/local-runs/codex-local-([0-9a-f]{8}-[0-9a-f]{4}-"
    r"4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\.yaml$")
LOCAL_SEARCH_LEDGER_REF_RE = re.compile(
    r"^verification/local-runs/codex-local-([0-9a-f]{8}-[0-9a-f]{4}-"
    r"4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})-search-events\.yaml$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PROMPT_VERSION_RE = re.compile(
    r"^evidence-v2-codex-local-v1\+sha256\.(?P<digest>[0-9a-f]{64})$")
SCOPES = {"stale", "stable", "exploratory", "all", "single", "discovery"}
SURFACES = {"codex-app", "codex-cli", "codex-ide"}
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_SEARCH_LEDGER_BYTES = 5 * 1024 * 1024
MAX_SEARCH_QUERIES_PER_UNIT = 12
SEARCH_MODES = ("name", "mechanism", "artifact")
DISCOVERY_MODE = "discovery"
SEARCH_TOOLS = {"web.search_query", "browser.search", "codex.search"}
REFUSED_API_ENV = {
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "EVIDENCE_OPENAI_API_KEY",
    "EVIDENCE_ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN",
}

MANIFEST_FIELDS = {
    "schema_version", "run_id", "plan_id", "base_sha", "checked_date",
    "scope", "selected_slugs", "include_discovery", "execution", "approval",
}
EXECUTION_FIELDS = {
    "provider", "surface", "auth_mode", "model", "prompt_version",
}
APPROVAL_FIELDS = {"status", "approved_at", "plan_id"}
SEARCH_LEDGER_FIELDS = {
    "schema_version", "run_id", "run_ref", "run_manifest_sha256",
    "research_contract_sha256", "events",
}
SEARCH_EVENT_FIELDS = {
    "sequence", "unit", "mode", "tool", "query", "candidate_count",
    "previous_event_sha256", "event_sha256",
}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that also rejects aliases and duplicate keys."""

    def compose_node(self, parent, index):
        if self.check_event(AliasEvent):
            event = self.peek_event()
            raise ConstructorError(
                "while composing YAML", event.start_mark,
                "aliases are not allowed in local run manifests", event.start_mark)
        return super().compose_node(parent, index)


def _construct_unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ConstructorError(
                "while constructing YAML", node.start_mark,
                "found an unhashable key", key_node.start_mark) from exc
        if duplicate:
            raise ConstructorError(
                "while constructing YAML", node.start_mark,
                f"found duplicate key {key!r}", key_node.start_mark)
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping)


def refuse_hosted_or_api_execution(environ=None):
    """Keep model-adjacent local controls out of Actions and API-key sessions."""
    environ = environ if environ is not None else os.environ
    if environ.get("GITHUB_ACTIONS") == "true":
        raise ValueError("local pattern evaluation is forbidden in GitHub Actions")
    configured = sorted(name for name in REFUSED_API_ENV if environ.get(name))
    if configured:
        raise ValueError(
            "refusing API-key-backed evaluation; unset these variables and use a "
            f"signed-in Codex client: {', '.join(configured)}")


def iso_date(value):
    """Return whether value is an exact YYYY-MM-DD calendar date."""
    if isinstance(value, datetime.date):
        value = value.isoformat()
    if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def approved_timestamp(value):
    """Return whether value is a UTC ISO timestamp emitted by the planner."""
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        datetime.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def canonical_plan(manifest):
    """Return the immutable fields covered by plan_id."""
    checked_date = manifest.get("checked_date")
    if isinstance(checked_date, datetime.date):
        checked_date = checked_date.isoformat()
    return {
        "schema_version": manifest.get("schema_version"),
        "run_id": manifest.get("run_id"),
        "base_sha": manifest.get("base_sha"),
        "checked_date": checked_date,
        "scope": manifest.get("scope"),
        "selected_slugs": manifest.get("selected_slugs"),
        "include_discovery": manifest.get("include_discovery"),
        "execution": manifest.get("execution"),
    }


def compute_plan_id(manifest):
    """Hash a canonical JSON encoding of the immutable research plan."""
    payload = json.dumps(
        canonical_plan(manifest), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def manifest_sha256(path):
    """Return the digest that evidence records after human approval."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_ref_for_id(run_id):
    """Return the only allowed repository-relative path for a local run ID."""
    match = LOCAL_RUN_ID_RE.fullmatch(run_id) if isinstance(run_id, str) else None
    if match is None:
        raise ValueError("local run_id must be codex-local:<UUIDv4>")
    return f"verification/local-runs/codex-local-{match.group(1)}.yaml"


def search_ledger_ref_for_id(run_id):
    """Return the only allowed search-event ledger path for a local run ID."""
    match = LOCAL_RUN_ID_RE.fullmatch(run_id) if isinstance(run_id, str) else None
    if match is None:
        raise ValueError("local run_id must be codex-local:<UUIDv4>")
    return (
        "verification/local-runs/"
        f"codex-local-{match.group(1)}-search-events.yaml")


def research_contract_sha256(prompt_version):
    """Extract the research-contract digest from a validated prompt version."""
    match = (
        PROMPT_VERSION_RE.fullmatch(prompt_version)
        if isinstance(prompt_version, str) else None)
    if match is None:
        raise ValueError("prompt_version does not contain a research-contract digest")
    return match.group("digest")


def search_ledger_binding(manifest, run_ref, manifest_digest):
    """Return the immutable run values copied into its search-event ledger."""
    if run_ref != run_ref_for_id(manifest.get("run_id")):
        raise ValueError("local run manifest path does not match its run_id")
    if not isinstance(manifest_digest, str) \
            or SHA256_RE.fullmatch(manifest_digest) is None:
        raise ValueError("run manifest digest must be 64 lowercase hex characters")
    return {
        "run_id": manifest["run_id"],
        "run_ref": run_ref,
        "run_manifest_sha256": manifest_digest,
        "research_contract_sha256": research_contract_sha256(
            manifest["execution"]["prompt_version"]),
    }


def _search_event_sha256(binding, event):
    """Hash one sanitized event and the immutable run binding."""
    payload = {
        "binding": binding,
        "event": {key: event.get(key) for key in SEARCH_EVENT_FIELDS - {"event_sha256"}},
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def new_search_ledger(manifest, run_ref, manifest_digest):
    """Create an empty, run-bound search-event ledger."""
    return {
        "schema_version": SEARCH_LEDGER_VERSION,
        **search_ledger_binding(manifest, run_ref, manifest_digest),
        "events": [],
    }


def validate_search_ledger(
        data, manifest, run_ref, manifest_digest, require_complete=False):
    """Validate a sanitized ledger, its hash chain, scope, and coverage."""
    if not isinstance(data, dict) or set(data) != SEARCH_LEDGER_FIELDS:
        raise ValueError("search-event ledger has missing or unknown top-level fields")
    if data.get("schema_version") != SEARCH_LEDGER_VERSION \
            or type(data.get("schema_version")) is not int:
        raise ValueError(
            f"search-event ledger schema_version must be {SEARCH_LEDGER_VERSION}")
    binding = search_ledger_binding(manifest, run_ref, manifest_digest)
    for field, expected in binding.items():
        if data.get(field) != expected:
            raise ValueError(f"search-event ledger {field} does not match this run")
    events = data.get("events")
    if not isinstance(events, list):
        raise ValueError("search-event ledger events must be a list")

    selected = set(manifest["selected_slugs"])
    allowed_units = set(selected)
    if manifest["include_discovery"]:
        allowed_units.add(DISCOVERY_MODE)
    unit_modes = {unit: set() for unit in allowed_units}
    unit_counts = {unit: 0 for unit in allowed_units}
    previous = None
    for index, event in enumerate(events, 1):
        label = f"search-event ledger events[{index - 1}]"
        if not isinstance(event, dict) or set(event) != SEARCH_EVENT_FIELDS:
            raise ValueError(f"{label} has missing or unknown fields")
        if event.get("sequence") != index or type(event.get("sequence")) is not int:
            raise ValueError(f"{label} sequence must be contiguous from 1")
        unit = event.get("unit")
        if unit not in allowed_units:
            raise ValueError(f"{label} unit is outside the approved run scope")
        mode = event.get("mode")
        allowed_modes = {DISCOVERY_MODE} if unit == DISCOVERY_MODE else set(SEARCH_MODES)
        if mode not in allowed_modes:
            raise ValueError(f"{label} mode is invalid for unit {unit!r}")
        if event.get("tool") not in SEARCH_TOOLS:
            raise ValueError(f"{label} tool is not an admitted local search tool")
        query = event.get("query")
        if not isinstance(query, str) or not query or query != query.strip() \
                or any(character in query for character in ("\n", "\r", "\x00")):
            raise ValueError(f"{label} query must be one non-empty sanitized line")
        if len(query.encode("utf-8")) > 2048:
            raise ValueError(f"{label} query exceeds 2048 UTF-8 bytes")
        candidate_count = event.get("candidate_count")
        if isinstance(candidate_count, bool) or not isinstance(candidate_count, int) \
                or candidate_count < 0:
            raise ValueError(f"{label} candidate_count must be a non-negative integer")
        if event.get("previous_event_sha256") != previous:
            raise ValueError(f"{label} previous_event_sha256 breaks the hash chain")
        expected_hash = _search_event_sha256(binding, event)
        if event.get("event_sha256") != expected_hash:
            raise ValueError(f"{label} event_sha256 does not match the sanitized event")
        previous = expected_hash
        unit_modes[unit].add(mode)
        unit_counts[unit] += 1
        if unit_counts[unit] > MAX_SEARCH_QUERIES_PER_UNIT:
            raise ValueError(
                f"search-event ledger unit {unit!r} exceeds "
                f"{MAX_SEARCH_QUERIES_PER_UNIT} search events")

    if require_complete:
        for unit in sorted(selected):
            missing = set(SEARCH_MODES) - unit_modes[unit]
            if missing:
                raise ValueError(
                    f"search-event ledger unit {unit!r} is missing modes "
                    f"{sorted(missing)}")
        if manifest["include_discovery"] and not unit_counts[DISCOVERY_MODE]:
            raise ValueError("search-event ledger is missing the discovery search event")
    return data


def search_projection(ledger, unit):
    """Aggregate trusted events into the evidence schema's three search modes."""
    projection = {
        mode: {"queries": [], "candidate_count": 0}
        for mode in SEARCH_MODES
    }
    for event in ledger["events"]:
        if event["unit"] != unit or event["mode"] not in projection:
            continue
        projection[event["mode"]]["queries"].append(event["query"])
        projection[event["mode"]]["candidate_count"] += event["candidate_count"]
    return projection


def reconcile_search_projection(ledger, unit, asserted_modes):
    """Fail unless evidence exactly projects the independently recorded events."""
    expected = search_projection(ledger, unit)
    if asserted_modes != expected:
        raise ValueError(
            f"search-event ledger does not exactly match search.modes for {unit!r}")
    return expected


def validate_manifest(data, run_ref=None, require_approved=True):
    """Validate a local plan manifest and return it unchanged."""
    if not isinstance(data, dict) or set(data) != MANIFEST_FIELDS:
        raise ValueError("local run manifest has missing or unknown top-level fields")
    if data.get("schema_version") != LOCAL_MANIFEST_VERSION \
            or type(data.get("schema_version")) is not int:
        raise ValueError(f"local run manifest schema_version must be {LOCAL_MANIFEST_VERSION}")
    run_id = data.get("run_id")
    run_match = LOCAL_RUN_ID_RE.fullmatch(run_id) if isinstance(run_id, str) else None
    if run_match is None:
        raise ValueError("local run manifest run_id must be codex-local:<UUIDv4>")
    if run_ref is not None:
        ref_match = (
            LOCAL_RUN_REF_RE.fullmatch(run_ref)
            if isinstance(run_ref, str) else None)
        if ref_match is None or ref_match.group(1) != run_match.group(1):
            raise ValueError("local run manifest path must match its run_id")
    base_sha = data.get("base_sha")
    if not isinstance(base_sha, str) or GIT_SHA_RE.fullmatch(base_sha) is None:
        raise ValueError("local run manifest base_sha must be a full Git SHA")
    if not iso_date(data.get("checked_date")):
        raise ValueError("local run manifest checked_date must be YYYY-MM-DD")
    if data.get("scope") not in SCOPES:
        raise ValueError(f"local run manifest scope must be one of {sorted(SCOPES)}")
    selected = data.get("selected_slugs")
    if not isinstance(selected, list) or not all(
            isinstance(slug, str) and SLUG_RE.fullmatch(slug) for slug in selected):
        raise ValueError("local run manifest selected_slugs must be canonical slugs")
    if len(selected) != len(set(selected)):
        raise ValueError("local run manifest selected_slugs contains duplicates")
    if data["scope"] == "single" and len(selected) != 1:
        raise ValueError("single scope must select exactly one pattern")
    if data["scope"] == "discovery" and selected:
        raise ValueError("discovery scope must not select evidence patterns")
    if type(data.get("include_discovery")) is not bool:
        raise ValueError("local run manifest include_discovery must be boolean")
    if data["scope"] == "discovery" and not data["include_discovery"]:
        raise ValueError("discovery scope must include discovery")

    execution = data.get("execution")
    if not isinstance(execution, dict) or set(execution) != EXECUTION_FIELDS:
        raise ValueError("local run manifest execution fields are invalid")
    if execution.get("provider") != "openai":
        raise ValueError("local Codex evaluation provider must be openai")
    if execution.get("surface") not in SURFACES:
        raise ValueError(f"local Codex surface must be one of {sorted(SURFACES)}")
    if execution.get("auth_mode") != "chatgpt-operator-attested":
        raise ValueError("local Codex auth_mode must be chatgpt-operator-attested")
    if not isinstance(execution.get("model"), str) or not execution["model"].strip():
        raise ValueError("local Codex model label must be non-empty")
    prompt_version = execution.get("prompt_version")
    if not isinstance(prompt_version, str) \
            or PROMPT_VERSION_RE.fullmatch(prompt_version) is None:
        raise ValueError("local Codex prompt_version must contain the contract SHA-256")

    plan_id = data.get("plan_id")
    if not isinstance(plan_id, str) or SHA256_RE.fullmatch(plan_id) is None \
            or plan_id != compute_plan_id(data):
        raise ValueError("local run manifest plan_id does not match its immutable plan")
    approval = data.get("approval")
    if not isinstance(approval, dict) or set(approval) != APPROVAL_FIELDS:
        raise ValueError("local run manifest approval fields are invalid")
    if approval.get("plan_id") != plan_id:
        raise ValueError("local run approval must bind the exact plan_id")
    if approval.get("status") == "pending":
        if approval.get("approved_at") is not None:
            raise ValueError("pending local run approval must have approved_at: null")
        if require_approved:
            raise ValueError("local run manifest has not been human-approved")
    elif approval.get("status") == "approved":
        if not approved_timestamp(approval.get("approved_at")):
            raise ValueError("approved local run must record a UTC approved_at timestamp")
    else:
        raise ValueError("local run approval status must be pending or approved")
    return data


def load_manifest(repo_root, run_ref, expected_sha256=None, require_approved=True):
    """Load a safe repository-relative manifest and bind its exact bytes."""
    if not isinstance(run_ref, str) or LOCAL_RUN_REF_RE.fullmatch(run_ref) is None:
        raise ValueError("search.run_ref must be a safe verification/local-runs path")
    if expected_sha256 is not None and (
            not isinstance(expected_sha256, str)
            or SHA256_RE.fullmatch(expected_sha256) is None):
        raise ValueError("search.run_manifest_sha256 must be 64 lowercase hex characters")
    root = Path(repo_root).resolve()
    relative = Path(run_ref)
    parent = root
    for part in relative.parts[:-1]:
        parent /= part
        info = parent.lstat()
        if parent.is_symlink() or not stat.S_ISDIR(info.st_mode):
            raise ValueError("local run manifest parent must be a real directory")
    path = root / relative
    info = path.lstat()
    if path.is_symlink() or not stat.S_ISREG(info.st_mode):
        raise ValueError("local run manifest must be a regular non-symlink file")
    if info.st_size > MAX_MANIFEST_BYTES:
        raise ValueError("local run manifest exceeds the size limit")
    digest = manifest_sha256(path)
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("search.run_manifest_sha256 does not match the local run manifest")
    data = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    return validate_manifest(data, run_ref, require_approved), path, digest


def load_search_ledger(
        repo_root, ledger_ref, manifest, run_ref, manifest_digest,
        require_complete=False):
    """Load the only safe ledger for a run and validate every stored event."""
    run_match = LOCAL_RUN_ID_RE.fullmatch(manifest.get("run_id", ""))
    ref_match = (
        LOCAL_SEARCH_LEDGER_REF_RE.fullmatch(ledger_ref)
        if isinstance(ledger_ref, str) else None)
    if run_match is None or ref_match is None \
            or ref_match.group(1) != run_match.group(1):
        raise ValueError("search-event ledger path must match the local run_id")
    root = Path(repo_root).resolve()
    relative = Path(ledger_ref)
    parent = root
    for part in relative.parts[:-1]:
        parent /= part
        info = parent.lstat()
        if parent.is_symlink() or not stat.S_ISDIR(info.st_mode):
            raise ValueError("search-event ledger parent must be a real directory")
    path = root / relative
    info = path.lstat()
    if path.is_symlink() or not stat.S_ISREG(info.st_mode):
        raise ValueError("search-event ledger must be a regular non-symlink file")
    if info.st_size > MAX_SEARCH_LEDGER_BYTES:
        raise ValueError("search-event ledger exceeds the size limit")
    data = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    return (
        validate_search_ledger(
            data, manifest, run_ref, manifest_digest, require_complete),
        path,
    )


def write_search_ledger(
        path, data, manifest, run_ref, manifest_digest,
        require_complete=False):
    """Atomically write only a validated, sanitized search-event ledger."""
    validate_search_ledger(
        data, manifest, run_ref, manifest_digest, require_complete)
    target = Path(path)
    if target.parent.is_symlink() or not target.parent.is_dir():
        raise ValueError("search-event ledger parent must be a real directory")
    if target.is_symlink() or (target.exists() and not target.is_file()):
        raise ValueError("search-event ledger target must be a regular non-symlink file")
    content = yaml.safe_dump(
        data, sort_keys=False, allow_unicode=True).encode("utf-8")
    if len(content) > MAX_SEARCH_LEDGER_BYTES:
        raise ValueError("search-event ledger exceeds the size limit")
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            os.fchmod(handle.fileno(), 0o600)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def append_search_event(
        ledger, manifest, run_ref, manifest_digest, unit, mode, tool, query,
        candidate_count):
    """Append one sanitized event and extend the ledger's binding hash chain."""
    binding = search_ledger_binding(manifest, run_ref, manifest_digest)
    previous = ledger["events"][-1]["event_sha256"] if ledger["events"] else None
    event = {
        "sequence": len(ledger["events"]) + 1,
        "unit": unit,
        "mode": mode,
        "tool": tool,
        "query": query,
        "candidate_count": candidate_count,
        "previous_event_sha256": previous,
        "event_sha256": "",
    }
    event["event_sha256"] = _search_event_sha256(binding, event)
    ledger["events"].append(event)
    try:
        validate_search_ledger(
            ledger, manifest, run_ref, manifest_digest, require_complete=False)
    except Exception:
        ledger["events"].pop()
        raise
    return event


def write_manifest(path, data):
    """Write a stable local manifest after validating its current state."""
    validate_manifest(data, require_approved=False)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink() or (target.exists() and not target.is_file()):
        raise ValueError("local run manifest target must be a regular non-symlink file")
    target.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def contract_digest(paths):
    """Hash ordered contract filenames and bytes without checkout-path variance."""
    digest = hashlib.sha256()
    for path in paths:
        source = Path(path)
        digest.update(source.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(source.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
