"""Private network discovery."""

from re import fullmatch
from typing import Iterator

from netifaces import AF_LINK, ifaddresses, interfaces


__all__ = ["get_mac_addresses"]


def get_mac_addresses(match: str = "enp\\ds\\d") -> Iterator[str]:
    """Yields the system's MAC addresses."""

    for interface in interfaces():
        if match is None or fullmatch(match, interface) is not None:
            if addresses := ifaddresses(interface).get(AF_LINK):
                for address in addresses:
                    yield address["addr"]
