"""Information about the built-in processor."""

from contextlib import suppress
from pathlib import Path
from typing import Iterator


__all__ = ['cpuinfo']


CPUINFO = Path('/proc/cpuinfo')
LIST_KEYS = {'flags', 'bugs'}
CPUInfoValue = str | int | float | list[str]


def parse(key: str, value: str) -> CPUInfoValue:
    """Parses a key / value pair."""

    if key in LIST_KEYS:
        return value.split()

    with suppress(ValueError):
        return int(value)

    with suppress(ValueError):
        return float(value)

    return value


def cpuinfo() -> Iterator[dict[str, CPUInfoValue]]:
    """Yields information about the built-in CPUs."""

    core = {}

    with CPUINFO.open('r', encoding='ascii') as file:
        for line in file:
            if line := line.strip():
                key, value = map(str.strip, line.split(':'))
                core[key] = parse(key, value)
            else:
                yield core
                core = {}
