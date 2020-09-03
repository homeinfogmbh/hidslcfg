"""Global constants and configuration."""

from argparse import Namespace
from logging import DEBUG, INFO, basicConfig, getLogger
from os import geteuid
from pathlib import Path
from sys import argv
from typing import Callable

from hidslcfg.exceptions import ProgramError


__all__ = [
    'APPLICATION_SERVICE',
    'DIGSIG_DATA_DIR',
    'LOGGER',
    'LOG_FORMAT',
    'SYSTEMD_NETWORKD',
    'SYSTEMD_NETWORK_DIR',
    'UNCONFIGURED_WARNING_SERVICE',
    'init_root_script'
]


APPLICATION_SERVICE = 'application.service'
DIGSIG_DATA_DIR = Path('/usr/share/digsig')
LOG_FORMAT = '[%(levelname)s] %(name)s: %(message)s'
LOGGER = getLogger(Path(argv[0]).name)
SYSTEMD_NETWORKD = 'systemd-networkd.service'
SYSTEMD_NETWORK_DIR = Path('/etc/systemd/network')
UNCONFIGURED_WARNING_SERVICE = 'unconfigured-warning.service'


def init_root_script(args_getter: Callable) -> Namespace:
    """Initializes a script that shall be run as root."""

    args = args_getter()
    basicConfig(level=DEBUG if args.verbose else INFO, format=LOG_FORMAT)

    if geteuid() != 0:
        raise ProgramError('You need to be root to run this script!')

    return args
