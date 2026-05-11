"""Command-line interface."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .core import checkpoint, generate
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
    generate_parser.add_argument("--tag", help="optional release tag, for example v0.1.0")
    generate_parser.add_argument("--max-commits", type=int, default=50, help="maximum recent commits to include")
    generate_parser.set_defaults(func=_generate)

    checkpoint_parser = subparsers.add_parser("checkpoint", help="write a deterministic Markdown checkpoint")
    checkpoint_parser.add_argument("--date", required=True, help="stable checkpoint date to embed")
    checkpoint_parser.add_argument("--output", default="CHECKPOINT.md", help="Markdown checkpoint output path")
    checkpoint_parser.add_argument("--checks", help="optional verification checks JSON path")
    checkpoint_parser.add_argument("--tag-candidate", help="optional tag candidate, for example v0.1.0")
    checkpoint_parser.set_defaults(func=_checkpoint)

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
        tag=args.tag,
        max_commits=args.max_commits,
    )


def _checkpoint(args) -> None:
    checkpoint(
        output=args.output,
        date=args.date,
        checks_path=args.checks,
        tag_candidate=args.tag_candidate,
    )


def _selfcheck(args) -> None:
    run_selfcheck()
    print("selfcheck passed")


if __name__ == "__main__":
    raise SystemExit(main())
