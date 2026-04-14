import json

import click

from ai_cli.constants import PROJECTS_ROOT
from ai_cli.utils import load_json


@click.command()
@click.argument("name")
def upgrade(name: str) -> None:
    """Upgrade an AI project with safe metadata-aware fixes"""
    project_path = PROJECTS_ROOT / name

    if not project_path.is_dir():
        raise click.ClickException(f"Project not found: {project_path}")

    metadata_file = project_path / ".ai-project.json"
    config_file = project_path / "config.json"
    ingest_file = project_path / "scripts" / "ingest.py"
    notes_dir = project_path / "notes"
    gitignore_file = project_path / ".gitignore"

    config = load_json(config_file) or {}

    if metadata_file.exists():
        metadata = load_json(metadata_file) or {}
    else:
        metadata = {}

    if isinstance(metadata, dict) and metadata.get("project_type") in {"agent", "rag"}:
        project_type = metadata["project_type"]
    else:
        if ingest_file.exists():
            project_type = "rag"
        else:
            project_type = "agent"

    changes = []

    if not metadata_file.exists():
        metadata = {
            "project_type": project_type,
            "template_version": "1.0",
            "created_by": "ai-toolkit",
        }
        metadata_file.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        changes.append(f"created {metadata_file}")

    if project_type == "agent" and not notes_dir.exists():
        notes_dir.mkdir(parents=True, exist_ok=True)
        changes.append(f"created {notes_dir}")

    if not gitignore_file.exists():
        lines = [
            ".venv/",
            ".env",
            "__pycache__/",
            "*.pyc",
            "data/memory.json",
            "data/runs.jsonl",
        ]
        gitignore_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        changes.append(f"created {gitignore_file}")

    click.echo(f"⬆ Upgraded project: {name}")
    click.echo(f"  detected type: {project_type}")
    click.echo(f"  template version: {metadata.get('template_version', '<unknown>') if isinstance(metadata, dict) else '<unknown>'}")

    if changes:
        for change in changes:
            click.echo(f"  changed: {change}")
    else:
        click.echo("  no changes needed")
