"""Disable OpenVPN."""

from hidslcfg.system import systemctl
from hidslcfg.system import CalledProcessErrorHandler

from hidslcfg.openvpn.common import CLIENT_DIR, DEFAULT_SERVICE


__all__ = ["clean", "disable"]


def clean() -> None:
    """Removes OpenVPN configuration."""

    for item in CLIENT_DIR.iterdir():
        if item.is_file():
            item.unlink()


def disable() -> None:
    """Disables OpenVPN."""

    with CalledProcessErrorHandler("Disabling of OpenVPN client failed."):
        systemctl("disable", "--now", DEFAULT_SERVICE)
