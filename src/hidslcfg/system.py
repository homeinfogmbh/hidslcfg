"""Operating system commands."""

from contextlib import suppress
from pathlib import Path
from subprocess import DEVNULL, CalledProcessError, run
from sys import exit as exit_, stderr

from hidslcfg.globals import OPTIONS
from hidslcfg.exceptions import ProgramError

__all__ = [
    'system',
    'systemctl',
    'ping',
    'hostname',
    'reboot',
    'rmsubtree',
    'CalledProcessErrorHandler',
    'ProgramErrorHandler']


SYSTEMCTL = Path('/usr/bin/systemctl')
PING = Path('/usr/bin/ping')
HOSTNAME = Path('/etc/hostname')


def system(*args):
    """Invoke system commands."""

    output = None if OPTIONS['verbose'] else DEVNULL
    cmd = [str(arg) for arg in args]
    completed_process = run(cmd, stdout=output, stderr=output)
    completed_process.check_returncode()
    return completed_process


def systemctl(*args):
    """Invokes systemctl."""

    return system(SYSTEMCTL, *args)


def ping(host, timeout=1, count=5):
    """Pings the respective host."""

    return system(PING, '-W', timeout, '-c', count, host)


def hostname(hostname_):
    """Sets the respective host name or deletes the host name file."""

    if hostname_ is None:
        with suppress(FileNotFoundError):
            HOSTNAME.unlink()
    else:
        with HOSTNAME.open('w') as file:
            file.write(hostname_)


def reboot():
    """Reboots the system."""

    return systemctl('reboot')


def rmsubtree(path):
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
        if isinstance(value, ProgramError):
            print(value, file=stderr, flush=True)
            exit_(value.exit_code)
