import os
import subprocess

import click

PROJECTS_ROOT = os.path.expanduser("~/projects/ai")


@click.command()
@click.argument("name")
def eval(name: str) -> None:
    """Run tests for an AI project"""
    project_path = os.path.join(PROJECTS_ROOT, name)

    if not os.path.isdir(project_path):
        raise click.ClickException(f"Project not found: {project_path}")

    click.echo(f"🧪 Running evals for: {name}")
    subprocess.run(
        ["uv", "run", "--active", "python", "-m", "pytest", "tests"],
        cwd=project_path,
        check=True,
    )
