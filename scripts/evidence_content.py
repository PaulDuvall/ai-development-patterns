#!/usr/bin/env python3
"""Fetch and fingerprint normalized evidence content for schema-v2 records."""

import argparse
import hashlib
import html
import ipaddress
import json
import re
import socket
import sys
import unicodedata
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup


MAX_REDIRECTS = 5
MAX_RESPONSE_BYTES = 5 * 1024 * 1024
USER_AGENT = "Mozilla/5.0 (ai-development-patterns evidence verifier)"


class UnsafeURL(ValueError):
    """Raised when evidence fetching would cross a public-network boundary."""


class ResponseTooLarge(ValueError):
    """Raised when a source exceeds the bounded evidence-fetch budget."""


class UnsupportedContent(ValueError):
    """Raised when a source cannot be normalized as visible text."""


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
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)), doseq=True)
    return urlunsplit((parsed.scheme.casefold(), hostname, path, query, ""))


def validate_public_url(url):
    """Resolve a URL and reject credentials, local names, and any non-global address."""
    if not isinstance(url, str) or any(character.isspace() for character in url):
        raise UnsafeURL("URL must be a whitespace-free string")
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or not parsed.netloc:
        raise UnsafeURL("only concrete HTTP(S) URLs are allowed")
    if parsed.username is not None or parsed.password is not None:
        raise UnsafeURL("URL credentials are not allowed")
    try:
        port = parsed.port
    except ValueError as exc:
        raise UnsafeURL("URL port is invalid") from exc
    expected_port = 443 if parsed.scheme == "https" else 80
    if port not in {None, expected_port}:
        raise UnsafeURL("only the default HTTP(S) port is allowed")

    hostname = parsed.hostname.rstrip(".").casefold()
    if "%" in hostname or hostname == "localhost" \
            or hostname.endswith((".localhost", ".local", ".internal")):
        raise UnsafeURL(f"local hostname is not allowed: {hostname}")
    try:
        literal = ipaddress.ip_address(hostname)
        addresses = {literal}
    except ValueError:
        try:
            answers = socket.getaddrinfo(
                hostname, expected_port, type=socket.SOCK_STREAM)
        except socket.gaierror as exc:
            raise UnsafeURL(f"hostname did not resolve: {hostname}") from exc
        addresses = {ipaddress.ip_address(answer[4][0]) for answer in answers}
    if not addresses or any(not address.is_global for address in addresses):
        rendered = ", ".join(sorted(str(address) for address in addresses)) or "none"
        raise UnsafeURL(f"hostname resolves to a non-public address: {rendered}")


def _read_bounded_text(response, max_bytes):
    """Read a streamed response up to a fixed byte ceiling."""
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
    chunks = []
    size = 0
    for chunk in response.iter_content(chunk_size=65536):
        if not chunk:
            continue
        size += len(chunk)
        if size > max_bytes:
            raise ResponseTooLarge(f"response exceeds {max_bytes} bytes")
        chunks.append(chunk)
    encoding = response.encoding or "utf-8"
    return b"".join(chunks).decode(encoding, errors="replace")


def fetch(
        url, quote=None, timeout=20, max_redirects=MAX_REDIRECTS,
        max_bytes=MAX_RESPONSE_BYTES, session=None):
    """Safely fetch one public URL and return the schema provenance values."""
    owns_session = session is None
    session = session or requests.Session()
    if owns_session:
        session.trust_env = False
    current_url = url
    try:
        for redirect_count in range(max_redirects + 1):
            validate_public_url(current_url)
            with session.get(
                    current_url,
                    timeout=timeout,
                    allow_redirects=False,
                    stream=True,
                    headers={"User-Agent": USER_AGENT}) as response:
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
                content = _read_bounded_text(response, max_bytes)
                resolved_url = response.url
                break
        else:  # pragma: no cover - loop either breaks or raises at its bound
            raise requests.TooManyRedirects(f"more than {max_redirects} redirects")
    finally:
        if owns_session:
            session.close()
    return {
        "resolved_url": resolved_url,
        "content_sha256": content_sha256(content),
        "mechanism_quote_present": (
            quote_is_present(quote, content) if quote is not None else None),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--quote")
    parser.add_argument("--timeout", type=int, default=20)
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
