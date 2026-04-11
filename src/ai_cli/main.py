import click

from ai_cli.commands.clean import clean
from ai_cli.commands.doctor import doctor
from ai_cli.commands.eval import eval
from ai_cli.commands.inspect import inspect
from ai_cli.commands.list import list
from ai_cli.commands.new import new
from ai_cli.commands.run import run
from ai_cli.commands.templates import templates
from ai_cli.commands.upgrade import upgrade


@click.group()
def cli():
    """AI CLI Toolkit"""
    pass


cli.add_command(clean)
cli.add_command(doctor)
cli.add_command(eval)
cli.add_command(inspect)
cli.add_command(list)
cli.add_command(new)
cli.add_command(run)
cli.add_command(templates)
cli.add_command(upgrade)


if __name__ == "__main__":
    cli()
