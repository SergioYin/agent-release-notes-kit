# Changelog

## 0.4.0 - 2026-05-11

- Added zero-dependency `github-body` command for deterministic GitHub release body Markdown from `release-summary.json`.
- Added optional `artifacts` and `upgrade_notes` rendering for concise release draft sections.
- Added GitHub body examples, CLI/unit tests, and selfcheck coverage for repeated deterministic output.
- Updated README release workflow documentation for GitHub release draft generation.

## 0.3.0 - 2026-05-11

- Added `compare` command for deterministic Markdown and JSON summaries from two local `release-summary.json` files.
- Added cross-asset example release-summary fixtures for prompt, dataset, model-card, tokenizer, and token-ledger style assets.
- Added comparison tests and selfcheck coverage for repeated deterministic comparison output.
- Updated release workflow documentation for previous-release comparisons.

## 0.2.0 - 2026-05-11

- Added `collect` command for deterministic release input JSON from local git state.
- Added semantic next-tag suggestions, conventional commit changelog skeletons, and skipped check skeletons.
- Added `generate --inputs` support for collected JSON containing `changelog` and `checks` sections.
- Updated selfcheck and tests to exercise the collect-to-generate workflow.

## 0.1.0 - 2026-05-11

- Added zero-dependency `release_notes_kit` Python package.
- Added `generate`, `checkpoint`, and `selfcheck` CLI commands.
- Added deterministic Markdown and JSON rendering from local git metadata and optional JSON inputs.
- Added unit tests and a `scripts/selfcheck.py` wrapper.
