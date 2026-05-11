import json
import tempfile
import unittest
from pathlib import Path

from release_notes_kit.compare import (
    compare_release_summaries,
    render_comparison_json,
    render_comparison_markdown,
)


class CompareTests(unittest.TestCase):
    def test_comparison_tracks_changes_checks_and_commits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            previous = root / "previous.json"
            current = root / "current.json"
            previous.write_text(json.dumps(_summary("0.2.0", ["a1"], "skipped")), encoding="utf-8")
            current.write_text(json.dumps(_summary("0.3.0", ["a1", "b2"], "passed")), encoding="utf-8")

            comparison = compare_release_summaries(str(previous), str(current))
            markdown = render_comparison_markdown(comparison)
            payload = json.loads(render_comparison_json(comparison))

        self.assertEqual("0.2.0", payload["previous"]["version"])
        self.assertEqual("0.3.0", payload["current"]["version"])
        self.assertEqual(1, payload["changes"]["delta"])
        self.assertEqual("passed", payload["checks"]["status_changed"][0]["current_status"])
        self.assertEqual("b2", payload["commits"]["new"][0]["hash"])
        self.assertIn("## Change Summary", markdown)
        self.assertIn("`python scripts/selfcheck.py`: `skipped` -> `passed`", markdown)

    def test_comparison_json_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            previous = root / "previous.json"
            current = root / "current.json"
            previous.write_text(json.dumps(_summary("0.2.0", ["a1"], "passed")), encoding="utf-8")
            current.write_text(json.dumps(_summary("0.3.0", ["a1"], "passed")), encoding="utf-8")

            first = render_comparison_json(compare_release_summaries(str(previous), str(current)))
            second = render_comparison_json(compare_release_summaries(str(previous), str(current)))

        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))

    def test_cross_asset_example_fixtures_compare(self):
        root = Path(__file__).resolve().parents[1] / "examples" / "cross-asset"
        comparison = compare_release_summaries(
            str(root / "previous-release-summary.json"),
            str(root / "current-release-summary.json"),
        )

        self.assertEqual("0.3.0", comparison["current"]["version"])
        self.assertEqual(3, len(comparison["changes"]["added"]))
        self.assertEqual("passed", comparison["checks"]["status_changed"][0]["current_status"])


def _summary(version, hashes, check_status):
    changes = [
        {"type": "Added", "description": "Prompt templates for text assets"},
        {"type": "Changed", "description": "Dataset card examples"},
    ]
    if version == "0.3.0":
        changes.append({"type": "Added", "description": "Model card and tokenizer asset examples"})
    return {
        "date": "2026-05-11",
        "version": version,
        "tag": "v" + version,
        "repo": {
            "root": "/repo",
            "branch": "main",
            "head": hashes[-1],
            "short_head": hashes[-1],
            "latest_tag": "v0.2.0",
            "dirty": False,
            "status": [],
        },
        "changes": changes,
        "checks": [
            {"command": "python scripts/selfcheck.py", "status": check_status, "detail": None},
        ],
        "commits": [
            {
                "hash": item,
                "short_hash": item,
                "author": "Tests",
                "date": "2026-05-11",
                "subject": "feat: cross asset example",
            }
            for item in hashes
        ],
    }


if __name__ == "__main__":
    unittest.main()
