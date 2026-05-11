"""Built-in deterministic fixture check."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from .core import checkpoint, collect, generate
from .errors import KitError


def run_selfcheck() -> None:
    with tempfile.TemporaryDirectory(prefix="release-notes-kit-") as tmp:
        repo = Path(tmp)
        _run(["git", "init"], repo)
        _run(["git", "config", "user.email", "selfcheck@example.invalid"], repo)
        _run(["git", "config", "user.name", "Self Check"], repo)
        (repo / "asset.txt").write_text("sample\n", encoding="utf-8")
        _run(["git", "add", "asset.txt"], repo)
        _run(["git", "commit", "-m", "Initial fixture"], repo)

        changelog = repo / "changelog.json"
        checks = repo / "checks.json"
        collected = repo / "release-inputs.json"
        changelog.write_text(
            json.dumps(
                {
                    "version": "0.1.0",
                    "title": "Selfcheck Release",
                    "changes": [
                        {"type": "Added", "description": "Fixture release note generation"},
                        {"type": "Changed", "description": "Stable checkpoint rendering"},
                    ],
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        checks.write_text(
            json.dumps(
                {
                    "commands": [
                        {"command": "python -m unittest", "status": "passed", "detail": "fixture"},
                        {"command": "python scripts/selfcheck.py", "status": "passed"},
                    ]
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        (repo / ".git" / "info" / "exclude").write_text(
            (
                "RELEASE_NOTES.md\n"
                "release-summary.json\n"
                "CHECKPOINT.md\n"
                "release-inputs.json\n"
                "RELEASE_NOTES_COLLECTED.md\n"
                "release-summary-collected.json\n"
            ),
            encoding="utf-8",
        )
        _run(["git", "add", "changelog.json", "checks.json"], repo)
        _run(["git", "commit", "-m", "Add fixture inputs"], repo)

        generate(
            output=str(repo / "RELEASE_NOTES.md"),
            summary=str(repo / "release-summary.json"),
            date="2026-05-11",
            changelog_path=str(changelog),
            checks_path=str(checks),
            tag="v0.1.0",
            cwd=str(repo),
            max_commits=10,
        )
        collect(
            output=str(collected),
            date="2026-05-11",
            cwd=str(repo),
            max_commits=10,
        )
        generate(
            output=str(repo / "RELEASE_NOTES_COLLECTED.md"),
            summary=str(repo / "release-summary-collected.json"),
            date="2026-05-11",
            inputs_path=str(collected),
            tag="v0.2.0",
            cwd=str(repo),
            max_commits=10,
        )
        checkpoint(
            output=str(repo / "CHECKPOINT.md"),
            date="2026-05-11",
            checks_path=str(checks),
            tag_candidate="v0.1.0",
            cwd=str(repo),
        )
        first = _snapshot(repo)
        generate(
            output=str(repo / "RELEASE_NOTES.md"),
            summary=str(repo / "release-summary.json"),
            date="2026-05-11",
            changelog_path=str(changelog),
            checks_path=str(checks),
            tag="v0.1.0",
            cwd=str(repo),
            max_commits=10,
        )
        collect(
            output=str(collected),
            date="2026-05-11",
            cwd=str(repo),
            max_commits=10,
        )
        generate(
            output=str(repo / "RELEASE_NOTES_COLLECTED.md"),
            summary=str(repo / "release-summary-collected.json"),
            date="2026-05-11",
            inputs_path=str(collected),
            tag="v0.2.0",
            cwd=str(repo),
            max_commits=10,
        )
        checkpoint(
            output=str(repo / "CHECKPOINT.md"),
            date="2026-05-11",
            checks_path=str(checks),
            tag_candidate="v0.1.0",
            cwd=str(repo),
        )
        second = _snapshot(repo)
        if first != second:
            raise KitError("Selfcheck failed: repeated generation was not deterministic.")


def _snapshot(repo: Path) -> str:
    return "\n--- release-summary.json ---\n".join(
        [
            (repo / "RELEASE_NOTES.md").read_text(encoding="utf-8"),
            (repo / "release-summary.json").read_text(encoding="utf-8"),
            (repo / "CHECKPOINT.md").read_text(encoding="utf-8"),
            (repo / "release-inputs.json").read_text(encoding="utf-8"),
            (repo / "RELEASE_NOTES_COLLECTED.md").read_text(encoding="utf-8"),
            (repo / "release-summary-collected.json").read_text(encoding="utf-8"),
        ]
    )


def _run(command, cwd: Path) -> None:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise KitError(f"Selfcheck command failed: {' '.join(command)}: {detail}")
