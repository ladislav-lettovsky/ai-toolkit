import click


TEMPLATES = {
    "agent": "Tool-using local agent with memory, logs, evals, and safe note writing",
    "rag": "Local retrieval-augmented generation project with ingestion and querying",
}


@click.command()
def templates() -> None:
    """List available project templates"""
    click.echo("Available templates:")
    for name, description in TEMPLATES.items():
        click.echo(f"- {name:<5} : {description}")
