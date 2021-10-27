"""Migrate OpenVPN to WireGuard."""

from subprocess import CalledProcessError
from time import sleep

from hidslcfg.api import Client
from hidslcfg.common import LOGGER
from hidslcfg.openvpn.guard import OpenVPNGuard
from hidslcfg.system import get_system_id, ping

from hidslcfg.wireguard.common import SERVER
from hidslcfg.wireguard.setup import patch
from hidslcfg.wireguard.disable import disable


__all__ = ['migrate']


class WireGuardMigrater:
    """Migrates to WireGuard."""

    def __init__(self, client: Client):
        self.client = client
        self.success = False

    def __enter__(self):
        LOGGER.info('Configuring WireGuard.')
        patch(self.client, get_system_id())
        return self

    def __exit__(self, *args):
        if not self.success:
            LOGGER.info('Rolling back WireGuard configuration.')
            disable()


def test_connection(gracetime: int = 10) -> bool:
    """Tests whether the WireGuard connection works."""

    LOGGER.info('Testing connection. Please wait %i seconds.', gracetime)
    sleep(gracetime)

    try:
        ping(str(SERVER))
    except CalledProcessError:
        return False

    return True


def migrate(client: Client, *, gracetime: int = 10) -> bool:
    """Migrate from OpenVPN to WireGuard."""

    with OpenVPNGuard() as guard:
        with WireGuardMigrater(client) as migrater:
            migrater.success = guard.success = test_connection(gracetime)

    return migrater.success
