"""HOMEINFO Digital Signage Linux configurator."""

from argparse import ArgumentParser

from hidslcfg.api import Client
from hidslcfg.common import LOGGER, init_root_script
from hidslcfg.system import ProgramErrorHandler, reboot
from hidslcfg.termio import ask, read_credentials


__all__ = ['run']


PARSER = ArgumentParser(description=__doc__)
PARSER.add_argument('-u', '--user', metavar='user', help='user name')
PARSER.add_argument('-s', '--serial-number', metavar='sn',
                    help="the system's serial number")
PARSER.add_argument('-g', '--grace-time', type=int, default=3, metavar='secs',
                    help='seconds to wait for contacting the VPN servers')
PARSER.add_argument('-f', '--force', action='store_true',
                    help='force setup of already configured systems')
PARSER.add_argument('-v', '--verbose', action='store_true', help='be gassy')
PARSER.add_argument('-o', '--operating-system', default='Arch Linux',
                    help='the operating system to use')
PARSER.add_argument('-m', '--model', metavar='model', help='hardware model')
PARSER.add_argument('-x', '--exclusive', action='store_true',
                    help='disable other VPN solutions')
SUBPARSERS = PARSER.add_subparsers(dest='vpn', help='VPN solutions',
                                   required=True)
OPENVPN = SUBPARSERS.add_parser('openvpn', help='use OpenVPN as VPN')
OPENVPN.add_argument('id', type=int, help='the system ID')
WIREGUARD = SUBPARSERS.add_parser('wireguard', help='use WireGuard as VPN')
WIREGUARD.add_argument('id', nargs='?', type=int, help='the system ID')
WIREGUARD.add_argument('-G', '--group', type=int, default=1,
                       help='the system group')


def main() -> None:
    """Runs the HIDSL configurations."""

    args = init_root_script(PARSER.parse_args)

    if args.vpn == 'openvpn':
        from hidslcfg.openvpn.setup import setup        # pylint: disable=C0415
        from hidslcfg.wireguard.disable import disable  # pylint: disable=C0415
    elif args.vpn == 'wireguard':
        from hidslcfg.wireguard.setup import setup      # pylint: disable=C0415
        from hidslcfg.openvpn.disable import disable    # pylint: disable=C0415

    with Client() as client:
        client.login(*read_credentials(args.user))
        setup(client, args)

    if args.exclusive:
        disable()

    LOGGER.info('Setup completed successfully.')

    if ask('Do you want to reboot now?'):
        reboot()
    else:
        LOGGER.info('Okay, not rebooting.')


def run() -> None:
    """Runs main() with error handling."""

    with ProgramErrorHandler():
        main()
