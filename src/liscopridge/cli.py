import click

from .app import reddit
from .app import statshunters


@click.group()
def cli():
    pass


cli.add_command(reddit.cli, name='reddit')
cli.add_command(statshunters.cli, name='statshunters')
