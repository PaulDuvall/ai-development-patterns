#!/usr/bin/env python3
"""Export one fixed-path research result with a trusted sidecar manifest."""

import argparse
import hashlib
import json
import re
import shutil
import stat
import sys
from pathlib import Path


UNIT_RE = re.compile(r"(?:evidence-[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*|discovery)")
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MAX_FILE_SIZE = 5 * 1024 * 1024


def source_path(root, kind, slug):
    if kind == "evidence" and SLUG_RE.fullmatch(slug or ""):
        return Path(root) / "verification" / "evidence" / f"{slug}.yaml"
    if kind == "discovery" and slug == "":
        return Path(root) / "experiments" / "NOTES.md"
    raise ValueError("unit kind and slug do not identify a fixed candidate path")


def export_unit(source_root, destination, metadata):
    unit_id = metadata.get("unit_id", "")
    if UNIT_RE.fullmatch(unit_id) is None:
        raise ValueError("unit_id is unsafe")
    source = source_path(source_root, metadata.get("kind"), metadata.get("slug"))
    info = source.lstat()
    if not stat.S_ISREG(info.st_mode) or source.is_symlink():
        raise ValueError("research output must be a regular non-symlink file")
    if info.st_size > MAX_FILE_SIZE:
        raise ValueError("research output exceeds 5 MiB")
    destination = Path(destination)
    if destination.exists():
        raise ValueError("unit export destination already exists")
    relative = source.relative_to(Path(source_root))
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest = dict(metadata)
    manifest.update({"path": relative.as_posix(), "sha256": digest})
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root")
    parser.add_argument("destination")
    parser.add_argument("--unit-id", required=True)
    parser.add_argument("--kind", choices=("evidence", "discovery"), required=True)
    parser.add_argument("--slug", default="")
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt-version", required=True)
    parser.add_argument("--run-id", required=True)
    provenance = parser.add_mutually_exclusive_group(required=True)
    provenance.add_argument("--run-url")
    provenance.add_argument("--run-ref")
    parser.add_argument("--run-manifest-sha256")
    args = parser.parse_args()
    metadata = {
        "unit_id": args.unit_id,
        "kind": args.kind,
        "slug": args.slug,
        "selected_slugs": [args.slug] if args.kind == "evidence" else [],
        "base_sha": args.base_sha,
        "provider": args.provider,
        "model": args.model,
        "prompt_version": args.prompt_version,
        "run_id": args.run_id,
    }
    if args.run_ref:
        if not args.run_manifest_sha256:
            parser.error("--run-manifest-sha256 is required with --run-ref")
        metadata.update({
            "run_ref": args.run_ref,
            "run_manifest_sha256": args.run_manifest_sha256,
        })
    else:
        if args.run_manifest_sha256:
            parser.error("--run-manifest-sha256 requires --run-ref")
        metadata["run_url"] = args.run_url
    try:
        manifest = export_unit(args.source_root, args.destination, metadata)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
