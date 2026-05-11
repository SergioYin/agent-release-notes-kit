# Release Comparison

- Previous: `0.2.0` (2026-05-11, `b970fba8c0f7`)
- Current: `0.3.0` (2026-05-11, `10fd723f53d0`)
- Previous summary: `release-summary-v0.2.0.json`
- Current summary: `release-summary.json`

## Change Summary

- Previous changes: `5`
- Current changes: `5`
- Delta: `0`

### Current Changes by Type

- Added: `2`
- Changed: `1`
- Documentation: `1`
- Tests: `1`

### Added Since Previous

- `Added` Compare command that writes deterministic Markdown and JSON release-summary deltas
- `Added` Cross-asset example fixtures for prompt, dataset, model-card, tokenizer, and token-ledger style assets
- `Changed` Selfcheck now exercises previous-release comparison output
- `Documentation` README documents local previous/current release-summary comparisons
- `Tests` Comparison unit and CLI tests cover deterministic deltas

### Removed Since Previous

- `Added` Collect command that writes deterministic reusable JSON inputs from local git state
- `Added` Generate support for collected JSON via top-level changelog and checks sections
- `Added` Suggested semantic next tag, conventional commit changelog skeleton, and skipped verification skeletons
- `Changed` README documents the collect, check, generate, and checkpoint workflow
- `Changed` Selfcheck now exercises the collect-to-generate path

## Verification Summary

- Previous checks: `3`
- Current checks: `3`

### Current Checks by Status

- passed: `3`

### Check Status Changes

- None.

## Commit Summary

- Previous commits listed: `2`
- Current commits listed: `3`

### New Commits

- `10fd723` 2026-05-11 feat: collect release input metadata (SergioYin)
