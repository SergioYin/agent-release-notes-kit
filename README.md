# agent-release-notes-kit

Deterministic release-note and checkpoint generator for small AI-agent asset repos.

`agent-release-notes-kit` is a zero-dependency Python 3.9+ CLI for turning local
git metadata, changelog JSON, verification-result JSON, and collected local
repo state into auditable Markdown and JSON release artifacts. It never calls
the network and only uses the Python standard library at runtime.

## Install-Free Usage

Run it directly from this repository:

```sh
python -m release_notes_kit --help
```

## JSON Inputs

Example `changelog.json`:

```json
{
  "version": "0.1.0",
  "title": "agent-release-notes-kit v0.1.0",
  "changes": [
    {"type": "Added", "description": "Generate deterministic Markdown release notes"},
    {"type": "Added", "description": "Write a machine-readable JSON release summary"}
  ]
}
```

Example `checks.json`:

```json
{
  "commands": [
    {"command": "python -m unittest discover -s tests -v", "status": "passed"},
    {"command": "python scripts/selfcheck.py", "status": "passed"}
  ]
}
```

Check statuses must be `passed`, `failed`, or `skipped`.

## Collect Release Inputs

Use `collect` to create a deterministic JSON starting point from local git
state:

```sh
python -m release_notes_kit collect \
  --date 2026-05-11 \
  --output release-inputs.json
```

The collected file includes repository root, branch, head, latest tag, dirty
status, recent commits, a suggested next semantic tag, a changelog skeleton
grouped from conventional commit prefixes, and skipped verification commands.

Useful options:

```sh
python -m release_notes_kit collect \
  --date 2026-05-11 \
  --output release-inputs.json \
  --max-commits 25 \
  --suggest-bump minor \
  --checks-command "python -m compileall release_notes_kit"
```

## Generate Release Notes

```sh
python -m release_notes_kit generate \
  --date 2026-05-11 \
  --tag v0.1.0 \
  --changelog changelog.json \
  --checks checks.json \
  --output RELEASE_NOTES.md \
  --summary release-summary.json
```

The command writes:

- `RELEASE_NOTES.md`: deterministic Markdown release notes.
- `release-summary.json`: sorted, deterministic JSON summary for ledgers.

To generate directly from collected inputs:

```sh
python -m release_notes_kit generate \
  --date 2026-05-11 \
  --tag v0.2.0 \
  --inputs release-inputs.json \
  --output RELEASE_NOTES.md \
  --summary release-summary.json
```

## Write a Checkpoint

```sh
python -m release_notes_kit checkpoint \
  --date 2026-05-11 \
  --tag-candidate v0.1.0 \
  --checks checks.json \
  --output CHECKPOINT.md
```

The checkpoint captures repository path, branch, head commit, tag candidate,
working-tree status, and supplied verification results.

## Compare Release Summaries

Use `compare` when you have two local `release-summary.json` files and need a
deterministic summary of what changed between releases:

```sh
python -m release_notes_kit compare \
  --previous examples/cross-asset/previous-release-summary.json \
  --current examples/cross-asset/current-release-summary.json \
  --output RELEASE_COMPARISON.md \
  --summary release-comparison.json
```

The comparison includes release identity, change-count deltas, changes added or
removed since the previous release, verification status changes, and new commits
listed in the current summary. The `examples/cross-asset` fixtures model a mixed
asset repo with prompt, dataset, model-card, tokenizer, and token-ledger entries.

## Write a GitHub Release Body

Use `github-body` after `generate` writes `release-summary.json` to create a
concise Markdown body suitable for a GitHub release draft:

```sh
python -m release_notes_kit github-body \
  --summary release-summary.json \
  --output GITHUB_RELEASE_BODY.md
```

The body includes deterministic sections for highlights, verification,
artifacts, and upgrade notes. Existing release-summary files work as-is; when no
artifact list is supplied, the command lists `RELEASE_NOTES.md` and
`release-summary.json`. To include explicit artifacts or upgrade notes, add
optional top-level fields to the release summary:

```json
{
  "artifacts": [
    {"path": "GITHUB_RELEASE_BODY.md", "description": "GitHub release body"},
    {"path": "release-summary.json", "description": "Release ledger", "sha256": "0123456789abcdef"}
  ],
  "upgrade_notes": [
    "Run `github-body` after regenerating `release-summary.json` for release drafts."
  ]
}
```

See `examples/github-body` for a complete input and rendered output pair.

## Selfcheck

```sh
python -m release_notes_kit selfcheck
python scripts/selfcheck.py
```

The selfcheck creates a temporary git fixture, generates release notes and a
checkpoint twice, exercises collected inputs, and fails if the output is not
byte-for-byte deterministic.

## Copy-Paste Release Workflow

```sh
python -m release_notes_kit collect --date 2026-05-11 --output release-inputs.json
python -m unittest discover -s tests -v
python scripts/selfcheck.py
git diff --check
python -m release_notes_kit generate --date 2026-05-11 --tag v0.4.0 --inputs release-inputs.json
python -m release_notes_kit compare --previous previous-release-summary.json --current release-summary.json
python -m release_notes_kit github-body --summary release-summary.json --output GITHUB_RELEASE_BODY.md
python -m release_notes_kit checkpoint --date 2026-05-11 --tag-candidate v0.4.0 --checks release-inputs.json
```

After running checks, update the `checks.commands` entries in
`release-inputs.json` from `skipped` to the observed result before generating
final release artifacts.

## Development

```sh
python -m unittest discover -s tests -v
python scripts/selfcheck.py
git diff --check
```

This project intentionally has no `.github/workflows` directory and no external
runtime dependencies.
