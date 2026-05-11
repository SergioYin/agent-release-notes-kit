"""Markdown and JSON renderers."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from .git import GitInfo
from .inputs import Changelog, CheckResult


def render_release_markdown(
    git_info: GitInfo,
    changelog: Changelog,
    checks: Iterable[CheckResult],
    date: str,
    tag: Optional[str] = None,
) -> str:
    title = changelog.title or "Release Notes"
    version = changelog.version or tag or "unversioned"
    lines = [
        f"# {title}",
        "",
        f"- Version: `{version}`",
        f"- Date: `{date}`",
        f"- Repository: `{git_info.repo_root}`",
        f"- Branch: `{git_info.branch}`",
        f"- Head: `{git_info.short_head}`",
        f"- Dirty: `{'yes' if git_info.dirty else 'no'}`",
        "",
        "## Changes",
        "",
    ]
    if changelog.changes:
        grouped: Dict[str, List[str]] = defaultdict(list)
        for change in changelog.changes:
            grouped[change.kind].append(change.description)
        for kind in sorted(grouped):
            lines.extend([f"### {kind}", ""])
            for description in sorted(grouped[kind]):
                lines.append(f"- {description}")
            lines.append("")
    else:
        lines.extend(["- No changelog entries supplied.", ""])
    lines.extend(["## Verification", ""])
    lines.extend(_checks_lines(checks))
    lines.extend(["", "## Recent Commits", ""])
    if git_info.commits:
        for commit in git_info.commits:
            lines.append(f"- `{commit.short_hash}` {commit.date} {commit.subject} ({commit.author})")
    else:
        lines.append("- No commits found.")
    lines.append("")
    return "\n".join(lines)


def render_summary_json(
    git_info: GitInfo,
    changelog: Changelog,
    checks: Iterable[CheckResult],
    date: str,
    tag: Optional[str] = None,
) -> str:
    payload = {
        "date": date,
        "version": changelog.version or tag or "unversioned",
        "tag": tag,
        "repo": {
            "root": git_info.repo_root,
            "branch": git_info.branch,
            "head": git_info.head,
            "short_head": git_info.short_head,
            "latest_tag": git_info.latest_tag,
            "dirty": git_info.dirty,
            "status": git_info.status,
        },
        "changes": [
            {"type": change.kind, "description": change.description}
            for change in changelog.changes
        ],
        "checks": [
            {"command": check.command, "status": check.status, "detail": check.detail}
            for check in checks
        ],
        "commits": [
            {
                "hash": commit.full_hash,
                "short_hash": commit.short_hash,
                "author": commit.author,
                "date": commit.date,
                "subject": commit.subject,
            }
            for commit in git_info.commits
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_checkpoint_markdown(
    git_info: GitInfo,
    checks: Iterable[CheckResult],
    date: str,
    tag_candidate: Optional[str] = None,
) -> str:
    lines = [
        "# Release Checkpoint",
        "",
        f"- Date: `{date}`",
        f"- Repository: `{git_info.repo_root}`",
        f"- Branch: `{git_info.branch}`",
        f"- Head: `{git_info.head}`",
        f"- Tag candidate: `{tag_candidate or 'none'}`",
        f"- Dirty: `{'yes' if git_info.dirty else 'no'}`",
        "",
        "## Verification",
        "",
    ]
    lines.extend(_checks_lines(checks))
    lines.extend(["", "## Working Tree", ""])
    if git_info.status:
        for item in git_info.status:
            lines.append(f"- `{item}`")
    else:
        lines.append("- Clean.")
    lines.append("")
    return "\n".join(lines)


def _checks_lines(checks: Iterable[CheckResult]) -> List[str]:
    items = list(checks)
    if not items:
        return ["- No verification results supplied."]
    lines: List[str] = []
    for check in items:
        line = f"- `{check.status}` `{check.command}`"
        if check.detail:
            line += f" - {check.detail}"
        lines.append(line)
    return lines
