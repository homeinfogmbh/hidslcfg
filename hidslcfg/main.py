"""HOMEINFO Digital Signage Linux configurator."""

from argparse import ArgumentParser
from logging import DEBUG, INFO, basicConfig
from os import geteuid

from hidslcfg.api import Client
from hidslcfg.configure import confirm, configure as configure_system
from hidslcfg.exceptions import ProgramError
from hidslcfg.globals import LOG_FORMAT, LOGGER
from hidslcfg.openvpn import configure as configure_openvpn
from hidslcfg.system import ProgramErrorHandler, reboot
from hidslcfg.termio import ask, read_credentials
from hidslcfg.wireguard import configure as configure_wireguard


__all__ = ['run']


DESCRIPTION = 'HOMEINFO Digital Signage Linux configurator.'


def get_args():
    """Parses the arguments."""

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('id', type=int, metavar='id', help='the system ID')
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
    return parser.parse_args()


def main():
    """Runs the HIDSL configurations."""

    if geteuid() != 0:
        raise ProgramError('You need to be root to run this script!')

    args = get_args()
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)
    user, passwd = read_credentials(args.user)

    with Client(user, passwd, args.id) as client:
        client.login()
        confirm(client.info, serial_number=args.sn, force=args.force)
        configure_system(args.id)
        configure_openvpn(client.openvpn, gracetime=args.grace_time)
        pubkey = configure_wireguard(client.wireguard)
        LOGGER.debug('Finalizing system.')
        client.finalize(sn=args.sn, wg_pubkey=pubkey)
        LOGGER.info('Setup completed successfully.')

    if ask('Do you want to reboot now?'):
        reboot()
    else:
        LOGGER.info('Okay, not rebooting.')


def run():
    """Runs main() with error handling."""

    with ProgramErrorHandler():
        main()
