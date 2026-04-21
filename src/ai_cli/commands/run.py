import subprocess

import click

from ai_cli.constants import PROJECTS_ROOT


@click.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.argument("name")
@click.pass_context
def run(ctx: click.Context, name: str) -> None:
    """Run an AI project"""
    project_path = PROJECTS_ROOT / name

    if not project_path.is_dir():
        raise click.ClickException(f"Project not found: {project_path}")

    runner = project_path / "scripts" / "run.py"
    if not runner.is_file():
        raise click.ClickException(f"Run script not found: {runner}")

    extra_args = ctx.args

    click.echo(f"▶ Running project: {name}")
    subprocess.run(
        ["uv", "run", "--active", "python", "scripts/run.py", *extra_args],
        cwd=project_path,
        check=True,
    )
