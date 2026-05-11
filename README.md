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
python -m release_notes_kit generate --date 2026-05-11 --tag v0.2.0 --inputs release-inputs.json
python -m release_notes_kit checkpoint --date 2026-05-11 --tag-candidate v0.2.0 --checks release-inputs.json
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
