"""Configure system for WireGuard."""

from argparse import Namespace
from typing import Iterator

from wgtools import keypair     # pylint: disable=E0401

from hidslcfg.api import Client
from hidslcfg.common import LOGGER
from hidslcfg.configure import configure
from hidslcfg.exceptions import ProgramError
from hidslcfg.system import chown
from hidslcfg.system import SystemdUnit

from hidslcfg.wireguard.common import DEVNAME
from hidslcfg.wireguard.common import DESCRIPTION
from hidslcfg.wireguard.common import NETDEV_UNIT_FILE
from hidslcfg.wireguard.common import NETWORK_UNIT_FILE
from hidslcfg.wireguard.common import NETDEV_OWNER
from hidslcfg.wireguard.common import NETDEV_GROUP
from hidslcfg.wireguard.common import NETDEV_MODE
from hidslcfg.wireguard.common import SERVER
from hidslcfg.wireguard.common import load


__all__ = ['patch', 'setup']


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


def write_netdev(wireguard: dict, private: str) -> None:
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


def write_network(wireguard: dict) -> None:
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


def configure_(system: dict, private: str) -> None:
    """Configures the system for WireGuard."""

    configure(system['id'], SERVER)
    write_units(system['wireguard'], private)
    LOGGER.debug('Disabling OpenVPN.')
    load()


def create(client: Client, **json) -> None:
    """Creates a new WireGuard system."""

    LOGGER.debug('Creating public / private key pair.')
    pubkey, private = keypair()
    LOGGER.info('Creating new WireGuard system.')
    system = client.add_system(**json, pubkey=pubkey)
    configure_(system, private)


def patch(client: Client, system: int, **json) -> None:
    """Patches an existing WireGuard system."""

    LOGGER.debug('Creating public / private key pair.')
    pubkey, private = keypair()
    LOGGER.info('Changing existing WireGuard system #%i.', system)
    system = client.patch_system(**json, system=system, pubkey=pubkey)
    configure_(system, private)


def setup(client: Client, args: Namespace) -> None:
    """Set up a system with WireGuard."""

    if args.id is None:
        return create(client, os=args.operating_system, model=args.model,
                      sn=args.serial_number, group=args.group)

    if args.force:
        return patch(client, args.id, os=args.operating_system,
                     model=args.model, sn=args.serial_number)

    raise ProgramError('Refusing to change existing system without --force.')
