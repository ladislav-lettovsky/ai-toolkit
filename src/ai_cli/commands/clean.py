from pathlib import Path

import click

PROJECTS_ROOT = Path("~/projects/ai").expanduser()


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

    memory_file = project_path / "data" / "memory.json"
    runs_file = project_path / "data" / "runs.jsonl"
    notes_dir = project_path / "notes"

    removed = []

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

    click.echo(f"🧹 Cleaned project: {name}")
    if removed:
        for item in removed:
            click.echo(f"  removed: {item}")
    else:
        click.echo("  nothing to remove")
