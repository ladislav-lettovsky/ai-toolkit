import click

from ai_cli.constants import PROJECTS_ROOT
from ai_cli.utils import load_json


@click.command("inspect")
@click.argument("name")
def inspect_project(name: str) -> None:
    """Inspect an AI project"""
    project_path = PROJECTS_ROOT / name

    if not project_path.is_dir():
        raise click.ClickException(f"Project not found: {project_path}")

    metadata_file = project_path / ".ai-project.json"
    config_file = project_path / "config.json"
    env_example_file = project_path / ".env.example"
    env_file = project_path / ".env"
    pyproject_file = project_path / "pyproject.toml"
    runner_file = project_path / "scripts" / "run.py"
    tests_dir = project_path / "tests"

    ingest_file = project_path / "scripts" / "ingest.py"
    docs_dir = project_path / "data" / "docs"
    index_file = project_path / "data" / "index" / "chunks.json"

    memory_file = project_path / "data" / "memory.json"
    runs_file = project_path / "data" / "runs.jsonl"
    notes_dir = project_path / "notes"

    metadata = load_json(metadata_file)
    if metadata is None:
        metadata = {}

    config = load_json(config_file)
    if config is None:
        config = {}

    if isinstance(metadata, dict) and metadata.get("project_type") in {"agent", "rag"}:
        project_type = metadata["project_type"]
    else:
        is_rag = ingest_file.exists() and index_file.parent.exists()
        project_type = "rag" if is_rag else "agent"

    click.echo(f"Project: {name}")
    click.echo(f"Path: {project_path}")
    click.echo(f"Type: {project_type}")
    click.echo("")

    click.echo("Metadata:")
    if metadata:
        for key, value in metadata.items():
            click.echo(f"  {key}: {value}")
    else:
        click.echo("  <none>")

    click.echo("")
    click.echo("Files:")
    click.echo(f"  .ai-project.json: {'yes' if metadata_file.exists() else 'no'}")
    click.echo(f"  config.json: {'yes' if config_file.exists() else 'no'}")
    click.echo(f"  .env.example: {'yes' if env_example_file.exists() else 'no'}")
    click.echo(f"  .env: {'yes' if env_file.exists() else 'no'}")
    click.echo(f"  pyproject.toml: {'yes' if pyproject_file.exists() else 'no'}")
    click.echo(f"  scripts/run.py: {'yes' if runner_file.exists() else 'no'}")
    click.echo(f"  tests/: {'yes' if tests_dir.exists() else 'no'}")

    if project_type == "rag":
        click.echo(f"  scripts/ingest.py: {'yes' if ingest_file.exists() else 'no'}")
        click.echo(f"  data/docs/: {'yes' if docs_dir.exists() else 'no'}")
        click.echo(f"  data/index/chunks.json: {'yes' if index_file.exists() else 'no'}")
    else:
        click.echo(f"  notes/: {'yes' if notes_dir.exists() else 'no'}")
        click.echo(f"  data/memory.json: {'yes' if memory_file.exists() else 'no'}")
        click.echo(f"  data/runs.jsonl: {'yes' if runs_file.exists() else 'no'}")

    click.echo("")
    click.echo("State:")

    if project_type == "rag":
        doc_count = 0
        if docs_dir.exists():
            doc_count = sum(1 for p in docs_dir.iterdir() if p.is_file())

        chunk_count = 0
        if index_file.exists():
            index_data = load_json(index_file)
            if isinstance(index_data, list):
                chunk_count = len(index_data)
            else:
                chunk_count = -1

        click.echo(f"  document files: {doc_count}")
        click.echo(f"  indexed chunks: {chunk_count}")
        click.echo(f"  top_k: {config.get('top_k', '<unset>') if isinstance(config, dict) else '<unset>'}")
    else:
        memory_count = 0
        if memory_file.exists():
            memory_data = load_json(memory_file)
            if isinstance(memory_data, list):
                memory_count = len(memory_data)
            else:
                memory_count = -1

        runs_count = 0
        if runs_file.exists():
            runs_count = sum(1 for _ in runs_file.open("r", encoding="utf-8"))

        note_count = 0
        if notes_dir.exists():
            note_count = sum(1 for p in notes_dir.iterdir() if p.is_file())

        click.echo(f"  memory entries: {memory_count}")
        click.echo(f"  run log entries: {runs_count}")
        click.echo(f"  note files: {note_count}")

    click.echo("")
    click.echo("Config:")
    if not config or not isinstance(config, dict):
        click.echo("  <none>")
    else:
        for key, value in config.items():
            click.echo(f"  {key}: {value}")
