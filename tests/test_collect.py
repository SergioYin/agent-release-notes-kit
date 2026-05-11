import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from release_notes_kit.collect import (
    changelog_changes_from_commits,
    collect,
    collect_payload,
    conventional_change,
    render_collect_json,
    suggest_next_tag,
)
from release_notes_kit.core import generate
from release_notes_kit.git import Commit


class CollectTests(unittest.TestCase):
    def test_suggest_next_tag_from_semver_tag(self):
        self.assertEqual("v0.1.1", suggest_next_tag("v0.1.0", "patch"))
        self.assertEqual("v0.2.0", suggest_next_tag("v0.1.0", "minor"))
        self.assertEqual("v1.0.0", suggest_next_tag("v0.1.0", "major"))
        self.assertEqual("v0.1.0", suggest_next_tag(None, "minor"))

    def test_conventional_commit_grouping(self):
        commits = [
            Commit("1", "1", "Ada", "2026-05-11", "fix: sort checks"),
            Commit("2", "2", "Ada", "2026-05-11", "feat(cli): collect git state"),
            Commit("3", "3", "Ada", "2026-05-11", "plain subject"),
            Commit("4", "4", "Ada", "2026-05-11", "docs: update workflow"),
        ]

        changes = changelog_changes_from_commits(commits)

        self.assertEqual(
            [
                {"type": "Added", "description": "collect git state"},
                {"type": "Changed", "description": "plain subject"},
                {"type": "Documentation", "description": "update workflow"},
                {"type": "Fixed", "description": "sort checks"},
            ],
            changes,
        )
        self.assertEqual(("Maintenance", "prepare release"), conventional_change("chore!: prepare release"))

    def test_collect_json_is_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _fixture_repo(Path(tmp))
            first = render_collect_json(collect_payload("2026-05-11", cwd=str(repo), max_commits=5))
            second = render_collect_json(collect_payload("2026-05-11", cwd=str(repo), max_commits=5))

        self.assertEqual(first, second)
        payload = json.loads(first)
        self.assertEqual("v0.2.0", payload["suggested_next_tag"])
        self.assertEqual("v0.1.0", payload["repo"]["latest_tag"])
        self.assertEqual("skipped", payload["checks"]["commands"][0]["status"])

    def test_generate_reads_collected_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _fixture_repo(Path(tmp))
            collected = repo / "release-inputs.json"
            notes = repo / "RELEASE_NOTES.md"
            summary = repo / "summary.json"
            collect(str(collected), "2026-05-11", cwd=str(repo), max_commits=5)

            generate(
                output=str(notes),
                summary=str(summary),
                date="2026-05-11",
                inputs_path=str(collected),
                tag="v0.2.0",
                cwd=str(repo),
                max_commits=5,
            )

            rendered = notes.read_text(encoding="utf-8")
            payload = json.loads(summary.read_text(encoding="utf-8"))

        self.assertIn("collect git state", rendered)
        self.assertIn("`skipped` `git diff --check`", rendered)
        self.assertEqual("0.2.0", payload["version"])


def _fixture_repo(path: Path) -> Path:
    _run(["git", "init"], path)
    _run(["git", "config", "user.email", "tests@example.invalid"], path)
    _run(["git", "config", "user.name", "Tests"], path)
    (path / "file.txt").write_text("one\n", encoding="utf-8")
    _run(["git", "add", "file.txt"], path)
    _run(["git", "commit", "-m", "chore: seed repo"], path)
    _run(["git", "tag", "v0.1.0"], path)
    (path / "file.txt").write_text("one\ntwo\n", encoding="utf-8")
    _run(["git", "add", "file.txt"], path)
    _run(["git", "commit", "-m", "feat: collect git state"], path)
    return path


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
        raise AssertionError(f"command failed: {' '.join(command)}: {detail}")


if __name__ == "__main__":
    unittest.main()
