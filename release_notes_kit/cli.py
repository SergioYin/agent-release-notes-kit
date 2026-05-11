"""Command-line interface."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .core import checkpoint, collect, compare, generate, github_body
from .errors import KitError
from .selfcheck import run_selfcheck


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="release-notes-kit",
        description="Generate deterministic release notes and checkpoint ledgers from local git metadata.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="write Markdown release notes and JSON summary")
    generate_parser.add_argument("--date", required=True, help="stable release date to embed, for example 2026-05-11")
    generate_parser.add_argument("--output", default="RELEASE_NOTES.md", help="Markdown output path")
    generate_parser.add_argument("--summary", default="release-summary.json", help="JSON summary output path")
    generate_parser.add_argument("--changelog", help="optional changelog JSON path")
    generate_parser.add_argument("--checks", help="optional verification checks JSON path")
    generate_parser.add_argument("--inputs", help="optional collected JSON path containing changelog and checks sections")
    generate_parser.add_argument("--tag", help="optional release tag, for example v0.1.0")
    generate_parser.add_argument("--max-commits", type=int, default=50, help="maximum recent commits to include")
    generate_parser.set_defaults(func=_generate)

    collect_parser = subparsers.add_parser("collect", help="write reusable JSON inputs from local git state")
    collect_parser.add_argument("--date", required=True, help="stable release date to embed, for example 2026-05-11")
    collect_parser.add_argument("--output", default="release-inputs.json", help="JSON output path")
    collect_parser.add_argument("--max-commits", type=int, default=50, help="maximum recent commits to include")
    collect_parser.add_argument(
        "--suggest-bump",
        choices=("patch", "minor", "major"),
        default="minor",
        help="semantic bump to suggest from the latest vX.Y.Z tag",
    )
    collect_parser.add_argument(
        "--checks-command",
        action="append",
        default=[],
        help="extra verification command to add to the skipped check skeleton",
    )
    collect_parser.set_defaults(func=_collect)

    checkpoint_parser = subparsers.add_parser("checkpoint", help="write a deterministic Markdown checkpoint")
    checkpoint_parser.add_argument("--date", required=True, help="stable checkpoint date to embed")
    checkpoint_parser.add_argument("--output", default="CHECKPOINT.md", help="Markdown checkpoint output path")
    checkpoint_parser.add_argument("--checks", help="optional verification checks JSON path")
    checkpoint_parser.add_argument("--tag-candidate", help="optional tag candidate, for example v0.1.0")
    checkpoint_parser.set_defaults(func=_checkpoint)

    compare_parser = subparsers.add_parser("compare", help="compare two local release-summary JSON files")
    compare_parser.add_argument("--previous", required=True, help="previous release-summary JSON path")
    compare_parser.add_argument("--current", required=True, help="current release-summary JSON path")
    compare_parser.add_argument("--output", default="RELEASE_COMPARISON.md", help="Markdown comparison output path")
    compare_parser.add_argument("--summary", default="release-comparison.json", help="JSON comparison output path")
    compare_parser.set_defaults(func=_compare)

    github_body_parser = subparsers.add_parser("github-body", help="write a concise GitHub release body from release-summary JSON")
    github_body_parser.add_argument("--summary", default="release-summary.json", help="release-summary JSON input path")
    github_body_parser.add_argument("--output", default="GITHUB_RELEASE_BODY.md", help="Markdown output path")
    github_body_parser.set_defaults(func=_github_body)

    selfcheck_parser = subparsers.add_parser("selfcheck", help="run the built-in deterministic fixture check")
    selfcheck_parser.set_defaults(func=_selfcheck)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except KitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def _generate(args) -> None:
    generate(
        output=args.output,
        summary=args.summary,
        date=args.date,
        changelog_path=args.changelog,
        checks_path=args.checks,
        inputs_path=args.inputs,
        tag=args.tag,
        max_commits=args.max_commits,
    )


def _collect(args) -> None:
    collect(
        output=args.output,
        date=args.date,
        max_commits=args.max_commits,
        suggest_bump=args.suggest_bump,
        checks_commands=args.checks_command,
    )


def _checkpoint(args) -> None:
    checkpoint(
        output=args.output,
        date=args.date,
        checks_path=args.checks,
        tag_candidate=args.tag_candidate,
    )


def _compare(args) -> None:
    compare(
        previous=args.previous,
        current=args.current,
        output=args.output,
        summary=args.summary,
    )


def _github_body(args) -> None:
    github_body(summary=args.summary, output=args.output)


def _selfcheck(args) -> None:
    run_selfcheck()
    print("selfcheck passed")


if __name__ == "__main__":
    raise SystemExit(main())
