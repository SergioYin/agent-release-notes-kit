import json
import tempfile
import unittest
from pathlib import Path

from release_notes_kit.github_body import (
    load_release_summary,
    render_github_body_markdown,
)


class GithubBodyTests(unittest.TestCase):
    def test_github_body_includes_required_sections(self):
        rendered = render_github_body_markdown(_summary())

        self.assertIn("Release `0.4.0` (`v0.4.0`)", rendered)
        self.assertIn("## Highlights", rendered)
        self.assertIn("- `Added` GitHub release body renderer", rendered)
        self.assertIn("## Verification", rendered)
        self.assertIn("- `passed` `python scripts/selfcheck.py`", rendered)
        self.assertIn("## Artifacts", rendered)
        self.assertIn("`dist/agent-release-notes-kit-0.4.0.tar.gz`", rendered)
        self.assertIn("## Upgrade Notes", rendered)
        self.assertIn("- Use `github-body` after `generate` writes `release-summary.json`.", rendered)

    def test_github_body_defaults_artifacts_for_legacy_summary(self):
        payload = _summary()
        payload.pop("artifacts")
        payload.pop("upgrade_notes")

        rendered = render_github_body_markdown(payload)

        self.assertIn("`RELEASE_NOTES.md`", rendered)
        self.assertIn("`release-summary.json`", rendered)
        self.assertIn("- No upgrade notes supplied.", rendered)

    def test_github_body_is_deterministic(self):
        first = render_github_body_markdown(_summary())
        second = render_github_body_markdown(_summary())

        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))

    def test_load_summary_rejects_non_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "release-summary.json"
            path.write_text(json.dumps([]), encoding="utf-8")

            with self.assertRaisesRegex(Exception, "must be an object"):
                load_release_summary(str(path))


def _summary():
    return {
        "date": "2026-05-11",
        "version": "0.4.0",
        "tag": "v0.4.0",
        "repo": {
            "root": "/repo",
            "branch": "main",
            "head": "abcdef1234567890",
            "short_head": "abcdef123456",
            "latest_tag": "v0.3.0",
            "dirty": False,
            "status": [],
        },
        "changes": [
            {"type": "Tests", "description": "Selfcheck coverage for GitHub body output"},
            {"type": "Added", "description": "GitHub release body renderer"},
        ],
        "checks": [
            {"command": "python scripts/selfcheck.py", "status": "passed", "detail": None},
            {"command": "python -m unittest discover -s tests -v", "status": "passed", "detail": "fixture"},
        ],
        "artifacts": [
            {
                "path": "dist/agent-release-notes-kit-0.4.0.tar.gz",
                "description": "Source distribution",
                "sha256": "abc123",
            },
            {"path": "release-summary.json", "description": "Release ledger"},
        ],
        "upgrade_notes": [
            "Use `github-body` after `generate` writes `release-summary.json`.",
        ],
        "commits": [],
    }


if __name__ == "__main__":
    unittest.main()
