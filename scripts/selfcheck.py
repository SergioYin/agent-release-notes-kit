#!/usr/bin/env python3
"""Run the release_notes_kit built-in selfcheck."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from release_notes_kit.selfcheck import run_selfcheck


if __name__ == "__main__":
    run_selfcheck()
    print("selfcheck passed")
