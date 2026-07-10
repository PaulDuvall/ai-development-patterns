#!/usr/bin/env python3
"""Fail when an untrusted verification artifact resembles a credential."""

import argparse
import re
import sys
from pathlib import Path


PATTERNS = {
    "Anthropic API key": re.compile(r"\bsk-ant-(?:api\d+-)?[A-Za-z0-9_-]{20,}"),
    "OpenAI API key": re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{32,}"),
    "GitHub token": re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "Google API key": re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential assignment": re.compile(
        r"(?i)\b(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret|password)"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9+/=_-]{20,}"
    ),
}


def iter_files(paths):
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_symlink():
            raise ValueError(f"symbolic link is not allowed: {path}")
        if path.is_file():
            yield path
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_symlink():
                    raise ValueError(f"symbolic link is not allowed: {child}")
                if child.is_file():
                    yield child
        else:
            raise ValueError(f"path does not exist: {path}")


def scan_file(path):
    """Return redacted finding descriptions for one UTF-8 candidate file."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"candidate file is not UTF-8 text: {path}") from exc
    findings = []
    for line_number, line in enumerate(text.splitlines(), 1):
        for label, pattern in PATTERNS.items():
            if pattern.search(line):
                findings.append(f"{path}:{line_number}: possible {label}")
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Candidate files or directories to scan")
    args = parser.parse_args()
    try:
        findings = [
            finding
            for path in iter_files(args.paths)
            for finding in scan_file(path)
        ]
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if findings:
        print("Candidate secret scan failed:", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1
    print("Candidate secret scan passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
