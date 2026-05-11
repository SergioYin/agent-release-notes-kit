Release `0.4.0` (`v0.4.0`) from `main` at `333333333333` on `2026-05-11`.

## Highlights

- `Added` Zero-dependency github-body command for concise GitHub release Markdown
- `Documentation` README documents release-summary to GitHub body workflow
- `Tests` Selfcheck fixture now covers GitHub release body determinism

## Verification

- `passed` `python -m unittest discover -s tests -v` - fixture
- `passed` `python scripts/selfcheck.py`

## Artifacts

- `GITHUB_RELEASE_BODY.md` - GitHub release body Markdown
- `release-summary.json` - Machine-readable release summary (`sha256:0123456789abcdef`)

## Upgrade Notes

- Run `github-body` after regenerating `release-summary.json` for GitHub release drafts.
