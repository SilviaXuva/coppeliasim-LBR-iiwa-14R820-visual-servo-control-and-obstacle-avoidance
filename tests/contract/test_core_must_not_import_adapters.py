from __future__ import annotations

import re
from pathlib import Path


FORBIDDEN_IMPORT_PATTERNS = (
    re.compile(r"^\s*from\s+manipulator_framework\.adapters(?:\.|\s|$)"),
    re.compile(r"^\s*import\s+manipulator_framework\.adapters(?:\.|\s|$)"),
    re.compile(r"^\s*from\s+\.+adapters(?:\.|\s|$)"),
    re.compile(r"^\s*import\s+\.+adapters(?:\.|\s|$)"),
)


def test_core_has_no_adapter_imports() -> None:
    core_path = Path("src/manipulator_framework/core")

    for py_file in core_path.rglob("*.py"):
        for line in py_file.read_text(encoding="utf-8").splitlines():
            for pattern in FORBIDDEN_IMPORT_PATTERNS:
                assert pattern.search(line) is None, (
                    f"{py_file} contains forbidden adapters import: {line.strip()}"
                )

