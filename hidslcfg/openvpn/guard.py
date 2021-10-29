"""OpenVPN to WireGuard migration guard."""

from hidslcfg.common import LOGGER
from hidslcfg.configure import configure
from hidslcfg.system import systemctl, get_system_id

from hidslcfg.openvpn.common import DEFAULT_SERVICE, SERVER
from hidslcfg.openvpn.disable import disable


__all__ = ['OpenVPNGuard']


class OpenVPNGuard:
    """Disable OpenVPN and restore on failure."""

    def __init__(self):
        self.success = False

    def __enter__(self):
        LOGGER.info('Disabling and stopping OpenVPN.')
        disable()
        return self

    def __exit__(self, *args):
        if not self.success:
            LOGGER.info('Enabling and starting OpenVPN.')
            systemctl('enable', '--now', DEFAULT_SERVICE)
            configure(get_system_id(), SERVER)