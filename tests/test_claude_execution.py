"""Tests for the fail-closed Claude execution-result checker."""

import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).parent.parent / "scripts" / "check-claude-execution.py"
SPEC = importlib.util.spec_from_file_location("check_claude_execution", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_events(tmp_path, events):
    path = tmp_path / "claude-execution-output.json"
    path.write_text(json.dumps(events), encoding="utf-8")
    return path


def test_accepts_only_explicit_non_error_success(tmp_path):
    path = write_events(
        tmp_path,
        [{"type": "system", "subtype": "init"},
         {"type": "result", "subtype": "success", "is_error": False}],
    )
    assert MODULE.validate_execution_file(path) is None


def test_rejects_success_subtype_when_is_error_is_true(tmp_path):
    path = write_events(
        tmp_path,
        [{"type": "result", "subtype": "success", "is_error": True,
          "result": "API Error: invalid x-api-key"}],
    )
    assert MODULE.validate_execution_file(path) == "authentication_failed"


def test_reports_only_safe_category_for_sensitive_error(
    tmp_path, capsys, monkeypatch
):
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    secret = "sk-ant-api03-" + "A" * 48
    path = write_events(
        tmp_path,
        [{"type": "result", "subtype": "success", "is_error": True,
          "result": f"API Error: invalid API key {secret}"}],
    )

    assert MODULE.main([str(path)]) == 1

    output = capsys.readouterr().err
    assert "authentication_failed" in output
    assert secret not in output


def test_rejects_missing_or_nonfinal_result(tmp_path):
    missing = tmp_path / "missing.json"
    assert MODULE.validate_execution_file(missing) == "missing_execution_file"
    assert MODULE.validate_execution_file(None) == "missing_execution_file"

    path = write_events(tmp_path, [{"type": "assistant", "message": {}}])
    assert MODULE.validate_execution_file(path) == "missing_final_result"

    path = write_events(
        tmp_path,
        [{"type": "result", "subtype": "success", "is_error": False},
         {"type": "result", "subtype": "success", "is_error": False}],
    )
    assert MODULE.validate_execution_file(path) == "missing_final_result"


def test_rejects_malformed_and_symlinked_files(tmp_path):
    malformed = tmp_path / "malformed.json"
    malformed.write_text("not json", encoding="utf-8")
    assert MODULE.validate_execution_file(malformed) == "invalid_execution_file"

    target = write_events(
        tmp_path,
        [{"type": "result", "subtype": "success", "is_error": False}],
    )
    link = tmp_path / "linked.json"
    link.symlink_to(target)
    assert MODULE.validate_execution_file(link) == "invalid_execution_file"


def test_requires_the_fixed_runner_temp_path_when_configured(tmp_path):
    path = write_events(
        tmp_path,
        [{"type": "result", "subtype": "success", "is_error": False}],
    )
    assert MODULE.validate_execution_file(path, runner_temp=tmp_path) is None

    other = tmp_path / "other"
    other.mkdir()
    assert MODULE.validate_execution_file(path, runner_temp=other) == (
        "unexpected_execution_file_path")
