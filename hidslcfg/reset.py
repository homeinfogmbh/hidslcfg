"""Reset operations."""

from argparse import ArgumentParser, Namespace
from functools import partial
from logging import DEBUG, INFO, basicConfig
from os import geteuid
from subprocess import CalledProcessError
from typing import Callable, NamedTuple

from hidslcfg.exceptions import ProgramError
from hidslcfg.globals import APPLICATION_SERVICE
from hidslcfg.globals import DIGSIG_DATA_DIR
from hidslcfg.globals import LOG_FORMAT
from hidslcfg.globals import UNCONFIGURED_WARNING_SERVICE
from hidslcfg.openvpn import DEFAULT_SERVICE, clean
from hidslcfg.system import systemctl, hostname, rmsubtree, ProgramErrorHandler
from hidslcfg.wireguard import remove


__all__ = ['run']


DESCRIPTION = 'HOMEINFO Digital Signage Linux resetter.'


class ResetOperation(NamedTuple):
    """A reset operation."""

    description: str
    function: Callable


# Oder matters here!
RESET_OPERATIONS = (
    ResetOperation('reset hostname', partial(hostname, None)),
    ResetOperation(
        'remove digital signage data',
        partial(rmsubtree, DIGSIG_DATA_DIR)
    ),
    ResetOperation(
        'disable OpenVPN service',
        partial(systemctl, 'disable', DEFAULT_SERVICE)
    ),
    ResetOperation('Removing OpenVPN configuration', clean),
    ResetOperation('remove WireGuard configuration', remove),
    ResetOperation(
        'disable application',
        partial(systemctl, 'disable', APPLICATION_SERVICE)
    ),
    ResetOperation(
        'disable application',
        partial(systemctl, 'enable', UNCONFIGURED_WARNING_SERVICE)
    )
)


def reset():
    """Resets the system's configuration."""

    for description, function in RESET_OPERATIONS:
        try:
            function()
        except CalledProcessError:
            raise ProgramError(f'Could not {description}.')


def get_args() -> Namespace:
    """Parses the arguments."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='be gassy')
    return parser.parse_args()


def main():
    """Runs the HIDSL reset."""

    if geteuid() != 0:
        raise ProgramError('You need to be root to run this script!')

    args = get_args()
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)

    try:
        reset()
    except KeyboardInterrupt:
        print()
        raise ProgramError('Reset aborted by user.')


def run():
    """Runs main() with error handling."""

    with ProgramErrorHandler():
        main()
