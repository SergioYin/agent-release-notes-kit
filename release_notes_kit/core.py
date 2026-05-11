"""Public operations used by the CLI and selfcheck."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .compare import compare_release_summaries, render_comparison_json, render_comparison_markdown
from .collect import collect as collect
from .git import read_git_info
from .github_body import render_github_body_from_file
from .inputs import load_changelog, load_checks
from .render import render_checkpoint_markdown, render_release_markdown, render_summary_json


def generate(
    output: str,
    summary: str,
    date: str,
    changelog_path: Optional[str] = None,
    checks_path: Optional[str] = None,
    inputs_path: Optional[str] = None,
    tag: Optional[str] = None,
    cwd: Optional[str] = None,
    max_commits: int = 50,
) -> None:
    git_info = read_git_info(cwd=cwd, max_commits=max_commits)
    if inputs_path:
        changelog_path = changelog_path or inputs_path
        checks_path = checks_path or inputs_path
    changelog = load_changelog(changelog_path)
    checks = load_checks(checks_path)
    Path(output).write_text(
        render_release_markdown(git_info, changelog, checks, date=date, tag=tag),
        encoding="utf-8",
    )
    Path(summary).write_text(
        render_summary_json(git_info, changelog, checks, date=date, tag=tag),
        encoding="utf-8",
    )


def checkpoint(
    output: str,
    date: str,
    checks_path: Optional[str] = None,
    tag_candidate: Optional[str] = None,
    cwd: Optional[str] = None,
) -> None:
    git_info = read_git_info(cwd=cwd, max_commits=1)
    checks = load_checks(checks_path)
    Path(output).write_text(
        render_checkpoint_markdown(git_info, checks, date=date, tag_candidate=tag_candidate),
        encoding="utf-8",
    )


def compare(
    previous: str,
    current: str,
    output: str,
    summary: Optional[str] = None,
) -> None:
    comparison = compare_release_summaries(previous, current)
    Path(output).write_text(render_comparison_markdown(comparison), encoding="utf-8")
    if summary:
        Path(summary).write_text(render_comparison_json(comparison), encoding="utf-8")


def github_body(summary: str, output: str) -> None:
    Path(output).write_text(render_github_body_from_file(summary), encoding="utf-8")
