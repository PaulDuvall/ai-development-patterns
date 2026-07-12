"""Tests for the specification-aware commit-message hook."""

from pathlib import Path
import sys


EXAMPLE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXAMPLE_ROOT))

import validate_commit_message as commit_message  # noqa: E402


def test_feature_commit_requires_specification_anchor():
    assert commit_message.validation_error("feat: add policy generation") == (
        "Feature commits must reference a specification anchor such as "
        "[spec:input_validation]."
    )


def test_feature_commit_accepts_anchor_in_body():
    message = "feat(generator): add policy\n\n[spec:policy_generation]\n"

    assert commit_message.validation_error(message) is None


def test_non_feature_commit_does_not_require_anchor():
    assert commit_message.validation_error("fix: reject malformed input") is None


def test_feature_commit_rejects_unknown_anchor():
    assert commit_message.validation_error(
        "feat: add policy [spec:not_a_real_anchor]"
    ) == "Unknown specification anchors: not_a_real_anchor"


def test_hook_main_returns_failure_and_success(tmp_path, capsys):
    message_file = tmp_path / "COMMIT_EDITMSG"
    message_file.write_text("feat!: replace contract\n", encoding="utf-8")

    assert commit_message.main([str(message_file)]) == 1
    assert "Feature commits must reference" in capsys.readouterr().err

    message_file.write_text(
        "feat!: replace contract [spec:cli_contract]\n", encoding="utf-8")
    assert commit_message.main([str(message_file)]) == 0
