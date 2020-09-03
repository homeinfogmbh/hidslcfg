"""Common VPN manager."""

from hidslcfg.common import LOGGER
from hidslcfg.openvpn import configure as configure_openvpn
from hidslcfg.wireguard import configure as configure_wg, check as check_wg


__all__ = ['VPNSetup']


class VPNSetup:
    """VPN connection configurator."""

    def __init__(self, client, gracetime, *, openvpn=False, wireguard=False):
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
            LOGGER.debug('Configuring OpenVPN.')
            configure_openvpn(self.client.openvpn, gracetime=self.gracetime)

        if self.wireguard:
            LOGGER.debug('Configuring WireGuard.')
            self.wireguard_config = self.client.wireguard
            self.wireguard_pubkey = configure_wg(self.wireguard_config)

        return self

    def __exit__(self, typ, value, traceback):
        """Exits a context."""
        if self.wireguard:
            LOGGER.debug('Checking WireGuard configuration.')
            check_wg(self.wireguard_config, gracetime=self.gracetime)
