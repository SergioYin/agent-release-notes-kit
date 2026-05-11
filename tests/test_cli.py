import subprocess
import sys
import tempfile
import unittest
import os
import json
from pathlib import Path


class CliTests(unittest.TestCase):
    def test_generate_outside_git_fails_helpfully(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "release_notes_kit",
                    "generate",
                    "--date",
                    "2026-05-11",
                ],
                cwd=tmp,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(2, completed.returncode)
        self.assertIn("inside a git repository", completed.stderr)

    def test_selfcheck_command_passes(self):
        completed = subprocess.run(
            [sys.executable, "-m", "release_notes_kit", "selfcheck"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("selfcheck passed", completed.stdout)

    def test_compare_command_writes_markdown_and_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            previous = root / "previous.json"
            current = root / "current.json"
            output = root / "comparison.md"
            summary = root / "comparison.json"
            previous.write_text(json.dumps(_summary("0.2.0", "a1", "skipped")), encoding="utf-8")
            current.write_text(json.dumps(_summary("0.3.0", "b2", "passed")), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "release_notes_kit",
                    "compare",
                    "--previous",
                    str(previous),
                    "--current",
                    str(current),
                    "--output",
                    str(output),
                    "--summary",
                    str(summary),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            rendered = output.read_text(encoding="utf-8")
            payload = json.loads(summary.read_text(encoding="utf-8"))

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("Current: `0.3.0`", rendered)
        self.assertEqual("0.2.0", payload["previous"]["version"])


def _summary(version, head, check_status):
    return {
        "date": "2026-05-11",
        "version": version,
        "tag": "v" + version,
        "repo": {
            "root": "/repo",
            "branch": "main",
            "head": head,
            "short_head": head,
            "latest_tag": "v0.2.0",
            "dirty": False,
            "status": [],
        },
        "changes": [{"type": "Added", "description": "Cross-asset fixture"}],
        "checks": [{"command": "python scripts/selfcheck.py", "status": check_status, "detail": None}],
        "commits": [
            {
                "hash": head,
                "short_hash": head,
                "author": "Tests",
                "date": "2026-05-11",
                "subject": "feat: cross asset fixture",
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()
