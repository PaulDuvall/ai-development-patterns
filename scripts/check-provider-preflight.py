#!/usr/bin/env python3
"""Fail fast on unusable evidence-provider credentials, quota, or models.

The probe makes exactly one minimal generation request. API keys are read only
from the environment, and diagnostics use fixed categories so provider bodies
or exception messages can never disclose credentials in Actions logs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
from typing import Callable, Mapping, NamedTuple
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


OPENAI_URL = "https://api.openai.com/v1/responses"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
REQUEST_TIMEOUT_SECONDS = 60
MAX_RESPONSE_BYTES = 64 * 1024
MODEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,99}")


class Response(NamedTuple):
    status: int
    body: bytes


class PreflightFailure(Exception):
    """A safe diagnostic category, never a raw provider error."""

    def __init__(self, category: str):
        super().__init__(category)
        self.category = category


Transport = Callable[[str, str, Mapping[str, str], bytes, int], Response]


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _read_response(response) -> Response:
    body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise PreflightFailure("oversized_provider_response")
    return Response(status=response.status, body=body)


def _stdlib_transport(
    method: str,
    url: str,
    headers: Mapping[str, str],
    body: bytes,
    timeout: int,
) -> Response:
    request = Request(url, data=body, headers=dict(headers), method=method)
    # Never let runner-level proxy variables receive provider credentials.
    opener = build_opener(ProxyHandler({}), _NoRedirects())
    try:
        try:
            response = opener.open(request, timeout=timeout)
        except HTTPError as error:
            response = error
        with response:
            return _read_response(response)
    except PreflightFailure:
        raise
    except (TimeoutError, socket.timeout) as error:
        raise PreflightFailure("provider_timeout") from error
    except URLError as error:
        if isinstance(error.reason, (TimeoutError, socket.timeout)):
            raise PreflightFailure("provider_timeout") from error
        raise PreflightFailure("provider_unavailable") from error
    except OSError as error:
        raise PreflightFailure("provider_unavailable") from error


def _json_body(body: bytes) -> dict | None:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _error_fields(document: dict | None) -> tuple[str, str]:
    error = document.get("error") if document else None
    if not isinstance(error, dict):
        return "", ""
    code = error.get("code") or error.get("type") or ""
    parameter = error.get("param") or ""
    return (
        code if isinstance(code, str) else "",
        parameter if isinstance(parameter, str) else "",
    )


def _failure_category(provider: str, status: int, document: dict | None) -> str:
    code, parameter = _error_fields(document)
    if status == 400 and (
        parameter == "model"
        or code in {"invalid_model", "model_not_found", "not_found_error"}
    ):
        return "model_unavailable"
    if status == 400:
        return "invalid_provider_request"
    if status == 401:
        return "authentication_failed"
    if status == 402:
        return "billing_or_credit_error"
    if status == 403:
        return "authorization_failed"
    if status == 404:
        return "model_unavailable"
    if status in {408, 504}:
        return "provider_timeout"
    if status == 429:
        if provider == "openai" and code == "insufficient_quota":
            return "quota_exhausted"
        return "rate_limited"
    if status in {500, 502, 503, 529}:
        return "provider_unavailable"
    if 300 <= status < 400:
        return "unexpected_provider_redirect"
    return "provider_request_failed"


def _is_success(provider: str, document: dict | None) -> bool:
    if document is None:
        return False
    if provider == "openai":
        return (
            document.get("object") == "response"
            and document.get("error") is None
            and document.get("status") in {"completed", "incomplete"}
        )
    return (
        document.get("type") == "message"
        and isinstance(document.get("id"), str)
        and bool(document["id"])
        and isinstance(document.get("model"), str)
        and bool(document["model"])
        and isinstance(document.get("content"), list)
    )


def probe(
    provider: str,
    model: str,
    api_key: str,
    *,
    transport: Transport = _stdlib_transport,
) -> None:
    """Make one generation request or raise a redacted failure category."""
    if provider == "openai":
        url = OPENAI_URL
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "input": "Reply with OK.",
            "max_output_tokens": 16,
            "store": False,
        }
    else:
        url = ANTHROPIC_URL
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "Reply with OK."}],
            "stream": False,
        }

    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    response = transport(
        "POST", url, headers, body, REQUEST_TIMEOUT_SECONDS
    )
    if len(response.body) > MAX_RESPONSE_BYTES:
        raise PreflightFailure("oversized_provider_response")
    document = _json_body(response.body)
    if response.status != 200:
        raise PreflightFailure(
            _failure_category(provider, response.status, document)
        )
    if not _is_success(provider, document):
        raise PreflightFailure("invalid_provider_response")


REMEDIATION = {
    "authentication_failed": "Check or rotate the configured API key, then rerun.",
    "authorization_failed": "Grant the key access to the selected model, then rerun.",
    "billing_or_credit_error": "Fix provider billing or add credits, then rerun.",
    "invalid_model_identifier": "Configure a safe, valid provider model identifier.",
    "invalid_provider_request": "Review the selected model and provider API contract.",
    "invalid_provider_response": "Retry later; the provider returned an invalid response.",
    "missing_credential": "Configure the selected provider API key, then rerun.",
    "model_unavailable": "Select a model available to this API project, then rerun.",
    "oversized_provider_response": "Retry later; the provider response was oversized.",
    "provider_request_failed": "Review provider status and configuration, then rerun.",
    "provider_timeout": "Retry after provider connectivity recovers.",
    "provider_unavailable": "Retry after provider service recovers.",
    "quota_exhausted": "Add credits or raise the project usage limit, then rerun.",
    "rate_limited": "Wait for the provider limit to reset, then rerun.",
    "unexpected_provider_redirect": "Review provider connectivity before rerunning.",
    "unexpected_preflight_error": "Review the preflight implementation before rerunning.",
}


def main(
    argv: list[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    transport: Transport = _stdlib_transport,
) -> int:
    parser = argparse.ArgumentParser(description="Probe an evidence provider")
    parser.add_argument("--provider", required=True, choices=("openai", "anthropic"))
    parser.add_argument("--model", required=True)
    args = parser.parse_args(argv)
    environment = os.environ if environ is None else environ
    label = "OpenAI" if args.provider == "openai" else "Anthropic"
    category = ""

    try:
        if MODEL_RE.fullmatch(args.model) is None:
            raise PreflightFailure("invalid_model_identifier")
        variable = (
            "OPENAI_API_KEY"
            if args.provider == "openai"
            else "ANTHROPIC_API_KEY"
        )
        api_key = environment.get(variable, "").strip()
        if not api_key:
            raise PreflightFailure("missing_credential")
        probe(args.provider, args.model, api_key, transport=transport)
    except PreflightFailure as error:
        category = error.category
    except Exception:
        category = "unexpected_preflight_error"

    if category:
        remediation = REMEDIATION.get(category, REMEDIATION["provider_request_failed"])
        print(
            f"::error::{label} provider preflight failed ({category}). {remediation}",
            file=sys.stderr,
        )
        return 1
    print(f"{label} provider preflight succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
