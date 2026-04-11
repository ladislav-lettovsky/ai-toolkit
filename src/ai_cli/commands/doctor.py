import json
from pathlib import Path

import click
from dotenv import dotenv_values

PROJECTS_ROOT = Path("~/projects/ai").expanduser()


@click.command()
@click.argument("name")
def doctor(name: str) -> None:
    """Run health checks for an AI project"""
    project_path = PROJECTS_ROOT / name

    if not project_path.is_dir():
        raise click.ClickException(f"Project not found: {project_path}")

    checks: list[tuple[str, bool, str]] = []

    config_file = project_path / "config.json"
    env_example_file = project_path / ".env.example"
    env_file = project_path / ".env"
    pyproject_file = project_path / "pyproject.toml"
    runner_file = project_path / "scripts" / "run.py"
    tests_dir = project_path / "tests"
    venv_dir = project_path / ".venv"

    checks.append(("config.json exists", config_file.exists(), str(config_file)))
    checks.append((".env.example exists", env_example_file.exists(), str(env_example_file)))
    checks.append((".env exists", env_file.exists(), str(env_file)))
    checks.append(("pyproject.toml exists", pyproject_file.exists(), str(pyproject_file)))
    checks.append(("scripts/run.py exists", runner_file.exists(), str(runner_file)))
    checks.append(("tests/ exists", tests_dir.exists(), str(tests_dir)))
    checks.append((".venv exists", venv_dir.exists(), str(venv_dir)))

    config_ok = False
    config_msg = str(config_file)
    if config_file.exists():
        try:
            data = json.loads(config_file.read_text(encoding="utf-8"))
            config_ok = isinstance(data, dict)
            if not config_ok:
                config_msg = "config.json parsed but is not a JSON object"
        except json.JSONDecodeError as exc:
            config_msg = f"invalid JSON: {exc}"
    checks.append(("config.json parses", config_ok, config_msg))

    env_key_ok = False
    env_key_msg = "OPENAI_API_KEY missing"
    if env_file.exists():
        env_values = dotenv_values(env_file)
        key = env_values.get("OPENAI_API_KEY")
        if key:
            env_key_ok = True
            env_key_msg = "OPENAI_API_KEY present"
    checks.append(("OPENAI_API_KEY configured", env_key_ok, env_key_msg))

    click.echo(f"🩺 Doctor report for: {name}")
    click.echo(f"Path: {project_path}")
    click.echo("")

    passed = 0
    failed = 0

    for label, ok, detail in checks:
        status = "OK" if ok else "FAIL"
        click.echo(f"[{status}] {label} -> {detail}")
        if ok:
            passed += 1
        else:
            failed += 1

    click.echo("")
    click.echo(f"Summary: {passed} passed, {failed} failed")

    if failed:
        raise click.ClickException("Doctor found one or more issues.")
