"""Tests for the redacted one-request provider preflight."""

import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parent.parent / "scripts" / "check-provider-preflight.py"
SPEC = importlib.util.spec_from_file_location("check_provider_preflight", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeTransport:
    def __init__(self, *results):
        self.results = list(results)
        self.calls = []

    def __call__(self, method, url, headers, body, timeout):
        self.calls.append((method, url, headers, body, timeout))
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def response(status, body):
    if not isinstance(body, bytes):
        body = json.dumps(body).encode()
    return MODULE.Response(status, body)


def openai_success(status="completed"):
    return response(
        200,
        {"id": "resp_test", "object": "response", "status": status, "error": None},
    )


def anthropic_success():
    return response(
        200,
        {
            "id": "msg_test",
            "type": "message",
            "model": "claude-test",
            "content": [{"type": "text", "text": "O"}],
            "stop_reason": "max_tokens",
        },
    )


@pytest.mark.parametrize("provider_status", ["completed", "incomplete"])
def test_openai_exact_request_and_success(provider_status, capsys):
    secret = "sk-openai-SENTINEL"
    transport = FakeTransport(openai_success(provider_status))

    assert MODULE.main(
        ["--provider", "openai", "--model", "gpt-test"],
        environ={"OPENAI_API_KEY": secret},
        transport=transport,
    ) == 0

    assert len(transport.calls) == 1
    method, url, headers, body, timeout = transport.calls[0]
    assert (method, url, timeout) == (
        "POST",
        "https://api.openai.com/v1/responses",
        60,
    )
    assert headers == {
        "Authorization": f"Bearer {secret}",
        "Content-Type": "application/json",
    }
    assert json.loads(body) == {
        "model": "gpt-test",
        "input": "Reply with OK.",
        "max_output_tokens": 16,
        "store": False,
    }
    output = capsys.readouterr()
    assert "OpenAI provider preflight succeeded" in output.out
    assert secret not in output.out + output.err


def test_anthropic_exact_request_and_success(capsys):
    secret = "sk-ant-SENTINEL"
    transport = FakeTransport(anthropic_success())

    assert MODULE.main(
        ["--provider", "anthropic", "--model", "claude-test"],
        environ={"ANTHROPIC_API_KEY": secret},
        transport=transport,
    ) == 0

    assert len(transport.calls) == 1
    method, url, headers, body, timeout = transport.calls[0]
    assert (method, url, timeout) == (
        "POST",
        "https://api.anthropic.com/v1/messages",
        60,
    )
    assert headers == {
        "x-api-key": secret,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    assert json.loads(body) == {
        "model": "claude-test",
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "Reply with OK."}],
        "stream": False,
    }
    output = capsys.readouterr()
    assert "Anthropic provider preflight succeeded" in output.out
    assert secret not in output.out + output.err


@pytest.mark.parametrize(
    ("provider", "other_environment"),
    [
        ("openai", {"ANTHROPIC_API_KEY": "not-selected"}),
        (
            "anthropic",
            {
                "OPENAI_API_KEY": "not-selected",
                "ANTHROPIC_FEDERATION_RULE_ID": "fdrl_not_handled_here",
                "ANTHROPIC_ORGANIZATION_ID": "org-not-handled-here",
            },
        ),
    ],
)
def test_missing_selected_key_fails_without_network(
    provider, other_environment, capsys
):
    transport = FakeTransport()

    assert MODULE.main(
        ["--provider", provider, "--model", "model-test"],
        environ=other_environment,
        transport=transport,
    ) == 1

    assert transport.calls == []
    output = capsys.readouterr()
    assert "(missing_credential)" in output.err
    assert "not-selected" not in output.out + output.err


@pytest.mark.parametrize(
    ("provider", "status", "error", "category"),
    [
        ("openai", 400, {"code": "model_not_found"}, "model_unavailable"),
        ("openai", 401, {"message": "SENTINEL"}, "authentication_failed"),
        ("anthropic", 402, {"type": "billing_error"}, "billing_or_credit_error"),
        ("openai", 403, {}, "authorization_failed"),
        ("anthropic", 404, {"type": "not_found_error"}, "model_unavailable"),
        ("openai", 408, {}, "provider_timeout"),
        ("openai", 429, {"code": "insufficient_quota"}, "quota_exhausted"),
        ("openai", 429, {"code": "rate_limit_exceeded"}, "rate_limited"),
        ("anthropic", 429, {"type": "rate_limit_error"}, "rate_limited"),
        ("anthropic", 529, {"type": "overloaded_error"}, "provider_unavailable"),
        ("openai", 302, {}, "unexpected_provider_redirect"),
    ],
)
def test_provider_errors_are_classified_without_leaking_body(
    provider, status, error, category, capsys
):
    secret = "SENTINEL-secret-value"
    error = {**error, "message": secret}
    key_name = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
    transport = FakeTransport(response(status, {"error": error}))

    assert MODULE.main(
        ["--provider", provider, "--model", "model-test"],
        environ={key_name: secret},
        transport=transport,
    ) == 1

    assert len(transport.calls) == 1
    output = capsys.readouterr()
    assert f"({category})" in output.err
    assert secret not in output.out + output.err


@pytest.mark.parametrize(
    ("provider", "result"),
    [
        ("openai", response(200, b"not json")),
        ("openai", response(200, {"object": "response", "status": "failed"})),
        ("anthropic", response(200, {"type": "message", "id": "msg"})),
    ],
)
def test_invalid_success_response_fails_closed(provider, result, capsys):
    key_name = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
    transport = FakeTransport(result)

    assert MODULE.main(
        ["--provider", provider, "--model", "model-test"],
        environ={key_name: "secret"},
        transport=transport,
    ) == 1

    assert "(invalid_provider_response)" in capsys.readouterr().err


def test_generation_request_is_not_retried(capsys):
    transport = FakeTransport(
        response(503, {"error": {"message": "temporary"}}),
        openai_success(),
    )

    assert MODULE.main(
        ["--provider", "openai", "--model", "gpt-test"],
        environ={"OPENAI_API_KEY": "secret"},
        transport=transport,
    ) == 1

    assert len(transport.calls) == 1
    assert "(provider_unavailable)" in capsys.readouterr().err


def test_oversized_and_unexpected_errors_are_redacted(capsys):
    secret = "SENTINEL-exception-secret"
    oversized = FakeTransport(
        response(200, b"x" * (MODULE.MAX_RESPONSE_BYTES + 1))
    )
    assert MODULE.main(
        ["--provider", "openai", "--model", "gpt-test"],
        environ={"OPENAI_API_KEY": secret},
        transport=oversized,
    ) == 1
    first = capsys.readouterr()
    assert "(oversized_provider_response)" in first.err
    assert secret not in first.out + first.err

    unexpected = FakeTransport(RuntimeError(secret))
    assert MODULE.main(
        ["--provider", "openai", "--model", "gpt-test"],
        environ={"OPENAI_API_KEY": secret},
        transport=unexpected,
    ) == 1
    second = capsys.readouterr()
    assert "(unexpected_preflight_error)" in second.err
    assert secret not in second.out + second.err


def test_invalid_model_identifier_fails_before_network(capsys):
    transport = FakeTransport()

    assert MODULE.main(
        ["--provider", "openai", "--model", "bad model\nSENTINEL"],
        environ={"OPENAI_API_KEY": "secret"},
        transport=transport,
    ) == 1

    assert transport.calls == []
    output = capsys.readouterr()
    assert "(invalid_model_identifier)" in output.err
    assert "SENTINEL" not in output.out + output.err


def test_stdlib_transport_explicitly_disables_environment_proxies(monkeypatch):
    captured = {}

    class StubResponse:
        status = 200

        def read(self, _size):
            return b"{}"

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    class StubOpener:
        def open(self, _request, timeout):
            captured["timeout"] = timeout
            return StubResponse()

    def proxy_handler(proxies):
        captured["proxies"] = proxies
        return "proxy-handler"

    def build(handlers_proxy, handlers_redirect):
        captured["handlers"] = (handlers_proxy, handlers_redirect)
        return StubOpener()

    monkeypatch.setattr(MODULE, "ProxyHandler", proxy_handler)
    monkeypatch.setattr(MODULE, "build_opener", build)

    result = MODULE._stdlib_transport(
        "POST", MODULE.OPENAI_URL, {}, b"{}", MODULE.REQUEST_TIMEOUT_SECONDS
    )

    assert result == MODULE.Response(200, b"{}")
    assert captured["proxies"] == {}
    assert captured["handlers"][0] == "proxy-handler"
    assert isinstance(captured["handlers"][1], MODULE._NoRedirects)
    assert captured["timeout"] == MODULE.REQUEST_TIMEOUT_SECONDS
