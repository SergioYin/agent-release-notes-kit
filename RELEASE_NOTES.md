# agent-release-notes-kit v0.1.0

- Version: `0.1.0`
- Date: `2026-05-11`
- Repository: `/home/xjyin/workspace/token-lab/20260511-agent-release-notes-kit`
- Branch: `main`
- Head: `31c7d7e23bb0`
- Dirty: `yes`

## Changes

### Added

- Deterministic Markdown release notes and JSON summary generation from local git metadata
- Strict changelog/checks JSON validation, unit tests, selfcheck wrapper, README, changelog, license, and pyproject
- Zero-dependency Python CLI with generate, checkpoint, and selfcheck commands

## Verification

- `passed` `git diff --check`
- `passed` `python -m unittest discover -s tests -v` - 9 tests
- `passed` `python scripts/selfcheck.py`
- `passed` `secret-pattern diff scan` - no secret-like patterns

## Recent Commits

- `31c7d7e` 2026-05-11 chore: seed release notes kit repo (SergioYin)
