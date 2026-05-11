# agent-release-notes-kit v0.2.0

- Version: `0.2.0`
- Date: `2026-05-11`
- Repository: `/home/xjyin/workspace/token-lab/20260511-agent-release-notes-kit`
- Branch: `main`
- Head: `b970fba8c0f7`
- Dirty: `yes`

## Changes

### Added

- Collect command that writes deterministic reusable JSON inputs from local git state
- Generate support for collected JSON via top-level changelog and checks sections
- Suggested semantic next tag, conventional commit changelog skeleton, and skipped verification skeletons

### Changed

- README documents the collect, check, generate, and checkpoint workflow
- Selfcheck now exercises the collect-to-generate path

## Verification

- `passed` `git diff --check`
- `passed` `python -m unittest discover -s tests -v` - 13 tests
- `passed` `python scripts/selfcheck.py`

## Recent Commits

- `b970fba` 2026-05-11 feat: initial release notes kit MVP (SergioYin)
- `31c7d7e` 2026-05-11 chore: seed release notes kit repo (SergioYin)
