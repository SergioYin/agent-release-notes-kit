"""Compare local release summary JSON files."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .errors import InputError


def compare_release_summaries(previous_path: str, current_path: str) -> Dict[str, object]:
    previous = _load_summary(previous_path, "previous")
    current = _load_summary(current_path, "current")
    previous_changes = _changes(previous)
    current_changes = _changes(current)
    previous_checks = _checks(previous)
    current_checks = _checks(current)
    previous_commits = _commits(previous)
    current_commits = _commits(current)

    return {
        "previous": _release_identity(previous, previous_path),
        "current": _release_identity(current, current_path),
        "changes": {
            "previous_total": len(previous_changes),
            "current_total": len(current_changes),
            "delta": len(current_changes) - len(previous_changes),
            "previous_by_type": _counter_dict(change["type"] for change in previous_changes),
            "current_by_type": _counter_dict(change["type"] for change in current_changes),
            "added": _change_delta(previous_changes, current_changes),
            "removed": _change_delta(current_changes, previous_changes),
        },
        "checks": {
            "previous_total": len(previous_checks),
            "current_total": len(current_checks),
            "previous_by_status": _counter_dict(check["status"] for check in previous_checks),
            "current_by_status": _counter_dict(check["status"] for check in current_checks),
            "added": _check_delta(previous_checks, current_checks),
            "removed": _check_delta(current_checks, previous_checks),
            "status_changed": _check_status_changes(previous_checks, current_checks),
        },
        "commits": {
            "previous_total": len(previous_commits),
            "current_total": len(current_commits),
            "new": _commit_delta(previous_commits, current_commits),
            "dropped": _commit_delta(current_commits, previous_commits),
        },
    }


def render_comparison_markdown(comparison: Dict[str, object]) -> str:
    previous = comparison["previous"]
    current = comparison["current"]
    changes = comparison["changes"]
    checks = comparison["checks"]
    commits = comparison["commits"]
    lines = [
        "# Release Comparison",
        "",
        f"- Previous: `{previous['version']}` ({previous['date']}, `{previous['short_head']}`)",
        f"- Current: `{current['version']}` ({current['date']}, `{current['short_head']}`)",
        f"- Previous summary: `{previous['path']}`",
        f"- Current summary: `{current['path']}`",
        "",
        "## Change Summary",
        "",
        f"- Previous changes: `{changes['previous_total']}`",
        f"- Current changes: `{changes['current_total']}`",
        f"- Delta: `{_signed(changes['delta'])}`",
        "",
        "### Current Changes by Type",
        "",
    ]
    lines.extend(_mapping_lines(changes["current_by_type"]))
    lines.extend(["", "### Added Since Previous", ""])
    lines.extend(_change_lines(changes["added"]))
    lines.extend(["", "### Removed Since Previous", ""])
    lines.extend(_change_lines(changes["removed"]))
    lines.extend(["", "## Verification Summary", ""])
    lines.extend(
        [
            f"- Previous checks: `{checks['previous_total']}`",
            f"- Current checks: `{checks['current_total']}`",
            "",
            "### Current Checks by Status",
            "",
        ]
    )
    lines.extend(_mapping_lines(checks["current_by_status"]))
    lines.extend(["", "### Check Status Changes", ""])
    lines.extend(_status_change_lines(checks["status_changed"]))
    lines.extend(["", "## Commit Summary", ""])
    lines.extend(
        [
            f"- Previous commits listed: `{commits['previous_total']}`",
            f"- Current commits listed: `{commits['current_total']}`",
            "",
            "### New Commits",
            "",
        ]
    )
    lines.extend(_commit_lines(commits["new"]))
    lines.append("")
    return "\n".join(lines)


def render_comparison_json(comparison: Dict[str, object]) -> str:
    return json.dumps(comparison, indent=2, sort_keys=True) + "\n"


def _load_summary(path: str, label: str) -> Dict[str, Any]:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"Unable to read {label} release summary {path!r}: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"Malformed JSON in {label} release summary {path!r}: line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise InputError(f"{label.capitalize()} release summary must be an object.")
    _required_string(data, "version", label)
    _required_string(data, "date", label)
    if not isinstance(data.get("repo"), dict):
        raise InputError(f"{label.capitalize()} release summary field 'repo' must be an object.")
    return data


def _release_identity(summary: Dict[str, Any], path: str) -> Dict[str, object]:
    repo = summary["repo"]
    return {
        "path": path,
        "version": _required_string(summary, "version", "release"),
        "date": _required_string(summary, "date", "release"),
        "tag": summary.get("tag"),
        "head": _optional_string(repo, "head") or "unknown",
        "short_head": _optional_string(repo, "short_head") or _shorten(_optional_string(repo, "head")),
        "branch": _optional_string(repo, "branch") or "unknown",
        "dirty": bool(repo.get("dirty", False)),
    }


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
    return sorted(changes, key=lambda item: (item["type"], item["description"]))


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
                "detail": detail.strip() if isinstance(detail, str) and detail.strip() else None,
            }
        )
    return sorted(checks, key=lambda item: (item["command"], item["status"], item["detail"] or ""))


def _commits(summary: Dict[str, Any]) -> List[Dict[str, str]]:
    raw_commits = summary.get("commits", [])
    if not isinstance(raw_commits, list):
        raise InputError("Release summary field 'commits' must be a list.")
    commits = []
    for index, item in enumerate(raw_commits):
        if not isinstance(item, dict):
            raise InputError(f"Release summary commit {index} must be an object.")
        full_hash = _required_string(item, "hash", f"commit {index}")
        commits.append(
            {
                "hash": full_hash,
                "short_hash": _optional_string(item, "short_hash") or _shorten(full_hash),
                "author": _optional_string(item, "author") or "unknown",
                "date": _optional_string(item, "date") or "unknown",
                "subject": _optional_string(item, "subject") or "",
            }
        )
    return sorted(commits, key=lambda item: (item["date"], item["hash"], item["subject"]))


def _change_delta(left: List[Dict[str, str]], right: List[Dict[str, str]]) -> List[Dict[str, str]]:
    left_keys = {(_normalize(item["type"]), _normalize(item["description"])) for item in left}
    return [item for item in right if (_normalize(item["type"]), _normalize(item["description"])) not in left_keys]


def _check_delta(left: List[Dict[str, Optional[str]]], right: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
    left_commands = {_normalize(item["command"]) for item in left}
    return [item for item in right if _normalize(item["command"]) not in left_commands]


def _check_status_changes(left: List[Dict[str, Optional[str]]], right: List[Dict[str, Optional[str]]]) -> List[Dict[str, str]]:
    left_by_command = {_normalize(item["command"]): item for item in left}
    changes = []
    for item in right:
        previous = left_by_command.get(_normalize(item["command"]))
        if previous and previous["status"] != item["status"]:
            changes.append(
                {
                    "command": item["command"] or "",
                    "previous_status": previous["status"] or "",
                    "current_status": item["status"] or "",
                }
            )
    return sorted(changes, key=lambda item: item["command"])


def _commit_delta(left: List[Dict[str, str]], right: List[Dict[str, str]]) -> List[Dict[str, str]]:
    left_hashes = {item["hash"] for item in left}
    return [item for item in right if item["hash"] not in left_hashes]


def _counter_dict(values: Iterable[str]) -> Dict[str, int]:
    counter = Counter(values)
    return {key: counter[key] for key in sorted(counter)}


def _mapping_lines(mapping: Dict[str, int]) -> List[str]:
    if not mapping:
        return ["- None."]
    return [f"- {key}: `{mapping[key]}`" for key in sorted(mapping)]


def _change_lines(changes: List[Dict[str, str]]) -> List[str]:
    if not changes:
        return ["- None."]
    return [f"- `{item['type']}` {item['description']}" for item in changes]


def _status_change_lines(changes: List[Dict[str, str]]) -> List[str]:
    if not changes:
        return ["- None."]
    return [f"- `{item['command']}`: `{item['previous_status']}` -> `{item['current_status']}`" for item in changes]


def _commit_lines(commits: List[Dict[str, str]]) -> List[str]:
    if not commits:
        return ["- None."]
    return [f"- `{item['short_hash']}` {item['date']} {item['subject']} ({item['author']})" for item in commits]


def _required_string(mapping: Dict[str, Any], key: str, label: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{label.capitalize()} field {key!r} must be a non-empty string.")
    return value.strip()


def _optional_string(mapping: Dict[str, Any], key: str) -> Optional[str]:
    value = mapping.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise InputError(f"Field {key!r} must be a string when provided.")
    value = value.strip()
    return value or None


def _shorten(value: Optional[str]) -> str:
    return value[:12] if value else "unknown"


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def _signed(value: int) -> str:
    if value > 0:
        return f"+{value}"
    return str(value)
