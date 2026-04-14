import subprocess

import click

from ai_cli.constants import PROJECTS_ROOT


@click.command("eval")
@click.argument("name")
def eval_project(name: str) -> None:
    """Run tests for an AI project"""
    project_path = PROJECTS_ROOT / name

    if not project_path.is_dir():
        raise click.ClickException(f"Project not found: {project_path}")

    click.echo(f"🧪 Running evals for: {name}")
    subprocess.run(
        ["uv", "run", "--active", "python", "-m", "pytest", "tests"],
        cwd=project_path,
        check=True,
    )
