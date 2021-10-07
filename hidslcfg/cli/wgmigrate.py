"""Migrate von OpenVPN to WireGuard."""

from argparse import ArgumentParser, Namespace

from hidslcfg.common import LOGGER, init_root_script
from hidslcfg.system import ProgramErrorHandler
from hidslcfg.termio import read_credentials
from hidslcfg.wgmigrate import migrate


__all__ = ['run']


DESCRIPTION = __doc__


def get_args() -> Namespace:
    """Parses the arguments."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-u', '--user', metavar='user', help='user name')
    parser.add_argument(
        '-g', '--grace-time', type=int, default=10, metavar='secs',
        help='seconds to wait for contacting the VPN servers')
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='be gassy')
    return parser.parse_args()


def main():
    """Runs the HIDSL configurations."""

    args = init_root_script(get_args)
    user, passwd = read_credentials(args.user)

    if migrate(user, passwd, gracetime=args.grace_time):
        LOGGER.info('System migrated to WireGuard.')
    else:
        LOGGER.error('Could not migrate system to WireGuard.')


def run():
    """Runs main() with error handling."""

    with ProgramErrorHandler():
        main()
