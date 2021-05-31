"""Common VPN manager."""

from hidslcfg.api import Client
from hidslcfg.common import LOGGER
from hidslcfg.openvpn import configure as configure_openvpn
from hidslcfg.openvpn import disable as disable_openvpn
from hidslcfg.wireguard import configure as configure_wg, load


__all__ = ['VPNSetup']


class VPNSetup:
    """VPN connection configurator."""

    def __init__(self, client: Client, gracetime: int, *,
                 openvpn: bool = False, wireguard: bool = False):
        """Sets the API client, openvpn and wireguard flags."""
        self.client = client
        self.gracetime = gracetime
        self.openvpn = openvpn
        self.wireguard = wireguard
        self.wireguard_config = None
        self.wireguard_pubkey = None

    def __enter__(self):
        """Enters a context."""
        if self.openvpn:
            self.setup_openvpn()
        elif self.wireguard:
            self.setup_wireguard()

        return self

    def __exit__(self, *_):
        """Exits a context."""
        if self.wireguard:
            LOGGER.debug('Checking WireGuard configuration.')
            load()

    def setup_openvpn(self):
        """Perform OpenVPN setup."""
        LOGGER.debug('Configuring OpenVPN.')
        configure_openvpn(self.client.openvpn, gracetime=self.gracetime)

    def setup_wireguard(self):
        """Perform WireGuard setup."""
        LOGGER.debug('Configuring WireGuard.')
        disable_openvpn()
        self.wireguard_config = self.client.wireguard
        self.wireguard_pubkey = configure_wg(self.wireguard_config)
