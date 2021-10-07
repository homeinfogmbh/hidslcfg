"""Migrate to WireGuard."""

from ipaddress import IPv6Address
from subprocess import CalledProcessError

from hidslcfg.api import Client
from hidslcfg.common import LOGGER
from hidslcfg.openvpn import OpenVPNGuard
from hidslcfg.system import get_system_id, ping
from hidslcfg.wireguard import configure, load, remove


__all__ = ['migrate']


WIREGUARD_SERVER = IPv6Address('fd56:1dda:8794:cb90:ffff:ffff:ffff:fffe')


def test_connection() -> bool:
    """Tests whether the WireGuard connection works."""

    try:
        ping(str(WIREGUARD_SERVER))
    except CalledProcessError:
        return False

    return True


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
        if not self.success:
            LOGGER.info('Rolling back WireGuard configuration.')
            remove()
            load()


def migrate(user: str, passwd: str) -> bool:
    """Migrate from OpenVPN to WireGuard."""

    with Client(user, passwd, get_system_id()) as client:
        with OpenVPNGuard() as openvpn_guard:
            with WireGuardMigrater(client) as migrater:
                if test_connection():
                    migrater.success = True
                    openvpn_guard.error = False
                    return True

    return False
