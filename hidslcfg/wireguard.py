"""Configures a WireGuard interface."""

from time import sleep
from typing import List

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


def create_netdev_unit(
        private: str, server_pubkey: str, allowed_ips: List[str],
        endpoint: str, psk: str = None, persistent_keepalive: int = None):
    """Creates a network device."""

    unit = SystemdUnit()
    unit.add_section('NetDev')
    unit['NetDev']['Name'] = DEVNAME
    unit['NetDev']['Kind'] = 'wireguard'
    unit['NetDev']['Description'] = DESCRIPTION
    unit.add_section('WireGuard')
    unit['WireGuard']['PrivateKey'] = private
    unit.add_section('WireGuardPeer')
    unit['WireGuardPeer']['PublicKey'] = server_pubkey

    if psk:
        unit['WireGuardPeer']['PresharedKey'] = psk

    unit['WireGuardPeer']['AllowedIPs'] = ', '.join(allowed_ips)
    unit['WireGuardPeer']['Endpoint'] = endpoint

    if persistent_keepalive:
        unit['WireGuardPeer']['PersistentKeepalive'] = str(
            persistent_keepalive)

    return unit


def write_netdev(
        private: str, server_pubkey: str, allowed_ips: List[str],
        endpoint: str, psk: str = None, persistent_keepalive: int = None):
    """Creates a network device."""

    unit = create_netdev_unit(
        private, server_pubkey, allowed_ips, endpoint, psk=psk,
        persistent_keepalive=persistent_keepalive)

    with NETDEV_UNIT_FILE.open('w') as netdev_unit_file:
        unit.write(netdev_unit_file)


def create_network_unit(ipaddress: str, routes: List[dict]):
    """Yields WireGuard network unit file parts."""

    unit = SystemdUnit()
    unit.add_section('Match')
    unit['Match']['Name'] = DEVNAME
    unit.add_section('Network')
    unit['Network']['Address'] = ipaddress
    yield unit

    for route in routes:
        unit = SystemdUnit()
        unit.add_section('Route')
        unit['Route']['Gateway'] = route['gateway']
        unit['Route']['Destination'] = route['destination']

        if route.get('gateway_onlink'):
            unit['Route']['GatewayOnlink'] = 'true'

        yield unit


def write_network(ipaddress: str, routes: List[dict]):
    """Creates a WireGuard network unit file."""

    with NETWORK_UNIT_FILE.open('w') as network_unit_file:
        for part in create_network_unit(ipaddress, routes):
            part.write(network_unit_file)


def create_units(wireguard: dict, private: str):
    """Configures a WireGuard interface for the given JSON-ish settings."""

    server_pubkey = wireguard.get('server_pubkey')

    if not server_pubkey:
        raise ProgramError('Missing server pubkey for WireGuard.')

    endpoint = wireguard.get('endpoint')

    if not endpoint:
        raise ProgramError('Missing endpoint for WireGuard.')

    psk = wireguard.get('psk')
    ipaddress = wireguard.get('ipaddress')

    if not ipaddress:
        raise ProgramError('Missing IP address for WireGuard.')

    routes = wireguard.get('routes')

    if not routes:
        raise ProgramError('No routes configured for WireGuard.')

    if pubkey := wireguard.get('pubkey'):
        LOGGER.warning('WireGuard already configured for pubkey %s.', pubkey)

    allowed_ips = [route['destination'] for route in routes]
    persistent_keepalive = wireguard.get('persistent_keepalive')
    write_netdev(private, server_pubkey, allowed_ips, endpoint, psk=psk,
                 persistent_keepalive=persistent_keepalive)
    write_network(ipaddress, routes)


def configure(wireguard):
    """Configures the WireGuard connection."""

    LOGGER.debug('Creating public / private key pair.')
    pubkey, private = keypair()
    LOGGER.debug('Installing WireGuard configuration.')
    create_units(wireguard, private)
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
