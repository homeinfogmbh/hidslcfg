"""Configures a WireGuard interface."""

from argparse import Namespace
from contextlib import suppress
from ipaddress import IPv6Address
from typing import Iterator

from wgtools import keypair     # pylint: disable=E0401

from hidslcfg.api import Client
from hidslcfg.common import LOGGER, SYSTEMD_NETWORKD, SYSTEMD_NETWORK_DIR
from hidslcfg.configure import configure as configure_system
from hidslcfg.exceptions import ProgramError
from hidslcfg.openvpn import disable as disable_openvpn
from hidslcfg.system import chown
from hidslcfg.system import systemctl
from hidslcfg.system import CalledProcessErrorHandler
from hidslcfg.system import SystemdUnit


__all__ = ['SERVER', 'configure', 'load', 'remove']


DEVNAME = 'terminals'
DESCRIPTION = 'Terminal maintenance VPN.'
NETDEV_UNIT_FILE = SYSTEMD_NETWORK_DIR.joinpath(f'{DEVNAME}.netdev')
NETWORK_UNIT_FILE = SYSTEMD_NETWORK_DIR.joinpath(f'{DEVNAME}.network')
NETDEV_OWNER = 'root'
NETDEV_GROUP = 'systemd-network'
NETDEV_MODE = 0o640
SERVER = IPv6Address('fd56:1dda:8794:cb90:ffff:ffff:ffff:fffe')


def create_netdev_unit(wireguard: dict, private: str) -> Iterator[SystemdUnit]:
    """Creates a network device."""

    unit = SystemdUnit()
    unit.add_section('NetDev')
    unit['NetDev']['Name'] = DEVNAME
    unit['NetDev']['Kind'] = 'wireguard'
    unit['NetDev']['Description'] = DESCRIPTION
    unit.add_section('WireGuard')
    unit['WireGuard']['PrivateKey'] = private
    yield unit

    for peer in wireguard.get('peers', []):
        unit = SystemdUnit()
        unit.add_section('WireGuardPeer')
        unit['WireGuardPeer']['PublicKey'] = peer['pubkey']

        if psk := peer.get('psk'):
            unit['WireGuardPeer']['PresharedKey'] = psk

        allowed_ips = [route['destination'] for route in peer['routes']]
        unit['WireGuardPeer']['AllowedIPs'] = ', '.join(allowed_ips)
        unit['WireGuardPeer']['Endpoint'] = peer['endpoint']

        if keepalive := peer.get('persistent_keepalive'):
            unit['WireGuardPeer']['PersistentKeepalive'] = str(keepalive)

        yield unit


def write_netdev(wireguard: dict, private: str):
    """Creates a network device."""

    with NETDEV_UNIT_FILE.open('w', encoding='utf-8') as netdev_unit_file:
        for part in create_netdev_unit(wireguard, private):
            part.write(netdev_unit_file)

    chown(NETDEV_UNIT_FILE, NETDEV_OWNER, NETDEV_GROUP)
    NETDEV_UNIT_FILE.chmod(NETDEV_MODE)


def create_network_unit(wireguard: dict) -> Iterator[SystemdUnit]:
    """Yields WireGuard network unit file parts."""

    unit = SystemdUnit()
    unit.add_section('Match')
    unit['Match']['Name'] = DEVNAME
    unit.add_section('Network')

    try:
        unit['Network']['Address'] = wireguard['ipaddress']
    except KeyError:
        raise ProgramError('Missing IP address for WireGuard.') from None

    yield unit

    for peer in wireguard.get('peers', []):
        for route in peer.get('routes', []):
            unit = SystemdUnit()
            unit.add_section('Route')
            unit['Route']['Gateway'] = route['gateway']
            unit['Route']['Destination'] = route['destination']

            if route.get('gateway_onlink'):
                unit['Route']['GatewayOnlink'] = 'true'

            yield unit


def write_network(wireguard: dict):
    """Creates a WireGuard network unit file."""

    with NETWORK_UNIT_FILE.open('w', encoding='utf-8') as network_unit_file:
        for part in create_network_unit(wireguard):
            part.write(network_unit_file)


def write_units(wireguard: dict, private: str) -> None:
    """Writes the WireGuard systemd units."""

    if pubkey := wireguard.get('pubkey'):
        LOGGER.warning('WireGuard already configured for pubkey %s.', pubkey)

    LOGGER.debug('Installing WireGuard configuration.')
    write_netdev(wireguard, private)
    write_network(wireguard)


def load():
    """Establishes the connection to the WireGuard server."""

    LOGGER.debug('Restarting %s.', SYSTEMD_NETWORKD)

    with CalledProcessErrorHandler(f'Restart of {SYSTEMD_NETWORKD} failed.'):
        systemctl('restart', SYSTEMD_NETWORKD)


def configure(system: dict, private: str) -> None:
    """Configures the system for WireGuard."""

    configure_system(system['id'], SERVER)
    write_units(system['wireguard'], private)
    LOGGER.debug('Disabling OpenVPN.')
    disable_openvpn()
    load()


def remove():
    """Removes the WireGuard configuration."""

    LOGGER.debug('Removing netdev unit file.')

    with suppress(FileNotFoundError):
        NETDEV_UNIT_FILE.unlink()

    LOGGER.debug('Removing network unit file.')

    with suppress(FileNotFoundError):
        NETWORK_UNIT_FILE.unlink()


def setup(client: Client, args: Namespace) -> bool:
    """Set up a system with WireGuard."""

    LOGGER.debug('Creating public / private key pair.')
    pubkey, private = keypair()

    if args.id is None:
        LOGGER.info('Creating new WireGuard system.')
        system = client.add_system(
            pubkey=pubkey, os=args.operating_system, model=args.model,
            sn=args.serial_number)
    elif args.force:
        LOGGER.info('Changing existing WireGuard system #%i.', args.id)
        system = client.patch_system(
            system=args.id, pubkey=pubkey, os=args.operating_system,
            model=args.model, sn=args.serial_number)
    else:
        LOGGER.error('Refusing to change existing system without --force.')
        return False

    configure(system, private)
    return True
