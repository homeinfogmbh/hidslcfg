"""HOMEINFO Digital Signage Linux configurator."""

from argparse import ArgumentParser

from hidslcfg.api import Client
from hidslcfg.common import LOGGER, init_root_script
from hidslcfg.system import ProgramErrorHandler, reboot
from hidslcfg.termio import ask, read_credentials
from hidslcfg.wireguard import MTU, setup


__all__ = ['run']


PARSER = ArgumentParser(description=__doc__)
PARSER.add_argument('-u', '--user', metavar='user', help='user name')
PARSER.add_argument(
    '-s', '--serial-number', metavar='sn', help="the system's serial number"
)
PARSER.add_argument(
    '-g', '--grace-time', type=int, default=3, metavar='secs',
    help='seconds to wait for contacting the VPN servers'
)
PARSER.add_argument(
    '-f', '--force', action='store_true',
    help='force setup of already configured systems'
)
PARSER.add_argument(
    '-M', '--mtu', type=int, default=MTU, metavar='bytes',
    help='MTU in bytes for the WireGuard interface'
)
PARSER.add_argument('-v', '--verbose', action='store_true', help='be gassy')
PARSER.add_argument(
    '-o', '--operating-system', default='Arch Linux',
    help='the operating system to use'
)
PARSER.add_argument(
    '-G', '--group', type=int, default=1, help='the system group'
)
MODELS = PARSER.add_mutually_exclusive_group()
MODELS.add_argument('-m', '--model', help='the hardware model')
MODELS.add_argument(
    '-S', '--stardard24', action='store_true', help='MOStron TSPC 24"'
)
MODELS.add_argument(
    '-T', '--stardard32', action='store_true', help='MOStron TSPC 32"'
)
MODELS.add_argument(
    '-P', '--phoenix', action='store_true', help='MOStron TSPC Phönix'
)
MODELS.add_argument(
    '-N', '--neptun', action='store_true', help='MOStron TSPC Neptun'
)
PARSER.add_argument('id', nargs='?', type=int, help='the system ID')


def main() -> None:
    """Runs the HIDSL configurations."""

    args = init_root_script(PARSER.parse_args)

    with Client() as client:
        client.login(*read_credentials(args.user))
        setup(client, args)

    LOGGER.info('Setup completed successfully.')

    if ask('Do you want to reboot now?'):
        reboot()
    else:
        LOGGER.info('Okay, not rebooting.')


def run() -> None:
    """Runs main() with error handling."""

    with ProgramErrorHandler():
        main()
