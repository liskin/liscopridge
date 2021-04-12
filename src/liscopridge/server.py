import logging

import click

from .app.root import app


def setup_logging(verbose: int) -> None:
    level = (
        logging.DEBUG if verbose >= 2 else
        logging.INFO if verbose >= 1 else
        logging.WARNING
    )
    logging.basicConfig(level=level)


@click.command()
@click.option('-v', '--verbose', count=True, help='Logging verbosity')
@click.option('-d', '--debug', is_flag=True, help='Bottle debug mode')
@click.option('-p', '--port', help='HTTP server port', default=12345, show_default=True)
@click.option('--host', help='HTTP server host', default="127.0.0.1", show_default=True)
def main(host, port, verbose, debug):
    """liskin's collection of protocol bridges"""
    setup_logging(verbose)
    app.run(server='waitress', host=host, port=port, debug=debug)
