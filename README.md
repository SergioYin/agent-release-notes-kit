# agent-release-notes-kit

Deterministic release-note and checkpoint generator for small AI-agent asset repos.

`agent-release-notes-kit` is a zero-dependency Python 3.9+ CLI for turning local
git metadata, changelog JSON, and verification-result JSON into auditable
Markdown and JSON release artifacts. It never calls the network and only uses
the Python standard library at runtime.

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
checkpoint twice, and fails if the output is not byte-for-byte deterministic.

## Development

```sh
python -m unittest discover -s tests -v
python scripts/selfcheck.py
git diff --check
```

This project intentionally has no `.github/workflows` directory and no external
runtime dependencies.
