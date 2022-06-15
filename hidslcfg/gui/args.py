"""Argument parsing."""

from argparse import ArgumentParser, Namespace


__all__ = ['get_args']


def get_args() -> Namespace:
    """Parses the command line arguments."""

    parser = ArgumentParser(description='HIDSL installer GUI')
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='print additional debug information'
    )
    return parser.parse_args()
