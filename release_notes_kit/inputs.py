"""JSON input parsing and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .errors import InputError


@dataclass(frozen=True)
class Change:
    kind: str
    description: str


@dataclass(frozen=True)
class Changelog:
    version: Optional[str]
    title: Optional[str]
    changes: List[Change]


@dataclass(frozen=True)
class CheckResult:
    command: str
    status: str
    detail: Optional[str]


def load_changelog(path: Optional[str]) -> Changelog:
    if not path:
        return Changelog(version=None, title=None, changes=[])
    data = _load_json(path)
    if isinstance(data, dict) and "changelog" in data:
        data = data["changelog"]
    if not isinstance(data, dict):
        raise InputError("Changelog JSON must be an object.")
    version = _optional_string(data, "version")
    title = _optional_string(data, "title")
    raw_changes = data.get("changes", [])
    if not isinstance(raw_changes, list):
        raise InputError("Changelog field 'changes' must be a list.")
    changes = [_parse_change(item, index) for index, item in enumerate(raw_changes)]
    return Changelog(version=version, title=title, changes=sorted(changes, key=lambda c: (c.kind, c.description)))


def load_checks(path: Optional[str]) -> List[CheckResult]:
    if not path:
        return []
    data = _load_json(path)
    if isinstance(data, dict) and "checks" in data:
        data = data["checks"]
    if isinstance(data, dict) and "commands" in data:
        raw_items = data["commands"]
    elif isinstance(data, list):
        raw_items = data
    else:
        raise InputError("Checks JSON must be a list or an object with a 'commands' list.")
    if not isinstance(raw_items, list):
        raise InputError("Checks field 'commands' must be a list.")
    checks = [_parse_check(item, index) for index, item in enumerate(raw_items)]
    return sorted(checks, key=lambda c: (c.command, c.status, c.detail or ""))


def _load_json(path: str) -> Any:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"Unable to read JSON file {path!r}: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"Malformed JSON in {path!r}: line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc


def _parse_change(item: Any, index: int) -> Change:
    if isinstance(item, str):
        return Change(kind="Changed", description=item)
    if not isinstance(item, dict):
        raise InputError(f"Changelog item {index} must be a string or object.")
    kind = _required_string(item, "type", f"Changelog item {index}")
    description = _required_string(item, "description", f"Changelog item {index}")
    return Change(kind=kind, description=description)


def _parse_check(item: Any, index: int) -> CheckResult:
    if not isinstance(item, dict):
        raise InputError(f"Check item {index} must be an object.")
    command = _required_string(item, "command", f"Check item {index}")
    status = _required_string(item, "status", f"Check item {index}").lower()
    if status not in {"passed", "failed", "skipped"}:
        raise InputError(f"Check item {index} field 'status' must be passed, failed, or skipped.")
    detail = _optional_string_any(item, ("detail", "output", "notes"))
    return CheckResult(command=command, status=status, detail=detail)


def _required_string(mapping: Dict[str, Any], key: str, label: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{label} field {key!r} must be a non-empty string.")
    return value.strip()


def _optional_string(mapping: Dict[str, Any], key: str) -> Optional[str]:
    value = mapping.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise InputError(f"Field {key!r} must be a string when provided.")
    value = value.strip()
    return value or None


def _optional_string_any(mapping: Dict[str, Any], keys: Iterable[str]) -> Optional[str]:
    for key in keys:
        value = mapping.get(key)
        if value is None:
            continue
        if not isinstance(value, str):
            raise InputError(f"Check field {key!r} must be a string when provided.")
        value = value.strip()
        return value or None
    return None
