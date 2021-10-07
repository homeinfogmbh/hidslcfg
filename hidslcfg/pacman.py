"""Pacman config handling."""

from ipaddress import IPv4Address, IPv6Address
from os import linesep
from pathlib import Path
from re import fullmatch, sub
from typing import Callable, Iterable, Iterator, Optional, Union


__all__ = ['set_server']


PACMAN_CONF = Path('/etc/pacman.conf')
URL_PATTERN = '(http://).*(:8080/)'
SECTION_PATTERN = r'^\[(.*)\]'


def read_lines() -> Iterator[str]:
    """Reads the file's lines."""

    with PACMAN_CONF.open('r', encoding='ascii') as file:
        for line in file:
            yield line.strip()


def read_lines_with_section() -> Iterator[tuple[Optional[str], str]]:
    """Yields lines with section names."""

    section = None

    for line in read_lines():
        if match := fullmatch(SECTION_PATTERN, line):
            section = match.group(1)

        yield (section, line)


def write_lines(lines: Iterable[str]) -> None:
    """Writes the lines to the file."""

    with PACMAN_CONF.open('w', encoding='ascii') as file:
        file.write(linesep.join(lines))


def get_modifier(repo: str, addr: Union[IPv4Address, IPv6Address]) -> Callable:
    """Sets the line to the server string."""

    def modifier(item: tuple[Optional[str], str]) -> str:
        """Modifies a line within a section."""
        section, line = item

        if section == repo:
            return sub(URL_PATTERN, fr'\g<1>{addr}\g<2>', line)

        return line

    return modifier


def set_server(repo: str, addr: Union[IPv4Address, IPv6Address]):
    """Sets the server of the respective repo."""

    write_lines(map(get_modifier(repo, addr), read_lines_with_section()))
