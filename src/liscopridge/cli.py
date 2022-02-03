import click

from .app import reddit
from .app import statshunters


@click.group()
def main():
    pass


main.add_command(reddit.cli, name='reddit')
main.add_command(statshunters.cli, name='statshunters')


if __name__ == "__main__":
    main()
