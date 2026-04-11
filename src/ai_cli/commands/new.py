import os

import click

from ai_cli.generators.agent_generator import create_agent
from ai_cli.generators.rag_generator import create_rag_project


PROJECTS_ROOT = os.path.expanduser("~/projects/ai")


@click.group()
def new() -> None:
    """Create a new project from a template"""
    pass


@new.command("agent")
@click.argument("name")
def new_agent(name: str) -> None:
    """Create a new agent project"""
    create_agent(name, PROJECTS_ROOT)


@new.command("rag")
@click.argument("name")
def new_rag(name: str) -> None:
    """Create a new RAG project"""
    create_rag_project(name, PROJECTS_ROOT)
