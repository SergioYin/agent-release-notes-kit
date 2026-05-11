import json
import unittest

from release_notes_kit.git import Commit, GitInfo
from release_notes_kit.inputs import Change, Changelog, CheckResult
from release_notes_kit.render import (
    render_checkpoint_markdown,
    render_release_markdown,
    render_summary_json,
)


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.git_info = GitInfo(
            repo_root="/repo",
            branch="main",
            head="abc123def456",
            short_head="abc123def456",
            latest_tag=None,
            dirty=False,
            status=[],
            commits=[Commit("abc123def456", "abc123d", "Ada", "2026-05-11", "Initial commit")],
        )
        self.changelog = Changelog(
            version="0.1.0",
            title="Release",
            changes=[Change("Added", "CLI"), Change("Fixed", "Ordering")],
        )
        self.checks = [CheckResult("python -m unittest", "passed", "ok")]

    def test_release_markdown_is_deterministic(self):
        first = render_release_markdown(self.git_info, self.changelog, self.checks, "2026-05-11", "v0.1.0")
        second = render_release_markdown(self.git_info, self.changelog, self.checks, "2026-05-11", "v0.1.0")

        self.assertEqual(first, second)
        self.assertIn("Version: `0.1.0`", first)
        self.assertIn("`passed` `python -m unittest`", first)

    def test_summary_json_is_sorted_and_parseable(self):
        rendered = render_summary_json(self.git_info, self.changelog, self.checks, "2026-05-11", "v0.1.0")
        payload = json.loads(rendered)

        self.assertEqual("2026-05-11", payload["date"])
        self.assertEqual("abc123def456", payload["repo"]["head"])
        self.assertTrue(rendered.endswith("\n"))

    def test_checkpoint_includes_clean_working_tree(self):
        rendered = render_checkpoint_markdown(self.git_info, self.checks, "2026-05-11", "v0.1.0")

        self.assertIn("Tag candidate: `v0.1.0`", rendered)
        self.assertIn("- Clean.", rendered)


if __name__ == "__main__":
    unittest.main()
