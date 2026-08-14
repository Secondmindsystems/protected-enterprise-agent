from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import BoundaryViolation


def load_leak_manifest(path: Path) -> tuple[str, ...]:
    data = json.loads(path.read_text(encoding="utf-8"))
    values = tuple(str(value) for value in data["forbidden_values"] if str(value))
    if not values:
        raise ValueError("leak manifest is empty")
    return values


def find_forbidden(value: object, forbidden: Iterable[str]) -> list[str]:
    serialized = value if isinstance(value, str) else json.dumps(value, sort_keys=True, ensure_ascii=False)
    return [candidate for candidate in forbidden if candidate in serialized]


def assert_boundary_clean(surface: str, value: object, forbidden: Iterable[str]) -> None:
    matches = find_forbidden(value, forbidden)
    if matches:
        raise BoundaryViolation(f"{surface} blocked: {len(matches)} forbidden fixture value(s) present")


def scan_paths(paths: Iterable[Path], forbidden: Iterable[str]) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        matches = find_forbidden(path.read_text(encoding="utf-8", errors="replace"), forbidden)
        if matches:
            findings[str(path)] = matches
    return findings

