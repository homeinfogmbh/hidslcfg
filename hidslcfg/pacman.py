"""Pacman config handling."""

from functools import partial
from ipaddress import IPv4Address, IPv6Address
from os import linesep
from pathlib import Path
from re import sub
from typing import Iterable, Iterator, Union


PACMAN_CONF = Path('/etc/pacman.conf')
PATTERN = '(http://).*(:8080/)'


def read_lines() -> Iterator[str]:
    """Reads the file's lines."""

    with PACMAN_CONF.open('r', encoding='ascii') as file:
        for line in file:
            yield line.strip()


def write_lines(lines: Iterable[str]) -> None:
    """Writes the lines to the file."""

    with PACMAN_CONF.open('w', encoding='ascii') as file:
        file.write(linesep.join(lines))


def modify_line(line: str, server: Union[IPv4Address, IPv6Address]):
    """Sets the line to the server string."""

    return sub(PATTERN, fr'\g<1>{server}\g<2>', line)


def set_server(server: Union[IPv4Address, IPv6Address]):
    """Sets the server of the respective repo."""

    write_lines(map(partial(modify_line, server=server), read_lines()))
