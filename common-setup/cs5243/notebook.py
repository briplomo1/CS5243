"""Notebook structural inspection helpers; never executes student code."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_notebook(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        notebook = json.load(handle)
    if notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
        raise ValueError("Expected a version 4 Jupyter notebook")
    return notebook


def markdown_headings(notebook: dict[str, Any]) -> list[str]:
    headings: list[str] = []
    for cell in notebook["cells"]:
        if cell.get("cell_type") == "markdown":
            for line in "".join(cell.get("source", [])).splitlines():
                match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
                if match:
                    headings.append(match.group(1))
    return headings


def is_executed(notebook: dict[str, Any]) -> bool:
    code_cells = [cell for cell in notebook["cells"] if cell.get("cell_type") == "code" and "".join(cell.get("source", [])).strip()]
    return bool(code_cells) and all(cell.get("execution_count") is not None for cell in code_cells)


def student_information(notebook: dict[str, Any]) -> dict[str, str]:
    """Extract ``- Key: value`` fields from the Student Information section."""
    fields: dict[str, str] = {}
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "markdown":
            continue
        source = "".join(cell.get("source", []))
        if "Student Information" not in source:
            continue
        for line in source.splitlines():
            match = re.match(r"\s*[-*]\s*([^:]+):\s*(.*?)\s*$", line)
            if match:
                key = re.sub(r"[^a-z0-9]+", "", match.group(1).lower())
                fields[key] = match.group(2).strip().strip("*_")
        break
    return fields
