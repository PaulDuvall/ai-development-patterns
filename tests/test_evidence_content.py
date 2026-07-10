"""Slow semantic-integrity checks for complete adoption evidence.

Schema validation proves that a quote and digest were recorded. This module
re-fetches complete-provenance sources weekly and proves that the quoted
mechanism is still present in the live content. Legacy imports are deliberately
excluded: their missing provenance is already surfaced as ``needs refresh``.
"""

import importlib.util
import json
import os
from pathlib import Path
import warnings

import pytest
import requests
import yaml
REPO_ROOT = Path(__file__).parent.parent
EVIDENCE_DIR = REPO_ROOT / "verification" / "evidence"
BOT_GUARDED = {401, 403, 429}
SPEC = importlib.util.spec_from_file_location(
    "evidence_content", REPO_ROOT / "scripts" / "evidence_content.py")
CONTENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTENT)


def complete_entries():
    """Yield complete-provenance entries carrying a mechanism quote."""
    scope = evidence_scope()
    for path in sorted(EVIDENCE_DIR.glob("*.yaml")):
        if scope is not None and path.stem not in scope:
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data.get("provenance_status") != "complete":
            continue
        evidence = data.get("evidence")
        for index, entry in enumerate(evidence if isinstance(evidence, list) else []):
            if isinstance(entry, dict) and entry.get("mechanism_quote"):
                yield path.name, index, entry


def evidence_scope():
    """Return an optional trusted candidate scope supplied by the workflow."""
    raw = os.environ.get("EVIDENCE_SCOPE_SLUGS")
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssertionError("EVIDENCE_SCOPE_SLUGS must be a JSON list") from exc
    assert isinstance(value, list) and all(isinstance(item, str) for item in value), \
        "EVIDENCE_SCOPE_SLUGS must be a JSON string list"
    return set(value)


def check_complete_entry(filename, index, entry, strict_hashes):
    """Fetch one submitted URL and return integrity failures for its record."""
    url = entry.get("url")
    try:
        result = CONTENT.fetch(url, quote=entry["mechanism_quote"])
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None
        message = f"{filename}[{index}]: {url} -> HTTP {status or 'error'}"
        if status in BOT_GUARDED and not strict_hashes:
            warnings.warn(f"{message}; source could not be machine-verified", stacklevel=1)
            return []
        return [message]
    except (
            requests.RequestException, CONTENT.UnsafeURL, CONTENT.ResponseTooLarge,
            CONTENT.UnsupportedContent) as exc:
        return [f"{filename}[{index}]: {url} -> {type(exc).__name__}: {exc}"]

    failures = []
    if CONTENT.canonical_url(result["resolved_url"]) != CONTENT.canonical_url(
            entry.get("resolved_url", "")):
        failures.append(
            f"{filename}[{index}]: submitted URL now resolves to "
            f"{result['resolved_url']}, not recorded {entry.get('resolved_url')}")
    if not result["mechanism_quote_present"]:
        failures.append(f"{filename}[{index}]: mechanism quote no longer found at {url}")
        return failures
    if result["content_sha256"] != entry.get("content_sha256"):
        message = (
            f"{filename}[{index}]: normalized content digest changed at {url}; "
            "refresh the evidence record")
        if strict_hashes:
            failures.append(message)
        else:
            warnings.warn(message, stacklevel=1)
    return failures


@pytest.mark.slow
def test_complete_evidence_quotes_still_present():
    """A source must retain its mechanism; normalized content drift is visible."""
    failures = []
    strict_hashes = os.environ.get("EVIDENCE_HASH_STRICT") == "1"
    for filename, index, entry in complete_entries():
        failures.extend(check_complete_entry(filename, index, entry, strict_hashes))

    assert not failures, "evidence content drift detected:\n" + "\n".join(failures)


def test_quote_normalization_tolerates_markup_and_typography():
    quote = "Specifications become executable — directly generating working implementations."
    page = "<p>Specifications become <strong>executable</strong> &mdash; directly generating " \
           "working implementations.</p>"
    assert CONTENT.quote_is_present(quote, page)
    assert CONTENT.content_sha256(page) == CONTENT.content_sha256(
        "Specifications become executable — directly generating working implementations.")


def test_quote_normalization_rejects_unrelated_content():
    assert not CONTENT.quote_is_present(
        "The sandbox restricts filesystem and network access.",
        "<p>This page only discusses model pricing.</p>",
    )


def test_canonical_url_discards_volatile_tracking_parameters():
    first = CONTENT.canonical_url(
        "https://blog.example/article?gi=random-a&utm_source=newsletter&section=proof")
    second = CONTENT.canonical_url(
        "https://blog.example/article?section=proof&gi=random-b&utm_medium=email")

    assert first == second == "https://blog.example/article?section=proof"


def test_weekly_recheck_tolerates_rotating_redirect_tracking_query(monkeypatch):
    monkeypatch.setattr(CONTENT, "fetch", lambda *args, **kwargs: {
        "resolved_url": "https://blog.example/article?gi=random-b",
        "content_sha256": "a" * 64,
        "mechanism_quote_present": True,
    })
    failures = check_complete_entry(
        "example.yaml", 0,
        {
            "url": "https://blog.example/article",
            "resolved_url": "https://blog.example/article?gi=random-a",
            "mechanism_quote": "A sufficiently long mechanism quote for validation.",
            "content_sha256": "a" * 64,
        },
        strict_hashes=False,
    )

    assert failures == []


@pytest.mark.parametrize("url", [
    "http://127.0.0.1/secret",
    "http://169.254.169.254/latest/meta-data/",
    "http://[::1]/secret",
    "http://localhost/secret",
])
def test_safe_fetch_rejects_literal_private_and_local_targets(url):
    with pytest.raises(CONTENT.UnsafeURL):
        CONTENT.validate_public_url(url)


def test_safe_fetch_rejects_hostnames_resolving_private(monkeypatch):
    monkeypatch.setattr(
        CONTENT.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(2, 1, 6, "", ("10.0.0.5", 443))],
    )
    with pytest.raises(CONTENT.UnsafeURL, match="non-public"):
        CONTENT.validate_public_url("https://apparently-public.example/source")


def test_safe_fetch_revalidates_redirect_targets(monkeypatch):
    class RedirectResponse:
        status_code = 302
        headers = {"Location": "http://127.0.0.1/private"}
        url = "https://public.example/start"
        is_redirect = True
        is_permanent_redirect = False

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class FakeSession:
        def get(self, *args, **kwargs):
            return RedirectResponse()

    checked = []

    def validate(url):
        checked.append(url)
        if "127.0.0.1" in url:
            raise CONTENT.UnsafeURL("private redirect")

    monkeypatch.setattr(CONTENT, "validate_public_url", validate)
    with pytest.raises(CONTENT.UnsafeURL, match="private redirect"):
        CONTENT.fetch("https://public.example/start", session=FakeSession())
    assert checked == ["https://public.example/start", "http://127.0.0.1/private"]


def fake_response(status=200, content=b"A sufficiently long mechanism quote from the source."):
    value = requests.Response()
    value.status_code = status
    value.url = "https://public.example/source"
    value.headers["Content-Type"] = "text/plain"
    value._content = content
    value._content_consumed = True
    value.encoding = "utf-8"
    return value


def test_safe_fetch_retries_transient_timeout_then_succeeds(monkeypatch):
    class FakeSession:
        calls = 0

        def get(self, *args, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise requests.ReadTimeout("temporary read timeout")
            return fake_response()

    session = FakeSession()
    delays = []
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url: None)

    result = CONTENT.fetch(
        "https://public.example/source",
        quote="A sufficiently long mechanism quote from the source.",
        session=session,
        attempts=3,
        retry_backoff=1,
        sleeper=delays.append,
    )

    assert session.calls == 2
    assert delays == [1]
    assert result["mechanism_quote_present"] is True


def test_safe_fetch_exhausts_bounded_transient_retries(monkeypatch):
    class FakeSession:
        calls = 0

        def get(self, *args, **kwargs):
            self.calls += 1
            raise requests.ConnectionError("temporary connection failure")

    session = FakeSession()
    delays = []
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url: None)

    with pytest.raises(requests.ConnectionError, match="temporary connection failure"):
        CONTENT.fetch(
            "https://public.example/source",
            session=session,
            attempts=3,
            retry_backoff=1,
            sleeper=delays.append,
        )

    assert session.calls == 3
    assert delays == [1, 2]


@pytest.mark.parametrize("status", [408, 425, 429, 500, 502, 503, 504])
def test_safe_fetch_retries_transient_http_status(monkeypatch, status):
    class FakeSession:
        calls = 0

        def get(self, *args, **kwargs):
            self.calls += 1
            return fake_response(status if self.calls == 1 else 200)

    session = FakeSession()
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url: None)

    CONTENT.fetch(
        "https://public.example/source",
        session=session,
        attempts=2,
        retry_backoff=0,
    )

    assert session.calls == 2


@pytest.mark.parametrize("status", [403, 404, 501])
def test_safe_fetch_does_not_retry_permanent_http_status(monkeypatch, status):
    class FakeSession:
        calls = 0

        def get(self, *args, **kwargs):
            self.calls += 1
            return fake_response(status)

    session = FakeSession()
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url: None)

    with pytest.raises(requests.HTTPError):
        CONTENT.fetch(
            "https://public.example/missing",
            session=session,
            attempts=3,
            retry_backoff=0,
        )

    assert session.calls == 1


def test_safe_fetch_retries_truncated_stream(monkeypatch):
    class TruncatedResponse:
        status_code = 200
        url = "https://public.example/source"
        headers = {"Content-Type": "text/plain"}
        encoding = "utf-8"
        is_redirect = False
        is_permanent_redirect = False

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def iter_content(self, chunk_size):
            raise requests.exceptions.ChunkedEncodingError("truncated response")

    class FakeSession:
        calls = 0

        def get(self, *args, **kwargs):
            self.calls += 1
            return TruncatedResponse() if self.calls == 1 else fake_response()

    session = FakeSession()
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url: None)

    CONTENT.fetch(
        "https://public.example/source",
        session=session,
        attempts=2,
        retry_backoff=0,
    )

    assert session.calls == 2


def test_safe_fetch_does_not_retry_certificate_failure(monkeypatch):
    class FakeSession:
        calls = 0

        def get(self, *args, **kwargs):
            self.calls += 1
            raise requests.exceptions.SSLError("certificate verify failed")

    session = FakeSession()
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url: None)

    with pytest.raises(requests.exceptions.SSLError, match="certificate verify failed"):
        CONTENT.fetch(
            "https://public.example/source",
            session=session,
            attempts=3,
            retry_backoff=0,
        )

    assert session.calls == 1


@pytest.mark.parametrize("status", [401, 403, 429])
def test_bot_guarded_responses_fail_strict_candidate_validation(monkeypatch, status):
    response = requests.Response()
    response.status_code = status
    response.url = "https://public.example/source"

    def guarded(*args, **kwargs):
        raise requests.HTTPError(response=response)

    monkeypatch.setattr(CONTENT, "fetch", guarded)
    failures = check_complete_entry(
        "example.yaml", 0,
        {
            "url": response.url,
            "resolved_url": response.url,
            "mechanism_quote": "A sufficiently long mechanism quote for validation.",
            "content_sha256": "a" * 64,
        },
        strict_hashes=True,
    )
    assert failures == [f"example.yaml[0]: {response.url} -> HTTP {status}"]


def test_bot_guarded_response_warns_during_weekly_recheck(monkeypatch):
    response = requests.Response()
    response.status_code = 403
    response.url = "https://public.example/source"
    monkeypatch.setattr(
        CONTENT,
        "fetch",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            requests.HTTPError(response=response)),
    )
    with pytest.warns(UserWarning, match="could not be machine-verified"):
        assert check_complete_entry(
            "example.yaml", 0,
            {
                "url": response.url,
                "resolved_url": response.url,
                "mechanism_quote": "A sufficiently long mechanism quote for validation.",
                "content_sha256": "a" * 64,
            },
            strict_hashes=False,
        ) == []


def test_candidate_scope_is_strict_json(monkeypatch):
    monkeypatch.setenv("EVIDENCE_SCOPE_SLUGS", '["one", "two"]')
    assert evidence_scope() == {"one", "two"}
    monkeypatch.setenv("EVIDENCE_SCOPE_SLUGS", "one,two")
    with pytest.raises(AssertionError, match="JSON list"):
        evidence_scope()
