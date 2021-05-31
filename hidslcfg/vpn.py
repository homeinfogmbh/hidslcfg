"""Common VPN manager."""

from hidslcfg.common import LOGGER
from hidslcfg.openvpn import configure as configure_openvpn
from hidslcfg.openvpn import disable as disable_openvpn
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
            self.setup_openvpn()
        elif self.wireguard:
            self.setup_wireguard()

        return self

    def __exit__(self, typ, value, traceback):
        """Exits a context."""
        if self.wireguard:
            self.finalize_wireguard()

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

    def finalize_wireguard(self):
        """Finalize WireGuard setup."""
        LOGGER.debug('Checking WireGuard configuration.')
        check_wg(self.wireguard_config, gracetime=self.gracetime)
