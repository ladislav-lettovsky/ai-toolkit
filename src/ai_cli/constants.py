"""Shared constants for the AI CLI toolkit."""

from pathlib import Path

PROJECTS_ROOT: Path = Path("~/projects/ai").expanduser()

TEMPLATES_DIR: Path = Path(__file__).resolve().parent / "templates"
