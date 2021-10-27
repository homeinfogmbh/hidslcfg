"""HOMEINFO Digital Signage Linux resetter."""

from argparse import ArgumentParser

from hidslcfg.common import init_root_script
from hidslcfg.exceptions import ProgramError
from hidslcfg.reset import reset
from hidslcfg.system import ProgramErrorHandler


__all__ = ['run']


PARSER = ArgumentParser(description=__doc__)
PARSER.add_argument('-v', '--verbose', action='store_true', help='be gassy')


def main() -> None:
    """Runs the HIDSL reset."""

    init_root_script(PARSER.parse_args)

    try:
        reset()
    except KeyboardInterrupt:
        print()
        raise ProgramError('Reset aborted by user.') from None


def run() -> None:
    """Runs main() with error handling."""

    with ProgramErrorHandler():
        main()
