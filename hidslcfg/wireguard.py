"""Configures a WireGuard interface."""

from ipaddress import ip_address
from ipaddress import ip_network
from ipaddress import _BaseAddress as Address
from ipaddress import _BaseNetwork as Network
from time import sleep
from typing import List, NamedTuple

from wgtools import keypair

from hidslcfg.exceptions import ProgramError
from hidslcfg.globals import LOGGER
from hidslcfg.globals import SYSTEMD_NETWORKD
from hidslcfg.globals import SYSTEMD_NETWORK_DIR
from hidslcfg.system import ping
from hidslcfg.system import systemctl
from hidslcfg.system import CalledProcessErrorHandler
from hidslcfg.system import SystemdUnit


__all__ = ['configure', 'remove']


DEVNAME = 'terminals'
DESCRIPTION = 'Terminal maintenance VPN.'
PORT = 51820
NETDEV_UNIT_FILE = SYSTEMD_NETWORK_DIR.joinpath(f'{DEVNAME}.netdev')
NETWORK_UNIT_FILE = SYSTEMD_NETWORK_DIR.joinpath(f'{DEVNAME}.network')


class Endpoint(NamedTuple):
    """A WireGuard endpoint."""

    address: Address
    port: int

    @classmethod
    def from_string(cls, string):
        """Parses an endpoint from a string."""
        address, port = string.split(':')
        address = ip_address(address)
        port = int(port)
        return cls(address, port)

    def __str__(self):
        """Returns a string representation of the endpoint."""
        return f'{self.address}:{self.port}'


def create_netdev_unit(
        private: str, server_pubkey: str, allowed_ips: List[Network],
        endpoint: Endpoint, psk: str = None):
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

    unit['WireGuardPeer']['AllowedIPs'] = ', '.join(
        str(ip) for ip in allowed_ips)
    unit['WireGuardPeer']['Endpoint'] = str(endpoint)
    return unit


def create_netdev(private: str, server_pubkey: str, allowed_ips: List[Network],
                  endpoint: Endpoint, psk: str = None):
    """Creates a network device."""

    unit = create_netdev_unit(
        private, server_pubkey, allowed_ips, endpoint, psk=psk)

    with NETDEV_UNIT_FILE.open('w') as netdev_unit_file:
        unit.write(netdev_unit_file)


def create_network_unit(ipaddress: Network, gateway: Address,
                        destination: Network):
    """Creates a WireGuard network unit file."""

    unit = SystemdUnit()
    unit.add_section('Match')
    unit['Match']['Name'] = DEVNAME
    unit.add_section('Network')
    unit['Network']['Address'] = str(ipaddress)
    unit.add_section('Route')
    unit['Route']['Gateway'] = str(gateway)
    unit['Route']['Destination'] = str(destination)
    unit['Route']['GatewayOnlink'] = 'true'
    return unit


def create_network(ipaddress: Network, gateway: Address,
                   destination: Network):
    """Creates a WireGuard network unit file."""

    unit = create_network_unit(ipaddress, gateway, destination)

    with NETWORK_UNIT_FILE.open('w') as network_unit_file:
        unit.write(network_unit_file)


def create_units(wireguard: dict, private: str):
    """Configures a WireGuard interface for the given JSON-ish settings."""

    ipaddress = wireguard.get('ipaddress')

    if not ipaddress:
        raise ProgramError('Missing IP address for WireGuard.')

    server_pubkey = wireguard.get('server_pubkey')

    if not server_pubkey:
        raise ProgramError('Missing server pubkey for WireGuard.')

    allowed_ips = wireguard.get('allowed_ips')

    if not allowed_ips:
        raise ProgramError('Missing allowed IPs for WireGuard.')

    # We need networks here, since WireGuard does not
    # function properly without the CIDR suffixes.
    allowed_ips = [ip_network(ip) for ip in allowed_ips]

    endpoint = wireguard.get('endpoint')

    if not endpoint:
        raise ProgramError('Missing endpoint for WireGuard.')

    endpoint = Endpoint.from_string(endpoint)
    psk = wireguard.get('psk')
    gateway = wireguard.get('gateway')

    if not gateway:
        raise ProgramError('Missing gateway address for WireGuard.')

    gateway = ip_address(gateway)
    destination = wireguard.get('destination')

    if not destination:
        raise ProgramError('Missing destination network for WireGuard.')

    destination = ip_network(destination)

    if pubkey := wireguard.get('pubkey'):
        LOGGER.warning('WireGuard already configured for pubkey %s.', pubkey)

    create_netdev(private, server_pubkey, allowed_ips, endpoint, psk=psk)
    create_network(ipaddress, gateway, destination)


def configure(wireguard, gracetime=3):
    """Configures the WireGuard connection."""

    LOGGER.debug('Creating public / private key pair.')
    pubkey, private = keypair()
    LOGGER.debug('Installing WireGuard configuration.')
    create_units(wireguard, private)
    LOGGER.debug('Restarting %s.', SYSTEMD_NETWORKD)

    with CalledProcessErrorHandler('Restart of OpenVPN client failed.'):
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

    return pubkey


def remove():
    """Removes the WireGuard configuration."""

    LOGGER.debug('Removing netdev unit file.')
    NETDEV_UNIT_FILE.unlink()
    LOGGER.debug('Removing network unit file.')
    NETWORK_UNIT_FILE.unlink()
