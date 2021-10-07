"""Migrate to WireGuard."""

from ipaddress import IPv6Address
from subprocess import CalledProcessError
from time import sleep

from hidslcfg.api import Client
from hidslcfg.common import LOGGER
from hidslcfg.hosts import set_ip
from hidslcfg.openvpn import OpenVPNGuard
from hidslcfg.pacman import set_server
from hidslcfg.system import get_system_id, ping
from hidslcfg.wireguard import configure, load, remove


__all__ = ['migrate']


WIREGUARD_SERVER = IPv6Address('fd56:1dda:8794:cb90:ffff:ffff:ffff:fffe')


def test_connection(gracetime: int = 10) -> bool:
    """Tests whether the WireGuard connection works."""

    sleep(gracetime)

    try:
        ping(str(WIREGUARD_SERVER))
    except CalledProcessError:
        return False

    return True


def postprocess() -> None:
    """Post-processes the WireGuard migration."""

    LOGGER.info('Updating /etc/hosts.')
    set_ip('appcmd', WIREGUARD_SERVER)
    LOGGER.info('Updating /etc/pacman.conf.')
    set_server('homeinfo', WIREGUARD_SERVER)


class WireGuardMigrater:
    """Migrates to WireGuard."""

    def __init__(self, client: Client):
        self.client = client
        self.success = False

    def __enter__(self):
        LOGGER.info('Configuring WireGuard.')
        pubkey = configure(self.client.wireguard)
        self.client.finalize({'wg_pubkey': pubkey})
        load()
        return self

    def __exit__(self, *args):
        if self.success:
            postprocess()
        else:
            LOGGER.info('Rolling back WireGuard configuration.')
            remove()
            load()


def migrate(user: str, passwd: str, *, gracetime: int = 10) -> bool:
    """Migrate from OpenVPN to WireGuard."""

    with Client(user, passwd, get_system_id()) as client:
        client.login()

        with OpenVPNGuard() as guard:
            with WireGuardMigrater(client) as migrater:
                migrater.success = guard.success = test_connection(gracetime)

    return migrater.success
