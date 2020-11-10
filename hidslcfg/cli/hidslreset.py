"""HOMEINFO Digital Signage Linux resetter."""

from argparse import ArgumentParser, Namespace

from hidslcfg.common import init_root_script
from hidslcfg.exceptions import ProgramError
from hidslcfg.reset import reset
from hidslcfg.system import ProgramErrorHandler


__all__ = ['run']


DESCRIPTION = 'HOMEINFO Digital Signage Linux resetter.'


def get_args() -> Namespace:
    """Parses the arguments."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='be gassy')
    return parser.parse_args()


def main():
    """Runs the HIDSL reset."""

    init_root_script(get_args)

    try:
        reset()
    except KeyboardInterrupt:
        print()
        raise ProgramError('Reset aborted by user.') from None


def run():
    """Runs main() with error handling."""

    with ProgramErrorHandler():
        main()
