"""Management of /etc/hosts."""

from __future__ import annotations
from dataclasses import dataclass
from ipaddress import ip_address, IPv4Address, IPv6Address
from os import linesep
from pathlib import Path
from typing import Iterable, Iterator, Optional, Union


__all__ = ['set_ip']


HOSTS = Path('/etc/hosts')


@dataclass
class HostsEntry:
    """An entry in /etc/hosts."""

    ipaddr: Union[IPv4Address, IPv6Address]
    hostname: str
    fullname: Optional[str] = None

    def __str__(self):
        items = [str(self.ipaddr), self.hostname]

        if self.fullname is not None:
            items.append(self.fullname)

        return '\t'.join(items)

    @classmethod
    def from_string(cls, line: str) -> HostsEntry:
        """Creates a host entry from a line."""
        try:
            ipaddr, hostname, fullname = line.split()
        except ValueError:
            ipaddr, hostname = line.split()
            fullname = None

        return cls(ip_address(ipaddr), hostname, fullname)


def read_hosts() -> Iterator[Union[str, HostsEntry]]:
    """Yields host entries."""

    with HOSTS.open('r', encoding='ascii') as file:
        for line in file:
            if not (line := line.strip()) or line.startswith('#'):
                yield line
            else:
                yield HostsEntry.from_string(line)


def write_hosts(entries: Iterable[Union[str, HostsEntry]]) -> None:
    """Yields host entries."""

    with HOSTS.open('w', encoding='ascii') as file:
        file.write(linesep.join(map(str, entries)))
        file.write(linesep)


def set_ip(hostname: str, ipaddr: Union[IPv4Address, IPv6Address]):
    """Sets the IP address of a host."""

    hosts = list(read_hosts())

    for entry in hosts:
        if isinstance(entry, HostsEntry):
            if hostname in {entry.hostname, entry.fullname}:
                entry.ipaddr = ipaddr

    write_hosts(hosts)
