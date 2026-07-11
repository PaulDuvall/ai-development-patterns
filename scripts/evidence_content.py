#!/usr/bin/env python3
"""Fetch and fingerprint normalized evidence content for schema-v2 records."""

import argparse
from contextlib import contextmanager
import hashlib
import html
import ipaddress
import json
import math
import queue
import re
import socket
import sys
import threading
import time
import unicodedata
from typing import NamedTuple
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

import idna
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPSConnection
from urllib3.connectionpool import HTTPSConnectionPool
from urllib3.exceptions import ConnectTimeoutError, NewConnectionError


MAX_REDIRECTS = 5
MAX_RESPONSE_BYTES = 5 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 30
MAX_FETCH_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 1
USER_AGENT = "Mozilla/5.0 (ai-development-patterns evidence verifier)"
VOLATILE_TRACKING_QUERY_KEYS = {
    "fbclid", "gclid", "gi", "mc_cid", "mc_eid",
}

# Python's ``ipaddress.is_global`` follows the tables bundled with the Python
# runtime, so it can lag additions to the IANA special-purpose registries. Keep
# an explicit conservative denylist for non-globally-reachable allocations. A
# runtime update may make an entry redundant; retaining it is intentional.
NON_PUBLIC_NETWORKS = tuple(ipaddress.ip_network(value) for value in (
    # IPv4 special-purpose ranges without ordinary global reachability.
    "0.0.0.0/8",
    "10.0.0.0/8",
    "100.64.0.0/10",
    "127.0.0.0/8",
    "169.254.0.0/16",
    "172.16.0.0/12",
    "192.0.0.0/24",
    "192.0.2.0/24",
    "192.88.99.0/24",
    "192.168.0.0/16",
    "198.18.0.0/15",
    "198.51.100.0/24",
    "203.0.113.0/24",
    "224.0.0.0/4",
    "240.0.0.0/4",
    # IPv6 special-purpose ranges without ordinary global reachability.
    "::/96",
    "::ffff:0:0/96",
    # Public NAT64 literals can embed private IPv4 destinations, including the
    # link-local metadata service, so evidence retrieval rejects the prefix.
    "64:ff9b::/96",
    "64:ff9b:1::/48",
    "100::/64",
    "100:0:0:1::/64",
    "2001::/23",
    "2001:db8::/32",
    "2002::/16",
    "3fff::/20",
    "5f00::/16",
    "fc00::/7",
    "fe80::/10",
    "fec0::/10",
    "ff00::/8",
))


class UnsafeURL(ValueError):
    """Raised when evidence fetching would cross a public-network boundary."""


class ResponseTooLarge(ValueError):
    """Raised when a source exceeds the bounded evidence-fetch budget."""


class UnsupportedContent(ValueError):
    """Raised when a source cannot be normalized as visible text."""


class ResolvedEndpoint(NamedTuple):
    """One resolver answer retained verbatim for a later pinned connection."""

    family: int
    socktype: int
    protocol: int
    sockaddr: tuple


class ResolvedTarget(NamedTuple):
    """A validated URL origin and the public endpoints resolved for this hop."""

    scheme: str
    hostname: str
    port: int
    endpoints: tuple


def normalize_text(value):
    """Normalize HTML, Unicode typography, case, and whitespace deterministically."""
    text = BeautifulSoup(html.unescape(str(value)), "html.parser").get_text(" ")
    text = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).strip()


def content_sha256(value):
    """Hash normalized visible text rather than volatile raw HTML markup."""
    return hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()


def quote_is_present(quote, content):
    """Return whether a sufficiently specific normalized quote remains present."""
    normalized_quote = normalize_text(quote)
    return len(normalized_quote) >= 20 and normalized_quote in normalize_text(content)


def canonical_url(value):
    """Canonicalize a fetched URL for an exact resolved-URL comparison."""
    parsed = urlsplit(value)
    hostname = (parsed.hostname or "").rstrip(".").casefold()
    try:
        if ipaddress.ip_address(hostname).version == 6:
            hostname = f"[{hostname}]"
    except ValueError:
        pass
    port = parsed.port
    if port and not ((parsed.scheme == "http" and port == 80)
                     or (parsed.scheme == "https" and port == 443)):
        hostname = f"{hostname}:{port}"
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    query_items = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.casefold() not in VOLATILE_TRACKING_QUERY_KEYS
        and not key.casefold().startswith("utm_")
    ]
    query = urlencode(sorted(query_items), doseq=True)
    return urlunsplit((parsed.scheme.casefold(), hostname, path, query, ""))


def _require_modern_requests():
    """Fail clearly when the pinned TLS adapter API is unavailable."""
    if not callable(getattr(HTTPAdapter, "get_connection_with_tls_context", None)):
        raise RuntimeError(
            "evidence retrieval requires Requests with "
            "HTTPAdapter.get_connection_with_tls_context (Requests 2.32.2+)")


def _remaining(deadline):
    """Return the positive remainder of one absolute monotonic budget."""
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise requests.Timeout("evidence fetch exceeded its total time budget")
    return remaining


def _cancel_quietly(cancel):
    """Best-effort cancellation must not conceal the deadline failure."""
    if cancel is None:
        return
    try:
        cancel()
    except BaseException:  # pragma: no cover - defensive cleanup only
        pass


def _run_before_deadline(operation, deadline, *, cancel=None, dispose=None):
    """Run a potentially blocking operation behind an absolute deadline."""
    outcomes = queue.Queue(maxsize=1)
    abandoned = threading.Event()

    def discard(outcome):
        succeeded, value = outcome
        if succeeded and dispose is not None:
            _cancel_quietly(lambda: dispose(value))

    def invoke():
        try:
            outcome = (True, operation())
        except BaseException as exc:  # propagate after cleanup in the caller
            outcome = (False, exc)
        if abandoned.is_set():
            discard(outcome)
            return
        try:
            outcomes.put_nowait(outcome)
        except queue.Full:  # pragma: no cover - caller has already timed out
            discard(outcome)
            return
        if abandoned.is_set():
            try:
                discard(outcomes.get_nowait())
            except queue.Empty:  # caller won the race and owns the outcome
                pass

    worker = threading.Thread(
        target=invoke, name="evidence-network-operation", daemon=True)
    worker.start()
    try:
        succeeded, value = outcomes.get(timeout=_remaining(deadline))
    except queue.Empty as exc:
        abandoned.set()
        _cancel_quietly(cancel)
        raise requests.Timeout(
            "evidence fetch exceeded its total time budget") from exc
    if time.monotonic() >= deadline:
        abandoned.set()
        _cancel_quietly(cancel)
        discard((succeeded, value))
        raise requests.Timeout("evidence fetch exceeded its total time budget")
    if not succeeded:
        raise value
    return value


def _resolve_hostname(hostname, port, deadline):
    """Resolve DNS on a bounded daemon thread within the total fetch budget."""
    try:
        return _run_before_deadline(
            lambda: socket.getaddrinfo(
                hostname, port, type=socket.SOCK_STREAM),
            deadline,
        )
    except requests.Timeout as exc:
        raise requests.ConnectTimeout(
            f"DNS resolution timed out for {hostname}") from exc


def _is_public_address(address):
    """Apply runtime and explicit IANA non-public address policy."""
    if not address.is_global or address.is_multicast or address.is_unspecified \
            or getattr(address, "is_site_local", False):
        return False
    return not any(
        address.version == network.version and address in network
        for network in NON_PUBLIC_NETWORKS)


def validate_public_url(url, deadline=None):
    """Resolve a URL once and return only its already-validated public endpoints."""
    if deadline is None:
        deadline = time.monotonic() + DEFAULT_TIMEOUT_SECONDS
    _remaining(deadline)
    if not isinstance(url, str) or any(character.isspace() for character in url):
        raise UnsafeURL("URL must be a whitespace-free string")
    try:
        parsed = urlsplit(url)
        parsed_hostname = parsed.hostname
    except ValueError as exc:
        raise UnsafeURL("URL authority is invalid") from exc
    if parsed.scheme != "https" or not parsed_hostname or not parsed.netloc:
        raise UnsafeURL("only concrete HTTPS URLs are allowed")
    if parsed.username is not None or parsed.password is not None:
        raise UnsafeURL("URL credentials are not allowed")
    try:
        port = parsed.port
    except ValueError as exc:
        raise UnsafeURL("URL port is invalid") from exc
    expected_port = 443
    if port not in {None, expected_port}:
        raise UnsafeURL("only the default HTTPS port is allowed")

    hostname = parsed_hostname.rstrip(".").casefold()
    if "%" in hostname:
        raise UnsafeURL(f"local hostname is not allowed: {hostname}")
    try:
        literal = ipaddress.ip_address(hostname)
        family = socket.AF_INET6 if literal.version == 6 else socket.AF_INET
        sockaddr = ((str(literal), expected_port, 0, 0) if literal.version == 6
                    else (str(literal), expected_port))
        answers = [(family, socket.SOCK_STREAM, 0, "", sockaddr)]
    except ValueError:
        try:
            hostname = idna.encode(hostname, uts46=True).decode("ascii")
        except idna.IDNAError as exc:
            raise UnsafeURL("URL hostname is invalid") from exc
        if hostname == "localhost" \
                or hostname.endswith((".localhost", ".local", ".internal")):
            raise UnsafeURL(f"local hostname is not allowed: {hostname}")
        try:
            answers = _resolve_hostname(hostname, expected_port, deadline)
        except socket.gaierror as exc:
            raise UnsafeURL(f"hostname did not resolve: {hostname}") from exc

    endpoints = []
    addresses = []
    seen = set()
    for family, socktype, protocol, _canonical_name, sockaddr in answers:
        if family not in {socket.AF_INET, socket.AF_INET6}:
            continue
        if socktype not in {0, socket.SOCK_STREAM}:
            continue
        if protocol not in {0, socket.IPPROTO_TCP}:
            continue
        socktype = socket.SOCK_STREAM
        try:
            address = ipaddress.ip_address(sockaddr[0])
            if sockaddr[1] != expected_port:
                continue
        except (IndexError, ValueError, TypeError):
            continue
        if ((family == socket.AF_INET and address.version != 4)
                or (family == socket.AF_INET6 and address.version != 6)):
            continue
        endpoint = ResolvedEndpoint(family, socktype, protocol, tuple(sockaddr))
        if endpoint not in seen:
            seen.add(endpoint)
            endpoints.append(endpoint)
            addresses.append(address)
    if not addresses or any(not _is_public_address(address) for address in addresses):
        rendered = ", ".join(sorted(str(address) for address in addresses)) or "none"
        raise UnsafeURL(f"hostname resolves to a non-public address: {rendered}")
    return ResolvedTarget(parsed.scheme, hostname, expected_port, tuple(endpoints))


class _PinnedConnectionMixin:
    """Open a socket without resolving the original hostname a second time."""

    def __init__(self, *args, verified_endpoints, socket_registrar, **kwargs):
        self.verified_endpoints = tuple(verified_endpoints)
        self._socket_registrar = socket_registrar
        if not self.verified_endpoints:
            raise UnsafeURL("a pinned connection requires a verified endpoint")
        super().__init__(*args, **kwargs)

    def _new_conn(self):
        timeout = self.timeout
        has_timeout = isinstance(timeout, (int, float)) and timeout is not None
        deadline = time.monotonic() + timeout if has_timeout else None
        last_error = None

        for endpoint in self.verified_endpoints:
            connection = None
            try:
                connection = socket.socket(
                    endpoint.family, endpoint.socktype, endpoint.protocol)
                self._socket_registrar(connection)
                if deadline is not None:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise socket.timeout("pinned connection timed out")
                    connection.settimeout(remaining)
                if self.source_address:
                    connection.bind(self.source_address)
                for option in self.socket_options or ():
                    connection.setsockopt(*option)
            except BaseException as exc:
                if connection is not None:
                    _cancel_quietly(connection.close)
                if not isinstance(exc, OSError):
                    raise
                last_error = exc
                continue
            try:
                sys.audit("http.client.connect", self, self.host, self.port)
            except BaseException:
                _cancel_quietly(connection.close)
                raise
            try:
                connection.connect(endpoint.sockaddr)
                return connection
            except BaseException as exc:
                _cancel_quietly(connection.close)
                if not isinstance(exc, OSError):
                    raise
                last_error = exc

        if isinstance(last_error, (socket.timeout, TimeoutError)):
            raise ConnectTimeoutError(
                self,
                f"Connection to {self.host} timed out. (connect timeout={timeout})",
            ) from last_error
        raise NewConnectionError(
            self, f"Failed to establish a pinned connection: {last_error}"
        ) from last_error


class _PinnedHTTPSConnection(_PinnedConnectionMixin, HTTPSConnection):
    """HTTPS connection retaining the origin hostname for TLS verification."""

    def connect(self):
        """Retain the TLS-wrapped socket so deadline cancellation can close it."""
        try:
            super().connect()
        except BaseException:
            if self.sock is not None:
                _cancel_quietly(self.sock.close)
            raise
        self._socket_registrar(self.sock)


class _PinnedHTTPSConnectionPool(HTTPSConnectionPool):
    ConnectionCls = _PinnedHTTPSConnection

    def __init__(
            self, host, port, *, verified_endpoints, socket_registrar, **kwargs):
        super().__init__(
            host,
            port,
            verified_endpoints=verified_endpoints,
            socket_registrar=socket_registrar,
            **kwargs,
        )


def _url_origin(url):
    """Return the normalized origin tuple used to bind an adapter to one hop."""
    parsed = urlsplit(url)
    scheme = parsed.scheme.casefold()
    hostname = (parsed.hostname or "").rstrip(".").casefold()
    port = parsed.port or (443 if scheme == "https" else 80)
    return scheme, hostname, port


def _host_header(target):
    """Render the original hostname, including IPv6 brackets, for HTTP Host."""
    try:
        if ipaddress.ip_address(target.hostname).version == 6:
            return f"[{target.hostname}]"
    except ValueError:
        pass
    return target.hostname


class _PinnedAddressAdapter(HTTPAdapter):
    """Requests transport bound to one validated origin and its resolved peers."""

    def __init__(self, target):
        _require_modern_requests()
        if target.scheme != "https":
            raise UnsafeURL("pinned evidence transport requires HTTPS")
        self.target = target
        self._pinned_pools = []
        self._active_sockets = []
        self._state_lock = threading.Lock()
        self._closed = False
        super().__init__(max_retries=0)

    def _register_socket(self, connection):
        with self._state_lock:
            if self._closed:
                cancelled = True
            else:
                self._active_sockets.append(connection)
                cancelled = False
        if cancelled:
            _cancel_quietly(connection.close)
            raise socket.timeout("pinned evidence transport was cancelled")

    def _assert_exact_origin(self, url):
        expected_origin = (
            self.target.scheme, self.target.hostname, self.target.port)
        if _url_origin(url) != expected_origin:
            raise UnsafeURL("pinned transport cannot be reused for another origin")

    def _pool_for(self, request, verify, cert):
        self._assert_exact_origin(request.url)
        _host_parameters, pool_kwargs = self.build_connection_pool_key_attributes(
            request, verify, cert)
        pool_kwargs.pop("assert_hostname", None)
        pool_kwargs.pop("server_hostname", None)
        pool = _PinnedHTTPSConnectionPool(
            self.target.hostname,
            self.target.port,
            verified_endpoints=self.target.endpoints,
            socket_registrar=self._register_socket,
            assert_hostname=self.target.hostname,
            server_hostname=self.target.hostname,
            **pool_kwargs,
        )
        with self._state_lock:
            if self._closed:
                cancelled = True
            else:
                self._pinned_pools.append(pool)
                cancelled = False
        if cancelled:
            pool.close()
            raise requests.Timeout("pinned evidence transport was cancelled")
        return pool

    def get_connection_with_tls_context(
            self, request, verify, proxies=None, cert=None):
        if any((proxies or {}).values()):
            raise UnsafeURL("proxies are disabled for evidence retrieval")
        return self._pool_for(request, verify, cert)

    def send(self, request, *args, **kwargs):
        if kwargs.get("verify", True) is not True:
            raise UnsafeURL("TLS verification cannot be disabled for evidence retrieval")
        if any((kwargs.get("proxies") or {}).values()):
            raise UnsafeURL("proxies are disabled for evidence retrieval")
        self._assert_exact_origin(request.url)
        request.headers["Host"] = _host_header(self.target)
        return super().send(request, *args, **kwargs)

    def close(self):
        with self._state_lock:
            self._closed = True
            sockets = self._active_sockets
            pools = self._pinned_pools
            self._active_sockets = []
            self._pinned_pools = []
        for connection in sockets:
            _cancel_quietly(connection.close)
        for pool in pools:
            _cancel_quietly(pool.close)
        super().close()


@contextmanager
def _open_pinned_response(session, url, target, deadline):
    """Yield one streamed response through a hop-specific pinned adapter."""
    prefix = "https://"
    previous_adapter = session.adapters[prefix]
    adapter = _PinnedAddressAdapter(target)
    session.mount(prefix, adapter)
    try:
        response = _run_before_deadline(
            lambda: session.get(
                url,
                timeout=_remaining(deadline),
                allow_redirects=False,
                stream=True,
                headers={"User-Agent": USER_AGENT},
                proxies={},
                verify=True,
            ),
            deadline,
            cancel=adapter.close,
            dispose=lambda response: response.close(),
        )
        with response:
            yield response
    finally:
        session.mount(prefix, previous_adapter)
        adapter.close()


def _read_bounded_text(response, max_bytes, deadline):
    """Read a streamed response up to a fixed byte ceiling."""
    _remaining(deadline)
    media_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().casefold()
    textual_application_types = {
        "application/json", "application/xml", "application/xhtml+xml",
    }
    if media_type and not (
            media_type.startswith("text/") or media_type in textual_application_types):
        raise UnsupportedContent(f"unsupported evidence content type: {media_type}")
    content_length = response.headers.get("Content-Length")
    if content_length:
        try:
            if int(content_length) > max_bytes:
                raise ResponseTooLarge(f"response exceeds {max_bytes} bytes")
        except ValueError:
            pass

    def read_stream():
        chunks = []
        size = 0
        for chunk in response.iter_content(chunk_size=65536):
            _remaining(deadline)
            if not chunk:
                continue
            size += len(chunk)
            if size > max_bytes:
                raise ResponseTooLarge(f"response exceeds {max_bytes} bytes")
            chunks.append(chunk)
        encoding = response.encoding or "utf-8"
        content = b"".join(chunks).decode(encoding, errors="replace")
        _remaining(deadline)
        return content

    return _run_before_deadline(
        read_stream, deadline, cancel=response.close)


def _fetch_once(url, quote, deadline, max_redirects, max_bytes, session):
    """Perform one pinned, redirect-bounded evidence retrieval."""
    current_url = url
    for redirect_count in range(max_redirects + 1):
        target = validate_public_url(current_url, deadline)
        with _open_pinned_response(
                session, current_url, target, deadline) as response:
            _remaining(deadline)
            if response.is_redirect or response.is_permanent_redirect:
                location = response.headers.get("Location")
                if not location:
                    raise requests.HTTPError(
                        "redirect response has no Location header", response=response)
                if redirect_count >= max_redirects:
                    raise requests.TooManyRedirects(
                        f"more than {max_redirects} redirects", response=response)
                current_url = urljoin(current_url, location)
                continue
            if not 200 <= response.status_code < 300:
                response.raise_for_status()
                raise requests.HTTPError(
                    f"unexpected HTTP status {response.status_code}", response=response)
            content = _read_bounded_text(response, max_bytes, deadline)
            resolved_url = response.url
            break
    else:  # pragma: no cover - loop either breaks or raises at its bound
        raise requests.TooManyRedirects(f"more than {max_redirects} redirects")
    result = {
        "resolved_url": resolved_url,
        "content_sha256": content_sha256(content),
        "mechanism_quote_present": (
            quote_is_present(quote, content) if quote is not None else None),
    }
    _remaining(deadline)
    return result


def _is_retryable_request_error(exc):
    """Return whether a bounded repeat can plausibly recover this request."""
    if isinstance(exc, requests.exceptions.SSLError):
        return False
    transient_transport_errors = (
        requests.Timeout,
        requests.ConnectionError,
        requests.exceptions.ChunkedEncodingError,
        requests.exceptions.ContentDecodingError,
    )
    if isinstance(exc, transient_transport_errors):
        return True
    if not isinstance(exc, requests.HTTPError) or exc.response is None:
        return False
    status = exc.response.status_code
    return status in {408, 425, 429, 500, 502, 503, 504}


def fetch(
        url, quote=None, timeout=DEFAULT_TIMEOUT_SECONDS, max_redirects=MAX_REDIRECTS,
        max_bytes=MAX_RESPONSE_BYTES, attempts=MAX_FETCH_ATTEMPTS,
        retry_backoff=RETRY_BACKOFF_SECONDS, sleeper=time.sleep):
    """Safely fetch one public HTTPS URL within one total time budget."""
    _require_modern_requests()
    if not isinstance(attempts, int) or attempts < 1:
        raise ValueError("attempts must be a positive integer")
    if retry_backoff < 0:
        raise ValueError("retry_backoff must be non-negative")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) \
            or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be a positive finite number")
    deadline = time.monotonic() + timeout
    with requests.Session() as session:
        # Evidence retrieval must not inherit proxy, CA-bundle, netrc, or other
        # ambient network settings from the runner environment.
        session.trust_env = False
        session.proxies.clear()
        for attempt in range(1, attempts + 1):
            _remaining(deadline)
            try:
                return _fetch_once(
                    url, quote, deadline, max_redirects, max_bytes, session)
            except requests.RequestException as exc:
                if attempt >= attempts or not _is_retryable_request_error(exc):
                    raise
                delay = retry_backoff * (2 ** (attempt - 1))
                remaining = _remaining(deadline)
                if delay >= remaining:
                    raise requests.Timeout(
                        "retry backoff would exceed the total evidence-fetch "
                        "time budget") from exc
                print(
                    f"warning: transient evidence fetch failed on attempt "
                    f"{attempt}/{attempts}; retrying in {delay:g}s",
                    file=sys.stderr,
                )
                if delay:
                    _run_before_deadline(
                        lambda: sleeper(delay), deadline)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--quote")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args()
    try:
        result = fetch(args.url, args.quote, args.timeout)
    except (requests.RequestException, UnsafeURL, ResponseTooLarge, UnsupportedContent) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if args.quote is not None and not result["mechanism_quote_present"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
