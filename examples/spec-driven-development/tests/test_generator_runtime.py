"""Direct runtime tests for policy generation and CLI error paths."""

import json
from pathlib import Path
import sys

import pytest


EXAMPLE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXAMPLE_ROOT))

import iam_policy_generator as generator_module  # noqa: E402
from iam_policy_generator import IAMPolicyGenerator  # noqa: E402


def test_input_safety_rejects_none_and_unsafe_policy_type():
    """REQ-005: Reject null and unsafe values without normalization."""
    generator = IAMPolicyGenerator()

    assert generator.validate_input_safety(None, "Value") == (
        False,
        "Value cannot be empty",
    )
    with pytest.raises(ValueError, match="contains unsafe characters"):
        generator.generate_policy(
            "s3-read;admin", "arn:aws:s3:::example-bucket/*")


@pytest.mark.parametrize(
    ("policy_type", "resource", "message"),
    [
        (
            "unknown",
            "arn:aws:s3:::example-bucket/*",
            "Policy type validation failed",
        ),
        ("s3-read", "not-an-arn", "ARN validation failed"),
        (
            "ec2-admin",
            "arn:aws:s3:::example-bucket/*",
            "Compatibility check failed",
        ),
    ],
)
def test_generation_rejects_each_validation_boundary(
    policy_type, resource, message
):
    """REQ-002 REQ-003 REQ-004: Reject invalid generation boundaries."""
    with pytest.raises(ValueError, match=message):
        IAMPolicyGenerator().generate_policy(policy_type, resource)


@pytest.mark.parametrize(
    ("resource", "message"),
    [
        (
            "arn:aws:s3:us-east-1:123456789012:example-bucket/*",
            "must use arn:aws:s3:::bucket",
        ),
        ("arn:aws:s3:::ab/*", "valid general-purpose bucket"),
        (
            "arn:aws:s3:::example-bucket/",
            "must name an object or prefix",
        ),
    ],
)
def test_s3_generation_rejects_non_bucket_resource_shapes(resource, message):
    """REQ-003 REQ-006: Require S3 bucket-compatible ARN shapes."""
    with pytest.raises(ValueError, match=message):
        IAMPolicyGenerator().generate_policy("s3-read", resource)


@pytest.mark.parametrize(
    "bucket_name",
    [
        "-leading-hyphen",
        "trailing-hyphen-",
        ".leading-period",
        "trailing-period.",
        "UPPERCASE",
        "invalid_bucket",
        "a" * 64,
        "adjacent..periods",
        "dot.-hyphen",
        "hyphen-.dot",
        "192.168.5.4",
        "xn--reserved",
        "sthree-reserved",
        "amzn-s3-demo-reserved",
        "reserved-s3alias",
        "reserved--ol-s3",
        "reserved.mrap",
        "reserved--x-s3",
        "reserved--table-s3",
    ],
)
def test_s3_generation_rejects_invalid_or_reserved_bucket_names(bucket_name):
    """REQ-003: Enforce general-purpose S3 bucket naming rules."""
    resource = f"arn:aws:s3:::{bucket_name}/*"

    with pytest.raises(ValueError, match="valid general-purpose bucket"):
        IAMPolicyGenerator().generate_policy("s3-read", resource)


@pytest.mark.parametrize(
    "bucket_name",
    ["abc", "valid-bucket", "valid.bucket", "bucket-123", "a" * 63],
)
def test_s3_generation_accepts_valid_general_purpose_bucket_names(bucket_name):
    """REQ-003: Accept valid general-purpose S3 bucket names."""
    policy = IAMPolicyGenerator().generate_policy(
        "s3-read", f"arn:aws:s3:::{bucket_name}/*")

    assert policy["Statement"][0]["Resource"] == f"arn:aws:s3:::{bucket_name}"


def test_bare_s3_bucket_expands_only_the_object_statement():
    """REQ-006: Derive the object wildcard while preserving the bucket ARN."""
    policy = IAMPolicyGenerator().generate_policy(
        "s3-write", "arn:aws:s3:::example-bucket")

    assert policy["Statement"][0] == {
        "Effect": "Allow",
        "Action": ["s3:ListBucket"],
        "Resource": "arn:aws:s3:::example-bucket",
    }
    assert policy["Statement"][1] == {
        "Effect": "Allow",
        "Action": ["s3:PutObject", "s3:DeleteObject", "s3:GetObject"],
        "Resource": "arn:aws:s3:::example-bucket/*",
    }


def test_output_format_covers_compact_and_metadata_modes(monkeypatch):
    """REQ-007: Format compact metadata and plain policy output."""
    generator = IAMPolicyGenerator()
    policy = generator.generate_policy(
        "iam-read", "arn:aws:iam::123456789012:role/example-role")
    monkeypatch.setattr(generator_module.time, "time", lambda: 0.0)
    monkeypatch.setattr(
        generator_module.time, "gmtime", lambda: generator_module.time.struct_time(
            (2026, 1, 2, 3, 4, 5, 4, 2, 0)
        ))

    compact = generator.format_output(policy, compact=True)
    plain = generator.format_output(
        policy, compact=True, include_validation=False)

    assert "\n" not in compact
    assert json.loads(compact)["metadata"] == {
        "validation_status": "passed",
        "generator_version": "1.0.0",
        "generated_at": "2026-01-02 03:04:05 UTC",
    }
    assert json.loads(plain) == policy


@pytest.mark.parametrize(
    ("error", "expected_suggestion"),
    [
        (ValueError("invalid ARN"), "Check ARN format"),
        (ValueError("unsupported policy type"), "Valid policy types"),
        (ValueError("compatibility mismatch"), "Ensure policy type matches"),
    ],
)
def test_structured_errors_include_actionable_suggestions(
    error, expected_suggestion
):
    """REQ-003 REQ-004: Return actionable structured errors."""
    response = IAMPolicyGenerator().handle_error(error, error_code=7)

    assert response["error"]["code"] == 7
    assert any(
        expected_suggestion in suggestion
        for suggestion in response["error"]["suggestions"]
    )


def test_structured_error_omits_irrelevant_suggestions():
    """REQ-003: Avoid unrelated guidance for unexpected errors."""
    response = IAMPolicyGenerator().handle_error(RuntimeError("boom"))

    assert "suggestions" not in response["error"]


def test_main_returns_success_and_serializes_policy(monkeypatch, capsys):
    """REQ-001 REQ-007: Return zero and JSON for a valid CLI request."""
    monkeypatch.setattr(sys, "argv", [
        "iam_policy_generator.py",
        "--policy-type",
        "s3-read",
        "--resource",
        "arn:aws:s3:::example-bucket/*",
        "--compact",
        "--no-validation-info",
    ])

    assert generator_module.main() == 0
    assert json.loads(capsys.readouterr().out)["Version"] == "2012-10-17"


def test_main_returns_validation_error(monkeypatch, capsys):
    """REQ-001: Return one and a structured validation error."""
    monkeypatch.setattr(sys, "argv", [
        "iam_policy_generator.py",
        "--policy-type",
        "unknown",
        "--resource",
        "arn:aws:s3:::example-bucket/*",
    ])

    assert generator_module.main() == 1
    assert json.loads(capsys.readouterr().out)["error"]["code"] == 1


def test_main_returns_unexpected_error(monkeypatch, capsys):
    """REQ-001: Distinguish an unexpected runtime failure."""
    monkeypatch.setattr(sys, "argv", [
        "iam_policy_generator.py",
        "--policy-type",
        "s3-read",
        "--resource",
        "arn:aws:s3:::example-bucket/*",
    ])
    monkeypatch.setattr(
        IAMPolicyGenerator,
        "generate_policy",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    assert generator_module.main() == 2
    assert json.loads(capsys.readouterr().out)["error"]["code"] == 2
