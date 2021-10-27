"""WireGuard un-configuration."""

from contextlib import suppress

from hidslcfg.common import LOGGER

from hidslcfg.wireguard.common import NETDEV_UNIT_FILE, NETWORK_UNIT_FILE, load


__all__ = ['remove', 'disable']


def remove():
    """Removes the WireGuard configuration."""

    LOGGER.debug('Removing netdev unit file.')

    with suppress(FileNotFoundError):
        NETDEV_UNIT_FILE.unlink()

    LOGGER.debug('Removing network unit file.')

    with suppress(FileNotFoundError):
        NETWORK_UNIT_FILE.unlink()


def disable():
    """Disables WireGuard."""

    remove()
    load()
