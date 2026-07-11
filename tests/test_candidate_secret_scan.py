"""Tests for the candidate artifact secret scanner."""

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parent.parent / "scripts" / "scan-candidate-secrets.py"
SPEC = importlib.util.spec_from_file_location("candidate_secret_scan", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_scanner_allows_evidence_hashes_and_secret_references(tmp_path):
    path = tmp_path / "candidate.yaml"
    path.write_text(
        "content_sha256: " + "a" * 64 + "\n"
        "anthropic: ${{ secrets.EVIDENCE_ANTHROPIC_API_KEY }}\n"
        "openai: ${{ secrets.EVIDENCE_OPENAI_API_KEY }}\n",
        encoding="utf-8",
    )
    assert MODULE.scan_file(path) == []


def test_scanner_redacts_detected_anthropic_key(tmp_path):
    path = tmp_path / "candidate.md"
    secret = "sk-ant-api03-" + "A" * 48
    path.write_text(f"accidental value: {secret}\n", encoding="utf-8")

    findings = MODULE.scan_file(path)

    assert findings == [f"{path}:1: possible Anthropic API key"]
    assert secret not in findings[0]


def test_scanner_redacts_detected_openai_project_key(tmp_path):
    path = tmp_path / "candidate.md"
    secret = "sk-proj-" + "B" * 48
    path.write_text(f"accidental value: {secret}\n", encoding="utf-8")

    findings = MODULE.scan_file(path)

    assert findings == [f"{path}:1: possible OpenAI API key"]
    assert secret not in findings[0]


def test_scanner_rejects_generic_credential_assignment(tmp_path):
    path = tmp_path / "candidate.md"
    path.write_text("access_token = abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")
    assert MODULE.scan_file(path) == [f"{path}:1: possible credential assignment"]
