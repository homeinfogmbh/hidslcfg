"""WireGuard subsystem."""

from hidslcfg.wireguard.common import MTU
from hidslcfg.wireguard.disable import disable
from hidslcfg.wireguard.setup import create, patch, setup


__all__ = ["MTU", "create", "disable", "patch", "setup"]
