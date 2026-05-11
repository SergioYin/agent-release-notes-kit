import subprocess
import sys
import tempfile
import unittest
import os
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


if __name__ == "__main__":
    unittest.main()
