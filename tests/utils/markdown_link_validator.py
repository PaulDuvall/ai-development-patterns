from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable
from urllib.parse import unquote, urlsplit

from utils.git_utils import git_ls_files


@dataclass(frozen=True)
class MarkdownLinkError:
    source_file: str
    source_line: int
    link: str
    message: str


class MarkdownLinkValidator:
    """
    Validate internal anchors and relative file links across git-tracked markdown files.

    Focus: deterministic checks with low flakiness (no network calls).
    """

    _LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.tracked_files = set(git_ls_files(self.repo_root))
        self.tracked_dirs = self._build_tracked_dirs(self.tracked_files)
        self._anchors_cache: dict[str, set[str]] = {}

    def validate_files(self, markdown_files: Iterable[Path]) -> list[MarkdownLinkError]:
        errors: list[MarkdownLinkError] = []
        for path in markdown_files:
            errors.extend(self.validate_file(path))
        return errors

    def validate_file(self, markdown_file: Path) -> list[MarkdownLinkError]:
        rel_source = self._rel_path(markdown_file)
        if rel_source is None:
            return []

        try:
            content = markdown_file.read_text(encoding="utf-8")
        except OSError as e:
            return [
                MarkdownLinkError(
                    source_file=rel_source,
                    source_line=1,
                    link="",
                    message=f"Unable to read file: {e}",
                )
            ]

        errors: list[MarkdownLinkError] = []
        for url, line_num in self._extract_markdown_links(content):
            url = self._normalize_link_destination(url)
            if not url or self._should_ignore_link(url):
                continue

            errors.extend(self._validate_link(rel_source, markdown_file, url, line_num))

        return errors

    def markdown_files_in_scope(self) -> list[Path]:
        """
        Return git-tracked markdown files in scope:
        - docs/
        - examples/
        - experiments/
        - selected top-level docs (excluding README.md)
        """
        top_level = {
            "pattern-spec.md",
            "PATTERN_MIGRATION_GUIDE.md",
            "CLAUDE.md",
            "AGENTS.md",
        }
        in_scope_prefixes = ("docs/", "examples/", "experiments/")

        paths: list[Path] = []
        for rel in sorted(self.tracked_files):
            if not rel.endswith(".md"):
                continue
            if rel == "README.md":
                continue
            if rel in top_level or rel.startswith(in_scope_prefixes):
                paths.append(self.repo_root / rel)
        return paths

    def _validate_link(
        self, rel_source: str, source_file: Path, url: str, line_num: int
    ) -> list[MarkdownLinkError]:
        parsed = urlsplit(url)

        # External or unsupported schemes are intentionally ignored here.
        if parsed.scheme or parsed.netloc:
            return []

        fragment = unquote(parsed.fragment or "").strip()
        raw_path = unquote(parsed.path or "").strip()

        # Internal anchor within the same file
        if not raw_path and fragment:
            return self._validate_anchor(
                rel_source=rel_source,
                source_line=line_num,
                link=url,
                target_file=source_file,
                fragment=fragment,
            )

        # Ignore empty or placeholder-only links (e.g., "(#)")
        if not raw_path:
            return []

        resolved_target = self._resolve_link_path(source_file, raw_path)
        if resolved_target is None:
            return [
                MarkdownLinkError(
                    source_file=rel_source,
                    source_line=line_num,
                    link=url,
                    message=f"Link resolves outside repository: {raw_path}",
                )
            ]

        rel_target = self._rel_path(resolved_target)
        if rel_target is None or not self._tracked_path_exists(rel_target):
            return [
                MarkdownLinkError(
                    source_file=rel_source,
                    source_line=line_num,
                    link=url,
                    message=f"Target not found in git-tracked paths: {raw_path}",
                )
            ]

        # Directory links: map anchors to README.md when present.
        target_for_anchor = resolved_target
        if self._is_tracked_dir(rel_target) and rel_target not in self.tracked_files:
            readme_rel = f"{rel_target.rstrip('/')}/README.md"
            if readme_rel in self.tracked_files:
                target_for_anchor = self.repo_root / readme_rel

        if fragment and target_for_anchor.suffix.lower() == ".md":
            return self._validate_anchor(
                rel_source=rel_source,
                source_line=line_num,
                link=url,
                target_file=target_for_anchor,
                fragment=fragment,
            )

        return []

    def _validate_anchor(
        self,
        rel_source: str,
        source_line: int,
        link: str,
        target_file: Path,
        fragment: str,
    ) -> list[MarkdownLinkError]:
        anchors = self._anchors_for_file(target_file)
        anchor = f"#{fragment}"
        if anchor not in anchors:
            target_rel = self._rel_path(target_file) or str(target_file)
            return [
                MarkdownLinkError(
                    source_file=rel_source,
                    source_line=source_line,
                    link=link,
                    message=f'Anchor "{anchor}" not found in {target_rel}',
                )
            ]
        return []

    def _anchors_for_file(self, markdown_file: Path) -> set[str]:
        rel = self._rel_path(markdown_file)
        if rel is None:
            return set()
        cached = self._anchors_cache.get(rel)
        if cached is not None:
            return cached

        try:
            content = markdown_file.read_text(encoding="utf-8")
        except OSError:
            anchors: set[str] = set()
            self._anchors_cache[rel] = anchors
            return anchors

        anchors = self._extract_anchors(content)
        self._anchors_cache[rel] = anchors
        return anchors

    def _extract_markdown_links(self, markdown_text: str) -> list[tuple[str, int]]:
        links: list[tuple[str, int]] = []
        in_fence = False

        for line_num, line in enumerate(markdown_text.splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue

            scan_line = self._strip_inline_code(line)
            for match in self._LINK_PATTERN.finditer(scan_line):
                dest = match.group(1).strip()
                # Markdown allows optional titles: (url "title")
                if dest.startswith("<") and ">" in dest:
                    dest = dest[1 : dest.find(">")].strip()
                else:
                    dest = dest.split()[0]

                links.append((dest, line_num))

        return links

    def _extract_anchors(self, markdown_text: str) -> set[str]:
        anchors: set[str] = set()
        in_fence = False
        slug_counts: dict[str, int] = {}
        lines = markdown_text.splitlines()

        def add_heading_anchor(heading_text: str) -> None:
            base = self._github_heading_slug(heading_text)
            if not base:
                return
            count = slug_counts.get(base, 0)
            slug_counts[base] = count + 1
            slug = base if count == 0 else f"{base}-{count}"
            anchors.add(f"#{slug}")

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                i += 1
                continue
            if in_fence:
                i += 1
                continue

            normalized = self._strip_blockquote_prefix(line).strip()

            atx = re.match(r"^(#{1,6})\s+(.+?)\s*$", normalized)
            if atx:
                heading = atx.group(2)
                heading = re.sub(r"\s+#+\s*$", "", heading).strip()
                add_heading_anchor(heading)
                i += 1
                continue

            # Setext-style headers
            if i + 1 < len(lines):
                underline = self._strip_blockquote_prefix(lines[i + 1]).strip()
                if underline and re.fullmatch(r"=+", underline):
                    add_heading_anchor(normalized)
                    i += 2
                    continue
                if underline and re.fullmatch(r"-+", underline):
                    add_heading_anchor(normalized)
                    i += 2
                    continue

            i += 1

        return anchors

    def _github_heading_slug(self, heading_text: str) -> str:
        text = heading_text.strip()
        text = self._strip_markdown_formatting(text)
        text = html.unescape(text)
        text = text.strip().lower()
        text = re.sub(r"\s+", "-", text)
        text = re.sub(r"[^\w-]", "", text)
        return text.strip("-")

    def _strip_markdown_formatting(self, text: str) -> str:
        # Replace markdown links with their text: [text](url) -> text
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        # Remove inline code ticks but keep content
        text = re.sub(r"`([^`]*)`", r"\1", text)
        # Remove emphasis markers
        text = text.replace("**", "").replace("__", "")
        text = text.replace("*", "").replace("_", "")
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        return text

    def _strip_inline_code(self, line: str) -> str:
        return re.sub(r"`[^`]*`", "", line)

    def _strip_blockquote_prefix(self, line: str) -> str:
        out = line.lstrip()
        while out.startswith(">"):
            out = out[1:].lstrip()
        return out

    def _normalize_link_destination(self, dest: str) -> str:
        dest = dest.strip()
        if dest.startswith("<") and dest.endswith(">"):
            dest = dest[1:-1].strip()
        return dest

    def _should_ignore_link(self, url: str) -> bool:
        lowered = url.lower()
        if url == "#":
            return True
        if lowered.startswith(("mailto:", "tel:", "javascript:")):
            return True
        if "{{" in url or "}}" in url:
            return True
        if "<" in url or ">" in url:
            return True
        if "example.com" in lowered:
            return True
        if "/path/to/" in lowered or lowered.startswith("path/to/"):
            return True
        return False

    def _resolve_link_path(self, source_file: Path, link_path: str) -> Path | None:
        link_path = link_path.strip()
        try:
            posix = PurePosixPath(link_path)
        except Exception:
            return None

        if posix.is_absolute():
            candidate = (self.repo_root / str(posix).lstrip("/")).resolve(strict=False)
        else:
            candidate = (source_file.parent / str(posix)).resolve(strict=False)

        if not candidate.is_relative_to(self.repo_root):
            return None
        return candidate

    def _tracked_path_exists(self, rel_path: str) -> bool:
        if rel_path in self.tracked_files:
            return True
        return self._is_tracked_dir(rel_path)

    def _is_tracked_dir(self, rel_path: str) -> bool:
        rel_path = rel_path.strip("/").replace("\\", "/")
        return rel_path in self.tracked_dirs

    def _rel_path(self, path: Path) -> str | None:
        try:
            return path.resolve(strict=False).relative_to(self.repo_root).as_posix()
        except Exception:
            return None

    def _build_tracked_dirs(self, tracked_files: Iterable[str]) -> set[str]:
        dirs: set[str] = set()
        for rel in tracked_files:
            p = PurePosixPath(rel)
            for parent in p.parents:
                if str(parent) == ".":
                    break
                dirs.add(str(parent))
        return dirs
