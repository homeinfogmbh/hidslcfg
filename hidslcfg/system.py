"""Operating system commands."""

from configparser import ConfigParser
from logging import DEBUG
from pathlib import Path
from subprocess import DEVNULL, CalledProcessError, CompletedProcess, run
from sys import exit    # pylint: disable=W0622

from hidslcfg.common import LOGGER
from hidslcfg.exceptions import ProgramError


__all__ = [
    'system',
    'systemctl',
    'ping',
    'hostname',
    'reboot',
    'rmsubtree',
    'CalledProcessErrorHandler',
    'ProgramErrorHandler',
    'SystemdUnit'
]


HOSTNAMECTL = Path('/usr/bin/hostnamectl')
PING = Path('/usr/bin/ping')
SYSTEMCTL = Path('/usr/bin/systemctl')


def system(*args) -> CompletedProcess:
    """Invoke system commands."""

    if LOGGER.getEffectiveLevel() > DEBUG:
        output = DEVNULL
    else:
        output = None

    cmd = tuple(str(arg) for arg in args)
    completed_process = run(cmd, check=True, stdout=output, stderr=output)
    completed_process.check_returncode()
    return completed_process


def ping(host: str, timeout: int = 1, count: int = 5) -> CompletedProcess:
    """Pings the respective host."""

    return system(PING, '-W', timeout, '-c', count, host)


def hostname(hostname: str) -> CompletedProcess:    # pylint: disable=W0621
    """Sets the respective host name or deletes the host name file."""

    return system(HOSTNAMECTL, 'set-hostname', hostname)


def systemctl(*args) -> CompletedProcess:
    """Invokes systemctl."""

    return system(SYSTEMCTL, *args)


def reboot() -> CompletedProcess:
    """Reboots the system."""

    return systemctl('reboot')


def rmsubtree(path: Path):
    """Removes all children within the specified directory."""

    for inode in path.iterdir():
        if inode.is_dir():
            rmsubtree(inode)
            inode.rmdir()
        else:
            inode.unlink()


class CalledProcessErrorHandler:
    """Handles subprocess errors."""

    def __init__(self, *messages):
        """Sets the respective error messages."""
        self.messages = messages

    def __enter__(self):
        return self

    def __exit__(self, _, exception, __):
        """Handles called process error."""
        if isinstance(exception, CalledProcessError):
            raise ProgramError('SUBPROCESS ERROR', *self.messages, exit_code=3)


class ProgramErrorHandler:
    """Catches and print program errors."""

    def __enter__(self):
        return self

    def __exit__(self, _, value, __):
        """Log program errors and exit accordingly."""
        if isinstance(value, ProgramError):
            LOGGER.fatal(value.error)
            LOGGER.error(value)
            exit(value.exit_code)


class SystemdUnit(ConfigParser):    # pylint: disable=R0901
    """A systemd unit."""

    def optionxform(self, optionstr):
        """Returns the option as stripped value."""
        if optionstr is None:
            return None

        return optionstr.strip()
