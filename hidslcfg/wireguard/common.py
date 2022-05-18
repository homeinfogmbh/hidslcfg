"""Common constants and functions for the WireGuard subsystem."""

from ipaddress import IPv6Address

from hidslcfg.common import LOGGER, SYSTEMD_NETWORKD, SYSTEMD_NETWORK_DIR
from hidslcfg.system import systemctl
from hidslcfg.system import CalledProcessErrorHandler


__all__ = [
    'DEVNAME',
    'DESCRIPTION',
    'MTU',
    'NETDEV_UNIT_FILE',
    'NETWORK_UNIT_FILE',
    'NETDEV_OWNER',
    'NETDEV_GROUP',
    'NETDEV_MODE',
    'SERVER',
    'load'
]


DEVNAME = 'terminals'
DESCRIPTION = 'Terminal maintenance VPN.'
MTU = 1280  # bytes
NETDEV_UNIT_FILE = SYSTEMD_NETWORK_DIR.joinpath(f'{DEVNAME}.netdev')
NETWORK_UNIT_FILE = SYSTEMD_NETWORK_DIR.joinpath(f'{DEVNAME}.network')
NETDEV_OWNER = 'root'
NETDEV_GROUP = 'systemd-network'
NETDEV_MODE = 0o640
SERVER = IPv6Address('fd56:1dda:8794:cb90:ffff:ffff:ffff:fffe')


def load() -> None:
    """Establishes the connection to the WireGuard server."""

    LOGGER.debug('Restarting %s.', SYSTEMD_NETWORKD)

    with CalledProcessErrorHandler(f'Restart of {SYSTEMD_NETWORKD} failed.'):
        systemctl('restart', SYSTEMD_NETWORKD)
