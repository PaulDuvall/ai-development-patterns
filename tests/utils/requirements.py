"""Helpers for asserting on exactly pinned Python requirement specifications.

Tests assert *which distributions* a manifest declares and that each one is
pinned to a single exact version. They deliberately do not assert the version
numbers themselves, so routine Dependabot patch and minor bumps do not require
an accompanying edit to a protected trust-root test file.
"""

import re

EXACT_PIN = re.compile(r"(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)==(?P<version>[^\s;]+)")


def normalize_distribution(name):
    """Return the PEP 503 normalized form of a distribution name.

    Args:
        name: A distribution name as written in a manifest, e.g. ``"PyYAML"``.

    Returns:
        The lowercase, hyphen-separated name, e.g. ``"pyyaml"``.
    """
    return re.sub(r"[-_.]+", "-", name).lower()


def requirement_lines(text):
    """Return the significant requirement lines of a requirements file.

    Args:
        text: The full contents of a ``requirements.txt`` style file.

    Returns:
        Stripped lines with blanks and ``#`` comments removed.
    """
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def pinned_distributions(specs):
    """Return the normalized distribution names behind exactly pinned specs.

    Args:
        specs: Requirement strings such as ``"PyYAML==6.0.3"``.

    Returns:
        The set of PEP 503 normalized distribution names.

    Raises:
        AssertionError: If any spec is not pinned to one exact version, or if
            two specs name the same distribution.
    """
    names = set()
    for spec in specs:
        match = EXACT_PIN.fullmatch(spec.strip())
        assert match, f"expected an exact pin like name==1.2.3, got {spec!r}"
        name = normalize_distribution(match.group("name"))
        assert name not in names, f"{name} is pinned more than once"
        names.add(name)
    return names
