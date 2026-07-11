#!/usr/bin/env python3
"""Create and approve a deterministic local Codex pattern-evaluation plan."""

import argparse
import datetime
import importlib.util
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

import yaml

from local_verification import (
    contract_digest,
    compute_plan_id,
    load_manifest,
    manifest_sha256,
    run_ref_for_id,
    write_manifest,
)


ROOT = Path(__file__).parent.parent.resolve()
REFUSED_API_ENV = {
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "EVIDENCE_OPENAI_API_KEY",
    "EVIDENCE_ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN",
}
EVIDENCE_PATH_RE = re.compile(
    r"^verification/evidence/([a-z0-9]+(?:-[a-z0-9]+)*)\.yaml$")


def inventory_module(root=ROOT):
    path = Path(root) / "scripts" / "build-verification-inventory.py"
    spec = importlib.util.spec_from_file_location("verification_inventory", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_base_sha(root=ROOT):
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True,
        capture_output=True, text=True)
    return result.stdout.strip()


def origin_main_sha(root=ROOT):
    result = subprocess.run(
        ["git", "rev-parse", "refs/remotes/origin/main"], cwd=root, check=True,
        capture_output=True, text=True)
    return result.stdout.strip()


def require_current_main_base(root=ROOT):
    """Fail unless the local run starts from the fetched default-branch tip."""
    head = git_base_sha(root)
    upstream = origin_main_sha(root)
    if head != upstream:
        raise ValueError(
            "local evaluation must start at the fetched origin/main tip; "
            f"HEAD={head}, origin/main={upstream}")
    return head


def worktree_status(root=ROOT):
    """Return non-ignored changes that could contaminate an evaluation run."""
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=root, check=True, capture_output=True, text=True)
    return [line for line in result.stdout.splitlines() if line]


def contract_paths(root):
    skill_root = Path(root) / ".agents" / "skills" / "evaluate-pattern-adoption"
    return [
        skill_root / "SKILL.md",
        skill_root / "references" / "evidence-methodology.md",
    ]


def prepare_new_manifest_path(root, run_ref):
    """Create only real parent directories and reject manifest collisions."""
    root = Path(root).resolve()
    relative = Path(run_ref)
    parent = root
    for part in relative.parts[:-1]:
        parent /= part
        parent.mkdir(exist_ok=True)
        if parent.is_symlink() or not parent.is_dir():
            raise ValueError("local run manifest parent must be a real directory")
    target = root / relative
    if target.exists() or target.is_symlink():
        raise ValueError("local run manifest path already exists")
    return target


def refuse_hosted_or_api_execution(environ=None):
    environ = environ if environ is not None else os.environ
    if environ.get("GITHUB_ACTIONS") == "true":
        raise ValueError("local pattern evaluation is forbidden in GitHub Actions")
    configured = sorted(name for name in REFUSED_API_ENV if environ.get(name))
    if configured:
        raise ValueError(
            "refusing API-key-backed evaluation; unset these variables and use a "
            f"signed-in Codex client: {', '.join(configured)}")


def inflight_slugs_from_prs(pull_requests):
    """Extract evidence slugs changed by open pull requests."""
    slugs = set()
    if not isinstance(pull_requests, list):
        raise ValueError("GitHub open-PR response must be a list")
    for pull_request in pull_requests:
        if not isinstance(pull_request, dict) \
                or not isinstance(pull_request.get("files"), list):
            raise ValueError("GitHub open-PR response has invalid file metadata")
        for item in pull_request["files"]:
            path = item.get("path") if isinstance(item, dict) else None
            match = EVIDENCE_PATH_RE.fullmatch(path or "")
            if match:
                slugs.add(match.group(1))
    return slugs


def discover_inflight_slugs(root=ROOT):
    """Read open main-targeting PR file lists so paid work is not duplicated."""
    result = subprocess.run(
        [
            "gh", "pr", "list", "--state", "open", "--base", "main",
            "--limit", "200", "--json", "number,files",
        ],
        cwd=root, check=True, capture_output=True, text=True)
    try:
        pull_requests = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("could not parse GitHub open-PR file metadata") from exc
    return inflight_slugs_from_prs(pull_requests)


def selected_for_scope(inventory, scope, pattern, limit, module):
    def exact(items):
        blocked = sorted(item["slug"] for item in items if item["in_flight"])
        if blocked:
            raise ValueError(
                f"{scope} scope is blocked by in-flight evidence: "
                f"{', '.join(blocked)}")
        return items

    if scope == "stable":
        return exact([item for item in inventory if item["location"] == "main"])
    if scope == "exploratory":
        return exact([
            item for item in inventory if item["location"] == "experimental"])
    if scope == "all":
        return exact(inventory)
    if scope == "single":
        matches = [item for item in inventory if item["name"] == pattern]
        if not matches:
            raise ValueError(f"pattern is unknown: {pattern!r}")
        return exact(matches)
    if scope == "discovery":
        return []
    return module.select_work(inventory, "stale-default", limit=limit)


def create_plan(args, root=ROOT):
    refuse_hosted_or_api_execution()
    root = Path(root).resolve()
    require_current_main_base(root)
    dirty = worktree_status(root)
    if dirty:
        raise ValueError(
            "local evaluation requires a dedicated clean worktree; preserve these "
            f"existing changes elsewhere before planning: {', '.join(dirty)}")
    if args.scope == "single" and not args.pattern:
        raise ValueError("single scope requires --pattern with an exact catalog name")
    if args.scope != "single" and args.pattern:
        raise ValueError("--pattern is valid only with --scope single")
    if args.limit < 1 or args.stale_days < 1:
        raise ValueError("--limit and --stale-days must be positive")
    if not isinstance(args.model, str) or not args.model.strip():
        raise ValueError("--model must be a non-empty local Codex model label")
    if not args.attest_chatgpt:
        raise ValueError(
            "--attest-chatgpt is required; local execution alone does not prove billing mode")

    module = inventory_module(root)
    today = (datetime.date.fromisoformat(args.today)
             if args.today else datetime.date.today())
    catalog = module.load_catalog(
        root / "patterns.yaml", root / "experiments" / "README.md")
    inflight = (module.load_inflight(args.inflight_slugs)
                if args.inflight_slugs else discover_inflight_slugs(root))
    inventory = module.build_inventory(
        catalog, root / "verification" / "evidence",
        inflight, today, args.stale_days)
    selected = selected_for_scope(
        inventory, args.scope, args.pattern, args.limit, module)
    if args.scope == "stale" and not selected:
        raise ValueError(
            "no eligible stale evidence work remains after freshness and "
            "open-PR de-duplication")
    include_discovery = bool(
        args.include_discovery or args.scope in {"all", "discovery"})
    matrix_mode = "full" if include_discovery else "stale-default"
    matrix, units = module.build_execution_matrix(
        selected, matrix_mode, root / "verification" / "run-plan" / "units")

    inventory_path = root / "verification" / "pattern-inventory.yaml"
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(
        yaml.safe_dump(
            {"generated": today.isoformat(), "patterns": inventory},
            sort_keys=False, allow_unicode=True),
        encoding="utf-8")
    (root / ".verify-worklist").write_text(
        "".join(f"{item['slug']}\n" for item in selected), encoding="utf-8")
    module.write_execution_plan(
        matrix, units, root / "verification" / "run-plan" / "units",
        root / "verification" / "run-plan" / "execution-matrix.json")

    run_id = f"codex-local:{uuid.uuid4()}"
    prompt_version = (
        "evidence-v2-codex-local-v1+sha256."
        + contract_digest(contract_paths(root))
    )
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "plan_id": "0" * 64,
        "base_sha": git_base_sha(root),
        "checked_date": today.isoformat(),
        "scope": args.scope,
        "selected_slugs": [item["slug"] for item in selected],
        "include_discovery": include_discovery,
        "execution": {
            "provider": "openai",
            "surface": args.surface,
            "auth_mode": "chatgpt-operator-attested",
            "model": args.model,
            "prompt_version": prompt_version,
        },
        "approval": {
            "status": "pending",
            "approved_at": None,
            "plan_id": "0" * 64,
        },
    }
    manifest["plan_id"] = compute_plan_id(manifest)
    manifest["approval"]["plan_id"] = manifest["plan_id"]
    run_ref = run_ref_for_id(run_id)
    write_manifest(prepare_new_manifest_path(root, run_ref), manifest)
    return manifest, run_ref, inventory


def approve_plan(manifest_path, confirmation, root=ROOT):
    refuse_hosted_or_api_execution()
    root = Path(root).resolve()
    relative = Path(manifest_path).as_posix()
    if Path(manifest_path).is_absolute():
        relative = Path(manifest_path).resolve().relative_to(root).as_posix()
    manifest, path, _ = load_manifest(
        root, relative, require_approved=False)
    if require_current_main_base(root) != manifest["base_sha"]:
        raise ValueError("repository HEAD changed after this plan was created")
    expected_prompt = (
        "evidence-v2-codex-local-v1+sha256."
        + contract_digest(contract_paths(root)))
    if manifest["execution"]["prompt_version"] != expected_prompt:
        raise ValueError("local evaluation contract changed after planning")
    changes = worktree_status(root)
    if changes != [f"?? {relative}"]:
        raise ValueError(
            "worktree changed after planning; only the pending run manifest may "
            f"be untracked, found: {', '.join(changes) or 'none'}")
    if manifest["approval"]["status"] != "pending":
        raise ValueError("local evaluation plan is already approved")
    expected = f"APPROVE LOCAL EVALUATION {manifest['plan_id']}"
    if confirmation != expected:
        raise ValueError(f"approval must exactly equal: {expected}")
    manifest["approval"] = {
        "status": "approved",
        "approved_at": (
            datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0).isoformat().replace("+00:00", "Z")),
        "plan_id": manifest["plan_id"],
    }
    write_manifest(path, manifest)
    path.chmod(0o444)
    return manifest, relative, manifest_sha256(path)


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="build a free deterministic plan")
    plan.add_argument(
        "--scope", required=True,
        choices=("stale", "stable", "exploratory", "all", "single", "discovery"))
    plan.add_argument("--pattern")
    plan.add_argument("--limit", type=int, default=10)
    plan.add_argument("--stale-days", type=int, default=90)
    plan.add_argument("--include-discovery", action="store_true")
    plan.add_argument("--surface", choices=("codex-app", "codex-cli", "codex-ide"),
                      default="codex-app")
    plan.add_argument("--model", default="codex-managed")
    plan.add_argument("--inflight-slugs")
    plan.add_argument("--today")
    plan.add_argument("--attest-chatgpt", action="store_true")
    approve = commands.add_parser("approve", help="bind explicit human approval")
    approve.add_argument("--manifest", required=True)
    approve.add_argument("--confirmation", required=True)
    return result


def main():
    args = parser().parse_args()
    try:
        if args.command == "plan":
            manifest, run_ref, inventory = create_plan(args)
            locations = {"main": 0, "experimental": 0}
            selected = set(manifest["selected_slugs"])
            for item in inventory:
                if item["slug"] in selected:
                    locations[item["location"]] += 1
            research_units = len(selected) + int(manifest["include_discovery"])
            inflight_count = sum(item["in_flight"] for item in inventory)
            print(f"Plan ID: {manifest['plan_id']}")
            print(f"Run manifest: {run_ref}")
            print(
                f"Pattern units: {len(selected)} "
                f"({locations['main']} stable, {locations['experimental']} exploratory)")
            print(f"Discovery unit: {'yes' if manifest['include_discovery'] else 'no'}")
            print(f"Total research-agent units: {research_units}")
            print(f"Maximum live searches: {research_units * 12}")
            print(f"Open-PR evidence exclusions checked: {inflight_count}")
            print("No model, subagent, or provider API call has run.")
            print(
                "WARNING: approval may consume substantial Codex/ChatGPT plan credits; "
                "subagents increase token use.")
            print("To authorize agent-credit use, respond exactly:")
            print(f"APPROVE LOCAL EVALUATION {manifest['plan_id']}")
        else:
            manifest, run_ref, digest = approve_plan(
                args.manifest, args.confirmation)
            print(f"Approved plan: {manifest['plan_id']}")
            print(f"RUN_ID={manifest['run_id']}")
            print(f"RUN_REF={run_ref}")
            print(f"RUN_MANIFEST_SHA256={digest}")
            print(f"CHECKED_DATE={manifest['checked_date']}")
            print(f"MODEL={manifest['execution']['model']}")
            print(f"PROMPT_VERSION={manifest['execution']['prompt_version']}")
    except (OSError, ValueError, yaml.YAMLError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
