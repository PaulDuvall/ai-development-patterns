"""Regex scanner for common secret patterns."""
from __future__ import annotations

import re

PATTERNS = {
    "aws_access_key":  re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_token":    re.compile(r"gh[pousr]_[A-Za-z0-9]{36}"),
    "private_key":     re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----"),
    "generic_secret":  re.compile(r"(?i)(api[_-]?key|secret|password)\s*=\s*['\"][^'\"]{8,}['\"]"),
}


def detect(file_path: str) -> list[dict]:
    try:
        text = open(file_path, encoding="utf-8", errors="replace").read()
    except OSError as exc:
        print(f"secrets: could not read {file_path} ({exc})", flush=True)
        return []

    findings: list[dict] = []
    for rule_id, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            findings.append({
                "rule_id": "secret_leak", "file": file_path, "line": line,
                "severity": "error",
                "message": f"possible {rule_id} found",
            })
    return findings
