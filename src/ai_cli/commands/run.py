import os
import subprocess

import click

PROJECTS_ROOT = os.path.expanduser("~/projects/ai")


@click.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True}
)
@click.argument("name")
@click.pass_context
def run(ctx: click.Context, name: str) -> None:
    """Run an AI project"""
    project_path = os.path.join(PROJECTS_ROOT, name)

    if not os.path.isdir(project_path):
        raise click.ClickException(f"Project not found: {project_path}")

    runner = os.path.join(project_path, "scripts", "run.py")
    if not os.path.isfile(runner):
        raise click.ClickException(f"Run script not found: {runner}")

    extra_args = list(ctx.args)

    click.echo(f"▶ Running project: {name}")
    subprocess.run(
        ["uv", "run", "--active", "python", "scripts/run.py", *extra_args],
        cwd=project_path,
        check=True,
    )
