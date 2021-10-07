"""OpenVPN configuration and un-configuration."""

from io import BytesIO
from ipaddress import IPv4Address
from pathlib import Path
from tarfile import open    # pylint: disable=W0622
from time import sleep

from hidslcfg.common import LOGGER
from hidslcfg.system import chown
from hidslcfg.system import ping
from hidslcfg.system import systemctl
from hidslcfg.system import CalledProcessErrorHandler


__all__ = [
    'DEFAULT_SERVICE',
    'clean',
    'disable',
    'install',
    'configure',
    'OpenVPNGuard'
]


SERVER = IPv4Address('10.8.0.1')
CLIENT_DIR = Path('/etc/openvpn/client')
DEFAULT_INSTANCE = 'terminals'
SERVICE_TEMPLATE = 'openvpn-client@{}.service'
DEFAULT_SERVICE = SERVICE_TEMPLATE.format(DEFAULT_INSTANCE)
OWNER = 'openvpn'
GROUP = 'network'


def clean():
    """Removes OpenVPN configuration."""

    for item in CLIENT_DIR.iterdir():
        if item.is_file():
            item.unlink()


def disable():
    """Disables OpenVPN."""

    with CalledProcessErrorHandler('Disabling of OpenVPN client failed.'):
        systemctl('disable', DEFAULT_SERVICE)


def install(tarball: bytes):
    """Installs the respective VPN configuration."""

    clean()     # Clean up config beforehand.

    with BytesIO(tarball) as fileobj:
        with open('r', fileobj=fileobj) as tarfile:
            tarfile.extractall(path=CLIENT_DIR)

    chown(CLIENT_DIR, OWNER, GROUP, recursive=True)


def configure(vpn_data: bytes, gracetime: int = 3):
    """Sets up the OpenVPN configuration."""

    LOGGER.debug('Installing OpenVPN configuration.')
    install(vpn_data)
    LOGGER.debug('Enabling OpenVPN.')

    with CalledProcessErrorHandler('Enabling of OpenVPN client failed.'):
        systemctl('enable', DEFAULT_SERVICE)

    LOGGER.debug('Restarting OpenVPN.')

    with CalledProcessErrorHandler('Restart of OpenVPN client failed.'):
        systemctl('restart', DEFAULT_SERVICE)

    LOGGER.debug('Waiting for OpenVPN server to start.')
    sleep(gracetime)
    LOGGER.debug('Checking OpenVPN connection.')

    with CalledProcessErrorHandler('Cannot contact OpenVPN server.'):
        ping(SERVER)


class OpenVPNGuard:
    """Disable OpenVPN and restore on failure."""

    def __init__(self):
        self.error = True

    def __enter__(self):
        systemctl('disable', '--now', DEFAULT_SERVICE)
        return self

    def __exit__(self, *args):
        if self.error:
            systemctl('enable', '--now', DEFAULT_SERVICE)
