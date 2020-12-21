"""HOMEINFO Digital Signage Linux configurator."""

from argparse import ArgumentParser, Namespace

from hidslcfg.api import Client
from hidslcfg.common import LOGGER, init_root_script
from hidslcfg.configure import confirm, configure
from hidslcfg.cpuinfo import cpuinfo
from hidslcfg.network import get_mac_addresses
from hidslcfg.system import ProgramErrorHandler, reboot
from hidslcfg.termio import ask, read_credentials
from hidslcfg.vpn import VPNSetup


__all__ = ['run']


DESCRIPTION = 'HOMEINFO Digital Signage Linux configurator.'


def get_args() -> Namespace:
    """Parses the arguments."""

    parser = ArgumentParser(description=DESCRIPTION)
    vpn = parser.add_mutually_exclusive_group(required=True)
    vpn.add_argument(
        '-O', '--openvpn', action='store_true', help='use OpenVPN as VPN')
    vpn.add_argument(
        '-W', '--wireguard', action='store_true', help='use WireGuard as VPN')
    parser.add_argument('-u', '--user', metavar='user', help='user name')
    parser.add_argument(
        '-s', '--serial-number', metavar='sn', dest='sn',
        help="the system's serial number")
    parser.add_argument(
        '-g', '--grace-time', type=int, default=3, metavar='secs',
        help='seconds to wait for contacting the VPN servers')
    parser.add_argument(
        '-f', '--force', action='store_true',
        help='force setup of already configured systems')
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='be gassy')
    parser.add_argument('id', type=int, metavar='id', help='the system ID')
    return parser.parse_args()


def main():
    """Runs the HIDSL configurations."""

    args = init_root_script(get_args)
    user, passwd = read_credentials(args.user)
    sysinfo = {
        'sn': args.sn,
        'mac_addresses': list(get_mac_addresses()),
        'cpuinfo': list(cpuinfo())
    }

    with Client(user, passwd, args.id) as client:
        client.login()
        confirm(client.info, serial_number=args.sn, force=args.force)
        configure(args.id)

        with VPNSetup(client, args.grace_time, openvpn=args.openvpn,
                      wireguard=args.wireguard) as vpn:
            sysinfo['wg_pubkey'] = vpn.wireguard_pubkey

        LOGGER.debug('Finalizing system.')
        client.finalize(sysinfo)
        LOGGER.info('Setup completed successfully.')

    if ask('Do you want to reboot now?'):
        reboot()
    else:
        LOGGER.info('Okay, not rebooting.')


def run():
    """Runs main() with error handling."""

    with ProgramErrorHandler():
        main()
