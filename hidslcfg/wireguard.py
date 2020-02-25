"""Configures a WireGuard interface."""

from os import chown
from pwd import getpwnam
from grp import getgrnam
from time import sleep

from wgtools import keypair

from hidslcfg.exceptions import ProgramError
from hidslcfg.globals import LOGGER
from hidslcfg.globals import SYSTEMD_NETWORKD
from hidslcfg.globals import SYSTEMD_NETWORK_DIR
from hidslcfg.system import ping
from hidslcfg.system import systemctl
from hidslcfg.system import CalledProcessErrorHandler
from hidslcfg.system import SystemdUnit


__all__ = ['configure', 'check', 'remove']


DEVNAME = 'terminals'
DESCRIPTION = 'Terminal maintenance VPN.'
NETDEV_UNIT_FILE = SYSTEMD_NETWORK_DIR.joinpath(f'{DEVNAME}.netdev')
NETWORK_UNIT_FILE = SYSTEMD_NETWORK_DIR.joinpath(f'{DEVNAME}.network')
NETDEV_OWNER = 'root'
NETDEV_GROUP = 'systemd-network'
NETDEV_MODE = 0o640


def create_netdev_unit(wireguard: dict, private: str):
    """Creates a network device."""

    unit = SystemdUnit()
    unit.add_section('NetDev')
    unit['NetDev']['Name'] = DEVNAME
    unit['NetDev']['Kind'] = 'wireguard'
    unit['NetDev']['Description'] = DESCRIPTION
    unit.add_section('WireGuard')
    unit['WireGuard']['PrivateKey'] = private
    unit.add_section('WireGuardPeer')

    try:
        unit['WireGuardPeer']['PublicKey'] = wireguard['server_pubkey']
    except KeyError:
        raise ProgramError('Missing server pubkey for WireGuard.')

    if psk := wireguard.get('psk'):
        unit['WireGuardPeer']['PresharedKey'] = psk

    try:
        allowed_ips = [route['destination'] for route in wireguard['routes']]
    except KeyError:
        raise ProgramError('Missing routes for WireGuard.')

    unit['WireGuardPeer']['AllowedIPs'] = ', '.join(allowed_ips)

    try:
        unit['WireGuardPeer']['Endpoint'] = wireguard['endpoint']
    except KeyError:
        raise ProgramError('Missing endpoint for WireGuard.')

    if keepalive := wireguard.get('persistent_keepalive'):
        unit['WireGuardPeer']['PersistentKeepalive'] = str(keepalive)

    return unit


def write_netdev(wireguard: dict, private: str):
    """Creates a network device."""

    unit = create_netdev_unit(wireguard, private)

    with NETDEV_UNIT_FILE.open('w') as netdev_unit_file:
        unit.write(netdev_unit_file)

    uid = getpwnam(NETDEV_OWNER).pw_uid
    gid = getgrnam(NETDEV_GROUP).gr_gid
    chown(NETDEV_UNIT_FILE, uid, gid)
    NETDEV_UNIT_FILE.chmod(NETDEV_MODE)


def create_network_unit(wireguard: dict):
    """Yields WireGuard network unit file parts."""

    unit = SystemdUnit()
    unit.add_section('Match')
    unit['Match']['Name'] = DEVNAME
    unit.add_section('Network')

    try:
        unit['Network']['Address'] = wireguard['ipaddress']
    except KeyError:
        raise ProgramError('Missing IP address for WireGuard.')

    yield unit

    for route in wireguard.get('routes') or ():
        unit = SystemdUnit()
        unit.add_section('Route')
        unit['Route']['Gateway'] = route['gateway']
        unit['Route']['Destination'] = route['destination']

        if route.get('gateway_onlink'):
            unit['Route']['GatewayOnlink'] = 'true'

        yield unit


def write_network(wireguard: dict):
    """Creates a WireGuard network unit file."""

    with NETWORK_UNIT_FILE.open('w') as network_unit_file:
        for part in create_network_unit(wireguard):
            part.write(network_unit_file)


def configure(wireguard):
    """Configures the WireGuard connection."""

    if pubkey := wireguard.get('pubkey'):
        LOGGER.warning('WireGuard already configured for pubkey %s.', pubkey)

    LOGGER.debug('Creating public / private key pair.')
    pubkey, private = keypair()
    LOGGER.debug('Installing WireGuard configuration.')
    write_netdev(wireguard, private)
    write_network(wireguard)
    return pubkey


def check(wireguard, gracetime: int = 3):
    """Checks the connection to the WireGuard server."""

    LOGGER.debug('Restarting %s.', SYSTEMD_NETWORKD)

    with CalledProcessErrorHandler('Restart of %s failed.', SYSTEMD_NETWORKD):
        systemctl('restart', SYSTEMD_NETWORKD)

    LOGGER.debug('Waiting for WireGuard to establish connection.')
    sleep(gracetime)
    LOGGER.debug('Checking WireGuard connection.')
    server = wireguard.get('server')

    if server:
        with CalledProcessErrorHandler('Cannot contact WireGuard server.'):
            ping(server)
    else:
        LOGGER.warning('No server address set. Cannot check connection.')


def remove():
    """Removes the WireGuard configuration."""

    LOGGER.debug('Removing netdev unit file.')
    NETDEV_UNIT_FILE.unlink()
    LOGGER.debug('Removing network unit file.')
    NETWORK_UNIT_FILE.unlink()
