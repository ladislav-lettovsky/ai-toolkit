import click

from ai_cli.constants import PROJECTS_ROOT


@click.command("list")
def list_projects() -> None:
    """List AI projects"""
    if not PROJECTS_ROOT.is_dir():
        click.echo("No projects directory found. Run 'ai new' to create your first project.")
        return

    projects = sorted(p.name for p in PROJECTS_ROOT.iterdir() if p.is_dir())

    if not projects:
        click.echo("No projects found. Run 'ai new' to create your first project.")
        return

    click.echo("📁 AI Projects:")
    for p in projects:
        click.echo(f" - {p}")
