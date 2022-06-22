"""Configure system for WireGuard."""

from argparse import Namespace
from typing import Iterator

from wgtools import keypair

from hidslcfg.api import Client
from hidslcfg.common import LOGGER
from hidslcfg.configure import configure
from hidslcfg.exceptions import ProgramError
from hidslcfg.system import chown
from hidslcfg.system import SystemdUnit

from hidslcfg.wireguard.common import DEVNAME
from hidslcfg.wireguard.common import DESCRIPTION
from hidslcfg.wireguard.common import MTU
from hidslcfg.wireguard.common import NETDEV_UNIT_FILE
from hidslcfg.wireguard.common import NETWORK_UNIT_FILE
from hidslcfg.wireguard.common import NETDEV_OWNER
from hidslcfg.wireguard.common import NETDEV_GROUP
from hidslcfg.wireguard.common import NETDEV_MODE
from hidslcfg.wireguard.common import SERVER
from hidslcfg.wireguard.common import load


__all__ = ['create', 'patch', 'setup']


def create(client: Client, mtu: int = MTU, **json) -> int:
    """Creates a new WireGuard system."""

    LOGGER.debug('Creating public / private key pair.')
    pubkey, private = keypair()
    LOGGER.info('Creating new WireGuard system.')
    system = client.add_system(**json, pubkey=pubkey)
    LOGGER.info('New system ID: %i', system_id := system['id'])
    configure_(system, private, mtu=mtu)
    return system_id


def patch(client: Client, system_id: int, mtu: int = MTU, **json) -> int:
    """Patches an existing WireGuard system."""

    LOGGER.debug('Creating public / private key pair.')
    pubkey, private = keypair()
    LOGGER.info('Changing existing WireGuard system #%i.', system_id)
    system = client.patch_system(**json, system=system_id, pubkey=pubkey)
    configure_(system, private, mtu=mtu)
    return system_id


def setup(client: Client, args: Namespace) -> int:
    """Set up a system with WireGuard."""

    if args.id is None:
        return create(
            client, mtu=args.mtu, os=args.operating_system,
            model=get_model(args), sn=args.serial_number, group=args.group
        )

    if args.force:
        return patch(
            client, args.id, mtu=args.mtu, os=args.operating_system,
            model=get_model(args), sn=args.serial_number
        )

    raise ProgramError('Refusing to change existing system without --force.')


def get_model(args: Namespace) -> str:
    """Returns the model name as string."""

    if args.model:
        return args.model

    if args.standard24:
        return 'Standard 24"'

    if args.standard32:
        return 'Standard 32"'

    if args.phoenix:
        return 'Phönix'

    if args.neptun:
        return 'Neptun'

    raise ValueError('No model specified.')


def create_netdev_unit(
        wireguard: dict,
        private: str,
        mtu: int
) -> Iterator[SystemdUnit]:
    """Creates a network device."""

    unit = SystemdUnit()
    unit.add_section('NetDev')
    unit['NetDev']['Name'] = DEVNAME
    unit['NetDev']['Kind'] = 'wireguard'
    unit['NetDev']['Description'] = DESCRIPTION

    if mtu > 0:
        unit['NetDev']['MTUBytes'] = str(mtu)

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


def write_netdev(wireguard: dict, private: str, mtu: int = MTU) -> None:
    """Creates a network device."""

    with NETDEV_UNIT_FILE.open('w', encoding='utf-8') as netdev_unit_file:
        for part in create_netdev_unit(wireguard, private, mtu=mtu):
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


def write_units(wireguard: dict, private: str, mtu: int = MTU) -> None:
    """Writes the WireGuard systemd units."""

    if pubkey := wireguard.get('pubkey'):
        LOGGER.warning('WireGuard already configured for pubkey %s.', pubkey)

    LOGGER.debug('Installing WireGuard configuration.')
    write_netdev(wireguard, private, mtu=mtu)
    write_network(wireguard)


def configure_(system: dict, private: str, mtu: int = MTU) -> None:
    """Configures the system for WireGuard."""

    configure(system['id'], SERVER)
    write_units(system['wireguard'], private, mtu=mtu)
    LOGGER.debug('Disabling OpenVPN.')
    load()
