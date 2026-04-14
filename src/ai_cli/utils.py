"""Shared utility functions for the AI CLI toolkit."""

from __future__ import annotations

import json
from pathlib import Path


def load_json(path: Path) -> dict | list | None:
    """Load and parse a JSON file, returning None on missing or invalid files."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
