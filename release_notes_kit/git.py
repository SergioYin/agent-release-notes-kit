"""Small deterministic git metadata reader."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import List, Optional, Sequence

from .errors import GitError


@dataclass(frozen=True)
class Commit:
    full_hash: str
    short_hash: str
    author: str
    date: str
    subject: str


@dataclass(frozen=True)
class GitInfo:
    repo_root: str
    branch: str
    head: str
    short_head: str
    latest_tag: Optional[str]
    dirty: bool
    status: List[str]
    commits: List[Commit]


def _git(args: Sequence[str], cwd: Optional[str] = None) -> str:
    command = ["git", *args]
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise GitError(f"Unable to run git: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown git error"
        raise GitError(detail)
    return completed.stdout.rstrip("\n")


def require_repo(cwd: Optional[str] = None) -> str:
    try:
        inside = _git(["rev-parse", "--is-inside-work-tree"], cwd=cwd)
    except GitError as exc:
        raise GitError("This command must be run inside a git repository.") from exc
    if inside != "true":
        raise GitError("This command must be run inside a git repository.")
    return _git(["rev-parse", "--show-toplevel"], cwd=cwd)


def read_git_info(cwd: Optional[str] = None, max_commits: int = 50) -> GitInfo:
    repo_root = require_repo(cwd)
    head = _git(["rev-parse", "HEAD"], cwd=repo_root)
    short_head = _git(["rev-parse", "--short=12", "HEAD"], cwd=repo_root)
    branch = _git(["branch", "--show-current"], cwd=repo_root) or "DETACHED"
    try:
        latest_tag = _git(["describe", "--tags", "--abbrev=0"], cwd=repo_root)
    except GitError:
        latest_tag = None
    status = sorted(line for line in _git(["status", "--porcelain"], cwd=repo_root).splitlines() if line)
    commits = _read_commits(repo_root, max_commits)
    return GitInfo(
        repo_root=repo_root,
        branch=branch,
        head=head,
        short_head=short_head,
        latest_tag=latest_tag,
        dirty=bool(status),
        status=status,
        commits=commits,
    )


def _read_commits(repo_root: str, max_commits: int) -> List[Commit]:
    if max_commits < 1:
        return []
    raw = _git(
        [
            "log",
            f"--max-count={max_commits}",
            "--date=short",
            "--pretty=format:%H%x1f%h%x1f%an%x1f%ad%x1f%s",
        ],
        cwd=repo_root,
    )
    commits: List[Commit] = []
    for line in raw.splitlines():
        parts = line.split("\x1f")
        if len(parts) != 5:
            continue
        commits.append(Commit(*parts))
    return commits
