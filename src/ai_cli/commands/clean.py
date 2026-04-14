import click

from ai_cli.constants import PROJECTS_ROOT
from ai_cli.utils import load_json


@click.command()
@click.argument("name")
@click.option(
    "--notes",
    is_flag=True,
    help="Also delete files inside the notes folder.",
)
def clean(name: str, notes: bool) -> None:
    """Clean project state files"""
    project_path = PROJECTS_ROOT / name

    if not project_path.is_dir():
        raise click.ClickException(f"Project not found: {project_path}")

    # Detect project type from metadata
    metadata_file = project_path / ".ai-project.json"
    metadata = load_json(metadata_file)
    if isinstance(metadata, dict) and metadata.get("project_type") == "rag":
        project_type = "rag"
    else:
        project_type = "agent"

    removed: list[str] = []

    # --- Agent state files ---
    memory_file = project_path / "data" / "memory.json"
    runs_file = project_path / "data" / "runs.jsonl"
    notes_dir = project_path / "notes"

    if memory_file.exists():
        memory_file.unlink()
        removed.append(str(memory_file))

    if runs_file.exists():
        runs_file.unlink()
        removed.append(str(runs_file))

    if notes and notes_dir.exists():
        for path in notes_dir.iterdir():
            if path.is_file():
                path.unlink()
                removed.append(str(path))

    # --- RAG state files ---
    if project_type == "rag":
        index_file = project_path / "data" / "index" / "chunks.json"
        if index_file.exists():
            index_file.unlink()
            removed.append(str(index_file))

    click.echo(f"🧹 Cleaned project: {name}")
    if removed:
        for item in removed:
            click.echo(f"  removed: {item}")
    else:
        click.echo("  nothing to remove")
