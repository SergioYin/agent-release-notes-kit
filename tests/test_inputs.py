import json
import tempfile
import unittest
from pathlib import Path

from release_notes_kit.errors import InputError
from release_notes_kit.inputs import load_changelog, load_checks


class InputTests(unittest.TestCase):
    def test_load_changelog_sorts_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "changelog.json"
            path.write_text(
                json.dumps(
                    {
                        "version": "0.1.0",
                        "changes": [
                            {"type": "Fixed", "description": "B"},
                            {"type": "Added", "description": "A"},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            changelog = load_changelog(str(path))

        self.assertEqual(["Added", "Fixed"], [change.kind for change in changelog.changes])

    def test_load_checks_accepts_commands_object_and_sorts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checks.json"
            path.write_text(
                json.dumps(
                    {
                        "commands": [
                            {"command": "z", "status": "passed"},
                            {"command": "a", "status": "skipped", "notes": "not needed"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            checks = load_checks(str(path))

        self.assertEqual(["a", "z"], [check.command for check in checks])
        self.assertEqual("not needed", checks[0].detail)

    def test_malformed_json_has_helpful_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{", encoding="utf-8")

            with self.assertRaises(InputError) as raised:
                load_checks(str(path))

        self.assertIn("Malformed JSON", str(raised.exception))

    def test_invalid_check_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "checks.json"
            path.write_text(json.dumps([{"command": "x", "status": "ok"}]), encoding="utf-8")

            with self.assertRaises(InputError) as raised:
                load_checks(str(path))

        self.assertIn("passed, failed, or skipped", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
