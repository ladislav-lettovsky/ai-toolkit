import click
import os

PROJECTS_ROOT = os.path.expanduser("~/projects/ai")


@click.command()
def list():
    """List AI projects"""
    projects = os.listdir(PROJECTS_ROOT)

    click.echo("📁 AI Projects:")
    for p in projects:
        click.echo(f" - {p}")
