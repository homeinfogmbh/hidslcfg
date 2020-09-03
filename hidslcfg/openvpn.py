"""OpenVPN configuration and un-configuration."""

from io import BytesIO
from ipaddress import IPv4Address
from pathlib import Path
from tarfile import open as TarFile
from time import sleep

from hidslcfg.globals import LOGGER
from hidslcfg.system import ping, systemctl, CalledProcessErrorHandler


__all__ = ['DEFAULT_SERVICE', 'clean', 'install', 'configure']


SERVER = IPv4Address('10.8.0.1')
CLIENT_DIR = Path('/etc/openvpn/client')
DEFAULT_INSTANCE = 'terminals'
SERVICE_TEMPLATE = 'openvpn-client@{}.service'
DEFAULT_SERVICE = SERVICE_TEMPLATE.format(DEFAULT_INSTANCE)


def clean():
    """Removes OpenVPN configuration."""

    for item in CLIENT_DIR.iterdir():
        if item.is_file():
            item.unlink()


def install(vpn_data: bytes):
    """Installs the respective VPN configuration."""

    clean()     # Clean up config beforehand.

    with BytesIO(vpn_data) as vpn_archive:
        with TarFile('r', fileobj=vpn_archive) as tar_file:
            tar_file.extractall(path=CLIENT_DIR)


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
