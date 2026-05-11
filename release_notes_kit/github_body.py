"""Render GitHub release body Markdown from release-summary JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .errors import InputError


DEFAULT_ARTIFACTS = [
    {"path": "RELEASE_NOTES.md", "description": "Markdown release notes"},
    {"path": "release-summary.json", "description": "Machine-readable release summary"},
]


def load_release_summary(path: str) -> Dict[str, Any]:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"Unable to read release summary {path!r}: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"Malformed JSON in release summary {path!r}: line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise InputError("Release summary must be an object.")
    _required_string(data, "version", "release summary")
    _required_string(data, "date", "release summary")
    return data


def render_github_body_markdown(summary: Dict[str, Any]) -> str:
    version = _required_string(summary, "version", "release summary")
    date = _required_string(summary, "date", "release summary")
    tag = _optional_string(summary, "tag")
    repo = summary.get("repo") if isinstance(summary.get("repo"), dict) else {}
    branch = _optional_string(repo, "branch") or "unknown"
    short_head = _optional_string(repo, "short_head") or _shorten(_optional_string(repo, "head"))
    identity = f"Release `{version}`"
    if tag:
        identity += f" (`{tag}`)"
    identity += f" from `{branch}` at `{short_head}` on `{date}`."

    lines = [
        identity,
        "",
        "## Highlights",
        "",
    ]
    lines.extend(_highlight_lines(_changes(summary)))
    lines.extend(["", "## Verification", ""])
    lines.extend(_verification_lines(_checks(summary)))
    lines.extend(["", "## Artifacts", ""])
    lines.extend(_artifact_lines(_artifacts(summary)))
    lines.extend(["", "## Upgrade Notes", ""])
    lines.extend(_upgrade_lines(_upgrade_notes(summary), _changes(summary)))
    lines.append("")
    return "\n".join(lines)


def render_github_body_from_file(path: str) -> str:
    return render_github_body_markdown(load_release_summary(path))


def _changes(summary: Dict[str, Any]) -> List[Dict[str, str]]:
    raw_changes = summary.get("changes", [])
    if not isinstance(raw_changes, list):
        raise InputError("Release summary field 'changes' must be a list.")
    changes = []
    for index, item in enumerate(raw_changes):
        if not isinstance(item, dict):
            raise InputError(f"Release summary change {index} must be an object.")
        changes.append(
            {
                "type": _required_string(item, "type", f"change {index}"),
                "description": _required_string(item, "description", f"change {index}"),
            }
        )
    return sorted(changes, key=lambda item: (_normalize(item["type"]), _normalize(item["description"])))


def _checks(summary: Dict[str, Any]) -> List[Dict[str, Optional[str]]]:
    raw_checks = summary.get("checks", [])
    if not isinstance(raw_checks, list):
        raise InputError("Release summary field 'checks' must be a list.")
    checks: List[Dict[str, Optional[str]]] = []
    for index, item in enumerate(raw_checks):
        if not isinstance(item, dict):
            raise InputError(f"Release summary check {index} must be an object.")
        status = _required_string(item, "status", f"check {index}").lower()
        if status not in {"passed", "failed", "skipped"}:
            raise InputError(f"Release summary check {index} field 'status' must be passed, failed, or skipped.")
        detail = item.get("detail")
        if detail is not None and not isinstance(detail, str):
            raise InputError(f"Release summary check {index} field 'detail' must be a string when provided.")
        checks.append(
            {
                "command": _required_string(item, "command", f"check {index}"),
                "status": status,
                "detail": _clean(detail) if isinstance(detail, str) and detail.strip() else None,
            }
        )
    return sorted(checks, key=lambda item: (_normalize(item["command"] or ""), item["status"] or "", item["detail"] or ""))


def _artifacts(summary: Dict[str, Any]) -> List[Dict[str, Optional[str]]]:
    raw_artifacts = summary.get("artifacts", DEFAULT_ARTIFACTS)
    if not isinstance(raw_artifacts, list):
        raise InputError("Release summary field 'artifacts' must be a list when provided.")
    artifacts: List[Dict[str, Optional[str]]] = []
    for index, item in enumerate(raw_artifacts):
        if not isinstance(item, dict):
            raise InputError(f"Release summary artifact {index} must be an object.")
        artifact = {
            "path": _required_string(item, "path", f"artifact {index}"),
            "description": _optional_string(item, "description"),
            "sha256": _optional_string(item, "sha256"),
        }
        artifacts.append(artifact)
    return sorted(artifacts, key=lambda item: (_normalize(item["path"] or ""), _normalize(item["description"] or "")))


def _upgrade_notes(summary: Dict[str, Any]) -> List[str]:
    raw_notes = summary.get("upgrade_notes", [])
    if not isinstance(raw_notes, list):
        raise InputError("Release summary field 'upgrade_notes' must be a list when provided.")
    notes = []
    for index, item in enumerate(raw_notes):
        if not isinstance(item, str):
            raise InputError(f"Release summary upgrade note {index} must be a string.")
        cleaned = _clean(item)
        if cleaned:
            notes.append(cleaned)
    return sorted(notes, key=_normalize)


def _highlight_lines(changes: List[Dict[str, str]]) -> List[str]:
    if not changes:
        return ["- No highlights supplied."]
    return [f"- `{item['type']}` {_clean(item['description'])}" for item in changes]


def _verification_lines(checks: List[Dict[str, Optional[str]]]) -> List[str]:
    if not checks:
        return ["- No verification results supplied."]
    lines = []
    for check in checks:
        line = f"- `{check['status']}` `{check['command']}`"
        if check["detail"]:
            line += f" - {check['detail']}"
        lines.append(line)
    return lines


def _artifact_lines(artifacts: List[Dict[str, Optional[str]]]) -> List[str]:
    if not artifacts:
        return ["- No artifacts listed."]
    lines = []
    for artifact in artifacts:
        line = f"- `{artifact['path']}`"
        if artifact["description"]:
            line += f" - {artifact['description']}"
        if artifact["sha256"]:
            line += f" (`sha256:{artifact['sha256']}`)"
        lines.append(line)
    return lines


def _upgrade_lines(notes: List[str], changes: List[Dict[str, str]]) -> List[str]:
    if notes:
        return [f"- {note}" for note in notes]
    upgrade_change_types = {"breaking", "deprecated", "removed"}
    upgrade_changes = [
        item
        for item in changes
        if _normalize(item["type"]) in upgrade_change_types
    ]
    if upgrade_changes:
        return [
            f"- Review `{item['type']}` change: {_clean(item['description'])}"
            for item in upgrade_changes
        ]
    return ["- No upgrade notes supplied."]


def _required_string(data: Dict[str, Any], field: str, label: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{label.capitalize()} field {field!r} must be a non-empty string.")
    return _clean(value)


def _optional_string(data: Dict[str, Any], field: str) -> Optional[str]:
    value = data.get(field)
    if isinstance(value, str) and value.strip():
        return _clean(value)
    return None


def _shorten(value: Optional[str]) -> str:
    if not value:
        return "unknown"
    return value[:12]


def _clean(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize(value: str) -> str:
    return _clean(value).lower()
