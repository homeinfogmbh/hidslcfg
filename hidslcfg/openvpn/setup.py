"""Configure sytem for OpenVPN."""

from argparse import Namespace
from io import BytesIO
from tarfile import open    # pylint: disable=W0622
from time import sleep

from hidslcfg.api import Client
from hidslcfg.common import LOGGER
from hidslcfg.configure import confirm, configure
from hidslcfg.cpuinfo import cpuinfo
from hidslcfg.network import get_mac_addresses
from hidslcfg.system import chown
from hidslcfg.system import efi_booted
from hidslcfg.system import ping
from hidslcfg.system import systemctl
from hidslcfg.system import CalledProcessErrorHandler

from hidslcfg.openvpn.common import CLIENT_DIR
from hidslcfg.openvpn.common import DEFAULT_SERVICE
from hidslcfg.openvpn.common import GROUP
from hidslcfg.openvpn.common import OWNER
from hidslcfg.openvpn.common import SERVER
from hidslcfg.openvpn.disable import clean


__all__ = ['setup']


def install(tarball: bytes):
    """Installs the respective VPN configuration."""

    clean()     # Clean up config beforehand.

    with BytesIO(tarball) as fileobj:
        with open('r', fileobj=fileobj) as tarfile:
            tarfile.extractall(path=CLIENT_DIR)

    chown(CLIENT_DIR, OWNER, GROUP, recursive=True)


def write_config(vpn_data: bytes, gracetime: int = 3):
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


def setup(client: Client, args: Namespace) -> None:
    """Set up a system with OpenVPN."""

    confirm(client.info(args.id), serial_number=args.serial_number,
            force=args.force)
    configure(args.id, SERVER)
    LOGGER.debug('Configuring OpenVPN.')
    write_config(client.openvpn(args.id), gracetime=args.grace_time)
    LOGGER.debug('Finalizing system.')
    client.finalize(system=args.id, sn=args.serial_number,
                    mac_addresses=list(get_mac_addresses()),
                    cpuinfo=list(cpuinfo()), efi_booted=efi_booted())
