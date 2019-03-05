"""OpenVPN configuration and un-configuration."""

from io import BytesIO
from ipaddress import IPv4Address
from pathlib import Path
from tarfile import open as TarFile


__all__ = ['SERVER', 'unit', 'clean', 'install']


SERVER = IPv4Address('10.8.0.1')
CLIENT_DIR = Path('/etc/openvpn/client')
DEFAULT_INSTANCE = 'terminals'
SERVICE_TEMPLATE = 'openvpn-client@{}.service'


def unit(instance=DEFAULT_INSTANCE):
    """Returns the respective OpenVPN service instance."""

    return SERVICE_TEMPLATE.format(instance)


def clean():
    """Removes OpenVPN configuration."""

    for item in CLIENT_DIR.iterdir():
        if item.is_file():
            item.unlink()


def install(vpn_data):
    """Installs the respective VPN configuration."""

    with BytesIO(vpn_data) as vpn_archive:
        with TarFile('r', fileobj=vpn_archive) as tar_file:
            tar_file.extractall(path=CLIENT_DIR)
