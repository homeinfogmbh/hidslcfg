"""Migrate von OpenVPN to WireGuard."""

from argparse import ArgumentParser

from hidslcfg.api import Client
from hidslcfg.common import LOGGER, init_root_script
from hidslcfg.system import ProgramErrorHandler
from hidslcfg.termio import read_credentials
from hidslcfg.wgmigrate import migrate


__all__ = ['run']


PARSER = ArgumentParser(description=__doc__)
PARSER.add_argument('-u', '--user', metavar='user', help='user name')
PARSER.add_argument(
    '-g', '--grace-time', type=int, default=10, metavar='secs',
    help='seconds to wait for contacting the VPN servers')
PARSER.add_argument('-v', '--verbose', action='store_true', help='be gassy')


def main():
    """Runs the HIDSL configurations."""

    args = init_root_script(PARSER.parse_args)

    with Client() as client:
        client.login(*read_credentials(args.user))

        if migrate(client, gracetime=args.grace_time):
            LOGGER.info('System migrated to WireGuard.')
        else:
            LOGGER.error('Could not migrate system to WireGuard.')


def run():
    """Runs main() with error handling."""

    with ProgramErrorHandler():
        main()
