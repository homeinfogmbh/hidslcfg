"""Operating system commands."""

from configparser import ConfigParser
from grp import getgrnam
from logging import DEBUG
from os import chown as _chown
from pathlib import Path
from pwd import getpwnam
from subprocess import DEVNULL, CalledProcessError, CompletedProcess, run
from sys import exit
from typing import Any

from hidslcfg.common import LOGGER
from hidslcfg.exceptions import ProgramError


__all__ = [
    "chown",
    "efi_booted",
    "system",
    "systemctl",
    "ping",
    "reboot",
    "rmsubtree",
    "set_hostname",
    "get_system_id",
    "CalledProcessErrorHandler",
    "ProgramErrorHandler",
    "SystemdUnit",
]


HOSTNAME = Path("/etc/hostname")
HOSTNAMECTL = Path("/usr/bin/hostnamectl")
PING = Path("/usr/bin/ping")
SYSTEMCTL = Path("/usr/bin/systemctl")
efi_booted = Path("/sys/firmware/efi").is_dir


def chown(
    path: Path, uid: int | str, gid: int | str, *, recursive: bool = False
) -> None:
    """Performs a recursive chown on the given path."""

    if isinstance(uid, str):
        uid = getpwnam(uid).pw_uid

    if isinstance(gid, str):
        gid = getgrnam(gid).gr_gid

    _chown(path, uid, gid)

    if recursive and path.is_dir():
        for child in path.iterdir():
            chown(child, uid, gid, recursive=recursive)


def system(*args: Any) -> CompletedProcess:
    """Invoke system commands."""

    output = DEVNULL if LOGGER.getEffectiveLevel() > DEBUG else None
    return run(tuple(map(str, args)), check=True, stdout=output, stderr=output)


def ping(host: str, timeout: int = 1, count: int = 5) -> CompletedProcess:
    """Pings the respective host."""

    return system(PING, "-W", timeout, "-c", count, host)


def systemctl(*args: Any) -> CompletedProcess:
    """Invokes systemctl."""

    return system(SYSTEMCTL, *args)


def reboot() -> CompletedProcess:
    """Reboots the system."""

    return systemctl("reboot")


def rmsubtree(path: Path) -> None:
    """Removes all children within the specified directory."""

    for inode in path.iterdir():
        if inode.is_dir():
            rmsubtree(inode)
            inode.rmdir()
        else:
            inode.unlink()


def set_hostname(hostname: str) -> CompletedProcess:
    """Sets the respective host name or deletes the host name file."""

    return system(HOSTNAMECTL, "set-hostname", hostname)


def get_system_id() -> int:
    """Returns the system id."""

    with HOSTNAME.open("r", encoding="ascii") as file:
        return int(file.read().strip())


class CalledProcessErrorHandler:
    """Handles subprocess errors."""

    def __init__(self, *messages: str):
        """Sets the respective error messages."""
        self.messages = messages

    def __enter__(self):
        return self

    def __exit__(self, _, exception, __):
        """Handles called process error."""
        if isinstance(exception, CalledProcessError):
            raise ProgramError("SUBPROCESS ERROR", *self.messages, exit_code=3)


class ProgramErrorHandler:
    """Catches and print program errors."""

    def __enter__(self):
        return self

    def __exit__(self, _, value: Exception, __):
        """Log program errors and exit accordingly."""
        if isinstance(value, ProgramError):
            LOGGER.critical(value.error)

            if message := str(value):
                LOGGER.error(message)

            exit(value.exit_code)


class SystemdUnit(ConfigParser):
    """A systemd unit."""

    def optionxform(self, optionstr: str) -> str | None:
        """Returns the option as stripped value."""
        if optionstr is None:
            return None

        return optionstr.strip()
