"""Migrate to WireGuard."""

from subprocess import CalledProcessError
from time import sleep

from wgtools import keypair     # pylint: disable=E0401

from hidslcfg.api import Client
from hidslcfg.common import LOGGER
from hidslcfg.openvpn import OpenVPNGuard
from hidslcfg.system import get_system_id, ping
from hidslcfg.wireguard import SERVER, configure, load, remove


__all__ = ['migrate']


def test_connection(gracetime: int = 10) -> bool:
    """Tests whether the WireGuard connection works."""

    LOGGER.info('Testing connection. Please wait %i seconds.', gracetime)
    sleep(gracetime)

    try:
        ping(str(SERVER))
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
        pubkey, private = keypair()
        system = self.client.patch_system(system=get_system_id(),
                                          pubkey=pubkey)
        configure(system, private)
        return self

    def __exit__(self, *args):
        if not self.success:
            LOGGER.info('Rolling back WireGuard configuration.')
            remove()
            load()


def migrate(client: Client, *, gracetime: int = 10) -> bool:
    """Migrate from OpenVPN to WireGuard."""

    with OpenVPNGuard() as guard:
        with WireGuardMigrater(client) as migrater:
            migrater.success = guard.success = test_connection(gracetime)

    return migrater.success
