"""Management of /etc/hosts."""

from __future__ import annotations
from dataclasses import dataclass
from ipaddress import ip_address, IPv4Address, IPv6Address
from os import linesep
from pathlib import Path
from typing import Iterable, Iterator


__all__ = ['set_ip']


HOSTS = Path('/etc/hosts')


@dataclass
class HostsEntry:
    """An entry in /etc/hosts."""

    ipaddr: IPv4Address | IPv6Address
    hostname: str
    short_name: str | None = None

    def __str__(self):
        items = [str(self.ipaddr), self.hostname]

        if self.short_name is not None:
            items.append(self.short_name)

        return '\t'.join(items)

    @classmethod
    def from_string(cls, line: str) -> HostsEntry:
        """Creates a host entry from a line."""
        try:
            ipaddr, hostname, short_name = line.split()
        except ValueError:
            ipaddr, hostname = line.split()
            short_name = None

        return cls(ip_address(ipaddr), hostname, short_name)


def read_hosts() -> Iterator[str | HostsEntry]:
    """Yields host entries."""

    with HOSTS.open('r', encoding='ascii') as file:
        for line in file:
            if not (line := line.strip()) or line.startswith('#'):
                yield line
            else:
                yield HostsEntry.from_string(line)


def write_hosts(entries: Iterable[str | HostsEntry]) -> None:
    """Yields host entries."""

    # Generate text before opening the file to prevent r/w race condition.
    text = linesep.join(map(str, entries))

    with HOSTS.open('w', encoding='ascii') as file:
        file.write(text)
        file.write(linesep)


def set_ip(hostname: str, ipaddr: IPv4Address | IPv6Address):
    """Sets the IP address of a host."""

    for entry in (hosts := list(read_hosts())):
        if isinstance(entry, HostsEntry):
            if hostname in {entry.hostname, entry.short_name}:
                entry.ipaddr = ipaddr

    write_hosts(hosts)
