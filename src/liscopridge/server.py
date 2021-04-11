import argparse
import logging

from .app.root import app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="liskin's collection of protocol bridges",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('-v', '--verbose', action='count', help='Logging verbosity', default=0)
    parser.add_argument('-d', '--debug', dest='debug', help='Bottle debug mode', action='store_true')
    parser.add_argument('-p', '--port', dest='port', help='HTTP server port', default=12345)
    parser.add_argument('--host', dest='host', help='HTTP server host', default="127.0.0.1")

    return parser.parse_args()


def setup_logging(args: argparse.Namespace) -> None:
    level = (
        logging.DEBUG if args.verbose >= 2 else
        logging.INFO if args.verbose >= 1 else
        logging.WARNING
    )
    logging.basicConfig(level=level)


def main() -> None:
    args = parse_args()
    setup_logging(args)

    app.run(
        server='waitress',
        host=args.host,
        port=args.port,
        debug=args.debug,
    )
