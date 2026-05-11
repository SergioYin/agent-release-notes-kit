# 20260511-agent-release-notes-kit v0.3.0

- Version: `0.3.0`
- Date: `2026-05-11`
- Repository: `/home/xjyin/workspace/token-lab/20260511-agent-release-notes-kit`
- Branch: `main`
- Head: `10fd723f53d0`
- Dirty: `yes`

## Changes

### Added

- Compare command that writes deterministic Markdown and JSON release-summary deltas
- Cross-asset example fixtures for prompt, dataset, model-card, tokenizer, and token-ledger style assets

### Changed

- Selfcheck now exercises previous-release comparison output

### Documentation

- README documents local previous/current release-summary comparisons

### Tests

- Comparison unit and CLI tests cover deterministic deltas

## Verification

- `passed` `git diff --check`
- `passed` `python -m unittest discover -s tests -v` - 17 tests
- `passed` `python scripts/selfcheck.py`

## Recent Commits

- `10fd723` 2026-05-11 feat: collect release input metadata (SergioYin)
- `b970fba` 2026-05-11 feat: initial release notes kit MVP (SergioYin)
- `31c7d7e` 2026-05-11 chore: seed release notes kit repo (SergioYin)
