"""Collect reusable release input JSON from local repository state."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .git import Commit, _git, read_git_info, require_repo


DEFAULT_CHECK_COMMANDS = (
    "python -m unittest discover -s tests -v",
    "python scripts/selfcheck.py",
    "git diff --check",
)

_SEMVER_TAG = re.compile(r"^v([0-9]+)\.([0-9]+)\.([0-9]+)$")
_CONVENTIONAL_PREFIX = re.compile(r"^(?P<prefix>[A-Za-z]+)(?:\([^)]*\))?(?:!)?:\s*(?P<subject>.+)$")
_CHANGE_KIND_BY_PREFIX = {
    "feat": "Added",
    "fix": "Fixed",
    "docs": "Documentation",
    "test": "Tests",
    "chore": "Maintenance",
}


def collect(
    output: str,
    date: str,
    max_commits: int = 50,
    suggest_bump: str = "minor",
    checks_commands: Optional[Sequence[str]] = None,
    cwd: Optional[str] = None,
) -> None:
    payload = collect_payload(
        date=date,
        max_commits=max_commits,
        suggest_bump=suggest_bump,
        checks_commands=checks_commands,
        cwd=cwd,
    )
    Path(output).write_text(render_collect_json(payload), encoding="utf-8")


def collect_payload(
    date: str,
    max_commits: int = 50,
    suggest_bump: str = "minor",
    checks_commands: Optional[Sequence[str]] = None,
    cwd: Optional[str] = None,
) -> Dict[str, object]:
    git_info = read_git_info(cwd=cwd, max_commits=max_commits)
    latest_semver_tag = latest_semver_tag_for_repo(git_info.repo_root)
    suggested_next_tag = suggest_next_tag(latest_semver_tag, suggest_bump)
    version = suggested_next_tag[1:] if suggested_next_tag.startswith("v") else suggested_next_tag
    repo_name = Path(git_info.repo_root).name
    return {
        "date": date,
        "repo": {
            "root": git_info.repo_root,
            "branch": git_info.branch,
            "head": git_info.head,
            "short_head": git_info.short_head,
            "latest_tag": git_info.latest_tag,
            "dirty": git_info.dirty,
            "status": git_info.status,
        },
        "commits": [_commit_payload(commit) for commit in git_info.commits],
        "suggested_bump": suggest_bump,
        "suggested_next_tag": suggested_next_tag,
        "latest_semver_tag": latest_semver_tag,
        "changelog": {
            "version": version,
            "title": f"{repo_name} {suggested_next_tag}",
            "changes": changelog_changes_from_commits(git_info.commits),
        },
        "checks": {
            "commands": check_skeleton(checks_commands),
        },
    }


def render_collect_json(payload: Dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def latest_semver_tag_for_repo(cwd: Optional[str] = None) -> Optional[str]:
    repo_root = require_repo(cwd)
    raw = _git(["tag", "--list", "v[0-9]*.[0-9]*.[0-9]*"], cwd=repo_root)
    tags = [tag for tag in raw.splitlines() if _SEMVER_TAG.match(tag)]
    if not tags:
        return None
    return max(tags, key=_semver_key)


def suggest_next_tag(latest_tag: Optional[str], bump: str) -> str:
    if bump not in {"patch", "minor", "major"}:
        raise ValueError("bump must be patch, minor, or major")
    if latest_tag is None:
        return "v0.1.0"
    major, minor, patch = _semver_key(latest_tag)
    if bump == "major":
        return f"v{major + 1}.0.0"
    if bump == "minor":
        return f"v{major}.{minor + 1}.0"
    return f"v{major}.{minor}.{patch + 1}"


def changelog_changes_from_commits(commits: Iterable[Commit]) -> List[Dict[str, str]]:
    changes = []
    for commit in commits:
        kind, description = conventional_change(commit.subject)
        changes.append({"type": kind, "description": description})
    return sorted(changes, key=lambda item: (item["type"], item["description"]))


def conventional_change(subject: str) -> Tuple[str, str]:
    match = _CONVENTIONAL_PREFIX.match(subject)
    if not match:
        return "Changed", subject.strip()
    prefix = match.group("prefix").lower()
    description = match.group("subject").strip()
    return _CHANGE_KIND_BY_PREFIX.get(prefix, "Changed"), description


def check_skeleton(commands: Optional[Sequence[str]] = None) -> List[Dict[str, str]]:
    ordered = list(DEFAULT_CHECK_COMMANDS)
    for command in commands or ():
        command = command.strip()
        if command and command not in ordered:
            ordered.append(command)
    return [{"command": command, "status": "skipped"} for command in ordered]


def _commit_payload(commit: Commit) -> Dict[str, str]:
    return {
        "hash": commit.full_hash,
        "short_hash": commit.short_hash,
        "author": commit.author,
        "date": commit.date,
        "subject": commit.subject,
    }


def _semver_key(tag: str) -> Tuple[int, int, int]:
    match = _SEMVER_TAG.match(tag)
    if not match:
        raise ValueError(f"not a vX.Y.Z tag: {tag}")
    return tuple(int(part) for part in match.groups())
