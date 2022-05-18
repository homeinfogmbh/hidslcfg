"""WireGuard subsystem."""

from hidslcfg.wireguard.common import MTU
from hidslcfg.wireguard.disable import disable
from hidslcfg.wireguard.migrate import migrate
from hidslcfg.wireguard.setup import setup


__all__ = ['MTU', 'disable', 'migrate', 'setup']
