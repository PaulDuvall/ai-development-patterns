"""Slow semantic-integrity checks for complete adoption evidence.

Schema validation proves that a quote and digest were recorded. This module
re-fetches complete-provenance sources weekly and proves that the quoted
mechanism is still present in the live content. Legacy imports are deliberately
excluded: their missing provenance is already surfaced as ``needs refresh``.
"""

from contextlib import contextmanager
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


def install_fake_transport(monkeypatch, handler):
    """Replace only the pinned network boundary while retaining fetch semantics."""
    @contextmanager
    def open_response(_session, url, target, deadline):
        response = handler(url, target, deadline)
        with response:
            yield response

    monkeypatch.setattr(CONTENT, "_open_pinned_response", open_response)


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
    "https://127.0.0.1/secret",
    "https://169.254.169.254/latest/meta-data/",
    "https://[::1]/secret",
    "https://localhost/secret",
])
def test_safe_fetch_rejects_literal_private_and_local_targets(url):
    with pytest.raises(CONTENT.UnsafeURL):
        CONTENT.validate_public_url(url)


@pytest.mark.parametrize("url", [
    "http://93.184.216.34/source",
    "http://public.example/source",
])
def test_safe_fetch_requires_https(url):
    with pytest.raises(CONTENT.UnsafeURL, match="only concrete HTTPS"):
        CONTENT.validate_public_url(url)


def test_safe_fetch_rejects_hostnames_resolving_private(monkeypatch):
    monkeypatch.setattr(
        CONTENT.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(2, 1, 6, "", ("10.0.0.5", 443))],
    )
    with pytest.raises(CONTENT.UnsafeURL, match="non-public"):
        CONTENT.validate_public_url("https://apparently-public.example/source")


@pytest.mark.parametrize(("url", "address"), [
    ("https://192.88.99.1/source", "192.88.99.1"),
    ("https://[64:ff9b::a9fe:a9fe]/source", "64:ff9b::a9fe:a9fe"),
    ("https://[100:0:0:1::1]/source", "100:0:0:1::1"),
    ("https://[5f00::1]/source", "5f00::1"),
])
def test_safe_fetch_rejects_explicitly_denied_literals(url, address):
    parsed_address = CONTENT.ipaddress.ip_address(address)
    assert any(
        parsed_address.version == network.version and parsed_address in network
        for network in CONTENT.NON_PUBLIC_NETWORKS)
    with pytest.raises(CONTENT.UnsafeURL, match="non-public"):
        CONTENT.validate_public_url(url)


@pytest.mark.parametrize(("family", "sockaddr"), [
    (CONTENT.socket.AF_INET, ("192.88.99.1", 443)),
    (CONTENT.socket.AF_INET6, ("64:ff9b::a9fe:a9fe", 443, 0, 0)),
    (CONTENT.socket.AF_INET6, ("100:0:0:1::1", 443, 0, 0)),
    (CONTENT.socket.AF_INET6, ("5f00::1", 443, 0, 0)),
])
def test_safe_fetch_rejects_dns_answers_in_explicitly_denied_ranges(
        monkeypatch, family, sockaddr):
    monkeypatch.setattr(
        CONTENT.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (family, CONTENT.socket.SOCK_STREAM, 6, "", sockaddr)],
    )

    with pytest.raises(CONTENT.UnsafeURL, match="non-public"):
        CONTENT.validate_public_url("https://special-use.example/source")


def test_dns_resolution_obeys_absolute_deadline(monkeypatch):
    release = CONTENT.threading.Event()
    monkeypatch.setattr(
        CONTENT.socket,
        "getaddrinfo",
        lambda *args, **kwargs: release.wait(1),
    )
    started = CONTENT.time.monotonic()
    try:
        with pytest.raises(requests.ConnectTimeout, match="DNS resolution timed out"):
            CONTENT.validate_public_url(
                "https://slow-dns.example/source", deadline=started + 0.05)
    finally:
        release.set()

    assert CONTENT.time.monotonic() - started < 0.75


@pytest.mark.parametrize(("family", "public_sockaddr", "private_sockaddr"), [
    (CONTENT.socket.AF_INET,
     ("93.184.216.34", 443), ("10.0.0.5", 443)),
    (CONTENT.socket.AF_INET6,
     ("2606:2800:220:1:248:1893:25c8:1946", 443, 0, 0),
     ("fd00::5", 443, 0, 0)),
])
def test_pinned_connection_cannot_follow_dns_rebinding(
        monkeypatch, family, public_sockaddr, private_sockaddr):
    """The socket consumes the validated answer, never a second DNS result."""
    resolver_calls = []

    def rebinding_resolver(*args, **kwargs):
        resolver_calls.append((args, kwargs))
        sockaddr = public_sockaddr if len(resolver_calls) == 1 else private_sockaddr
        return [(family, CONTENT.socket.SOCK_STREAM, 6, "", sockaddr)]

    monkeypatch.setattr(CONTENT.socket, "getaddrinfo", rebinding_resolver)
    target = CONTENT.validate_public_url("https://rebind.example/source")

    connected = []

    class FakeSocket:
        def settimeout(self, _timeout):
            pass

        def setsockopt(self, *_option):
            pass

        def bind(self, _source):
            pass

        def connect(self, sockaddr):
            connected.append(sockaddr)

        def close(self):
            pass

    socket_families = []

    def socket_factory(socket_family, *_args):
        socket_families.append(socket_family)
        return FakeSocket()

    monkeypatch.setattr(CONTENT.socket, "socket", socket_factory)
    connection = CONTENT._PinnedHTTPSConnection(
        target.hostname,
        target.port,
        timeout=1,
        verified_endpoints=target.endpoints,
        socket_registrar=lambda _connection: None,
    )
    connection._new_conn()

    assert len(resolver_calls) == 1
    assert socket_families == [family]
    assert connected == [public_sockaddr]
    assert private_sockaddr not in connected


def test_pinned_connection_audits_before_connect(monkeypatch):
    events = []

    class FakeSocket:
        def settimeout(self, _timeout):
            pass

        def setsockopt(self, *_option):
            pass

        def connect(self, _sockaddr):
            events.append("connect")

        def close(self):
            events.append("close")

    monkeypatch.setattr(CONTENT.socket, "socket", lambda *args: FakeSocket())
    monkeypatch.setattr(
        CONTENT.sys,
        "audit",
        lambda event, *_args: events.append("audit")
        if event == "http.client.connect" else None,
    )
    endpoint = CONTENT.ResolvedEndpoint(
        CONTENT.socket.AF_INET,
        CONTENT.socket.SOCK_STREAM,
        6,
        ("93.184.216.34", 443),
    )
    connection = CONTENT._PinnedHTTPSConnection(
        "public.example",
        443,
        timeout=1,
        verified_endpoints=(endpoint,),
        socket_registrar=lambda _connection: None,
    )

    connection._new_conn()

    assert events == ["audit", "connect"]


@pytest.mark.parametrize("failure", [
    RuntimeError("audit rejected connection"),
    OSError("audit rejected connection"),
])
def test_pinned_connection_closes_socket_when_audit_raises(
        monkeypatch, failure):
    closed = []

    class FakeSocket:
        def settimeout(self, _timeout):
            pass

        def setsockopt(self, *_option):
            pass

        def connect(self, _sockaddr):
            raise AssertionError("connect must not run after a failed audit hook")

        def close(self):
            closed.append(True)

    def reject_audit(event, *_args):
        if event == "http.client.connect":
            raise failure

    monkeypatch.setattr(CONTENT.socket, "socket", lambda *args: FakeSocket())
    monkeypatch.setattr(CONTENT.sys, "audit", reject_audit)
    endpoint = CONTENT.ResolvedEndpoint(
        CONTENT.socket.AF_INET,
        CONTENT.socket.SOCK_STREAM,
        6,
        ("93.184.216.34", 443),
    )
    connection = CONTENT._PinnedHTTPSConnection(
        "public.example",
        443,
        timeout=1,
        verified_endpoints=(endpoint,),
        socket_registrar=lambda _connection: None,
    )

    with pytest.raises(type(failure), match="audit rejected connection"):
        connection._new_conn()

    assert closed == [True]


def test_https_connection_closes_socket_on_tls_setup_exception(monkeypatch):
    closed = []

    class FakeSocket:
        def close(self):
            closed.append(True)

    def fail_tls(connection):
        connection.sock = FakeSocket()
        raise RuntimeError("TLS setup failed")

    monkeypatch.setattr(CONTENT.HTTPSConnection, "connect", fail_tls)
    endpoint = CONTENT.ResolvedEndpoint(
        CONTENT.socket.AF_INET,
        CONTENT.socket.SOCK_STREAM,
        6,
        ("93.184.216.34", 443),
    )
    connection = CONTENT._PinnedHTTPSConnection(
        "public.example",
        443,
        timeout=1,
        verified_endpoints=(endpoint,),
        socket_registrar=lambda _connection: None,
    )

    with pytest.raises(RuntimeError, match="TLS setup failed"):
        connection.connect()

    assert closed == [True]


def test_https_pool_preserves_original_hostname_for_sni_and_certificate():
    endpoint = CONTENT.ResolvedEndpoint(
        CONTENT.socket.AF_INET,
        CONTENT.socket.SOCK_STREAM,
        6,
        ("93.184.216.34", 443),
    )
    target = CONTENT.ResolvedTarget(
        "https", "public.example", 443, (endpoint,))
    adapter = CONTENT._PinnedAddressAdapter(target)
    request = requests.Request(
        "GET", "https://public.example/source").prepare()
    try:
        pool = adapter.get_connection_with_tls_context(
            request, verify=True, proxies={}, cert=None)
        connection = pool._new_conn()
    finally:
        adapter.close()

    assert pool.host == "public.example"
    assert connection.host == "public.example"
    assert connection.server_hostname == "public.example"
    assert connection.assert_hostname == "public.example"
    assert connection.verified_endpoints == (endpoint,)


def test_pinned_adapter_requires_modern_requests_api(monkeypatch):
    monkeypatch.setattr(
        CONTENT.HTTPAdapter, "get_connection_with_tls_context", None)
    monkeypatch.setattr(
        CONTENT,
        "validate_public_url",
        lambda *_args: pytest.fail("unsupported Requests must fail before DNS"),
    )

    with pytest.raises(RuntimeError, match=r"Requests 2.32.2\+"):
        CONTENT.fetch("https://public.example/source", attempts=1)


def test_fetch_ignores_proxy_and_request_environment(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9999")
    monkeypatch.setenv("REQUESTS_CA_BUNDLE", "/tmp/untrusted-ca.pem")
    target = CONTENT.ResolvedTarget(
        "https",
        "public.example",
        443,
        (CONTENT.ResolvedEndpoint(
            CONTENT.socket.AF_INET,
            CONTENT.socket.SOCK_STREAM,
            6,
            ("93.184.216.34", 443),
        ),),
    )
    monkeypatch.setattr(
        CONTENT, "validate_public_url", lambda _url, _deadline: target)
    observed = {}

    def fake_get(session, _url, **kwargs):
        observed["trust_env"] = session.trust_env
        observed["session_proxies"] = dict(session.proxies)
        observed["request_proxies"] = kwargs["proxies"]
        observed["verify"] = kwargs["verify"]
        return fake_response()

    monkeypatch.setattr(requests.Session, "get", fake_get)
    CONTENT.fetch("https://public.example/source", attempts=1)

    assert observed == {
        "trust_env": False,
        "session_proxies": {},
        "request_proxies": {},
        "verify": True,
    }


def test_connect_and_response_headers_share_deadline_and_close_socket():
    release = CONTENT.threading.Event()
    closed = []
    previous_adapter = object()

    class ActiveSocket:
        def close(self):
            closed.append(True)

    class BlockingSession:
        def __init__(self):
            self.adapters = {"https://": previous_adapter}

        def mount(self, prefix, adapter):
            self.adapters[prefix] = adapter

        def get(self, *_args, **_kwargs):
            self.adapters["https://"]._register_socket(ActiveSocket())
            release.wait(1)
            return fake_response()

    target = CONTENT.ResolvedTarget(
        "https",
        "public.example",
        443,
        (CONTENT.ResolvedEndpoint(
            CONTENT.socket.AF_INET,
            CONTENT.socket.SOCK_STREAM,
            6,
            ("93.184.216.34", 443),
        ),),
    )
    session = BlockingSession()
    started = CONTENT.time.monotonic()
    try:
        with pytest.raises(requests.Timeout, match="total time budget"):
            with CONTENT._open_pinned_response(
                    session, "https://public.example/source", target,
                    started + 0.05):
                pytest.fail("a response must not outlive the deadline")
    finally:
        release.set()

    assert CONTENT.time.monotonic() - started < 0.75
    assert closed == [True]
    assert session.adapters["https://"] is previous_adapter


def test_pinned_adapter_rejects_proxy_and_disabled_tls_verification():
    target = CONTENT.ResolvedTarget(
        "https",
        "public.example",
        443,
        (CONTENT.ResolvedEndpoint(
            CONTENT.socket.AF_INET,
            CONTENT.socket.SOCK_STREAM,
            6,
            ("93.184.216.34", 443),
        ),),
    )
    request = requests.Request(
        "GET", "https://public.example/source").prepare()
    adapter = CONTENT._PinnedAddressAdapter(target)
    try:
        with pytest.raises(CONTENT.UnsafeURL, match="proxies are disabled"):
            adapter.send(
                request, proxies={"https": "http://127.0.0.1:9999"}, verify=True)
        with pytest.raises(CONTENT.UnsafeURL, match="TLS verification"):
            adapter.send(request, proxies={}, verify=False)
    finally:
        adapter.close()


def test_safe_fetch_rejects_https_to_http_redirect(monkeypatch):
    class RedirectResponse:
        status_code = 302
        headers = {"Location": "http://public.example/downgrade"}
        url = "https://public.example/start"
        is_redirect = True
        is_permanent_redirect = False

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    real_validate = CONTENT.validate_public_url
    checked = []

    def validate(url, deadline):
        checked.append(url)
        return real_validate(url, deadline)

    monkeypatch.setattr(
        CONTENT.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (CONTENT.socket.AF_INET, CONTENT.socket.SOCK_STREAM, 6, "",
             ("93.184.216.34", 443))],
    )
    monkeypatch.setattr(CONTENT, "validate_public_url", validate)
    install_fake_transport(
        monkeypatch, lambda _url, _target, _timeout: RedirectResponse())
    with pytest.raises(CONTENT.UnsafeURL, match="only concrete HTTPS"):
        CONTENT.fetch("https://public.example/start")
    assert checked == [
        "https://public.example/start", "http://public.example/downgrade"]


def test_redirect_chain_shares_one_absolute_deadline(monkeypatch):
    class RedirectResponse:
        status_code = 302
        headers = {"Location": "/next"}
        url = "https://public.example/start"
        is_redirect = True
        is_permanent_redirect = False

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    clock = [100.0]
    deadlines = []
    calls = []
    monkeypatch.setattr(CONTENT.time, "monotonic", lambda: clock[0])

    def validate(_url, deadline):
        deadlines.append(deadline)
        CONTENT._remaining(deadline)

    def respond(*args):
        calls.append(args)
        clock[0] += 0.6
        return RedirectResponse()

    monkeypatch.setattr(CONTENT, "validate_public_url", validate)
    install_fake_transport(monkeypatch, respond)

    with pytest.raises(requests.Timeout, match="total time budget"):
        CONTENT.fetch(
            "https://public.example/start", timeout=1, attempts=1)

    assert calls
    assert set(deadlines) == {101.0}


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
    calls = []
    delays = []
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url, deadline: None)

    def respond(*args):
        calls.append(args)
        if len(calls) == 1:
            raise requests.ReadTimeout("temporary read timeout")
        return fake_response()

    install_fake_transport(monkeypatch, respond)

    result = CONTENT.fetch(
        "https://public.example/source",
        quote="A sufficiently long mechanism quote from the source.",
        attempts=3,
        retry_backoff=1,
        sleeper=delays.append,
    )

    assert len(calls) == 2
    assert delays == [1]
    assert result["mechanism_quote_present"] is True


def test_safe_fetch_exhausts_bounded_transient_retries(monkeypatch):
    calls = []
    delays = []
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url, deadline: None)

    def fail(*args):
        calls.append(args)
        raise requests.ConnectionError("temporary connection failure")

    install_fake_transport(monkeypatch, fail)

    with pytest.raises(requests.ConnectionError, match="temporary connection failure"):
        CONTENT.fetch(
            "https://public.example/source",
            attempts=3,
            retry_backoff=1,
            sleeper=delays.append,
        )

    assert len(calls) == 3
    assert delays == [1, 2]


def test_stream_read_is_cancelled_at_total_deadline(monkeypatch):
    closed = []

    class SlowResponse:
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
            CONTENT.time.sleep(1)
            yield b"late content"

        def close(self):
            closed.append(True)

    monkeypatch.setattr(
        CONTENT, "validate_public_url", lambda url, deadline: None)
    install_fake_transport(
        monkeypatch, lambda _url, _target, _deadline: SlowResponse())
    started = CONTENT.time.monotonic()

    with pytest.raises(requests.Timeout, match="total time budget"):
        CONTENT.fetch(
            "https://public.example/source", timeout=0.05, attempts=1)

    assert CONTENT.time.monotonic() - started < 0.75
    assert closed == [True]


def test_retry_backoff_cannot_overrun_total_deadline(monkeypatch):
    release = CONTENT.threading.Event()
    monkeypatch.setattr(
        CONTENT, "validate_public_url", lambda url, deadline: None)
    install_fake_transport(
        monkeypatch,
        lambda *_args: (_ for _ in ()).throw(
            requests.ConnectionError("temporary failure")),
    )
    started = CONTENT.time.monotonic()
    try:
        with pytest.raises(requests.Timeout, match="total time budget"):
            CONTENT.fetch(
                "https://public.example/source",
                timeout=0.05,
                attempts=3,
                retry_backoff=0.01,
                sleeper=lambda _delay: release.wait(1),
            )
    finally:
        release.set()

    assert CONTENT.time.monotonic() - started < 0.75


@pytest.mark.parametrize("status", [408, 425, 429, 500, 502, 503, 504])
def test_safe_fetch_retries_transient_http_status(monkeypatch, status):
    calls = []
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url, deadline: None)

    def respond(*args):
        calls.append(args)
        return fake_response(status if len(calls) == 1 else 200)

    install_fake_transport(monkeypatch, respond)

    CONTENT.fetch(
        "https://public.example/source",
        attempts=2,
        retry_backoff=0,
    )

    assert len(calls) == 2


@pytest.mark.parametrize("status", [403, 404, 501])
def test_safe_fetch_does_not_retry_permanent_http_status(monkeypatch, status):
    calls = []
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url, deadline: None)

    def respond(*args):
        calls.append(args)
        return fake_response(status)

    install_fake_transport(monkeypatch, respond)

    with pytest.raises(requests.HTTPError):
        CONTENT.fetch(
            "https://public.example/missing",
            attempts=3,
            retry_backoff=0,
        )

    assert len(calls) == 1


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

        def close(self):
            pass

    calls = []
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url, deadline: None)

    def respond(*args):
        calls.append(args)
        return TruncatedResponse() if len(calls) == 1 else fake_response()

    install_fake_transport(monkeypatch, respond)

    CONTENT.fetch(
        "https://public.example/source",
        attempts=2,
        retry_backoff=0,
    )

    assert len(calls) == 2


def test_safe_fetch_does_not_retry_certificate_failure(monkeypatch):
    calls = []
    monkeypatch.setattr(CONTENT, "validate_public_url", lambda url, deadline: None)

    def fail(*args):
        calls.append(args)
        raise requests.exceptions.SSLError("certificate verify failed")

    install_fake_transport(monkeypatch, fail)

    with pytest.raises(requests.exceptions.SSLError, match="certificate verify failed"):
        CONTENT.fetch(
            "https://public.example/source",
            attempts=3,
            retry_backoff=0,
        )

    assert len(calls) == 1


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
