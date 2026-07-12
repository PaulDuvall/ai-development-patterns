#!/usr/bin/env python3
"""Require feature commits to identify the specification anchor they implement."""

import argparse
from pathlib import Path
import re
import sys


FEATURE_COMMIT = re.compile(r"^feat(?:\([^)]+\))?!?:")
SPECIFICATION_REFERENCE = re.compile(r"\[spec:([A-Za-z0-9_-]+)\]")
SPECIFICATION_FILE = Path(__file__).with_name("iam_policy_spec.md")


def specification_anchors() -> set[str]:
    """Return the anchors declared by the executable specification."""
    content = SPECIFICATION_FILE.read_text(encoding="utf-8")
    return set(re.findall(
        r"\{#([A-Za-z0-9_-]+)(?:\s+[^}]*)?\}", content))


def validation_error(message: str) -> str | None:
    """Return a validation error for an untraceable feature commit."""
    subject = message.splitlines()[0] if message.splitlines() else ""
    if not FEATURE_COMMIT.match(subject):
        return None

    references = set(SPECIFICATION_REFERENCE.findall(message))
    if not references:
        return (
            "Feature commits must reference a specification anchor such as "
            "[spec:input_validation]."
        )

    unknown = references - specification_anchors()
    if unknown:
        return "Unknown specification anchors: " + ", ".join(sorted(unknown))
    return None


def main(argv: list[str] | None = None) -> int:
    """Validate the commit-message file supplied by pre-commit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message_file", type=Path)
    args = parser.parse_args(argv)

    error = validation_error(args.message_file.read_text(encoding="utf-8"))
    if error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
